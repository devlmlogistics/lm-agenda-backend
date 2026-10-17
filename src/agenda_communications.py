import logging
import os
import uuid
from pathlib import Path

from sqlalchemy import create_engine, text

from src.agenda_auth import (
    authenticate_request,
    authenticate_staff,
    can_access_order,
    hash_token,
    new_access_token,
)
from src.config.db_config import conexion
from src.oracle_storage import delete_object, get_object, put_object
from src.push_notifications import send_order_update


logger = logging.getLogger(__name__)
MAX_FILE_BYTES = 15 * 1024 * 1024
MAX_FILES_PER_MESSAGE = 10


def _engine():
    return create_engine(conexion)


def _error(message, status=400):
    return {"success": False, "message": message}, status


def _detect_type(data):
    if data.startswith(b"%PDF-"):
        return "application/pdf", ".pdf"
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg", ".jpg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png", ".png"
    if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        return "image/webp", ".webp"
    if len(data) > 12 and data[4:8] == b"ftyp" and data[8:12] in {
        b"heic", b"heix", b"hevc", b"hevx", b"mif1"
    }:
        return "image/heic", ".heic"
    return None, None


def _serialize_message(row, attachments):
    item = dict(row)
    for key in ("created_at", "updated_at", "deleted_at"):
        if item.get(key):
            item[key] = item[key].isoformat()
    item["attachments"] = attachments.get(item["id"], [])
    if item.get("deleted_at"):
        item["body"] = None
        item["attachments"] = []
    return item


def _load_messages(connection, delivery_order, user_id):
    rows = connection.execute(
        text(
            """
            SELECT m.id, m.delivery_order, m.body, m.created_at, m.updated_at,
                   m.deleted_at, u.id AS author_id, u.display_name AS author_name,
                   u.role AS author_role, (u.id = :user_id) AS own,
                   EXISTS (
                       SELECT 1 FROM lm_agenda.message_reads r
                       WHERE r.message_id = m.id AND r.user_id = :user_id
                   ) AS read
            FROM lm_agenda.messages m
            JOIN lm_agenda.users u ON u.id = m.author_user_id
            WHERE trim(m.delivery_order) = trim(:delivery_order)
            ORDER BY m.created_at ASC, m.id ASC
            """
        ),
        {"delivery_order": delivery_order, "user_id": user_id},
    ).mappings().all()
    message_ids = [row["id"] for row in rows if not row["deleted_at"]]
    by_message = {}
    if message_ids:
        files = connection.execute(
            text(
                """
                SELECT id, message_id, original_filename, content_type, size_bytes
                FROM lm_agenda.attachments
                WHERE message_id = ANY(:message_ids) AND deleted_at IS NULL
                ORDER BY id
                """
            ),
            {"message_ids": message_ids},
        ).mappings().all()
        for file in files:
            item = dict(file)
            item["download_url"] = f"/agenda/attachments/{item['id']}"
            by_message.setdefault(item.pop("message_id"), []).append(item)
    return [_serialize_message(row, by_message) for row in rows]


def list_messages(headers, delivery_order):
    engine = _engine()
    try:
        with engine.begin() as connection:
            user = authenticate_request(connection, headers)
            if not user:
                return _error("Unauthorized.", 401)
            if not can_access_order(connection, user, delivery_order):
                return _error("You cannot access this order.", 403)
            messages = _load_messages(connection, str(delivery_order), user["id"])
            connection.execute(
                text(
                    """
                    INSERT INTO lm_agenda.message_reads (message_id, user_id)
                    SELECT id, :user_id FROM lm_agenda.messages
                    WHERE trim(delivery_order) = trim(:delivery_order)
                    ON CONFLICT (message_id, user_id)
                    DO UPDATE SET read_at = now()
                    """
                ),
                {"user_id": user["id"], "delivery_order": delivery_order},
            )
            return {"success": True, "user": user, "messages": messages}, 200
    except Exception:
        logger.exception("Unable to list order messages")
        return _error("Unable to retrieve the conversation.", 500)
    finally:
        engine.dispose()


