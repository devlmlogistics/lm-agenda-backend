import json
import logging
import os

from sqlalchemy import text


logger = logging.getLogger(__name__)


def send_order_update(connection, author, delivery_order, message_id):
    private_key = os.environ.get("VAPID_PRIVATE_KEY")
    subject = os.environ.get("VAPID_SUBJECT")
    if not private_key or not subject:
        return

    if author["role"] == "DRIVER":
        recipient_filter = "u.role IN ('SUPERVISOR', 'OPERATIONS')"
        params = {"author_id": author["id"]}
    else:
        recipient_filter = """
            u.role = 'DRIVER' AND EXISTS (
                SELECT 1 FROM jotform.planificacion p
                WHERE trim(p.delivery_order::text) = trim(:delivery_order)
                  AND upper(trim(p.driver)) = upper(trim(u.driver_name))
            )
        """
        params = {"author_id": author["id"], "delivery_order": delivery_order}

    subscriptions = connection.execute(
        text(
            f"""
            SELECT s.id, s.endpoint, s.p256dh, s.auth
            FROM lm_agenda.push_subscriptions s
            JOIN lm_agenda.users u ON u.id = s.user_id
            WHERE u.active = TRUE AND u.id <> :author_id AND {recipient_filter}
            """
        ),
        params,
    ).mappings().all()

    try:
        from pywebpush import WebPushException, webpush
    except ImportError:
        logger.warning("pywebpush is not installed; push notifications are disabled")
        return

    payload = json.dumps(
        {
            "title": f"New update for order {delivery_order}",
            "body": f"{author['display_name']} added a new update.",
            "url": f"/#/order/{delivery_order}?message={message_id}",
        }
    )
    expired_ids = []
    for subscription in subscriptions:
        try:
            webpush(
                subscription_info={
                    "endpoint": subscription["endpoint"],
                    "keys": {
                        "p256dh": subscription["p256dh"],
                        "auth": subscription["auth"],
                    },
                },
                data=payload,
                vapid_private_key=private_key,
                vapid_claims={"sub": subject},
            )
        except WebPushException as exc:
            status = getattr(exc.response, "status_code", None)
            if status in {404, 410}:
                expired_ids.append(subscription["id"])
            else:
                logger.exception("Unable to send push notification")
    if expired_ids:
        connection.execute(
            text("DELETE FROM lm_agenda.push_subscriptions WHERE id = ANY(:ids)"),
            {"ids": expired_ids},
        )

