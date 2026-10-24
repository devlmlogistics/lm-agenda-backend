import hmac
import logging
import os
from datetime import date

from sqlalchemy import create_engine, text

from src.config.db_config import conexion


logger = logging.getLogger(__name__)
TIMEZONE = "America/Los_Angeles"
RECENT_MINUTES = 15


def _unauthorized():
    return {"success": False, "message": "Dashboard access is not authorized.", "tasks": []}


def _status(completed_at, has_error):
    if has_error:
        return {"state": "error", "completed_at": None}
    if completed_at:
        return {"state": "completed", "completed_at": completed_at.isoformat()}
    return {"state": "pending", "completed_at": None}


def dashboard_transportes(token, selected_date=None):
    expected_token = os.environ.get("DASHBOARD_KEY", "")
    if not expected_token or not hmac.compare_digest(str(token or ""), expected_token):
        return _unauthorized()

    try:
        requested_date = date.fromisoformat(str(selected_date or "")) if selected_date else None
    except ValueError:
        return {"success": False, "message": "Enter a valid date.", "tasks": []}

    engine = create_engine(conexion)
    try:
        with engine.connect() as connection:
            rows = connection.execute(
                text(
                    f"""
                    WITH plan AS (
                        SELECT p.*,
                               d.id_device_gps,
                               (current_timestamp AT TIME ZONE '{TIMEZONE}')::date AS today
                        FROM jotform.planificacion p
                        LEFT JOIN facturacion.drivers d
                          ON upper(trim(d.driver)) = upper(trim(p.driver))
                        WHERE (:selected_date IS NULL OR p.delivery_date = :selected_date)
                    )
                    SELECT plan.driver,
                           plan.delivery_order,
                           to_char(plan.delivery_date, 'YYYY-MM-DD') AS delivery_date,
                           plan.id_transaction,
                           plan.pick_location,
                           plan.drop_location,
                           plan.movement_type,
                           plan.location_pickup_code,
                           plan.location_drop_code,
                           plan.fecha_hora_pickup,
                           plan.fecha_hora_etadrop,
                           plan.comments,
                           plan.today,
                           eto.pickup_empty_at,
                           eto.pickup_checkin_at,
                           eto.pickup_checkout_at,
                           eto.dropoff_checkin_at,
                           eto.dropoff_checkout_at,
                           eto.return_empty_at,
                           eto.has_error AS e2open_error,
                           gps.fecha_hora_local AS gps_date_time,
                           gps.city AS gps_city,
                           gps.postal_code AS gps_postal_code,
                           gps.speed_mph,
                           gps.remaining_distance_mi,
                           gps.fecha_hora_eta AS gps_eta,
                           gps.gps_active,
                           gps.has_error AS gps_error,
                           GREATEST(
                               eto.latest_event_at,
                               gps.fecha_hora_local,
                               plan.fecha_hora_pickup,
                               plan.fecha_hora_etadrop
                           ) AS last_updated_at,
                           GREATEST(
                               eto.latest_event_at,
                               gps.fecha_hora_local,
                               plan.fecha_hora_pickup,
                               plan.fecha_hora_etadrop
                           ) >= current_timestamp AT TIME ZONE '{TIMEZONE}' - INTERVAL '{RECENT_MINUTES} minutes' AS changed_recently
                    FROM plan
                    LEFT JOIN LATERAL (
                        SELECT
                            MAX(e.fecha_hora_local) FILTER (WHERE upper(trim(coalesce(e.formulario, ''))) = 'PICKUP_EMPTY_CHIQUITA-OXNARD' AND upper(trim(coalesce(e.estado, ''))) = 'PROCESADO') AS pickup_empty_at,
                            MAX(e.fecha_hora_local) FILTER (WHERE upper(trim(coalesce(e.formulario, ''))) = 'CHECK-IN_CHIQUITA-OXNARD' AND upper(trim(coalesce(e.estado, ''))) = 'PROCESADO') AS pickup_checkin_at,
                            MAX(e.fecha_hora_local) FILTER (WHERE upper(trim(coalesce(e.formulario, ''))) = 'CHECK-OUT_CHIQUITA-OXNARD' AND upper(trim(coalesce(e.estado, ''))) = 'PROCESADO') AS pickup_checkout_at,
                            MAX(e.fecha_hora_local) FILTER (WHERE upper(trim(coalesce(e.formulario, ''))) = 'CHECK-IN_WALMART/KROGER' AND upper(trim(coalesce(e.estado, ''))) = 'PROCESADO') AS dropoff_checkin_at,
                            MAX(e.fecha_hora_local) FILTER (WHERE upper(trim(coalesce(e.formulario, ''))) = 'CHECK-OUT_WALMART/KROGER' AND upper(trim(coalesce(e.estado, ''))) = 'PROCESADO') AS dropoff_checkout_at,
                            MAX(e.fecha_hora_local) FILTER (WHERE upper(trim(coalesce(e.formulario, ''))) = 'RETURN_EMPTY_CHIQUITA-OXNARD' AND upper(trim(coalesce(e.estado, ''))) = 'PROCESADO') AS return_empty_at,
                            COALESCE(bool_or(upper(trim(coalesce(e.formulario, ''))) = 'PICKUP_EMPTY_CHIQUITA-OXNARD' AND upper(trim(coalesce(e.estado, ''))) = 'ERROR'), false) AS pickup_empty_error,
                            COALESCE(bool_or(upper(trim(coalesce(e.formulario, ''))) = 'CHECK-IN_CHIQUITA-OXNARD' AND upper(trim(coalesce(e.estado, ''))) = 'ERROR'), false) AS pickup_checkin_error,
                            COALESCE(bool_or(upper(trim(coalesce(e.formulario, ''))) = 'CHECK-OUT_CHIQUITA-OXNARD' AND upper(trim(coalesce(e.estado, ''))) = 'ERROR'), false) AS pickup_checkout_error,
                            COALESCE(bool_or(upper(trim(coalesce(e.formulario, ''))) = 'CHECK-IN_WALMART/KROGER' AND upper(trim(coalesce(e.estado, ''))) = 'ERROR'), false) AS dropoff_checkin_error,
                            COALESCE(bool_or(upper(trim(coalesce(e.formulario, ''))) = 'CHECK-OUT_WALMART/KROGER' AND upper(trim(coalesce(e.estado, ''))) = 'ERROR'), false) AS dropoff_checkout_error,
                            COALESCE(bool_or(upper(trim(coalesce(e.formulario, ''))) = 'RETURN_EMPTY_CHIQUITA-OXNARD' AND upper(trim(coalesce(e.estado, ''))) = 'ERROR'), false) AS return_empty_error,
                            MAX(e.fecha_hora_local) AS latest_event_at,
                            COALESCE(bool_or(upper(trim(coalesce(e.estado, ''))) = 'ERROR'), false) AS has_error
                        FROM jotform.e_to_open e
                        WHERE e.id_transaction = plan.id_transaction
                          AND upper(trim(coalesce(e.formulario, ''))) <> 'SUPERVISOR_MESSAGE_FOR_E2OPEN'
                          AND upper(trim(coalesce(e.estado, ''))) <> 'ANULADO'
                    ) eto ON TRUE
                    LEFT JOIN LATERAL (
                        SELECT g.fecha_hora_local,
                               g.city,
                               g.postal_code,
                               round((g.speed * 1.151)::numeric, 2)::double precision AS speed_mph,
                               round((g.distancia_por_recorrer / 1609.344)::numeric, 2)::double precision AS remaining_distance_mi,
                               CASE WHEN g.delayed THEN g.fecha_hora_etadrop ELSE g.fecha_hora_eta END AS fecha_hora_eta,
                               g.fecha_hora_local >= current_timestamp AT TIME ZONE '{TIMEZONE}' - INTERVAL '{RECENT_MINUTES} minutes' AS gps_active,
                               upper(trim(coalesce(g.estado, ''))) = 'ERROR' AS has_error
                        FROM jotform.gps g
                        WHERE g.id_transaction = plan.id_transaction
                          AND (plan.id_device_gps IS NULL OR g.id_device = plan.id_device_gps)
                        ORDER BY g.fecha_hora_local DESC NULLS LAST, g.id_gps DESC
                        LIMIT 1
                    ) gps ON TRUE
                    WHERE (:selected_date IS NOT NULL OR plan.delivery_date >= plan.today)
                      AND (
                          (:selected_date IS NOT NULL AND :selected_date <> plan.today)
                          OR NOT (
                              eto.return_empty_at IS NOT NULL
                              OR eto.dropoff_checkout_at IS NOT NULL
                          )
                      )
                    ORDER BY plan.driver, COALESCE(plan.fecha_hora_pickup, plan.fecha_hora_etadrop), plan.delivery_order
                    """
                ),
                {"selected_date": requested_date},
            ).mappings().all()

            tasks = []
            for row in rows:
                item = dict(row)
                movement_type = str(item.get("movement_type") or "").strip().upper()
                pickup_empty = _status(item.pop("pickup_empty_at"), bool(item.pop("pickup_empty_error")))
                pickup_checkin = _status(item.pop("pickup_checkin_at"), bool(item.pop("pickup_checkin_error")))
                pickup_checkout = _status(item.pop("pickup_checkout_at"), bool(item.pop("pickup_checkout_error")))
                dropoff_checkin = _status(item.pop("dropoff_checkin_at"), bool(item.pop("dropoff_checkin_error")))
                dropoff_checkout = _status(item.pop("dropoff_checkout_at"), bool(item.pop("dropoff_checkout_error")))
                return_empty = _status(item.pop("return_empty_at"), bool(item.pop("return_empty_error")))
                e2open_error = bool(item.pop("e2open_error"))
                gps_error = bool(item.pop("gps_error"))
                gps_date_time = item.pop("gps_date_time")
                last_updated_at = item.pop("last_updated_at")
                item.pop("today")
                changed_recently = bool(item.pop("changed_recently"))
                gps = {
                    "active": bool(item.pop("gps_active")),
                    "date_time": gps_date_time.isoformat() if gps_date_time else None,
                    "city": item.pop("gps_city"),
                    "postal_code": item.pop("gps_postal_code"),
                    "speed_mph": item.pop("speed_mph"),
                    "remaining_distance_mi": item.pop("remaining_distance_mi"),
                    "eta": item.pop("gps_eta").isoformat() if item.get("gps_eta") else None,
                    "error": gps_error,
                }
                item.pop("gps_eta", None)
                item["event_time"] = (
                    item["fecha_hora_etadrop"] if movement_type == "DELIVERY" else item["fecha_hora_pickup"]
                )
                item["event_time"] = item["event_time"].strftime("%H:%M") if item["event_time"] else None
                item["fecha_hora_pickup"] = item["fecha_hora_pickup"].isoformat() if item["fecha_hora_pickup"] else None
                item["fecha_hora_etadrop"] = item["fecha_hora_etadrop"].isoformat() if item["fecha_hora_etadrop"] else None
                item["stages"] = {
                    "pickup_empty": pickup_empty,
                    "pickup_checkin": pickup_checkin,
                    "pickup_checkout": pickup_checkout,
                    "dropoff_checkin": dropoff_checkin,
                    "dropoff_checkout": dropoff_checkout,
                    "return_empty": return_empty,
                }
                item["errors"] = {"e2open": e2open_error, "gps": gps_error}
                item["gps"] = gps
                item["completed"] = return_empty["state"] == "completed" or dropoff_checkout["state"] == "completed"
                item["changed_recently"] = changed_recently
                item["last_updated_at"] = last_updated_at.isoformat() if last_updated_at else None
                tasks.append(item)

            return {
                "success": True,
                "date": requested_date.isoformat() if requested_date else None,
                "timezone": TIMEZONE,
                "refresh_seconds": 60,
                "recent_minutes": RECENT_MINUTES,
                "tasks": tasks,
            }
    except Exception:
        logger.exception("Unable to load dashboard transport data")
        return {"success": False, "message": "Unable to load dashboard data.", "tasks": []}
    finally:
        engine.dispose()
