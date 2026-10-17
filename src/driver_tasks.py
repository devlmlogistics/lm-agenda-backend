import logging
import hmac
import hashlib
import os
from datetime import date

from sqlalchemy import create_engine, text

from src.config.db_config import conexion


logger = logging.getLogger(__name__)


SUPERVISOR_TIMEZONE = "America/Los_Angeles"


def _response(success, message, driver=None, tasks=None):
    return {
        "success": success,
        "message": message,
        "driver": driver,
        "tasks": tasks or [],
    }


def tareas_programadas_driver(codigo_driver):
    if codigo_driver is None or not str(codigo_driver).strip():
        return _response(False, "Debe ingresar un código de driver.")

    normalized_code = str(codigo_driver).strip()
    engine = create_engine(conexion)

    try:
        with engine.connect() as connection:
            driver_name = connection.execute(
                text(
                    """
                    SELECT driver
                    FROM facturacion.drivers
                    WHERE upper(trim(codigo_app)) = upper(trim(:codigo_driver))
                    LIMIT 1
                    """
                ),
                {"codigo_driver": normalized_code},
            ).scalar_one_or_none()

            if driver_name is None:
                return _response(False, "El código de driver no existe.")

            driver = {
                "codigo_driver": normalized_code,
                "name": driver_name,
            }

            rows = connection.execute(
                text(
                    """
                    SELECT delivery_order,
                           to_char(delivery_date, 'YYYY-MM-DD') AS delivery_date,
                           location_pickup_code,
                           location_drop_code,
                           movement_type,
                           pick_location,
                           drop_location,
                           CASE
                               WHEN upper(trim(movement_type)) = 'DELIVERY'
                                   THEN to_char(fecha_hora_etadrop, 'HH24:MI')
                               WHEN upper(trim(movement_type)) = 'PICKUP'
                                   THEN to_char(fecha_hora_pickup, 'HH24:MI')
                               ELSE NULL
                           END AS event_time,
                           comments
                    FROM jotform.planificacion
                    WHERE upper(trim(driver)) = upper(trim(:driver))
                      AND delivery_date >=
                          (current_timestamp AT TIME ZONE 'America/Los_Angeles')::date - 1
                    ORDER BY delivery_date ASC, delivery_order ASC
                    """
                ),
                {"driver": driver_name},
            ).mappings().all()

            tasks = [dict(row) for row in rows]
            if not tasks:
                return _response(
                    True,
                    "No hay tareas programadas para este driver desde el día anterior a la fecha actual.",
                    driver=driver,
                )

            return _response(True, None, driver=driver, tasks=tasks)
    except Exception:
        logger.exception("Error al consultar las tareas programadas del driver")
        return _response(False, "Error al procesar la solicitud.")
    finally:
        engine.dispose()


def planificacion_supervisor(
    supervisor_key, mode, selected_date=None, driver_name=None, week_scope=None
):
    expected_key = os.environ.get("SUPERVISOR_KEY", "")
    provided_key = str(supervisor_key or "")
    legacy_valid = bool(expected_key) and hmac.compare_digest(provided_key, expected_key)
    staff_valid = False
    if provided_key and not legacy_valid:
        auth_engine = create_engine(conexion)
        try:
            with auth_engine.connect() as auth_connection:
                staff_valid = bool(
                    auth_connection.execute(
                        text(
                            """
                            SELECT EXISTS (
                                SELECT 1 FROM lm_agenda.users
                                WHERE access_token_hash = :token_hash AND active = TRUE
                                  AND role IN ('SUPERVISOR', 'OPERATIONS')
                            )
                            """
                        ),
                        {"token_hash": hashlib.sha256(provided_key.encode("utf-8")).hexdigest()},
                    ).scalar()
                )
        except Exception:
            logger.exception("Unable to validate the staff access token")
        finally:
            auth_engine.dispose()
    if not legacy_valid and not staff_valid:
        return _response(False, "Acceso de supervisor no autorizado.")

    normalized_mode = str(mode or "day").strip().lower()
    if normalized_mode not in {"day", "week", "driver"}:
        return _response(False, "El modo de planificación no es válido.")

    params = {}
    if normalized_mode == "day":
        try:
            normalized_date = date.fromisoformat(str(selected_date or ""))
        except ValueError:
            return _response(False, "Debe ingresar una fecha válida.")
        date_filter = "p.delivery_date = :selected_date"
        params["selected_date"] = normalized_date
    elif normalized_mode == "week":
        normalized_week = str(week_scope or "current").strip().lower()
        if normalized_week not in {"current", "next"}:
            return _response(False, "La semana seleccionada no es válida.")
        params["week_offset"] = 0 if normalized_week == "current" else 1
        date_filter = f"""
            p.delivery_date >= (
                date_trunc('week', current_timestamp AT TIME ZONE '{SUPERVISOR_TIMEZONE}')::date
                + (:week_offset * INTERVAL '7 days')
            )
            AND p.delivery_date < (
                date_trunc('week', current_timestamp AT TIME ZONE '{SUPERVISOR_TIMEZONE}')::date
                + ((:week_offset + 1) * INTERVAL '7 days')
            )
        """
    else:
        normalized_driver = str(driver_name or "").strip()
        if not normalized_driver:
            return _response(False, "Debe seleccionar un driver.")
        date_filter = f"""
            upper(trim(p.driver)) = upper(trim(:driver))
            AND p.delivery_date >=
                (current_timestamp AT TIME ZONE '{SUPERVISOR_TIMEZONE}')::date - 1
        """
        params["driver"] = normalized_driver

    engine = create_engine(conexion)
    try:
        with engine.connect() as connection:
            drivers = connection.execute(
                text(
                    """
                    SELECT DISTINCT trim(driver) AS driver
                    FROM jotform.planificacion
                    WHERE driver IS NOT NULL AND trim(driver) <> ''
                      AND delivery_date >=
                          (current_timestamp AT TIME ZONE 'America/Los_Angeles')::date - 1
                    ORDER BY driver
                    """
                )
            ).scalars().all()

            rows = connection.execute(
                text(
                    f"""
                    SELECT p.driver,
                           p.delivery_order,
                           to_char(p.delivery_date, 'YYYY-MM-DD') AS delivery_date,
                           p.location_pickup_code,
                           p.location_drop_code,
                           p.movement_type,
                           p.pick_location,
                           p.drop_location,
                           CASE
                               WHEN upper(trim(p.movement_type)) = 'DELIVERY'
                                   THEN to_char(p.fecha_hora_etadrop, 'HH24:MI')
                               WHEN upper(trim(p.movement_type)) = 'PICKUP'
                                   THEN to_char(p.fecha_hora_pickup, 'HH24:MI')
                               ELSE NULL
                           END AS event_time,
                           p.comments
                    FROM jotform.planificacion p
                    WHERE {date_filter}
                    ORDER BY p.delivery_date ASC,
                             event_time ASC NULLS LAST,
                             p.driver ASC,
                             p.delivery_order ASC
                    """
                ),
                params,
            ).mappings().all()

            return {
                "success": True,
                "message": None if rows else "No hay trabajos para el filtro seleccionado.",
                "mode": normalized_mode,
                "week": normalized_week if normalized_mode == "week" else None,
                "drivers": drivers,
                "tasks": [dict(row) for row in rows],
            }
    except Exception:
        logger.exception("Error al consultar la planificación del supervisor")
        return _response(False, "Error al procesar la solicitud.")
    finally:
        engine.dispose()
