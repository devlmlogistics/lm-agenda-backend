from flask import Flask, request, jsonify, send_file, json
import os
from src.index import resumen_semanal
from src.index import resumen_semanal_v2
from src.index import resumen_semanal_v3
from src.index import resumen_semanal_serie
from src.index import lista_week
from src.index import total_events
from src.index import total_events_v2
from src.index import fechas_gps
from src.index import resumen_gps
from src.index import drivers_gps
from src.index import routes_gps
from src.index import summary_routes
from src.index import summary_routes_v2
from src.index import eto_open_route
from src.index import coordenada_test
from src.index import coordenadas_gps
from src.index import fechas_por_semana
from src.index import fechas_por_semana_v2
from src.index import detalle_movimientos_drayage
from src.index import detalle_movimientos_drayage_v2
from src.index import detalle_movimientos_drayage_v3
from src.index import detalle_movimientos_drayage_v4
from src.index import listado_driver_drayage_v3
from src.index import consulta_container
from src.index import lista_month_diesel
from src.index import eventos_total_diesel
from src.index import eventos_detalle_diesel_v2
from src.index import eventos_detalle_diesel
from src.index import registro_diesel_odometro_x_id
from src.index import registro_diesel_receipt_x_id
from src.index import registro_diesel_x_id
from src.index import update_registro_diesel_x_id
from src.index import viajes_facturacion_por_periodo
from src.index import get_reg_doc_por_tipo
from src.index import get_reg_doc_por_tipo_valor
from src.index import drivers_check_list_truck
from src.index import registros_check_list_truck
from src.index import inserta_drayage
from src.index import get_imagen_drayage
from src.index import get_registros_drayage_ws
from src.index import ver_activacion_bot
from src.index import get_inicio_jornada
from src.index import ingresa_inicio_jornada
from src.index import formulario_aceptacion
from src.index import formulario_aceptacion_v2
from src.index import webhook_drayage_aceptacion
from src.viajes import siguiente_formulario_viaje
from src.driver_tasks import tareas_programadas_driver, planificacion_supervisor
from src.agenda_communications import (
    create_message,
    create_user,
    current_user,
    delete_message,
    download_attachment,
    list_messages,
    list_users,
    public_push_config,
    retention_settings,
    save_push_subscription,
    unread_counts,
    update_message,
    update_user,
)


app = Flask(__name__)
API_KEY = os.environ.get('API_KEY')
FRONTEND_ORIGIN = os.environ.get(
    'FRONTEND_ORIGIN',
    'https://lm-driver-agenda.hamg36.chatgpt.site'
)


@app.after_request
def add_cors_headers(response):
    origin = request.headers.get('Origin')
    if origin == FRONTEND_ORIGIN:
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PATCH, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, X-Supervisor-Key, X-Access-Token, X-Driver-Code'
        response.headers['Vary'] = 'Origin'
    return response

@app.route('/')
def inicio():
    return 'hola'


@app.route('/resumen_semanal', methods=['GET'])
def get_resumen_driver_semana():
    args = request.args
    week_number = args.get('week_number', None)
    return resumen_semanal(week_number)


@app.route('/resumen_semanal_v2', methods=['GET'])
def get_resumen_driver_semana_v2():
    args = request.args
    tipo = args.get('tipo', 0)
    week_number = args.get('week_number', None)
    return resumen_semanal_v2(week_number, tipo)


@app.route('/resumen_semanal_v3', methods=['GET'])
def get_resumen_driver_semana_v3():
    args = request.args
    tipo = args.get('tipo', 0)
    week_number = args.get('week_number', None)
    return resumen_semanal_v3(week_number, tipo)


@app.route('/resumen_semanal_serie')
def get_resumen_driver_semana_serie():
    return resumen_semanal_serie()


@app.route('/lista_week')
def get_week():
    return lista_week()


@app.route('/fechas_por_semana', methods=['GET'])
def get_fechas_por_semana():
    args = request.args
    week_number = args.get('week_number', 0)
    return fechas_por_semana(week_number)


@app.route('/fechas_por_semana_v2', methods=['GET'])
def get_fechas_por_semana_v2():
    args = request.args
    week_number = args.get('week_number', 0)
    special = args.get('special', 0)
    return fechas_por_semana_v2(week_number, special)


@app.route('/total_events', methods=['GET'])
def get_total_events():
    args = request.args
    week_number = args.get('week_number', 0)
    return total_events(week_number)


@app.route('/total_events_v2', methods=['GET'])
def get_total_events_v2():
    args = request.args
    week_number = args.get('week_number', 0)
    tipo = args.get('tipo', 0)
    return total_events_v2(week_number, tipo)