def create_message(headers, delivery_order, body, files):
    normalized_body = str(body or "").strip()
    files = list(files or [])
    if not normalized_body and not files:
        return _error("Add a comment or an attachment.")
    if len(normalized_body) > 10000:
        return _error("The comment is too long.")
    if len(files) > MAX_FILES_PER_MESSAGE:
        return _error(f"A message can contain up to {MAX_FILES_PER_MESSAGE} files.")

    prepared = []
    for uploaded in files:
        data = uploaded.read(MAX_FILE_BYTES + 1)
        if not data:
            return _error("Empty files are not allowed.")
        if len(data) > MAX_FILE_BYTES:
            return _error("Each file must be 15 MB or smaller.")
        content_type, extension = _detect_type(data)
        if not content_type:
            return _error("Only images and PDF files are allowed.")
        safe_name = Path(uploaded.filename or f"attachment{extension}").name[:255]
        object_key = f"{os.environ.get('OCI_OBJECT_PREFIX', 'staging').strip('/')}/orders/{delivery_order}/{uuid.uuid4().hex}{extension}"
        prepared.append((safe_name, content_type, data, object_key))

    engine = _engine()
    uploaded_keys = []
    try:
        with engine.begin() as connection:
            user = authenticate_request(connection, headers)
            if not user:
                return _error("Unauthorized.", 401)
            if not can_access_order(connection, user, delivery_order):
                return _error("You cannot access this order.", 403)
            message_id = connection.execute(
                text(
                    """
                    INSERT INTO lm_agenda.messages (delivery_order, author_user_id, body)
                    VALUES (:delivery_order, :user_id, :body)
                    RETURNING id
                    """
                ),
                {
                    "delivery_order": str(delivery_order),
                    "user_id": user["id"],
                    "body": normalized_body or None,
                },
            ).scalar_one()
            for filename, content_type, data, object_key in prepared:
                put_object(object_key, data, content_type)
                uploaded_keys.append(object_key)
                connection.execute(
                    text(
                        """
                        INSERT INTO lm_agenda.attachments
                            (message_id, object_key, original_filename, content_type, size_bytes)
                        VALUES (:message_id, :object_key, :filename, :content_type, :size)
                        """
                    ),
                    {
                        "message_id": message_id,
                        "object_key": object_key,
                        "filename": filename,
                        "content_type": content_type,
                        "size": len(data),
                    },
                )
            connection.execute(
                text(
                    "INSERT INTO lm_agenda.message_reads (message_id, user_id) VALUES (:message_id, :user_id)"
                ),
                {"message_id": message_id, "user_id": user["id"]},
            )
            send_order_update(connection, user, str(delivery_order), message_id)
            return {
                "success": True,
                "message_id": message_id,
                "messages": _load_messages(connection, str(delivery_order), user["id"]),
            }, 201
    except Exception:
        logger.exception("Unable to create order message")
        for object_key in uploaded_keys:
            try:
                delete_object(object_key)
            except Exception:
                logger.exception("Unable to rollback uploaded object %s", object_key)
        return _error("Unable to publish the update.", 500)
    finally:
        engine.dispose()


def update_message(headers, message_id, body):
    normalized_body = str(body or "").strip()
    if not normalized_body or len(normalized_body) > 10000:
        return _error("Enter a valid comment.")
    engine = _engine()
    try:
        with engine.begin() as connection:
            user = authenticate_request(connection, headers)
            if not user:
                return _error("Unauthorized.", 401)
            updated = connection.execute(
                text(
                    """
                    UPDATE lm_agenda.messages
                    SET body = :body, updated_at = now()
                    WHERE id = :message_id AND author_user_id = :user_id
                      AND deleted_at IS NULL
                    RETURNING delivery_order
                    """
                ),
                {"body": normalized_body, "message_id": message_id, "user_id": user["id"]},
            ).scalar_one_or_none()
            if not updated:
                return _error("You can only edit your own active posts.", 403)
            return {"success": True}, 200
    finally:
        engine.dispose()


