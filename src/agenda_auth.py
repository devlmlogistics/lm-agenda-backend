import hashlib
import hmac
import secrets

from sqlalchemy import text


def hash_token(token):
    return hashlib.sha256(str(token).encode("utf-8")).hexdigest()


def new_access_token():
    return secrets.token_urlsafe(32)


def authenticate_staff(connection, token):
    normalized = str(token or "").strip()
    if not normalized:
        return None
    user = connection.execute(
        text(
            """
            SELECT id, display_name, role, driver_code, driver_name
            FROM lm_agenda.users
            WHERE access_token_hash = :token_hash AND active = TRUE
              AND role IN ('SUPERVISOR', 'OPERATIONS')
            """
        ),
        {"token_hash": hash_token(normalized)},
    ).mappings().first()
    if user:
        connection.execute(
            text("UPDATE lm_agenda.users SET last_seen_at = now() WHERE id = :id"),
            {"id": user["id"]},
        )
    return dict(user) if user else None


def authenticate_driver(connection, driver_code):
    normalized = str(driver_code or "").strip()
    if not normalized:
        return None
    driver_name = connection.execute(
        text(
            """
            SELECT driver FROM facturacion.drivers
            WHERE upper(trim(codigo_app)) = upper(trim(:code))
            LIMIT 1
            """
        ),
        {"code": normalized},
    ).scalar_one_or_none()
    if not driver_name:
        return None
    user = connection.execute(
        text(
            """
            INSERT INTO lm_agenda.users
                (display_name, role, driver_code, driver_name, last_seen_at)
            VALUES (:name, 'DRIVER', :code, :name, now())
            ON CONFLICT (upper(trim(driver_code))) WHERE driver_code IS NOT NULL
            DO UPDATE SET display_name = EXCLUDED.display_name,
                          driver_name = EXCLUDED.driver_name,
                          active = TRUE,
                          last_seen_at = now(),
                          updated_at = now()
            RETURNING id, display_name, role, driver_code, driver_name
            """
        ),
        {"name": driver_name, "code": normalized},
    ).mappings().one()
    return dict(user)


def authenticate_request(connection, headers):
    staff = authenticate_staff(connection, headers.get("X-Access-Token"))
    if staff:
        return staff
    return authenticate_driver(connection, headers.get("X-Driver-Code"))


def can_access_order(connection, user, delivery_order):
    if user["role"] in {"SUPERVISOR", "OPERATIONS"}:
        return True
    return connection.execute(
        text(
            """
            SELECT EXISTS (
                SELECT 1 FROM jotform.planificacion
                WHERE trim(delivery_order::text) = trim(:delivery_order)
                  AND upper(trim(driver)) = upper(trim(:driver_name))
            )
            """
        ),
        {"delivery_order": delivery_order, "driver_name": user["driver_name"]},
    ).scalar()