@app.route('/detalle_movimientos_drayage', methods=['GET'])
def get_detalle_movimientos_drayage():
    args = request.args
    fecha = args.get('fecha', None)
    return detalle_movimientos_drayage(fecha)


@app.route('/detalle_movimientos_drayage_v2', methods=['GET'])
def get_detalle_movimientos_drayage_v2():
    args = request.args
    fecha = args.get('fecha', None)
    tipo = args.get('tipo', 0)
    return detalle_movimientos_drayage_v2(fecha, tipo)


@app.route('/detalle_movimientos_drayage_v3', methods=['GET'])
def get_detalle_movimientos_drayage_v3():
    args = request.args
    fecha = args.get('fecha', None)
    tipo = args.get('tipo', 0)
    driver = args.get('driver', None)
    return detalle_movimientos_drayage_v3(fecha, tipo, driver)


@app.route('/detalle_movimientos_drayage_v4', methods=['GET'])
def get_detalle_movimientos_drayage_v4():
    args = request.args
    fecha = args.get('fecha', None)
    tipo = args.get('tipo', 0)
    week_number = args.get('week_number', None)
    return detalle_movimientos_drayage_v4(fecha, tipo, week_number)


@app.route('/listado_driver_drayage_v3', methods=['GET'])
def get_listado_driver_drayage_v3():
    args = request.args
    fecha = args.get('fecha', None)
    tipo = args.get('tipo', 0)
    week_number = args.get('week_number', 0)
    return listado_driver_drayage_v3(fecha, tipo, week_number)


@app.route('/consulta_container', methods=['GET'])
def get_consulta_container():
    args = request.args
    container = args.get('container', None)
    return consulta_container(container)


@app.route('/gps/fechas', methods=['GET'])
def get_gps_fechas():
    return fechas_gps()


@app.route('/gps/routes', methods=['GET'])
def get_gps_routes():
    return routes_gps()


@app.route('/gps/drivers', methods=['GET'])
def get_gps_drivers():
    args = request.args
    fecha = args.get('fecha', 0)
    return drivers_gps(fecha)


@app.route('/gps/resumen', methods=['GET'])
def get_gps_resumen():
    args = request.args
    fecha = args.get('fecha', 0)
    device = args.get('device', 0)
    return resumen_gps(fecha, device)


@app.route('/gps/summary_routes', methods=['GET'])
def get_gps_summary_routes():
    args = request.args
    transaction = args.get('transaction', 0)
    return summary_routes(transaction)


@app.route('/gps/summary_routes_v2', methods=['GET'])
def get_gps_summary_routes_v2():
    args = request.args
    transaction = args.get('transaction', 0)
    return summary_routes_v2(transaction)


@app.route('/gps/eto_open_route', methods=['GET'])
def get_eto_open_route():
    args = request.args
    transaction = args.get('transaction', 0)
    return eto_open_route(transaction)


@app.route('/gps/coordenada', methods=['GET'])
def get_gps_coordenada():
    args = request.args
    id_gps = args.get('id_gps', 0)
    return coordenada_test(id_gps)


@app.route('/gps/coordenadas_gps', methods=['GET'])
def get_gps_coordenadas():
    args = request.args
    id_gps = args.get('id_gps', 0)
    return coordenadas_gps(id_gps)


@app.route('/lista_month_diesel')
def get_month_diesel():
    return lista_month_diesel()


@app.route('/diesel_total_events', methods=['GET'])
def get_diesel_total_events():
    args = request.args
    periodo = args.get('periodo', 0)
    return eventos_total_diesel(periodo)


@app.route('/diesel_detalle_events', methods=['GET'])
def get_diesel_detalle_events():
    try:
        periodo = request.args.get('periodo', default=0, type=int)
        resultados = eventos_detalle_diesel(periodo)
        return jsonify(resultados), 200
    except Exception as e:
        print(f"[ERROR] {e}")
        return jsonify({"error": "Error al procesar la solicitud"}), 500


@app.route('/diesel_registro_odometro', methods=['GET'])
def get_diesel_odometro_registro():
    args = request.args
    id_envio = args.get('id_envio', 0)
    return registro_diesel_odometro_x_id(id_envio)


@app.route('/diesel_registro_receipt', methods=['GET'])
def get_diesel_receipt_registro():
    args = request.args
    id_envio = args.get('id_envio', 0)
    return registro_diesel_receipt_x_id(id_envio)


