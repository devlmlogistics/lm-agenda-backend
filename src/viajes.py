import logging
from urllib.parse import urlencode

from sqlalchemy import create_engine, text

from src.config.db_config import conexion


logger = logging.getLogger(__name__)


PICKUP_EMPTY = "PICKUP_EMPTY_CHIQUITA-OXNARD"
CHECK_IN_CHIQUITA = "CHECK-IN_CHIQUITA-OXNARD"
CHECK_OUT_CHIQUITA = "CHECK-OUT_CHIQUITA-OXNARD"
CHECK_IN_WALMART = "CHECK-IN_WALMART/KROGER"
CHECK_OUT_WALMART = "CHECK-OUT_WALMART/KROGER"
RETURN_EMPTY = "RETURN_EMPTY_CHIQUITA-OXNARD"


FORM_TITLES = {
    PICKUP_EMPTY: "0-PickUp_Empty",
    CHECK_IN_CHIQUITA: "1-Check-In Pick Up",
    CHECK_OUT_CHIQUITA: "2-Check-Out Pick Up",
    CHECK_IN_WALMART: "3-Check-In Drop Off",
    CHECK_OUT_WALMART: "4-Check-Out Drop Off",
    RETURN_EMPTY: "5-Return Empty",
}


FORM_FIELDS = {
    PICKUP_EMPTY: {
        "escribaUna": "delivery_order",
        "driver": "driver",
        "delivery_order_": "delivery_order",
        "deliveryDate29": "delivery_date",
        "Id_transaction": "id_transaction",
        "email": "email",
        "pick_location": "pick_location",
        "drop_location35": "drop_location",
        "movement_type": "movement_type",
    },
    CHECK_IN_CHIQUITA: {
        "escribaUna": "delivery_order",
        "driver": "driver",
        "delivery_order_": "delivery_order",
        "deliveryDate29": "delivery_date",
        "id_transaction": "id_transaction",
        "email": "email",
        "pick_location": "pick_location",
        "drop_location35": "drop_location",
        "movement_type": "movement_type",
    },
    CHECK_OUT_CHIQUITA: {
        "typeA": "delivery_order",
        "driver": "driver",
        "officeId": "delivery_order",
        "delivery_date": "delivery_date",
        "id_transaction": "id_transaction",
        "email": "email",
        "pick_location": "pick_location",
        "drop_location30": "drop_location",
        "movement_type": "movement_type",
    },
    CHECK_IN_WALMART: {
        "escribaUna": "delivery_order",
        "driver": "driver",
        "delivery_order_": "delivery_order",
        "deliveryDate29": "delivery_date",
        "Id_transaction": "id_transaction",
        "email": "email",
        "pick_location": "pick_location",
        "drop_location36": "drop_location",
        "movement_type": "movement_type",
    },
    CHECK_OUT_WALMART: {
        "typeA24": "delivery_order",
        "driver": "driver",
        "delivery_order_": "delivery_order",
        "delivery_date": "delivery_date",
        "id_transaction": "id_transaction",
        "email": "email",
        "pick_location": "pick_location",
        "drop_location31": "drop_location",
        "movement_type": "movement_type",
    },
    RETURN_EMPTY: {
        "escribaUna": "delivery_order",
        "driver": "driver",
        "delivery_order_": "delivery_order",
        "deliveryDate29": "delivery_date",
        "Id_transaction": "id_transaction",
        "email": "email",
        "pick_location": "pick_location",
        "drop_location35": "drop_location",
        "movement_type": "movement_type",
    },
}


FLOW_BY_MOVEMENT = {
    "PICKUP": {
        None: PICKUP_EMPTY,
        PICKUP_EMPTY: CHECK_IN_CHIQUITA,
        CHECK_IN_CHIQUITA: CHECK_OUT_CHIQUITA,
        CHECK_OUT_CHIQUITA: CHECK_IN_WALMART,
        CHECK_IN_WALMART: CHECK_OUT_WALMART,
        CHECK_OUT_WALMART: None,
    },
    "DELIVERY": {
        None: CHECK_IN_CHIQUITA,
        CHECK_IN_CHIQUITA: CHECK_OUT_CHIQUITA,
        CHECK_OUT_CHIQUITA: CHECK_IN_WALMART,
        CHECK_IN_WALMART: CHECK_OUT_WALMART,
        CHECK_OUT_WALMART: RETURN_EMPTY,
        RETURN_EMPTY: None,
    },
}