def delete_message(headers, message_id):
    engine = _engine()
    try:
        with engine.begin() as connection:
            user = authenticate_request(connection, headers)
            if not user:
                return _error("Unauthorized.", 401)
            deleted = connection.execute(
                text(
                    """
                    UPDATE lm_agenda.messages
                    SET body = NULL, deleted_at = now(), updated_at = now()
                    WHERE id = :message_id AND author_user_id = :user_id
                      AND deleted_at IS NULL
                    RETURNING id
                    """
                ),
                {"message_id": message_id, "user_id": user["id"]},
            ).scalar_one_or_none()
            if not deleted:
                return _error("You can only delete your own active posts.", 403)
            connection.execute(
                text("UPDATE lm_agenda.attachments SET deleted_at = now() WHERE message_id = :id"),
                {"id": message_id},
            )
            return {"success": True}, 200
    finally:
        engine.dispose()


def download_attachment(headers, attachment_id):
    engine = _engine()
    try:
        with engine.begin() as connection:
            user = authenticate_request(connection, headers)
            if not user:
                return None, None, None, 401
            row = connection.execute(
                text(
                    """
                    SELECT a.object_key, a.original_filename, a.content_type, m.delivery_order
                    FROM lm_agenda.attachments a
                    JOIN lm_agenda.messages m ON m.id = a.message_id
                    WHERE a.id = :id AND a.deleted_at IS NULL AND m.deleted_at IS NULL
                    """
                ),
                {"id": attachment_id},
            ).mappings().first()
            if not row or not can_access_order(connection, user, row["delivery_order"]):
                return None, None, None, 404
            return get_object(row["object_key"]), row["original_filename"], row["content_type"], 200
    finally:
        engine.dispose()


def unread_counts(headers):
    engine = _engine()
    try:
        with engine.begin() as connection:
            user = authenticate_request(connection, headers)
            if not user:
                return _error("Unauthorized.", 401)
            if user["role"] == "DRIVER":
                access_clause = """
                    AND EXISTS (SELECT 1 FROM jotform.planificacion p
                        WHERE trim(p.delivery_order::text) = trim(m.delivery_order)
                          AND upper(trim(p.driver)) = upper(trim(:driver_name)))
                """
            else:
                access_clause = ""
            rows = connection.execute(
                text(
                    f"""
                    SELECT m.delivery_order, count(*)::int AS unread
                    FROM lm_agenda.messages m
                    WHERE m.author_user_id <> :user_id AND m.deleted_at IS NULL
                      AND NOT EXISTS (SELECT 1 FROM lm_agenda.message_reads r
                          WHERE r.message_id = m.id AND r.user_id = :user_id)
                      {access_clause}
                    GROUP BY m.delivery_order
                    """
                ),
                {"user_id": user["id"], "driver_name": user.get("driver_name")},
            ).mappings().all()
            return {"success": True, "counts": {r["delivery_order"]: r["unread"] for r in rows}}, 200
    finally:
        engine.dispose()


def list_users(headers):
    engine = _engine()
    try:
        with engine.begin() as connection:
            user = authenticate_staff(connection, headers.get("X-Access-Token"))
            if not user or user["role"] != "SUPERVISOR":
                return _error("Supervisor access is required.", 403)
            rows = connection.execute(
                text(
                    """
                    SELECT id, display_name, role, active, created_at, last_seen_at
                    FROM lm_agenda.users WHERE role IN ('SUPERVISOR', 'OPERATIONS')
                    ORDER BY display_name
                    """
                )
            ).mappings().all()
            return {"success": True, "users": [dict(row) for row in rows]}, 200
    finally:
        engine.dispose()


def create_user(headers, display_name, role):
    normalized_role = str(role or "").upper()
    normalized_name = str(display_name or "").strip()
    if not normalized_name or normalized_role not in {"SUPERVISOR", "OPERATIONS"}:
        return _error("Enter a name and a valid role.")
    engine = _engine()
    try:
        with engine.begin() as connection:
            actor = authenticate_staff(connection, headers.get("X-Access-Token"))
            if not actor or actor["role"] != "SUPERVISOR":
                return _error("Supervisor access is required.", 403)
            token = new_access_token()
            user_id = connection.execute(
                text(
                    """
                    INSERT INTO lm_agenda.users (display_name, role, access_token_hash)
                    VALUES (:name, :role, :token_hash) RETURNING id
                    """
                ),
                {"name": normalized_name, "role": normalized_role, "token_hash": hash_token(token)},
            ).scalar_one()
            return {"success": True, "id": user_id, "access_token": token}, 201
    finally:
        engine.dispose()