@app.route('/diesel_registro', methods=['GET'])
def get_diesel_registro():
    args = request.args
    id_envio = args.get('id_envio', 0)
    return registro_diesel_x_id(id_envio)


@app.route('/diesel_registro/<id_envio>', methods=['PUT'])
def put_diesel_registro(id_envio=0):
    print("id_envio (path param):", id_envio)

    ## print("request.args (query params):", request.args.to_dict())
    ## print("request.form (form data):", request.form.to_dict())
    ## print("request.json (JSON body):", request.get_json(silent=True))
    ## print("request.data (raw body):", request.data.decode('utf-8'))
    ## print("request.headers:", dict(request.headers))
    ## print("request.files:", request.files)

    datos = request.get_json(silent=True)
    return update_registro_diesel_x_id(id_envio, datos)


@app.route('/viajes_facturacion_periodo', methods=['GET'])
def get_viajes_facturacion_periodo():
    args = request.args
    periodo = args.get('periodo', 0)
    return viajes_facturacion_por_periodo(periodo)


@app.route('/reg_doc_por_tipo', methods=['GET'])
def getreg_doc_por_tipo():
    print("get_reg_doc_por_tipo")
    args = request.args
    tipo = args.get('tipo', 0)
    return get_reg_doc_por_tipo(tipo)


@app.route('/reg_doc_por_tipo_valor', methods=['GET'])
def getreg_doc_por_tipo_valor():
    args = request.args
    tipo = args.get('tipo', 0)
    valor = args.get('valor', 0)
    return get_reg_doc_por_tipo_valor(tipo, valor)


@app.route('/drivers_check_list_truck', methods=['GET'])
def get_drivers_check_list_truck():
    return drivers_check_list_truck()


@app.route('/registros_check_list_truck', methods=['GET'])
def get_registros_check_list_truck():
    args = request.args
    driver = args.get('driver', None)
    return registros_check_list_truck(driver)


@app.route('/inserta_drayage', methods=['POST'])
def post_drayage():
    apikey = request.headers.get('apikey')
    if apikey != API_KEY:
        return jsonify({"error": "API Key no valida"}), 401
    uid = request.json['uid']
    origen_ws = request.json['origen_ws']
    nombre_ws = request.json['nombre_ws']
    localizacion = request.json['localizacion']
    tipo = request.json['tipo']
    code = request.json['code']
    geolocation = request.json['geolocation']
    localpath = request.json['localpath']
    shift = request.json['shift']
    weekday = request.json['weekday']
    file_b64 = request.json['file_b64']
    return inserta_drayage(uid, origen_ws, nombre_ws, localizacion, tipo, code,
                           geolocation, localpath, shift, weekday, file_b64)


@app.route('/activacion_bot', methods=['GET'])
def get_activacion_bot():
    apikey = request.headers.get('apikey')
    if apikey != API_KEY:
        return jsonify({"error": "API Key no valida"}), 401
    args = request.args
    proceso = args.get('proceso', 0)
    return ver_activacion_bot(proceso)


@app.route('/get_imagen_drayage', methods=['GET'])
def get_imagendrayage():
    uid = request.args.get('uid')
    image_stream = get_imagen_drayage(uid)
    return send_file(image_stream, mimetype='image/jpeg')


@app.route('/get_registros_drayage_ws', methods=['GET'])
def get_registros_drayage():
    return get_registros_drayage_ws()


@app.route('/jornada/get_inicio_jornada', methods=['GET'])
def get_iniciojornada():
    codigo_driver = request.args.get('codigo_driver')
    return get_inicio_jornada(codigo_driver)


@app.route('/jornada/save_inicio_jornada', methods=['POST'])
def ingresa_iniciojornada():
    id_working_hours = request.json.get('id_working_hours')
    codigo_driver = request.json.get('codigo_driver')
    driver = request.json.get('driver')
    week_number = request.json.get('week_number')
    email = request.json.get('email')
    longitud = request.json.get('longitud')
    latitud = request.json.get('latitud')
    date_time_driver = request.json.get('date_time_driver')
    return ingresa_inicio_jornada(id_working_hours, codigo_driver, driver, week_number, email, longitud, latitud, date_time_driver)


@app.route('/drayage/formulario_aceptacion', methods=['GET'])
def get_formulario_aceptacion():
    args = request.args
    codigo_driver = args.get('codigo_driver', None)
    return formulario_aceptacion(codigo_driver)


@app.route('/drayage/formulario_aceptacion_v2', methods=['GET'])
def get_formulario_aceptacion_v2():
    args = request.args
    codigo_driver = args.get('codigo_driver', None)
    return formulario_aceptacion_v2(codigo_driver)

