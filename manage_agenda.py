import argparse
import logging
import os
from pathlib import Path

from sqlalchemy import create_engine, text

from src.agenda_auth import hash_token, new_access_token
from src.config.db_config import conexion
from src.oracle_storage import delete_object


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("manage_agenda")


def migrate():
    sql_path = Path(__file__).parent / "sql" / "001_lm_agenda_communications.sql"
    engine = create_engine(conexion)
    with engine.begin() as connection:
        connection.exec_driver_sql(sql_path.read_text(encoding="utf-8"))
    engine.dispose()
    logger.info("Agenda schema is ready")


def bootstrap_supervisor(name):
    token = new_access_token()
    engine = create_engine(conexion)
    with engine.begin() as connection:
        existing = connection.execute(
            text(
                """
                SELECT id FROM lm_agenda.users
                WHERE role = 'SUPERVISOR' AND upper(display_name) = upper(:name)
                """
            ),
            {"name": name},
        ).scalar_one_or_none()
        if existing:
            connection.execute(
                text("UPDATE lm_agenda.users SET access_token_hash=:hash, active=TRUE, updated_at=now() WHERE id=:id"),
                {"hash": hash_token(token), "id": existing},
            )
        else:
            connection.execute(
                text(
                    "INSERT INTO lm_agenda.users (display_name, role, access_token_hash) VALUES (:name, 'SUPERVISOR', :hash)"
                ),
                {"name": name, "hash": hash_token(token)},
            )
    engine.dispose()
    print(token)


def cleanup():
    engine = create_engine(conexion)
    removed_orders = 0
    removed_files = 0
    with engine.begin() as connection:
        retention_days = int(
            connection.execute(
                text("SELECT value FROM lm_agenda.settings WHERE key='retention_days'")
            ).scalar_one()
        )
        orders = connection.execute(
            text(
                """
                SELECT delivery_order
                FROM lm_agenda.messages
                GROUP BY delivery_order
                HAVING max(created_at) < now() - (:days * interval '1 day')
                """
            ),
            {"days": retention_days},
        ).scalars().all()
        for delivery_order in orders:
            objects = connection.execute(
                text(
                    """
                    SELECT a.object_key FROM lm_agenda.attachments a
                    JOIN lm_agenda.messages m ON m.id = a.message_id
                    WHERE m.delivery_order = :delivery_order
                    """
                ),
                {"delivery_order": delivery_order},
            ).scalars().all()
            for object_key in objects:
                try:
                    delete_object(object_key)
                    removed_files += 1
                except Exception:
                    logger.exception("Object cleanup failed; database records were retained")
                    raise
            connection.execute(
                text("DELETE FROM lm_agenda.messages WHERE delivery_order = :delivery_order"),
                {"delivery_order": delivery_order},
            )
            removed_orders += 1
        connection.execute(
            text(
                """
                INSERT INTO lm_agenda.audit_log (action, target_type, details)
                VALUES ('RETENTION_CLEANUP', 'SYSTEM', jsonb_build_object(
                    'orders', :orders, 'files', :files, 'retention_days', :days))
                """
            ),
            {"orders": removed_orders, "files": removed_files, "days": retention_days},
        )
    engine.dispose()
    logger.info("Cleanup completed: %s orders, %s files", removed_orders, removed_files)


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("migrate")
    bootstrap = sub.add_parser("bootstrap-supervisor")
    bootstrap.add_argument("--name", default="FROMERO")
    sub.add_parser("cleanup")
    args = parser.parse_args()
    if args.command == "migrate":
        migrate()
    elif args.command == "bootstrap-supervisor":
        bootstrap_supervisor(args.name)
    else:
        cleanup()


if __name__ == "__main__":
    main()