def update_user(headers, user_id, active=None, regenerate=False):
    engine = _engine()
    try:
        with engine.begin() as connection:
            actor = authenticate_staff(connection, headers.get("X-Access-Token"))
            if not actor or actor["role"] != "SUPERVISOR":
                return _error("Supervisor access is required.", 403)
            if actor["id"] == user_id and active is False:
                return _error("You cannot deactivate your own account.")
            token = new_access_token() if regenerate else None
            updated = connection.execute(
                text(
                    """
                    UPDATE lm_agenda.users
                    SET active = COALESCE(:active, active),
                        access_token_hash = CASE WHEN :token_hash IS NULL THEN access_token_hash ELSE :token_hash END,
                        updated_at = now()
                    WHERE id = :id AND role IN ('SUPERVISOR', 'OPERATIONS')
                    RETURNING id
                    """
                ),
                {
                    "id": user_id,
                    "active": active,
                    "token_hash": hash_token(token) if token else None,
                },
            ).scalar_one_or_none()
            if not updated:
                return _error("User not found.", 404)
            return {"success": True, "access_token": token}, 200
    finally:
        engine.dispose()


def retention_settings(headers, new_days=None):
    engine = _engine()
    try:
        with engine.begin() as connection:
            user = authenticate_staff(connection, headers.get("X-Access-Token"))
            if not user:
                return _error("Staff access is required.", 403)
            if new_days is not None:
                if user["role"] != "SUPERVISOR":
                    return _error("Supervisor access is required.", 403)
                try:
                    days = int(new_days)
                except (TypeError, ValueError):
                    return _error("Retention must be a number of days.")
                if days < 7 or days > 3650:
                    return _error("Retention must be between 7 and 3650 days.")
                connection.execute(
                    text(
                        """
                        INSERT INTO lm_agenda.settings (key, value, updated_by, updated_at)
                        VALUES ('retention_days', :days, :user_id, now())
                        ON CONFLICT (key) DO UPDATE
                        SET value = EXCLUDED.value, updated_by = EXCLUDED.updated_by, updated_at = now()
                        """
                    ),
                    {"days": str(days), "user_id": user["id"]},
                )
            days = int(connection.execute(text("SELECT value FROM lm_agenda.settings WHERE key='retention_days'")).scalar_one())
            return {"success": True, "retention_days": days, "can_edit": user["role"] == "SUPERVISOR"}, 200
    finally:
        engine.dispose()


def save_push_subscription(headers, subscription):
    try:
        endpoint = subscription["endpoint"]
        p256dh = subscription["keys"]["p256dh"]
        auth = subscription["keys"]["auth"]
    except (KeyError, TypeError):
        return _error("Invalid push subscription.")
    engine = _engine()
    try:
        with engine.begin() as connection:
            user = authenticate_request(connection, headers)
            if not user:
                return _error("Unauthorized.", 401)
            connection.execute(
                text(
                    """
                    INSERT INTO lm_agenda.push_subscriptions (user_id, endpoint, p256dh, auth)
                    VALUES (:user_id, :endpoint, :p256dh, :auth)
                    ON CONFLICT (endpoint) DO UPDATE
                    SET user_id = EXCLUDED.user_id, p256dh = EXCLUDED.p256dh,
                        auth = EXCLUDED.auth, last_used_at = now()
                    """
                ),
                {"user_id": user["id"], "endpoint": endpoint, "p256dh": p256dh, "auth": auth},
            )
            return {"success": True}, 200
    finally:
        engine.dispose()


def public_push_config():
    return {
        "success": True,
        "enabled": bool(os.environ.get("VAPID_PUBLIC_KEY")),
        "public_key": os.environ.get("VAPID_PUBLIC_KEY"),
    }, 200


def current_user(headers):
    engine = _engine()
    try:
        with engine.begin() as connection:
            user = authenticate_request(connection, headers)
            if not user:
                return _error("Unauthorized.", 401)
            return {"success": True, "user": user}, 200
    finally:
        engine.dispose()