@app.route('/drayage/webhook_drayage_aceptacion', methods=['POST'])
def post_webhook_drayage_aceptacion():
    #print("========== WEBHOOK ==========")
    #print("Metodo:", request.method)
    #print("Headers:")
    #print(request.headers)
    #print("Content-Type:", request.content_type)
    #print("Mimetype:", request.mimetype)
    #print("Body:")
    #print(request.get_data(as_text=True))
    #request_data = request.get_json()
    #print(request_data)
    #print("=============================")
    raw_request = request.form.get("rawRequest")
    submissionID = request.form.get("submissionID")
    if raw_request:
        data = json.loads(raw_request)
        webhook_drayage_aceptacion(submissionID, data["q57_weekNumber"], data["q25_email"], data["q58_driver58"])
    return jsonify({"status": "success"}), 200


@app.route('/viajes/siguiente_formulario', methods=['GET'])
def get_siguiente_formulario_viaje():
    delivery_order = request.args.get('delivery_order')
    return jsonify(siguiente_formulario_viaje(delivery_order)), 200


@app.route('/drivers/tareas', methods=['GET'])
def get_tareas_programadas_driver():
    codigo_driver = request.args.get('codigo_driver')
    return jsonify(tareas_programadas_driver(codigo_driver)), 200


@app.route('/drivers/planificacion-supervisor', methods=['GET'])
def get_planificacion_supervisor():
    return jsonify(planificacion_supervisor(
        request.headers.get('X-Supervisor-Key'),
        request.args.get('mode'),
        request.args.get('date'),
        request.args.get('driver'),
        request.args.get('week'),
    )), 200


@app.route('/agenda/orders/<delivery_order>/messages', methods=['GET', 'POST'])
def order_messages(delivery_order):
    if request.method == 'GET':
        payload, status = list_messages(request.headers, delivery_order)
    else:
        payload, status = create_message(
            request.headers,
            delivery_order,
            request.form.get('body'),
            request.files.getlist('files'),
        )
    return jsonify(payload), status


@app.route('/agenda/messages/<int:message_id>', methods=['PATCH', 'DELETE'])
def agenda_message(message_id):
    if request.method == 'PATCH':
        payload, status = update_message(
            request.headers, message_id, (request.get_json(silent=True) or {}).get('body')
        )
    else:
        payload, status = delete_message(request.headers, message_id)
    return jsonify(payload), status


@app.route('/agenda/attachments/<int:attachment_id>', methods=['GET'])
def agenda_attachment(attachment_id):
    stream, filename, content_type, status = download_attachment(request.headers, attachment_id)
    if status != 200:
        return jsonify({'success': False, 'message': 'Attachment not found.'}), status
    return send_file(stream, mimetype=content_type, download_name=filename)


@app.route('/agenda/unread', methods=['GET'])
def agenda_unread():
    payload, status = unread_counts(request.headers)
    return jsonify(payload), status


@app.route('/agenda/me', methods=['GET'])
def agenda_me():
    payload, status = current_user(request.headers)
    return jsonify(payload), status


@app.route('/agenda/admin/users', methods=['GET', 'POST'])
def agenda_users():
    if request.method == 'GET':
        payload, status = list_users(request.headers)
    else:
        data = request.get_json(silent=True) or {}
        payload, status = create_user(request.headers, data.get('display_name'), data.get('role'))
    return jsonify(payload), status


@app.route('/agenda/admin/users/<int:user_id>', methods=['PATCH'])
def agenda_user(user_id):
    data = request.get_json(silent=True) or {}
    payload, status = update_user(
        request.headers, user_id, data.get('active'), bool(data.get('regenerate_token'))
    )
    return jsonify(payload), status


@app.route('/agenda/settings/retention', methods=['GET', 'PATCH'])
def agenda_retention():
    data = request.get_json(silent=True) or {}
    payload, status = retention_settings(
        request.headers, data.get('retention_days') if request.method == 'PATCH' else None
    )
    return jsonify(payload), status


@app.route('/agenda/push/config', methods=['GET'])
def agenda_push_config():
    payload, status = public_push_config()
    return jsonify(payload), status


@app.route('/agenda/push/subscriptions', methods=['POST'])
def agenda_push_subscription():
    payload, status = save_push_subscription(request.headers, request.get_json(silent=True) or {})
    return jsonify(payload), status


if __name__ == '__main__':
    app.run(debug=False, use_reloader=False, port=5000, host="0.0.0.0")