def _normalize(value):
    if value is None:
        return None
    return str(value).strip().upper()


def _next_form(movement_type, last_form):
    movement = _normalize(movement_type)
    current_form = _normalize(last_form)
    flow = FLOW_BY_MOVEMENT.get(movement)
    if flow is None or current_form not in flow:
        return "INVALID", current_form
    next_form = flow[current_form]
    if next_form is None:
        return "COMPLETE", None
    return "OPEN_FORM", next_form


def _build_form_url(base_url, form_type, trip):
    field_mapping = FORM_FIELDS[form_type]
    params = {
        jotform_field: trip[source_field]
        for jotform_field, source_field in field_mapping.items()
    }
    separator = "&" if "?" in base_url else "?"
    return f"{base_url}{separator}{urlencode(params)}"


def _message_response(message, success=False):
    return {
        "success": success,
        "action": "MESSAGE",
        "message": message,
    }


def siguiente_formulario_viaje(delivery_order):
    if delivery_order is None or not str(delivery_order).strip():
        return _message_response("Enter Delivery Order")

    engine = create_engine(conexion)
    try:
        with engine.connect() as connection:
            row = connection.execute(
                text(
                    """
                    SELECT driver,
                           delivery_order,
                           to_char(delivery_date, 'MM/DD/YYYY') AS delivery_date,
                           id_transaction,
                           email,
                           pick_location,
                           drop_location,
                           upper(trim(movement_type)) AS movement_type
                    FROM jotform.planificacion
                    WHERE upper(trim(unique_code)) = upper(trim(:unique_code))
                    LIMIT 1
                    """
                ),
                {"unique_code": str(delivery_order)},
            ).mappings().first()

            if row is None:
                return _message_response(
                    "No existe Delivery Order en Base de Datos"
                )

            trip = dict(row)
            last_form = connection.execute(
                text(
                    """
                    SELECT upper(trim(formulario)) AS formulario
                    FROM jotform.e_to_open
                    WHERE trim(delivery_order) = trim(:delivery_order)
                      AND upper(trim(coalesce(estado, ''))) <> 'ANULADO'
                      AND upper(trim(coalesce(formulario, ''))) <>
                          'SUPERVISOR_MESSAGE_FOR_E2OPEN'
                    ORDER BY fecha_hora_local DESC NULLS LAST, id_envio DESC
                    LIMIT 1
                    """
                ),
                {"delivery_order": trip["delivery_order"]},
            ).scalar_one_or_none()

            action, form_type = _next_form(trip["movement_type"], last_form)

            if action == "COMPLETE":
                return _message_response(
                    "Usted ya ha completado el viaje. Muchas Gracias...",
                    success=True,
                )

            if action == "INVALID":
                invalid_type = last_form or trip["movement_type"]
                return _message_response(
                    f"Tipo de Registro {invalid_type} inválido, "
                    "comuníquese con Administrador..."
                )

            base_url = connection.execute(
                text(
                    """
                    SELECT link
                    FROM jotform.links
                    WHERE nombre = :form_type
                    LIMIT 1
                    """
                ),
                {"form_type": form_type},
            ).scalar_one_or_none()

            if base_url is None:
                logger.error("No existe URL para el formulario %s", form_type)
                return _message_response(
                    "No existe configuración para el formulario solicitado"
                )

            return {
                "success": True,
                "action": "OPEN_FORM",
                "form_type": form_type,
                "title": FORM_TITLES[form_type],
                "form_url": _build_form_url(base_url, form_type, trip),
                "trip": trip,
            }
    except Exception:
        logger.exception("Error al determinar el siguiente formulario del viaje")
        return _message_response("Error al procesar la solicitud")
    finally:
        engine.dispose()
