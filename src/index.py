from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
import base64
import io
import logging
from urllib.parse import quote
from urllib.parse import urlencode

from sqlalchemy import create_engine, text, func, and_, true
from sqlalchemy.orm import sessionmaker
from src.config.db_config import conexion
from src.config.db_config import esquema
from src.models.resumenDriverSemana_model import ResumenDriverSemana
from src.models.detalleMovimientosDrayage import DetalleMovimientoDrayage
from src.models.detalleMovimientosDrayageNormal import DetalleMovimientoDrayageNormal
from src.models.detalleMovimientosDrayageSpecial import DetalleMovimientoDrayageSpecial
from src.models.movimientosContainer import MovimientosContainer
from src.models.resumenDriverSemanaDrayage_model import ResumenDriverSemanaDrayage
from src.models.resumenDriverSemanaSpecial_model import ResumenDriverSemanaSpecial


logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)


def resumen_semanal(week_number):
    try:
        week_number = int(week_number)
    except Exception as e:
        week_number = 0

    engine2 = create_engine(conexion).execution_options(autocommit=True)
    sessionMaker = sessionmaker(bind=engine2)
    session = sessionMaker()

    salida = []
    ## Si week_number es None consultar todos los registros, si trae valor consultar los registros para el week_number dado
    if (week_number is None) or (week_number == "") or (week_number == 0) or (week_number == "0") or (week_number < 0):
        ## obtener el valor del week_number para el registro con el mínimo id de la tabla ResumenDriverSemana limit 1
        maximo_valor_week = session.query(ResumenDriverSemana.week_number).first()[0]
        resultado = session.query(ResumenDriverSemana).filter(ResumenDriverSemana.week_number == maximo_valor_week).all()
    else:
        resultado = session.query(ResumenDriverSemana).filter(ResumenDriverSemana.week_number == week_number).all()

    eventos = 0
    week_number = 0
    for r in resultado:
        eventos = eventos + r.events
        week_number = r.week_number
        registro = {"id": r.id, "driver": r.driver, "last_movement": r.last_movement, "day": r.day, "range": r.range, "events": r.events,
                    "week_number": r.week_number}
        salida.append(registro)
    session.close()
    resultado = {"eventos": eventos, "week_number": week_number, "serie": salida}
    return resultado


def resumen_semanal_v2(week_number, tipo):
    try:
        week_number = int(week_number)
    except Exception as e:
        week_number = 0

    try:
        tipo = int(tipo)
    except Exception as e:
        tipo = 0

    engine2 = create_engine(conexion).execution_options(autocommit=True)
    sessionMaker = sessionmaker(bind=engine2)
    session = sessionMaker()

    salida = []
    ## Si week_number es None consultar todos los registros, si trae valor consultar los registros para el week_number dado
    if (week_number is None) or (week_number == "") or (week_number == 0) or (week_number == "0") or (week_number < 0):
        ## obtener el valor del week_number para el registro con el mínimo id de la tabla ResumenDriverSemana limit 1
        if (tipo == 1):
            ##maximo_valor_week = session.query(ResumenDriverSemanaSpecial.week_number).first()[0]
            maximo_valor_week = session.query(func.max(ResumenDriverSemanaSpecial.week_number)).scalar()

            if maximo_valor_week is None:
                maximo_valor_week = 2506

            resultado = session.query(ResumenDriverSemanaSpecial).filter(
                ResumenDriverSemanaSpecial.week_number == maximo_valor_week).all()
        else:
            ##maximo_valor_week = session.query(ResumenDriverSemanaDrayage.week_number).first()[0]
            maximo_valor_week = session.query(func.max(ResumenDriverSemanaDrayage.week_number)).scalar()

            if maximo_valor_week is None:
                maximo_valor_week = 2506

            resultado = session.query(ResumenDriverSemanaDrayage).filter(
                ResumenDriverSemanaDrayage.week_number == maximo_valor_week).all()
    else:
        if (tipo == 1):
            resultado = session.query(ResumenDriverSemanaSpecial).filter(
                ResumenDriverSemanaSpecial.week_number == week_number).all()
        else:
            resultado = session.query(ResumenDriverSemanaDrayage).filter(ResumenDriverSemanaDrayage.week_number == week_number).all()

    eventos = 0
    week_number = 0
    for r in resultado:
        eventos = eventos + r.events
        week_number = r.week_number
        registro = {"id": r.id, "driver": r.driver, "last_movement": r.last_movement, "day": r.day, "range": r.range, "events": r.events,
                    "week_number": r.week_number}
        salida.append(registro)
    session.close()
    resultado = {"eventos": eventos, "week_number": week_number, "serie": salida}
    return resultado

def resumen_semanal_v3(week_number, tipo):
    try:
        week_number = int(week_number)
    except Exception as e:
        week_number = 0

    try:
        tipo = int(tipo)
    except Exception as e:
        tipo = 0

    engine2 = create_engine(conexion).execution_options(autocommit=True)
    sessionMaker = sessionmaker(bind=engine2)
    session = sessionMaker()

    salida = []
    ## Si week_number es None consultar todos los registros, si trae valor consultar los registros para el week_number dado
    if (week_number is None) or (week_number == "") or (week_number == 0) or (week_number == "0") or (week_number < 0):
        ## obtener el valor del week_number para el registro con el mínimo id de la tabla ResumenDriverSemana limit 1
        if (tipo == 1):
            ##maximo_valor_week = session.query(ResumenDriverSemanaSpecial.week_number).first()[0]
            maximo_valor_week = session.query(func.max(ResumenDriverSemanaSpecial.week_number)).scalar()

            if maximo_valor_week is None:
                maximo_valor_week = 2506

            resultado = session.query(ResumenDriverSemanaSpecial).filter(
                ResumenDriverSemanaSpecial.week_number == maximo_valor_week).all()
        else:
            ##maximo_valor_week = session.query(ResumenDriverSemanaDrayage.week_number).first()[0]
            maximo_valor_week = session.query(func.max(ResumenDriverSemanaDrayage.week_number)).scalar()

            if maximo_valor_week is None:
                maximo_valor_week = 2506

            resultado = session.query(ResumenDriverSemanaDrayage).filter(
                ResumenDriverSemanaDrayage.week_number == maximo_valor_week).all()
    else:
        if (tipo == 1):
            resultado = session.query(ResumenDriverSemanaSpecial).filter(
                ResumenDriverSemanaSpecial.week_number == week_number).all()
        else:
            resultado = session.query(ResumenDriverSemanaDrayage).filter(ResumenDriverSemanaDrayage.week_number == week_number).all()

    eventos = 0
    week_number = 0
    for r in resultado:
        eventos = eventos + r.events
        week_number = r.week_number
        dia = r.dia
        color = 'u-color-29'
        if dia == 0:  ##Domingo
            color = 'u-color-29'
        elif dia == 1:
            color = 'u-color-17'
        elif dia == 2:
            color = 'u-color-21'
        elif dia == 3:
            color = 'u-color-16'
        elif dia == 4:
            color = 'u-color-22'
        elif dia == 5:
            color = 'u-color-18'
        elif dia == 6:
            color = 'u-color-20'

        registro = {"id": r.id, "driver": r.driver, "last_movement": r.last_movement, "day": r.day, "range": r.range, "events": r.events,
                    "week_number": r.week_number, "color": color}
        salida.append(registro)
    session.close()
    resultado = {"eventos": eventos, "week_number": week_number, "serie": salida}
    return resultado


def resumen_semanal_serie():

    engine2 = create_engine(conexion).execution_options(autocommit=True)
    sessionMaker = sessionmaker(bind=engine2)
    session = sessionMaker()

    salida = []
    resultado = session.query(ResumenDriverSemana).all()
    eventos = 0
    week_number = 0
    for r in resultado:
        eventos = eventos + r.events
        week_number = r.week_number
        registro = {"id": r.id, "driver": r.driver, "day": r.day, "range": r.range, "events": r.events,
                    "week_number": r.week_number}
        salida.append(registro)
    session.close()
    resultado = [{"eventos": eventos, "week_number": week_number, "serie": salida}]
    return resultado


def lista_week():

    engine2 = create_engine(conexion).execution_options(autocommit=True)
    sessionMaker = sessionmaker(bind=engine2)
    session = sessionMaker()
    # query_week = text("SELECT DISTINCT ON (fecha_hora_local::date - (EXTRACT(DOW FROM fecha_hora_local)::INT + 6) % 7, \
    # week_number) 'Week ' || to_char(week_number, '00') \
    # as week, week_number FROM jotform.drayage where drayage.considerar_movimiento = 'yes'::text \
    # and week_number IS NOT NULL ORDER BY (fecha_hora_local::date - (EXTRACT(DOW FROM fecha_hora_local)::INT + 6) % 7) \
    # desc, week_number DESC")
    query_week = text("select distinct on (min_id, week_number) 'Week ' || to_char(week_number, '0000') as week, week_number \
    FROM (select min(id) as min_id, week_number from jotform.resumen_semanal group by week_number) s \
    order by min_id, week_number")
    salida = []
    try:
        resultado = session.execute(query_week)
        resultado = resultado.fetchall()
        for row in resultado:
            registro = {"week": row[0], "week_number": row[1]}
            salida.append(registro)
    except Exception as e:
        print(e)
    session.close()
    return salida


def fechas_por_semana(week_number):
    print(week_number, type(week_number))
    engine2 = create_engine(conexion).execution_options(autocommit=True)
    sessionMaker = sessionmaker(bind=engine2)
    session = sessionMaker()
    if (week_number is None) or (week_number == "") or (week_number == 0) or (week_number == "0"):
        query = text("select week_number from jotform.drayage order by fecha_hora_local desc limit 1")
        result = session.execute(query)
        result = result.fetchall()
        week_number = result[0][0]


    query_week = text("""
    SELECT DISTINCT to_char(date_trunc('d'::text, fecha_hora_local)::date, 'MM/dd/YYYY') as fecha_valor, 
    (fecha_hora_local::date)::text as fecha_id	FROM jotform.drayage WHERE week_number=:week_number ORDER BY 1 DESC""")
    salida = []
    respuesta = {}
    try:
        resultado = session.execute(query_week, {"week_number": week_number})
        resultado = resultado.fetchall()
        for row in resultado:
            ## registro = {"fecha_valor": row[0], "fecha_id": row[1]}
            registro = {"id": row[0], "fecha": row[1]}
            salida.append(registro)
        respuesta = {"data": salida}
    except Exception as e:
        print(e)
    session.close()
    return respuesta


def fechas_por_semana_v2(week_number, special):
    engine2 = create_engine(conexion).execution_options(autocommit=True)
    sessionMaker = sessionmaker(bind=engine2)
    session = sessionMaker()
    if (week_number is None) or (week_number == "") or (week_number == 0) or (week_number == "0"):
        if (special is None) or (special == "") or (special == 0) or (special == "0"):
            query = text("""
            select week_number from jotform.drayage WHERE ubicacion <> 'Special Chiquita Yard Move'::text 
            order by fecha_hora_local desc limit 1
                         """)
            result = session.execute(query)
            result = result.fetchall()
            week_number = result[0][0]
        else:
            query = text("""
            select week_number from jotform.drayage WHERE ubicacion = 'Special Chiquita Yard Move'::text 
            order by fecha_hora_local desc limit 1
                         """)
            result = session.execute(query)
            result = result.fetchall()
            week_number = result[0][0]
    if (special is None) or (special == "") or (special == 0) or (special == "0"):
        query_week = text("""
        SELECT DISTINCT ON (fecha_hora_local::date) to_char(date_trunc('d'::text, fecha_hora_local)::date, 'MM/dd/YYYY') as 
        fecha_valor, (fecha_hora_local::date)::text as fecha_id	FROM jotform.drayage WHERE week_number=:week_number 
        AND ubicacion <> 'Special Chiquita Yard Move'::text	ORDER BY fecha_hora_local::date DESC
        """)
    else:
        query_week = text("""
        SELECT DISTINCT ON (fecha_hora_local::date) to_char(date_trunc('d'::text, fecha_hora_local)::date, 'MM/dd/YYYY') as 
        fecha_valor, (fecha_hora_local::date)::text as fecha_id	FROM jotform.drayage WHERE week_number=:week_number 
        AND ubicacion = 'Special Chiquita Yard Move'::text	ORDER BY fecha_hora_local::date DESC
        """)
    salida = []
    respuesta = {}
    try:
        resultado = session.execute(query_week, {"week_number": week_number})

        resultado = resultado.fetchall()
        for row in resultado:
            registro = {"id": row[0], "fecha": row[1]}
            salida.append(registro)
        respuesta = {"data": salida}
    except Exception as e:
        print(e)
    session.close()
    return respuesta


def detalle_movimientos_drayage(fecha):
    ## print('fecha: -> ', fecha)
    engine2 = create_engine(conexion).execution_options(autocommit=True)
    sessionMaker = sessionmaker(bind=engine2)
    session = sessionMaker()
    salida = []
    eventos = 0
    dia_semana = ''
    numero_dia_semana = 0
    fecha_salida = ''
    ## print('fecha 1: ', fecha, ' >>')
    if (fecha is None or fecha == '' or fecha == 0):
        max_fecha = session.query(func.max(DetalleMovimientoDrayage.date_local)).first()
        ## print(max_fecha)
        fecha = max_fecha[0]
        fecha_salida = max_fecha[0].strftime("%m/%d/%Y")
        numero_dia_semana = fecha.weekday()
    else:
        fecha_salida = datetime.strptime(fecha, "%Y-%m-%d").strftime("%m/%d/%Y")
        numero_dia_semana = datetime.strptime(fecha, "%Y-%m-%d").weekday()
    ##else:
    ##    fecha = datetime.strptime(fecha, '%Y-%m-%d')

    if (numero_dia_semana == 0):
        dia_semana = 'Monday'
    elif (numero_dia_semana == 1):
        dia_semana = 'Tuesday'
    elif (numero_dia_semana == 2):
        dia_semana = 'Wednesday'
    elif (numero_dia_semana == 3):
        dia_semana = 'Thursday'
    elif (numero_dia_semana == 4):
        dia_semana = 'Friday'
    elif (numero_dia_semana == 5):
        dia_semana = 'Saturday'
    elif (numero_dia_semana == 6):
        dia_semana = 'Sunday'
    resultado = session.query(DetalleMovimientoDrayage).filter(DetalleMovimientoDrayage.date_local == fecha).all()
    for r in resultado:
        eventos = eventos + 1
        registro = {"id": r.id, "date_time_local": r.date_time_local, "driver": r.driver, "movement": r.movement,
                    "date_local": r.date_local}
        salida.append(registro)
    session.close()
    resultado = [{"eventos": eventos, "fecha": fecha_salida + ' ' + dia_semana, "serie": salida}]
    ## print('resultado', resultado)
    return resultado



def detalle_movimientos_drayage_v2(fecha, tipo):
    ## print('fecha: -> ', fecha)
    engine2 = create_engine(conexion).execution_options(autocommit=True)
    sessionMaker = sessionmaker(bind=engine2)
    session = sessionMaker()
    salida = []
    eventos = 0
    dia_semana = ''
    numero_dia_semana = 0
    fecha_salida = ''
    ## print('fecha 1: ', fecha, ' >>')

    if (tipo is None or tipo == '' or tipo == '0'):
        tipo = 0

    try:
        tipo = int(tipo)
    except Exception as e:
        tipo = 0

    if (fecha is None or fecha == '' or fecha == 0):
        if (tipo == 0):
            max_fecha = session.query(func.max(DetalleMovimientoDrayageNormal.date_local)).first()
        else:
            max_fecha = session.query(func.max(DetalleMovimientoDrayageSpecial.date_local)).first()
        print(max_fecha)
        fecha = max_fecha[0]
        fecha_salida = max_fecha[0].strftime("%m/%d/%Y")
        numero_dia_semana = fecha.weekday()
    else:
        fecha_salida = datetime.strptime(fecha, "%Y-%m-%d").strftime("%m/%d/%Y")
        numero_dia_semana = datetime.strptime(fecha, "%Y-%m-%d").weekday()
    ##else:
    ##    fecha = datetime.strptime(fecha, '%Y-%m-%d')

    if (numero_dia_semana == 0):
        dia_semana = 'Monday'
    elif (numero_dia_semana == 1):
        dia_semana = 'Tuesday'
    elif (numero_dia_semana == 2):
        dia_semana = 'Wednesday'
    elif (numero_dia_semana == 3):
        dia_semana = 'Thursday'
    elif (numero_dia_semana == 4):
        dia_semana = 'Friday'
    elif (numero_dia_semana == 5):
        dia_semana = 'Saturday'
    elif (numero_dia_semana == 6):
        dia_semana = 'Sunday'

    if tipo == 0:
        resultado = session.query(DetalleMovimientoDrayageNormal).filter(DetalleMovimientoDrayageNormal.date_local == fecha).all()
    else:
        resultado = session.query(DetalleMovimientoDrayageSpecial).filter(DetalleMovimientoDrayageSpecial.date_local == fecha).all()
    for r in resultado:
        eventos = eventos + 1
        registro = {"id": r.id, "date_time_local": r.date_time_local, "driver": r.driver, "movement": r.movement,
                    "date_local": r.date_local}
        salida.append(registro)
    session.close()
    resultado = [{"eventos": eventos, "fecha": fecha_salida + ' ' + dia_semana, "serie": salida}]
    ## print('resultado', resultado)
    return resultado


def detalle_movimientos_drayage_v3(fecha, tipo, driver):
    ## print('fecha: -> ', fecha)
    engine2 = create_engine(conexion).execution_options(autocommit=True)
    sessionMaker = sessionmaker(bind=engine2)
    session = sessionMaker()
    salida = []
    eventos = 0
    dia_semana = ''
    numero_dia_semana = 0
    fecha_salida = ''
    ## print('fecha 1: ', fecha, ' >>')

    if (tipo is None or tipo == '' or tipo == '0'):
        tipo = 0

    try:
        tipo = int(tipo)
    except Exception as e:
        tipo = 0

    if (fecha is None or fecha == '' or fecha == 0):
        if (driver is None or driver == '' or driver == 0):
            if (tipo == 0):
                max_fecha = session.query(func.max(DetalleMovimientoDrayageNormal.date_local)).scalar()

            else:
                max_fecha = session.query(func.max(DetalleMovimientoDrayageSpecial.date_local)).scalar()
        else:
            if (tipo == 0):
                max_fecha = session.query(func.max(DetalleMovimientoDrayageNormal.date_local)).filter(DetalleMovimientoDrayageNormal.driver == driver).scalar()
            else:
                max_fecha = session.query(func.max(DetalleMovimientoDrayageSpecial.date_local)).filter(DetalleMovimientoDrayageSpecial.driver == driver).scalar()
        print(max_fecha)
        fecha = max_fecha
        fecha_salida = max_fecha.strftime("%m/%d/%Y")
        numero_dia_semana = fecha.weekday()
    else:
        fecha_salida = datetime.strptime(fecha, "%Y-%m-%d").strftime("%m/%d/%Y")
        numero_dia_semana = datetime.strptime(fecha, "%Y-%m-%d").weekday()
    ##else:
    ##    fecha = datetime.strptime(fecha, '%Y-%m-%d')

    if (numero_dia_semana == 0):
        dia_semana = 'Monday'
    elif (numero_dia_semana == 1):
        dia_semana = 'Tuesday'
    elif (numero_dia_semana == 2):
        dia_semana = 'Wednesday'
    elif (numero_dia_semana == 3):
        dia_semana = 'Thursday'
    elif (numero_dia_semana == 4):
        dia_semana = 'Friday'
    elif (numero_dia_semana == 5):
        dia_semana = 'Saturday'
    elif (numero_dia_semana == 6):
        dia_semana = 'Sunday'

    if tipo == 0:
        if (driver is None or driver == '' or driver == 0):
            resultado = session.query(DetalleMovimientoDrayageNormal).filter(DetalleMovimientoDrayageNormal.date_local == fecha).all()
        else:
            resultado = session.query(DetalleMovimientoDrayageNormal).filter(DetalleMovimientoDrayageNormal.date_local == fecha).filter(DetalleMovimientoDrayageNormal.driver == driver).all()
    else:
        if (driver is None or driver == '' or driver == 0):
            resultado = session.query(DetalleMovimientoDrayageSpecial).filter(DetalleMovimientoDrayageSpecial.date_local == fecha).all()
        else:
            resultado = session.query(DetalleMovimientoDrayageSpecial).filter(DetalleMovimientoDrayageSpecial.date_local == fecha).filter(DetalleMovimientoDrayageSpecial.driver == driver).all()
    for r in resultado:
        eventos = eventos + 1
        registro = {"id": r.id, "date_time_local": r.date_time_local, "driver": r.driver, "movement": r.movement,
                    "date_local": r.date_local}
        salida.append(registro)
    session.close()
    resultado = [{"eventos": eventos, "fecha": fecha_salida + ' ' + dia_semana, "serie": salida}]
    ## print('resultado', resultado)
    return resultado


def detalle_movimientos_drayage_v4(fecha, tipo, week_number):

    engine2 = create_engine(conexion).execution_options(autocommit=True)
    sessionMaker = sessionmaker(bind=engine2)
    session = sessionMaker()
    salida = []

    if (tipo is None or tipo == '' or tipo == '0'):
        tipo = 0

    try:
        tipo = int(tipo)
    except Exception as e:
        tipo = 0

    if (week_number is None or week_number == '' or week_number == '0'):
        week_number = session.query(func.max(DetalleMovimientoDrayageNormal.week_number)).scalar()
    try:
        week_number = int(week_number)
    except Exception as e:
        week_number = 0

    dia_semana = ''
    eventos = 0

    if fecha is None or fecha == '' or fecha == 0:
        if tipo == 0:
            if week_number == 0:
                resultado = session.query(DetalleMovimientoDrayageNormal).all()
            else:
                resultado = session.query(DetalleMovimientoDrayageNormal).filter(
                    DetalleMovimientoDrayageNormal.week_number == week_number).all()
        else:
            if week_number == 0:
                resultado = session.query(DetalleMovimientoDrayageSpecial).all()
            else:
                resultado = session.query(DetalleMovimientoDrayageSpecial).filter(
                    DetalleMovimientoDrayageSpecial.week_number == week_number).all()
        fecha_salida = 'All events for week day ' + str(week_number)
    else:
        if tipo == 0:
            resultado = (session.query(DetalleMovimientoDrayageNormal)
                         .filter(DetalleMovimientoDrayageNormal.date_local == fecha).all())
        else:
            resultado = (session.query(DetalleMovimientoDrayageSpecial)
                         .filter(DetalleMovimientoDrayageSpecial.date_local == fecha).all())
        fecha_salida = datetime.strptime(fecha, "%Y-%m-%d").strftime("%m/%d/%Y")
        numero_dia_semana = datetime.strptime(fecha, "%Y-%m-%d").weekday()
        if numero_dia_semana == 0:
            dia_semana = 'Monday'
        elif numero_dia_semana == 1:
            dia_semana = 'Tuesday'
        elif numero_dia_semana == 2:
            dia_semana = 'Wednesday'
        elif numero_dia_semana == 3:
            dia_semana = 'Thursday'
        elif numero_dia_semana == 4:
            dia_semana = 'Friday'
        elif numero_dia_semana == 5:
            dia_semana = 'Saturday'
        elif numero_dia_semana == 6:
            dia_semana = 'Sunday'


    for r in resultado:
        eventos = eventos + 1
        registro = {"id": r.id, "date_time_local": r.date_time_local, "driver": r.driver, "movement": r.movement,
                    "date_local": r.date_local}
        salida.append(registro)
    session.close()
    resultado = [{"eventos": eventos, "fecha": fecha_salida + ' ' + dia_semana, "serie": salida}]
    return resultado


def listado_driver_drayage_v3(fecha, tipo, week_number):
    ## print('fecha: -> ', fecha)
    engine2 = create_engine(conexion).execution_options(autocommit=True)
    sessionMaker = sessionmaker(bind=engine2)
    session = sessionMaker()
    salida = []

    if (tipo is None or tipo == '' or tipo == '0'):
        tipo = 0

    try:
        tipo = int(tipo)
    except Exception as e:
        tipo = 0

    if (week_number is None or week_number == '' or week_number == '0'):
        week_number = 0
    try:
        week_number = int(week_number)
    except Exception as e:
        week_number = 0

    print('tipo: ', tipo)
    print('week_number: ', week_number)
    print('fecha: ', fecha)

    if (fecha is None or fecha == '' or fecha == 0):
        if tipo == 0:
            if week_number == 0:
                resultado = session.query(DetalleMovimientoDrayageNormal.driver).distinct().all()
            else:
                resultado = session.query(DetalleMovimientoDrayageNormal.driver).filter(DetalleMovimientoDrayageNormal.week_number == week_number).distinct().all()
        else:
            if week_number == 0:
                resultado = session.query(DetalleMovimientoDrayageSpecial.driver).distinct().all()
            else:
                resultado = session.query(DetalleMovimientoDrayageSpecial.driver).filter(DetalleMovimientoDrayageSpecial.week_number == week_number).distinct().all()
    else:
        if tipo == 0:
            resultado = (session.query(DetalleMovimientoDrayageNormal.driver)
                             .filter(DetalleMovimientoDrayageNormal.date_local == fecha).distinct().all())
        else:
            resultado = (session.query(DetalleMovimientoDrayageSpecial.driver)
                             .filter(DetalleMovimientoDrayageSpecial.date_local == fecha).distinct().all())

    for r in resultado:
        registro = {"driver": r.driver}
        salida.append(registro)
    session.close()
    resultado = salida
    return resultado


def consulta_container(container_code):
    if (container_code is None or container_code == ''):
        return []
    engine2 = create_engine(conexion).execution_options(autocommit=True)
    sessionMaker = sessionmaker(bind=engine2)
    session = sessionMaker()

    result = session.query(MovimientosContainer).filter(MovimientosContainer.container_code == container_code).all()
    salida = []
    if (len(result) == 0):
        return []
    else:
        for r in result:
            registro = {"id_envio": r.id_envio, "date_time": r.fecha_hora_local.strftime("%m/%d/%Y %H:%M:%S"),
                        "driver": r.driver, "operation": r.tipo_operacion, "week_number": r.week_number, "location": r.ubicacion,
                        "container_code": r.container_code, "code": r.code}
            salida.append(registro)

    session.close()
    return salida


def fechas_gps():
    engine2 = create_engine(conexion).execution_options(autocommit=True)
    sessionMaker = sessionmaker(bind=engine2)
    session = sessionMaker()
    salida = []
    query_fecha = text("SELECT DISTINCT ON (date_trunc('day', fecha_hora_local)) to_char(fecha_hora_local, \
    'YYYYMMdd')::integer as id, to_char(fecha_hora_local, 'MM/dd/YYYY') as valor FROM jotform.gps g \
    JOIN facturacion.drivers d ON d.id_device_gps = g.id_device order \
    by date_trunc('day', fecha_hora_local) desc")
    try:
        resultado = session.execute(query_fecha)
        resultado = resultado.fetchall()
        for row in resultado:
            registro = {"id": row[0], "valor": row[1]}
            salida.append(registro)
    except Exception as e:
        print(e)
    session.close()
    return salida


def routes_gps():
    engine2 = create_engine(conexion).execution_options(autocommit=True)
    sessionMaker = sessionmaker(bind=engine2)
    session = sessionMaker()
    salida = []
    query = text("SELECT id_transaction as id, (to_char(delivery_date, 'MM/dd/YYYY') || ' - ' || p.driver || ' - ' || \
    delivery_order || ' - ' || 'ID:' || id_transaction::text || '-' || 'GPS:'  || id_device_gps::text) \
    as valor FROM jotform.planificacion p join facturacion.drivers \
    d ON p.driver = d.driver WHERE id_transaction IN (SELECT id_transaction FROM jotform.gps where \
    fecha_hora_local > '2025-03-30') ORDER BY delivery_date DESC, p.driver ASC, delivery_order ASC")
    try:
        resultado = session.execute(query)
        resultado = resultado.fetchall()
        for row in resultado:
            registro = {"id": row[0], "valor": row[1]}
            salida.append(registro)
    except Exception as e:
        print(e)
    session.close()
    return salida


def resumen_gps(fecha, device):
    engine2 = create_engine(conexion).execution_options(autocommit=True)
    sessionMaker = sessionmaker(bind=engine2)
    session = sessionMaker()
    salida = []
    if (fecha is None) or (fecha == "") or (fecha == 0) or (fecha == "0"):
        if (device is None) or (device == "") or (device == 0) or (device == "0"):
            query_gps = text("SELECT d.driver || ' - ' || id_device::text as driver,id_transaction::text, \
            to_char(fecha_hora_local, 'MM/dd/YYYY HH24:MI:SS') as fecha_hora,	speed::text as speed_mph, \
            (city || '/' || state_province || '/' || postal_code) as city_st_zip FROM jotform.gps g JOIN \
            facturacion.drivers d ON d.id_device_gps = g.id_device \
            ORDER BY d.driver, id_transaction DESC, fecha_hora_local DESC")
        else:
            query_gps = text("SELECT d.driver || ' - ' || id_device::text as driver,id_transaction::text, \
            to_char(fecha_hora_local, 'MM/dd/YYYY HH24:MI:SS') as fecha_hora,	speed::text as speed_mph, \
            (city || '/' || state_province || '/' || postal_code) as city_st_zip FROM jotform.gps g JOIN \
            facturacion.drivers d ON d.id_device_gps = g.id_device where \
            id_device = :device ORDER BY d.driver, id_transaction DESC, fecha_hora_local DESC")
    else:
        fecha = int(fecha)
        if (device is None) or (device == "") or (device == 0) or (device == "0"):
            query_gps = text("SELECT d.driver || ' - ' || id_device::text as driver,id_transaction::text, \
            to_char(fecha_hora_local, 'MM/dd/YYYY HH24:MI:SS') as fecha_hora,	speed::text as speed_mph, \
            (city || '/' || state_province || '/' || postal_code) as city_st_zip FROM jotform.gps g JOIN \
            facturacion.drivers d ON d.id_device_gps = g.id_device where \
            to_char(fecha_hora_local::date, 'YYYYMMdd')::integer = :fecha \
            ORDER BY d.driver, id_transaction DESC, fecha_hora_local DESC")
        else:
            query_gps = text("SELECT d.driver || ' - ' || id_device::text as driver,id_transaction::text, \
            to_char(fecha_hora_local, 'MM/dd/YYYY HH24:MI:SS') as fecha_hora,	speed::text as speed_mph, \
            (city || '/' || state_province || '/' || postal_code) as city_st_zip FROM jotform.gps g JOIN \
            facturacion.drivers d ON d.id_device_gps = g.id_device where \
            to_char(fecha_hora_local::date, 'YYYYMMdd')::integer = :fecha and \
            id_device = :device ORDER BY d.driver, id_transaction DESC, fecha_hora_local DESC")
    try:
        resultado = session.execute(query_gps, {"fecha": fecha, "device": device})
        resultado = resultado.fetchall()
        for row in resultado:
            registro = {"driver": row[0], "id_transaction": row[1], "fecha_hora": row[2], "speed_mph": row[3],
                        "city_st_zip": row[4]}
            salida.append(registro)
    except Exception as e:
        print(e)
    session.close()
    return salida


def drivers_gps(fecha):
    engine2 = create_engine(conexion).execution_options(autocommit=True)
    sessionMaker = sessionmaker(bind=engine2)
    session = sessionMaker()
    salida = []
    if (fecha is None) or (fecha == "") or (fecha == 0) or (fecha == "0"):
        query = text("SELECT DISTINCT ON (g.id_device) g.id_device as id, d.driver as valor FROM jotform.gps g \
        JOIN facturacion.drivers d ON d.id_device_gps = g.id_device	ORDER BY g.id_device DESC")
    else:
        fecha = int(fecha)
        query = text("SELECT DISTINCT ON (g.id_device) g.id_device as id, d.driver as valor FROM jotform.gps g \
                JOIN facturacion.drivers d ON d.id_device_gps = g.id_device	WHERE \
                to_char(fecha_hora_local::date, 'YYYYMMdd')::integer = :fecha ORDER BY g.id_device DESC")
    try:
        resultado = session.execute(query, {"fecha": fecha})
        resultado = resultado.fetchall()
        for row in resultado:
            registro = {"id": row[0], "valor": row[1]}
            salida.append(registro)
    except Exception as e:
        print(e)
    session.close()
    return salida


def summary_routes(transaction):
    engine2 = create_engine(conexion).execution_options(autocommit=True)
    sessionMaker = sessionmaker(bind=engine2)
    session = sessionMaker()
    ## salida = [{"date_time": "-", "city_st_zip": "-", "speed_mph": "-", "latitude_longitude": "-", "id_gps": 0}]
    salida = []
    if (transaction is None) or (transaction == "") or (transaction == 0) or (transaction == "0"):
        transaction = 0
        query = text("SELECT '-'::text as fecha_hora, '-'::text as city_st_zip, '-'::text \
        as speed_mph, '-'::text as latitude_longitude, 0 as id_gps, json_build_object('coordinates', \
        ARRAY[0::double precision, 0::double precision], 'type', 'Point') as json_geo, \
        0::double precision as lat, 0::double precision as lng;")
    else:
        transaction = int(transaction)
        query = text("SELECT to_char(fecha_hora_local, 'MM/dd/YYYY HH24:MI:SS') as date_time, (city || '/' || \
        state_province || '/' || postal_code) as city_st_zip, round(speed::numeric*1.151::numeric,2)::text \
        as speed_mph, latitud || '/' || longitud as latitude_longitude, g.id_gps, json_build_object('coordinates', \
        ARRAY[longitud::double precision, latitud::double precision], 'type', 'Point') AS json_geo, \
        latitud::double precision as lat, longitud::double precision as lng FROM \
        jotform.gps g JOIN facturacion.drivers d ON d.id_device_gps = g.id_device JOIN jotform.planificacion p \
        ON p.id_transaction = g.id_transaction WHERE g.id_transaction = :transaction ORDER BY d.driver, \
        p.id_transaction DESC, fecha_hora_local DESC")
    try:
        resultado = session.execute(query, {"transaction": transaction})
        resultado = resultado.fetchall()
        if not resultado:
            return salida
        for row in resultado:
            registro = {"date_time": row[0], "city_st_zip": row[1], "speed_mph": row[2], "latitude_longitude": row[3],
                        "id_gps": row[4], "json_geo": row[5], "lat": row[6], "lng": row[7]}
            salida.append(registro)
    except Exception as e:
        print(e)
    session.close()
    return salida


def summary_routes_v2(transaction):
    engine2 = create_engine(conexion).execution_options(autocommit=True)
    sessionMaker = sessionmaker(bind=engine2)
    session = sessionMaker()
    salida = []
    if (transaction is None) or (transaction == "") or (transaction == 0) or (transaction == "0"):
        transaction = 0
        query = text("SELECT '-'::text as fecha_hora, '-'::text as city_st_zip, '-'::text \
        as speed_mph, '-'::text as latitude_longitude, 0 as id_gps, json_build_object('coordinates', \
        ARRAY[0::double precision, 0::double precision], 'type', 'Point') as json_geo, \
        0::double precision as lat, 0::double precision as lng, '-'::text as remaining_distance, '-'::text as fecha_eta;")
    else:
        transaction = int(transaction)
        query = text("SELECT to_char(fecha_hora_local, 'MM/dd/YYYY HH24:MI:SS') as date_time, (city || '/' || \
        state_province || '/' || postal_code) as city_st_zip, round(speed::numeric*1.151::numeric,2)::text \
        as speed_mph, latitud || '/' || longitud as latitude_longitude, g.id_gps, json_build_object('coordinates', \
        ARRAY[longitud::double precision, latitud::double precision], 'type', 'Point') AS json_geo, \
        latitud::double precision as lat, longitud::double precision as lng, round(g.distancia_por_recorrer/1609,2)::text \
        as remaining_distance, to_char(CASE WHEN g.delayed is null THEN g.fecha_hora_eta ELSE CASE WHEN g.delayed \
        THEN g.fecha_hora_etadrop ELSE g.fecha_hora_eta END END, 'MM/dd/YYYY HH24:MI:SS') as fecha_eta FROM jotform.gps \
        g JOIN facturacion.drivers d ON d.id_device_gps = g.id_device JOIN jotform.planificacion p \
        ON p.id_transaction = g.id_transaction WHERE g.id_transaction = :transaction ORDER BY d.driver, \
        p.id_transaction DESC, fecha_hora_local DESC")
    try:
        resultado = session.execute(query, {"transaction": transaction})
        resultado = resultado.fetchall()
        if not resultado:
            return salida
        for row in resultado:
            registro = {"date_time": row[0], "city_st_zip": row[1], "speed_mph": row[2], "latitude_longitude": row[3],
                        "id_gps": row[4], "json_geo": row[5], "lat": row[6], "lng": row[7], "remaining_distance": row[8],
                        "fecha_eta": row[9]}
            salida.append(registro)
    except Exception as e:
        print(e)
    session.close()
    return salida


def eto_open_route(transaction):
    engine2 = create_engine(conexion).execution_options(autocommit=True)
    sessionMaker = sessionmaker(bind=engine2)
    session = sessionMaker()
    salida = []
    if (transaction is None) or (transaction == "") or (transaction == 0) or (transaction == "0"):
        transaction = 0
        query = text("SELECT '-'::text as date_time, '-'::text as driver, '-'::text as mensaje, \
        '-'::text as pick_location, '-'::text as drop_location, '-'::text as movement_type, '-'::text as estado, \
        '-'::text as error_envio_mensaje")
    else:
        transaction = int(transaction)
        query = text("SELECT to_char(fecha_hora_local, 'MM/dd/YYYY HH24:MI:SS') as date_time, driver, mensaje, \
        pick_location, drop_location, movement_type, estado, error_envio_mensaje FROM jotform.e_to_open \
        where id_transaction = :transaction and estado <> 'ANULADO' \
        and upper(trim(coalesce(formulario, ''))) <> 'SUPERVISOR_MESSAGE_FOR_E2OPEN' \
        ORDER BY fecha_hora_local desc")
    try:
        resultado = session.execute(query, {"transaction": transaction})
        resultado = resultado.fetchall()
        if not resultado:
            return salida
        for row in resultado:
            registro = {"date_time": row[0], "driver": row[1], "mensaje": row[2], "pick_location": row[3],
                        "drop_location": row[4], "movement_type": row[5], "estado": row[6],
                        "error_envio_mensaje": row[7]}
            salida.append(registro)
    except Exception as e:
        print(e)
    session.close()
    return salida


def coordenada_test(id_gps):
    print('id_gps', id_gps)
    geojson = {"type": "FeatureCollection", "features": [{"type": "Feature","properties": {"Name": "Caprese"},
                                                          "geometry": {"type": "Point",
                                                                       "coordinates": [11.35983, 44.49036]}}]}
    return geojson


def coordenadas_gps(id_gps):
    engine2 = create_engine(conexion).execution_options(autocommit=True)
    sessionMaker = sessionmaker(bind=engine2)
    session = sessionMaker()
    ## registro = {"latitud": -155.223266, "longitud": 19.957491}  ## Hawaii
    registro = {"latitud": -118.390514, "longitud": 33.386749}  ## Santa Catalina
    if (id_gps is None) or (id_gps == "") or (id_gps == 0) or (id_gps == "0"):
        id_gps = 0
        query = text("SELECT latitud, longitud FROM jotform.gps WHERE id_gps = :id_gps")
    else:
        id_gps = int(id_gps)
        query = text("SELECT latitud, longitud FROM jotform.gps WHERE id_gps = :id_gps")
    try:
        resultado = session.execute(query, {"id_gps": id_gps})
        resultado = resultado.fetchall()

        for row in resultado:
            registro = {"latitud": row[0], "longitud": row[1]}
    except Exception as e:
        print(e)
    session.close()
    geojson = {"type": "FeatureCollection", "features": [{"type": "Feature","properties": {"Name": "Caprese"},
                                                          "geometry": {"type": "Point",
                                                                       "coordinates": [registro["latitud"], registro["longitud"]]}},]}
    return geojson


def total_events(week_number):
    try:
        week_number = int(week_number)
    except Exception as e:
        week_number = 0
    engine2 = create_engine(conexion).execution_options(autocommit=True)
    sessionMaker = sessionmaker(bind=engine2)
    session = sessionMaker()
    if (week_number is None) or (week_number == "") or (week_number == 0) or (week_number == "0") or (week_number < 0):
        ##print("entro (1) " + str(week_number))
        query_week = text("select (select week_number::integer from jotform.resumen_semanal limit 1) as week_number, \
        sum(events) as total_events  from jotform.resumen_semanal where week_number = \
        (select week_number from jotform.resumen_semanal limit 1)")
    else:
        ##print("entro (2) " + str(week_number))
        query_week = text("SELECT max(week_number) as week_number, COUNT(*)::integer as total_events FROM jotform.drayage where \
        drayage.considerar_movimiento = 'yes'::text and week_number IS NOT NULL and week_number = " + str(week_number))
    salida = []
    try:
        resultado = session.execute(query_week)
        resultado = resultado.fetchone()
        salida = {"week_number": resultado[0],  "total_events": resultado[1]}
    except Exception as e:
        print(e)
    session.close()
    return salida



def total_events_v2(week_number, tipo):
    try:
        week_number = int(week_number)
    except Exception as e:
        week_number = 0
    try:
        tipo = int(tipo)
    except Exception as e:
        tipo = 0
    engine2 = create_engine(conexion).execution_options(autocommit=True)
    sessionMaker = sessionmaker(bind=engine2)
    session = sessionMaker()
    if (week_number is None) or (week_number == "") or (week_number == 0) or (week_number == "0") or (week_number < 0):
        ##print("entro (1) " + str(week_number))
        if tipo == 0:
            query_week = text("""select (select max(week_number)::integer from jotform.resumen_semanal_drayage) 
            as week_number, sum(events) as total_events  from jotform.resumen_semanal_drayage 
            where week_number = (select max(week_number) from jotform.resumen_semanal_drayage)""")
        else:
            query_week = text("""select (select max(week_number)::integer from jotform.resumen_semanal_special) 
            as week_number, sum(events) as total_events  from jotform.resumen_semanal_special 
            where week_number = (select max(week_number) from jotform.resumen_semanal_special)""")
    else:
        ##print("entro (2) " + str(week_number))
        if tipo == 0:
            query_week = text("""
            SELECT max(week_number) as week_number, COUNT(*)::integer as total_events FROM jotform.drayage 
            where drayage.considerar_movimiento = 'yes'::text and week_number IS NOT NULL 
            AND upper(substring(ubicacion, 1, 7)) <> 'SPECIAL' and week_number = """ + str(week_number))
        else:
            query_week = text("""
                SELECT max(week_number) as week_number, COUNT(*)::integer as total_events FROM jotform.drayage 
                where drayage.considerar_movimiento = 'yes'::text and week_number IS NOT NULL 
                AND upper(substring(ubicacion, 1, 7)) = 'SPECIAL' and week_number = """ + str(week_number))
    salida = []
    try:
        resultado = session.execute(query_week)
        resultado = resultado.fetchone()
        salida = {"week_number": resultado[0],  "total_events": resultado[1]}
    except Exception as e:
        print(e)
    session.close()
    return salida


def lista_month_diesel():
    engine2 = create_engine(conexion).execution_options(autocommit=True)
    sessionMaker = sessionmaker(bind=engine2)
    session = sessionMaker()
    query_week = text("SELECT periodo_nombre, periodo_numero FROM (SELECT to_char(year, '0000') || '_' || CASE \
    WHEN month = 1 THEN 'January' WHEN month = 2 THEN 'February' WHEN month = 3 THEN 'March' WHEN month = 4 THEN 'April' \
    WHEN month = 5 THEN 'May' WHEN month = 6 THEN 'June' WHEN month = 7 THEN 'July' WHEN month = 8 THEN 'August' \
    WHEN month = 9 THEN 'September' WHEN month = 10 THEN 'October' WHEN month = 11 THEN 'November' WHEN month = 12 \
    THEN 'December'	ELSE 'No month' END as periodo_nombre, mes as periodo_numero FROM (SELECT extract('year' from \
    fecha_hora_local) as year, extract('month' from fecha_hora_local) as month,	(trim(to_char(extract('year' from \
    fecha_hora_local), '0000')) || trim(to_char(extract('month' from fecha_hora_local), '00')))::integer as mes FROM \
    jotform.diesel) a) GROUP BY periodo_nombre, periodo_numero ORDER BY periodo_numero DESC")
    salida = []
    try:
        resultado = session.execute(query_week)
        resultado = resultado.fetchall()
        for row in resultado:
            registro = {"periodo_nombre": row[0], "periodo_numero": row[1]}
            salida.append(registro)
    except Exception as e:
        print(e)
    session.close()
    return salida


def eventos_total_diesel(periodo):
    try:
        periodo = int(periodo)
    except Exception as e:
        periodo = 0
    engine2 = create_engine(conexion).execution_options(autocommit=True)
    sessionMaker = sessionmaker(bind=engine2)
    session = sessionMaker()
    if (periodo is None) or (periodo == "") or (periodo == 0) or (periodo == "0") or (periodo < 0):
        query_week = text("SELECT to_char(anual, '0000') || '_' || CASE WHEN month = 1 THEN 'January' WHEN month = 2 \
        THEN 'February' WHEN month = 3 THEN 'March' WHEN month = 4 THEN 'April' WHEN month = 5 THEN 'May' WHEN \
        month = 6 THEN 'June' WHEN month = 7 THEN 'July' WHEN month = 8 THEN 'August' WHEN month = 9 THEN 'September' \
        WHEN month = 10 THEN 'October' WHEN month = 11 THEN 'November' WHEN month = 12 THEN 'December'	ELSE 'No month' \
        END as periodo_nombre, cuenta::integer FROM (SELECT extract('year' from fecha_hora_local) as anual, \
        extract('month' from fecha_hora_local) as month, count(id_envio) as cuenta FROM jotform.diesel GROUP BY \
        extract('year' from fecha_hora_local), extract('month' from fecha_hora_local) ORDER BY extract('year' from \
        fecha_hora_local) DESC, extract('month' from fecha_hora_local) DESC LIMIT 1 ) a")
    else:
        query_week = text("SELECT to_char(anual, '0000') || '_' || CASE WHEN month = 1 THEN 'January' WHEN month = 2 \
                THEN 'February' WHEN month = 3 THEN 'March' WHEN month = 4 THEN 'April' WHEN month = 5 THEN 'May' \
                WHEN month = 6 THEN 'June' WHEN month = 7 THEN 'July' WHEN month = 8 THEN 'August' WHEN month = 9 \
                THEN 'September' WHEN month = 10 THEN 'October' WHEN month = 11 THEN 'November' WHEN month = 12 \
                THEN 'December'	ELSE 'No month' END as periodo_nombre, cuenta::integer FROM (SELECT extract('year' \
                from fecha_hora_local) as anual, extract('month' from fecha_hora_local) as month, count(id_envio) \
                as cuenta FROM jotform.diesel WHERE (trim(to_char(extract('year' from fecha_hora_local), '0000')) || \
                trim(to_char(extract('month' from fecha_hora_local), '00')))::integer = " + str(periodo) + " GROUP BY \
                extract('year' from fecha_hora_local), extract('month' from fecha_hora_local) ORDER BY \
                extract('year' from fecha_hora_local) DESC, extract('month' from fecha_hora_local) DESC ) a")
    salida = []
    try:
        resultado = session.execute(query_week)
        resultado = resultado.fetchone()
        salida = {"periodo": resultado[0],  "total": resultado[1]}
    except Exception as e:
        print(e)
    session.close()
    return salida


def eventos_detalle_diesel(periodo):
    try:
        periodo = int(periodo)
    except Exception as e:
        periodo = 0
    engine2 = create_engine(conexion).execution_options(autocommit=True)
    sessionMaker = sessionmaker(bind=engine2)
    session = sessionMaker()
    if (periodo is None) or (periodo == "") or (periodo == 0) or (periodo == "0") or (periodo < 0):
        query_week = text("SELECT 'A' || trim(to_char(row_number() OVER (ORDER BY fecha_hora_local DESC), '0000')) \
        AS id, \
        id_envio, \
        to_char(fecha_hora_local, 'MM/dd/YYYY HH24:MI:SS') as fecha_hora, \
        driver, \
        truck_number, \
        location, \
        code_odometro, \
        CASE WHEN photo_odometro IS NULL THEN 'Not Available' ELSE trim(photo_odometro) END as photo_odometro, \
        code_receipt, \
        gallons_diesel, \
        code_gallons_diesel, \
        code_price_diesel, \
        code_amount_diesel, \
        gallons_def, \
        code_gallons_def, \
        code_price_def, \
        code_amount_def, \
        (replace(replace(receipt_amount,'$',''),',','.'))::numeric as receipt_amount, \
        code_total_amount_receipt, \
        CASE WHEN photo_receipt IS NULL THEN 'Not Available' ELSE trim(photo_receipt) END as photo_receipt,	\
        delivery_order,	\
        latitud || '/' || longitud as latitude_longitude, \
        latitud::double precision as lat, \
        longitud::double precision as lng  \
        FROM jotform.diesel ORDER BY fecha_hora_local DESC")
    else:
        query_week = text("SELECT 'A' || trim(to_char(row_number() OVER (ORDER BY fecha_hora_local DESC), '0000')) \
        AS id, \
        id_envio, \
        to_char(fecha_hora_local, 'MM/dd/YYYY HH24:MI:SS') as fecha_hora, \
        driver, \
        truck_number, \
        location, \
        code_odometro, \
        CASE WHEN photo_odometro IS NULL THEN 'Not Available' ELSE trim(photo_odometro) END as photo_odometro, \
        code_receipt, \
        gallons_diesel, \
        code_gallons_diesel, \
        code_price_diesel, \
        code_amount_diesel, \
        gallons_def, \
        code_gallons_def, \
        code_price_def, \
        code_amount_def, \
        (replace(replace(receipt_amount,'$',''),',','.'))::numeric as receipt_amount, \
        code_total_amount_receipt, \
        CASE WHEN photo_receipt IS NULL THEN 'Not Available' ELSE trim(photo_receipt) END as photo_receipt,	\
        delivery_order,	\
        latitud || '/' || longitud as latitude_longitude, \
        latitud::double precision as lat, \
        longitud::double precision as lng  \
        FROM jotform.diesel \
        WHERE (trim(to_char(extract('year' from fecha_hora_local), '0000')) || trim(to_char(extract('month' \
        from fecha_hora_local), '00')))::integer = " + str(periodo) + " ORDER BY fecha_hora_local DESC")
    salida = []
    try:

        resultado = session.execute(query_week)
        resultado = resultado.fetchall()
        if not resultado:
            return salida
        for row in resultado:
            status = "OK"
            message_status = "No errors found"
            photo_odometro = None
            photo_receipt = None

            receipt_amount = row[17]
            code_total_amount_receipt = row[18]
            if receipt_amount is None or receipt_amount == "" or receipt_amount == "0" or receipt_amount == 0:
                receipt_amount = -1

            gallons_diesel = row[9]
            code_gallons_diesel = row[10]
            if gallons_diesel is None or gallons_diesel == "" or gallons_diesel == "0" or gallons_diesel == 0:
                gallons_diesel = -1

            gallons_def = row[13]
            code_gallons_def = row[14]
            if gallons_def is None or gallons_def == "" or gallons_def == "0" or gallons_def == 0:
                gallons_def = -1

            if gallons_diesel != code_gallons_diesel:
                gallons_diesel = '<span style="color: #990000; font-weight: bold;">' + str(gallons_diesel) + '</span>'
                code_gallons_diesel = '<span style="color: #990000; font-weight: bold;">' + str(code_gallons_diesel) + '</span>'

            if gallons_def != code_gallons_def:
                gallons_def = '<span style="color: #CC0000; font-weight: bold;">' + str(gallons_def) + '</span>'
                code_gallons_def = '<span style="color: #CC0000; font-weight: bold;">' + str(code_gallons_def) + '</span>'

            if receipt_amount != code_total_amount_receipt:
                receipt_amount = '<span style="color: #FF0000; font-weight: bold;">' + str(receipt_amount) + '</span>'
                code_total_amount_receipt = '<span style="color: #FF0000; font-weight: bold;">' + str(code_total_amount_receipt) + '</span>'

            if row[7] != 'Not Available':
                ## photo_odometro = '<a href="' + row[7] + '" target="_blank">Show Image</a>'
                photo_odometro = 'Show Image'
            if row[19] != 'Not Available':
                ## photo_receipt = '<a href="' + row[19] + '" target="_blank">Show Image</a>'
                photo_receipt = 'Show Image'
            code_price_diesel = row[11]
            code_amount_diesel = row[12]
            code_price_def = row[15]
            code_amount_def = row[16]

            message_diesel = ''
            message_def = ''
            message_receipt = ''

            if es_decimal(code_gallons_diesel) and es_decimal(code_price_diesel) and es_decimal(code_amount_diesel):
                if Decimal(code_gallons_diesel) > 0 and Decimal(code_price_diesel) > 0 and Decimal(code_amount_diesel) > 0:
                    valor_1 = Decimal(Decimal(code_gallons_diesel)*Decimal(code_price_diesel)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                    valor_2 = Decimal(Decimal(code_amount_diesel)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                    if valor_1 != valor_2:
                        message_diesel = "Gallons Diesel * Price Diesel is not Amount Diesel"

            if es_decimal(code_gallons_def) and es_decimal(code_price_def) and es_decimal(code_amount_def):
                if Decimal(code_gallons_def) > 0 and Decimal(code_price_def) > 0 and Decimal(code_amount_def) > 0:
                    valor_1 = Decimal(Decimal(code_gallons_def)*Decimal(code_price_def)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                    valor_2 = Decimal(Decimal(code_amount_def)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                    if valor_1 != valor_2:
                        print('code_gallons_def', code_gallons_def, 'code_price_def', code_price_def, 'code_amount_def', code_amount_def)
                        print('valor_1', valor_1, 'valor_2', valor_2)
                        message_def = "Gallons Def * Price Def is not Amount Def"

            if es_decimal(code_total_amount_receipt) and es_decimal(receipt_amount):
                if Decimal(code_total_amount_receipt) > 0 and Decimal(receipt_amount) > 0:
                    if Decimal(code_total_amount_receipt) != Decimal(receipt_amount):
                        message_receipt = "Receipt Amount is not Total Amount Receipt"

            if len(message_diesel) > 0:
                message_status = message_diesel
                print('message_diesel (1)', message_diesel)
                if len(message_def) > 0:
                    message_status = message_status + chr(10) + message_def
                    print('message_def (2)', message_def)
                    if len(message_receipt) > 0:
                        print('message_receipt (3)', message_receipt)
                        message_status = message_status + chr(10) + message_receipt
            else:
                if len(message_def) > 0:
                    message_status = message_def
                    print('message_def (4)', message_def)
                    if len(message_receipt) > 0:
                        print('message_receipt (5)', message_receipt)
                        message_status = message_status + chr(10) + message_receipt
                else:
                    if len(message_receipt) > 0:
                        print('message_receipt (6)', message_receipt)
                        message_status = message_receipt
            if len(message_status) > 0 and message_status != 'No errors found':
                status = "ERROR"
                print("ERROR: " + row[0] + " - " + message_status)

            registro = {"id": row[0], "id_envio": row[1], "fecha_hora": row[2], "driver": row[3], "truck_number": row[4],
                         "location": row[5], "code_odometro": row[6], "photo_odometro": photo_odometro, "code_receipt": row[8],
                         "gallons_diesel": gallons_diesel, "code_gallons_diesel": code_gallons_diesel, "code_price_diesel": row[11],
                         "code_amount_diesel": row[12], "gallons_def": gallons_def, "code_gallons_def": code_gallons_def,
                         "code_price_def": row[15], "code_amount_def": row[16], "receipt_amount": receipt_amount,
                         "code_total_amount_receipt": code_total_amount_receipt, "photo_receipt": photo_receipt, "delivery_order": row[20],
                         "latitude_longitude": row[21], "lat": row[22], "lng": row[23], "status": status, "message_status": message_status}
            salida.append(registro)
    except Exception as e:
        print(e)
    session.close()
    return salida


def get_periodo_query(periodo):
    base_query = """
        SELECT 'A' || trim(to_char(row_number() OVER (ORDER BY fecha_hora_local DESC), '0000')) AS id,
               id_envio,
               to_char(fecha_hora_local, 'MM/dd/YYYY HH24:MI:SS') as fecha_hora,
               driver,
               truck_number,
               location,
               code_odometro,
               CASE WHEN photo_odometro IS NULL THEN 'Not Available' ELSE trim(photo_odometro) END as photo_odometro,
               code_receipt,
               gallons_diesel,
               code_gallons_diesel,
               code_price_diesel,
               code_amount_diesel,
               gallons_def,
               code_gallons_def,
               code_price_def,
               code_amount_def,
               (replace(replace(receipt_amount,'$',''),',','.'))::numeric as receipt_amount,
               code_total_amount_receipt,
               CASE WHEN photo_receipt IS NULL THEN 'Not Available' ELSE trim(photo_receipt) END as photo_receipt,
               delivery_order,
               latitud || '/' || longitud as latitude_longitude,
               latitud::double precision as lat,
               longitud::double precision as lng
        FROM jotform.diesel
    """

    if periodo and isinstance(periodo, int) and periodo > 0:
        return text(base_query + """
            WHERE (trim(to_char(extract('year' from fecha_hora_local), '0000')) ||
                   trim(to_char(extract('month' from fecha_hora_local), '00')))::integer = :periodo
            ORDER BY fecha_hora_local DESC
        """), {'periodo': periodo}
    else:
        return text(base_query + " ORDER BY fecha_hora_local DESC"), {}


def eventos_detalle_diesel_v2(periodo):
    try:
        periodo = int(periodo)
    except (ValueError, TypeError):
        periodo = 0

    engine2 = create_engine(conexion).execution_options(autocommit=True)
    Session = sessionmaker(bind=engine2)
    session = Session()

    query_week, params = get_periodo_query(periodo)

    salida = []
    try:
        resultado = session.execute(query_week, params).fetchall()

        for row in resultado:
            registro = dict(zip((
                "id", "id_envio", "fecha_hora", "driver", "truck_number", "location", "code_odometro",
                "photo_odometro", "code_receipt", "gallons_diesel", "code_gallons_diesel", "code_price_diesel",
                "code_amount_diesel", "gallons_def", "code_gallons_def", "code_price_def", "code_amount_def",
                "receipt_amount", "code_total_amount_receipt", "photo_receipt", "delivery_order",
                "latitude_longitude", "lat", "lng"
            ), row))

            def set_default_if_invalid(val):
                return -1 if val in (None, '', '0', 0) else val

            # Ajustes y colores para discrepancias
            for campo, codigo, color in [
                ("gallons_diesel", "code_gallons_diesel", "#990000"),
                ("gallons_def", "code_gallons_def", "#CC0000"),
                ("receipt_amount", "code_total_amount_receipt", "#FF0000")
            ]:
                val1 = set_default_if_invalid(registro[campo])
                val2 = registro[codigo]
                if val1 != val2:
                    registro[campo] = f'<span style="color: {color}; font-weight: bold;">{val1}</span>'
                    registro[codigo] = f'<span style="color: {color}; font-weight: bold;">{val2}</span>'

            # Validación de cálculos
            mensajes = []

            def validar_multiplicacion(gal, pre, monto, msg):
                if all(map(es_decimal, [gal, pre, monto])):
                    if round(float(gal)*float(pre), 2) != round(float(monto), 2):
                        mensajes.append(msg)

            validar_multiplicacion(registro["code_gallons_diesel"], registro["code_price_diesel"], registro["code_amount_diesel"],
                                   "Gallons Diesel * Price Diesel is not Amount Diesel")
            validar_multiplicacion(registro["code_gallons_def"], registro["code_price_def"], registro["code_amount_def"],
                                   "Gallons Def * Price Def is not Amount Def")

            if all(map(es_decimal, [registro["code_amount_diesel"], registro["code_amount_def"], registro["code_total_amount_receipt"]])):
                if round(float(registro["code_amount_diesel"]) + float(registro["code_amount_def"]), 2) != round(float(registro["code_total_amount_receipt"]), 2):
                    mensajes.append("Amount Diesel + Amount Def is not Total Amount Receipt")

            # Fotos
            registro["photo_odometro"] = "Show Image" if registro["photo_odometro"] != "Not Available" else None
            registro["photo_receipt"] = "Show Image" if registro["photo_receipt"] != "Not Available" else None

            registro["status"] = "ERROR" if mensajes else ""
            registro["message_status"] = "\n".join(mensajes)

            salida.append(registro)

    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        session.close()

    return salida


def registro_diesel_odometro_x_id(id_envio):
    engine2 = create_engine(conexion).execution_options(autocommit=True)
    sessionMaker = sessionmaker(bind=engine2)
    session = sessionMaker( )
    query_week = text("SELECT photo_odometro || '?apiKey=' || (SELECT passwd FROM jotform.credenciales WHERE websiteid = 'JOTFORMAPI') FROM jotform.diesel WHERE id_envio = " + str(id_envio))
    salida = []
    try:
        resultado = session.execute(query_week)
        resultado = resultado.fetchall()
        if not resultado:
            return salida
        for row in resultado:
            photo_odometro = 'Not Available'
            if row[0] != 'Not Available':
                photo_odometro = row[0]
            registro = {"photo_odometro": photo_odometro}
            salida.append(registro)
    except Exception as e:
        print(e)
    session.close()
    return salida


def registro_diesel_receipt_x_id(id_envio):
    engine2 = create_engine(conexion).execution_options(autocommit=True)
    sessionMaker = sessionmaker(bind=engine2)
    session = sessionMaker( )
    query_week = text("SELECT photo_receipt || '?apiKey=' || (SELECT passwd FROM jotform.credenciales WHERE websiteid = 'JOTFORMAPI') FROM jotform.diesel WHERE id_envio = " + str(id_envio))
    salida = []
    try:
        resultado = session.execute(query_week)
        resultado = resultado.fetchall()
        if not resultado:
            return salida
        for row in resultado:
            photo_receipt = 'Not Available'
            if row[0] != 'Not Available':
                photo_receipt = row[0]
            registro = {"photo_receipt": photo_receipt}
            salida.append(registro)
    except Exception as e:
        print(e)
    session.close()
    return salida


def registro_diesel_x_id(id_envio):
    engine2 = create_engine(conexion).execution_options(autocommit=True)
    sessionMaker = sessionmaker(bind=engine2)
    session = sessionMaker()
    query_week = text("SELECT id_envio, fecha_creacion, to_char(fecha_hora_local, 'MM/dd/YYYY HH24:MI:SS') \
    as fecha_hora, formulario, fecha_hora_driver, \
    delivery_order, driver, truck_number, email, location, (replace(replace(receipt_amount,'$',''),',','.'))::numeric \
    as receipt_amount, status, photo_odometro, photo_dispending, \
    photo_fuel_level, photo_receipt, longitud, latitud, estado, gallons_diesel, gallons_def, code_odometro, \
    code_dispending, code_fuel_level, code_receipt, code_diesel_level, code_gallons_diesel, code_price_diesel, \
    code_amount_diesel, code_gallons_def, code_price_def, code_amount_def, code_total_amount_receipt \
    FROM jotform.diesel WHERE id_envio = " + str(id_envio))
    salida = []
    try:
        resultado = session.execute(query_week)
        resultado = resultado.fetchall()
        if not resultado:
            return {"id_envio": id_envio, "fecha_creacion": 'Not Available', "fecha_hora": 'Not Available',
                    "formulario": 'Not Available', "fecha_hora_driver": 'Not Available', "delivery_order": 'Not Available',
                    "driver": 'Not Available', "truck_number": 'Not Available', "email": 'Not Available',
                    "location": 'Not Available', "receipt_amount": 'Not Available', "status": 'Not Available',
                    "photo_odometro": 'Not Available', "photo_dispending": 'Not Available', "photo_fuel_level": 'Not Available',
                    "photo_receipt": 'Not Available', "longitud": 'Not Available', "latitud": 'Not Available',
                    "estado": 'Not Available', "gallons_diesel": 'Not Available', "gallons_def": 'Not Available',
                    "code_odometro": 'Not Available', "code_dispending": 'Not Available', "code_fuel_level": 'Not Available',
                    "code_receipt": 'Not Available', "code_diesel_level": 'Not Available',
                    "code_gallons_diesel": 'Not Available', "code_price_diesel": 'Not Available',
                    "code_amount_diesel": 'Not Available', "code_gallons_def": 'Not Available',
                    "code_price_def": 'Not Available', "code_amount_def": 'Not Available',
                    "code_total_amount_receipt": 'Not Available'}
        for row in resultado:
            registro = {"id_envio": row[0], "fecha_creacion": row[1], "fecha_hora": row[2], "formulario": row[3],
                      "fecha_hora_driver": row[4], "delivery_order": row[5], "driver": row[6], "truck_number": row[7],
                      "email": row[8], "location": row[9], "receipt_amount": row[10], "status": row[11],
                      "photo_odometro": row[12], "photo_dispending": row[13], "photo_fuel_level": row[14],
                      "photo_receipt": row[15], "longitud": row[16], "latitud": row[17], "estado": row[18],
                      "gallons_diesel": row[19], "gallons_def": row[20], "code_odometro": row[21],
                      "code_dispending": row[22], "code_fuel_level": row[23], "code_receipt": row[24],
                      "code_diesel_level": row[25], "code_gallons_diesel": row[26], "code_price_diesel": row[27],
                      "code_amount_diesel": row[28], "code_gallons_def": row[29], "code_price_def": row[30],
                      "code_amount_def": row[31], "code_total_amount_receipt": row[32]}
            salida.append(registro)
    except Exception as e:
        print(e)
    session.close()
    return salida[0]


def update_registro_diesel_x_id(id_envio, data):
    print('id_envio: ', id_envio)
    print('data: ', data)
    truck_number = data['truck_number']
    code_odometro = data['code_odometro']
    code_receipt = data['code_receipt']
    gallons_diesel = data['gallons_diesel']
    code_gallons_diesel = data['code_gallons_diesel']
    code_price_diesel = data['code_price_diesel']
    code_amount_diesel = data['code_amount_diesel']
    gallons_def = data['gallons_def']
    code_gallons_def = data['code_gallons_def']
    code_price_def = data['code_price_def']
    code_amount_def = data['code_amount_def']
    receipt_amount = data['receipt_amount']
    code_total_amount_receipt = data['code_total_amount_receipt']
    engine2 = create_engine(conexion).execution_options(autocommit=True)
    sessionMaker = sessionmaker(bind=engine2)
    session = sessionMaker()
    query = text("UPDATE jotform.diesel SET truck_number = :truck_number, code_odometro = :code_odometro, \
    code_receipt = :code_receipt, gallons_diesel = :gallons_diesel, code_gallons_diesel = :code_gallons_diesel, \
    code_price_diesel = :code_price_diesel, code_amount_diesel = :code_amount_diesel, gallons_def = :gallons_def, \
    code_gallons_def = :code_gallons_def, code_price_def = :code_price_def, code_amount_def = :code_amount_def, \
    receipt_amount = :receipt_amount, code_total_amount_receipt = :code_total_amount_receipt WHERE id_envio = :id_envio")
    try:
        session.execute(query, {"truck_number": truck_number, "code_odometro": code_odometro, "code_receipt": code_receipt,
                                "gallons_diesel": gallons_diesel, "code_gallons_diesel": code_gallons_diesel,
                                "code_price_diesel": code_price_diesel, "code_amount_diesel": code_amount_diesel,
                                "gallons_def": gallons_def, "code_gallons_def": code_gallons_def,
                                "code_price_def": code_price_def, "code_amount_def": code_amount_def,
                                "receipt_amount": receipt_amount, "code_total_amount_receipt": code_total_amount_receipt,
                                "id_envio": id_envio})
        session.commit()
    except Exception as e:
        print(e)
        return {"msg": "Error al ingresar los datos", "success": False}
    session.close()
    return {"msg": "Dato ingresado correctamente", "success": True}


def viajes_facturacion_por_periodo(periodo):
    try:
        periodo = int(periodo)
    except (ValueError, TypeError):
        periodo = 0

    subquery = """
    SELECT week_number, client, year, day, month, facturado, no_facturado, facturado+no_facturado as total, 
    pagado, CASE WHEN facturado+no_facturado-pagado < 0 THEN 0 ELSE facturado+no_facturado-pagado END as unpaid, 
    cuenta FROM (SELECT week_number, upper(client) as client, to_char(delivered, 'YYYY') as year, 
    to_char(delivered, 'YYYY_MM_DD') as day, to_char(delivered, 'YYYY_MM') as month, 
    CASE WHEN invoice IS NOT NULL THEN amount_invoice ELSE 0 END as facturado, 
    CASE WHEN invoice IS NULL AND upper(client) <> 'CHIQUITA' THEN amount_invoice ELSE 0 END as no_facturado, 
    CASE WHEN payment_date IS NOT NULL THEN amount_invoice ELSE 0 END as pagado, 
    CASE WHEN upper(client) = 'CHIQUITA DRAYAGE' THEN container_code::integer ELSE 1 END as cuenta 
    FROM peneca.viajes) s
    """

    query = ""

    if periodo == 0:
        ## consulta por weekday
        query = text("""
        SELECT 'A' || trim(to_char(row_number() OVER (ORDER BY week_number DESC, client), '0000')) AS id, 
        a.week_number::text as period, a.client, sum(a.cuenta) as count,	sum(a.facturado)::numeric as invoiced, 
        sum(a.no_facturado)::numeric as uninvoiced, sum(a.total)::numeric as total, sum(a.pagado)::numeric as paid, 
        sum(a.unpaid)::numeric as unpaid  
        FROM (""" + subquery + """) a 
        GROUP BY week_number, client 
        ORDER BY week_number DESC, client
        """)
    elif periodo == 1:
        query = text("""
        SELECT 'A' || trim(to_char(row_number() OVER (ORDER BY month DESC, client), '0000')) AS id,	
        a.month::text as period, a.client, sum(a.cuenta) as count, sum(a.facturado)::numeric as invoiced, 
        sum(a.no_facturado)::numeric as uninvoiced, sum(a.total)::numeric as total, sum(a.pagado)::numeric as paid, 
        sum(a.unpaid)::numeric as unpaid  
        FROM (""" + subquery + """) a 
        GROUP BY month, client 
        ORDER BY month DESC, client
        """)
    elif periodo == 2:
        query = text("""
        SELECT 'A' || trim(to_char(row_number() OVER (ORDER BY day DESC, client), '0000')) AS id, 
        a.day::text as period, a.client, sum(a.cuenta) as count,	sum(a.facturado)::numeric as invoiced, 
        sum(a.no_facturado)::numeric as uninvoiced, sum(a.total)::numeric as total, sum(a.pagado)::numeric as paid, 
        sum(a.unpaid)::numeric as unpaid   
        FROM (""" + subquery + """) a 
        GROUP BY day, client 
        ORDER BY day DESC, client
        """)
    elif periodo == 3:
        query = text("""
                SELECT 'A' || trim(to_char(row_number() OVER (ORDER BY week_number DESC), '0000')) AS id, 
                a.week_number::text as period, 'ALL' as client, sum(a.cuenta) as count,	sum(a.facturado)::numeric as invoiced, 
                sum(a.no_facturado)::numeric as uninvoiced, sum(a.total)::numeric as total, sum(a.pagado)::numeric as paid, 
                sum(a.unpaid)::numeric as unpaid  
                FROM (""" + subquery + """) a 
                GROUP BY week_number 
                ORDER BY week_number DESC
                """)
    elif periodo == 4:
        query = text("""
                SELECT 'A' || trim(to_char(row_number() OVER (ORDER BY month DESC), '0000')) AS id,	
                a.month::text as period, 'ALL' as client, sum(a.cuenta) as count, sum(a.facturado)::numeric as invoiced, 
                sum(a.no_facturado)::numeric as uninvoiced, sum(a.total)::numeric as total, sum(a.pagado)::numeric as paid, 
                sum(a.unpaid)::numeric as unpaid  
                FROM (""" + subquery + """) a 
                GROUP BY month 
                ORDER BY month DESC
                """)
    elif periodo == 5:
        query = text("""
                SELECT 'A' || trim(to_char(row_number() OVER (ORDER BY day DESC), '0000')) AS id, 
                a.day::text as period, 'ALL' as client, sum(a.cuenta) as count,	sum(a.facturado)::numeric as invoiced, 
                sum(a.no_facturado)::numeric as uninvoiced, sum(a.total)::numeric as total, sum(a.pagado)::numeric as paid, 
                sum(a.unpaid)::numeric as unpaid   
                FROM (""" + subquery + """) a 
                GROUP BY day 
                ORDER BY day DESC
                """)
    else:
        return {"msg": "Error al obtener los datos", "success": False}

    ## print('query', query)

    engine2 = create_engine(conexion).execution_options(autocommit=True)
    Session = sessionmaker(bind=engine2)
    session = Session()

    salida = []
    try:
        resultado = session.execute(query).fetchall()

        for row in resultado:
            registro = {"id": row[0], "period": row[1], "client": row[2], "count": row[3], "invoiced": row[4],
                        "uninvoiced": row[5], "total": row[6], "paid": row[7], "unpaid": row[8]}
            salida.append(registro)
    except Exception as e:
        print(e)
    session.close()
    return salida


def get_reg_doc_por_tipo(tipo):
    if tipo == 'Driver':
        query = text("""
        SELECT DISTINCT ON (driver) driver as id, driver as valor FROM jotform.truck_driver_info WHERE driver 
        IS NOT NULL AND tipo = 'Driver' ORDER BY driver
        """)
    elif tipo == 'Truck':
        query = text("""
        SELECT DISTINCT ON (truck) truck as id, truck as valor FROM jotform.truck_driver_info WHERE truck 
        IS NOT NULL AND tipo = 'Truck' ORDER BY truck
        """)
    elif tipo == 'LM':
        query = text("""
        SELECT DISTINCT ON (other) other as id, other as valor FROM jotform.truck_driver_info WHERE other 
        IS NOT NULL AND tipo = 'LM' ORDER BY other
        """)
    else:
        return []
    engine2 = create_engine(conexion).execution_options(autocommit=True)
    Session = sessionmaker(bind=engine2)
    session = Session()

    salida = []
    try:
        resultado = session.execute(query).fetchall()
        for row in resultado:
            registro = {"id": row[0], "valor": row[1]}
            salida.append(registro)
    except Exception as e:
        print(e)
    session.close()
    return salida


def get_reg_doc_por_tipo_valor(tipo, valor):
    if tipo == 'Driver':
        query = text("""
        SELECT DISTINCT ON (dp.driver_parameter) dp.prioridad as id, tdi.driver_parameter as nombre, 
        dp.driver_parameter as parametro, tdi.documento as link, to_char(tdi.fecha_hora_local, 'MM/dd/YYYY HH24:MI:SS')
         as fecha_hora_local 
        FROM jotform.truck_driver_info tdi INNER JOIN jotform.driver_parameters dp 
        ON tdi.driver_parameter = dp.driver_parameter WHERE tdi.tipo = 'Driver' AND tdi.driver = :a 
        ORDER BY dp.driver_parameter, tdi.fecha_hora_local DESC
        """)
    elif tipo == 'Truck':
        query = text("""
        SELECT DISTINCT ON (dp.truck_parameter) dp.prioridad as id, tdi.truck_parameter as nombre, 
        dp.truck_parameter as parametro, tdi.documento as link, to_char(tdi.fecha_hora_local, 'MM/dd/YYYY HH24:MI:SS') 
        as fecha_hora_local
        FROM jotform.truck_driver_info tdi INNER JOIN jotform.truck_parameters dp 
        ON tdi.truck_parameter = dp.truck_parameter WHERE tdi.tipo = 'Truck' AND tdi.truck = :a 
        ORDER BY dp.truck_parameter, tdi.fecha_hora_local DESC
        """)
    elif tipo == 'LM':
        query = text("""
        SELECT DISTINCT ON (dp.other_parameter) dp.prioridad as id, tdi.other_parameter as nombre, 
        dp.other_parameter as parametro, tdi.documento as link, to_char(tdi.fecha_hora_local, 'MM/dd/YYYY HH24:MI:SS') 
        as fecha_hora_local 
        FROM jotform.truck_driver_info tdi INNER JOIN jotform.other_parameters dp 
        ON tdi.other_parameter = dp.other_parameter WHERE tdi.tipo = 'LM' AND tdi.other = :a 
        ORDER BY dp.other_parameter, tdi.fecha_hora_local DESC
        """)
    else:
        return []
    engine2 = create_engine(conexion).execution_options(autocommit=True)
    Session = sessionmaker(bind=engine2)
    session = Session()

    salida = []
    try:
        resultado = session.execute(query, {"a": valor}).fetchall()
        for row in resultado:
            registro = {
                "id": row[0], "name": row[1], "parameter": row[2], "link": row[3], "date_time_local": row[4]}
            salida.append(registro)
    except Exception as e:
        print(e)
    session.close()
    return salida


def drivers_check_list_truck():
    try:
        query = text("""
        SELECT DISTINCT ON (driver) driver as id, driver as valor FROM jotform.check_list_truck 
        WHERE driver IS NOT NULL ORDER BY driver
        """)
        engine2 = create_engine(conexion).execution_options(autocommit=True)
        Session = sessionmaker(bind=engine2)
        session = Session()

        salida = []
        try:
            resultado = session.execute(query).fetchall()
            for row in resultado:
                registro = {
                    "id": row[0], "valor": row[1]}
                salida.append(registro)
        except Exception as e:
            print(e)
        session.close()
        return salida
    except Exception as e:
        print(e)
        return []


def registros_check_list_truck(driver):
    try:
        ##print("uno", driver, ">")
        if driver is None or driver == "" or driver == 0 or driver == "0":
            query = text("""
            SELECT 'A' || trim(to_char(row_number() OVER (ORDER BY checklist_driver DESC), '0000')) AS id, 
            week_number,comment, to_char(checklist_driver, 'MM/dd/YYYY HH24:MI:SS') as checklist_driver, inspeccion,
            signature, to_char(fecha_hora_local, 'MM/dd/YYYY HH24:MI:SS') as fecha_hora_local, driver,longitud, latitud, 
            to_char(checklist_date_amp_time, 'MM/dd/YYYY HH24:MI:SS') as checklist_date_amp_time, truck_number, 
            CASE WHEN foto_odometro IS NULL THEN 'Not Available' ELSE trim(foto_odometro) END as foto_odometro  
            FROM 
            jotform.check_list_truck WHERE checklist_driver IS NOT NULL ORDER BY checklist_driver DESC,  driver ASC
            """)
        else:
            query = text("""
            SELECT 'A' || trim(to_char(row_number() OVER (ORDER BY checklist_driver DESC), '0000')) AS id, 
            week_number,comment, to_char(checklist_driver, 'MM/dd/YYYY HH24:MI:SS') as checklist_driver, inspeccion,
            signature, to_char(fecha_hora_local, 'MM/dd/YYYY HH24:MI:SS') as fecha_hora_local, driver,longitud, latitud, 
            to_char(checklist_date_amp_time, 'MM/dd/YYYY HH24:MI:SS') as checklist_date_amp_time, truck_number, 
            CASE WHEN foto_odometro IS NULL THEN 'Not Available' ELSE trim(foto_odometro) END as foto_odometro 
            FROM 
            jotform.check_list_truck WHERE checklist_driver IS NOT NULL AND driver = :a ORDER BY checklist_driver DESC
            """)
        engine2 = create_engine(conexion).execution_options(autocommit=True)
        Session = sessionmaker(bind=engine2)
        session = Session()

        salida = []
        try:
            resultado = session.execute(query, {"a": driver}).fetchall()
            print("dos")
            for row in resultado:
                registro = {
                    "id": row[0], "week_number": row[1], "comment": row[2], "checklist_driver": row[3],
                    "inspeccion": row[4], "signature": row[5], "fecha_hora_local": row[6], "driver": row[7],
                    "longitud": row[8], "latitud": row[9], "checklist_date_amp_time": row[10], "truck_number": row[11],
                    "foto_odometro": row[12]
                }
                salida.append(registro)
        except Exception as e:
            print(e)
        session.close()
        return salida
    except Exception as e:
        print(e)
        return []


def ver_activacion_bot(proceso):
    try:
        query = text("""
        SELECT activo FROM wsbot.activacion_bot WHERE proceso = :a
        """)
        engine2 = create_engine(conexion).execution_options(autocommit=True)
        Session = sessionmaker(bind=engine2)
        session = Session()

        salida = []
        try:
            resultado = session.execute(query, {"a": proceso}).fetchall()
            for row in resultado:
                registro = {
                    "activo": row[0]
                    }
                salida.append(registro)
        except Exception as e:
            print(e)
        session.close()
        return salida
    except Exception as e:
        print(e)
        return []




def inserta_drayage(uid, origen_ws, nombre_ws, localizacion, tipo, code, geolocation, localpath, shift, weekday,
                    file_b64):
    engine2 = create_engine(conexion).execution_options(autocommit=True)
    sessionMaker = sessionmaker(bind=engine2)
    session = sessionMaker()
    query_week = text(
        """
        DO $$
        BEGIN 
        IF NOT EXISTS (SELECT uid FROM wsbot.lm_drayage WHERE uid = :a) 
        THEN 
        INSERT INTO wsbot.lm_drayage(uid, origen_ws, nombre_ws, localizacion, tipo, code, 
        geolocation, localpath, shift, weekday, file_b64) 
        VALUES (:a, :b, :c, :d, :e, :f, :g, :h, :i, :j, :k); 
        END IF; END $$;
        """)
    try:
        session.execute(query_week, {"a": uid, "b": origen_ws, "c": nombre_ws, "d": localizacion,
                                     "e": tipo, "f": code, "g": geolocation, "h": localpath,
                                     "i": shift, "j": weekday, "k": file_b64})
        session.commit()
        resultado = {"status": "success"}
    except Exception as e:
        print(e)
        resultado = {"status": "error"}
    session.close()
    return resultado


def get_imagen_drayage(uid):
    engine2 = create_engine(conexion).execution_options(autocommit=True)
    sessionMaker = sessionmaker(bind=engine2)
    session = sessionMaker()
    query_week = text("select file_b64 from wsbot.lm_drayage where uid = :a")
    try:
        resultado = session.execute(query_week, {"a": uid})
        resultado = resultado.fetchone()
        if resultado:
            image_b64 = resultado[0]
            # Si incluye encabezado tipo "data:image/png;base64,", lo eliminamos
            if "," in image_b64:
                image_b64 = image_b64.split(",")[1]

            # Decodificar a bytes
            image_bytes = base64.b64decode(image_b64)

            # Crear un stream en memoria
            image_stream = io.BytesIO(image_bytes)
            return image_stream
        else:
            return None
    except Exception as e:
        print(e)
        return None


def get_registros_drayage_ws():
    engine2 = create_engine(conexion).execution_options(autocommit=True)
    sessionMaker = sessionmaker(bind=engine2)
    session = sessionMaker()
    query_week = text("""
    SELECT 'A' || trim(to_char(row_number() OVER (ORDER BY fecha_hora_local DESC), '000000')) AS id, fecha_hora_local, 
    uid, origen_ws, nombre_ws, localizacion, tipo, code, geolocation, localpath, shift, 
    weekday	FROM wsbot.lm_drayage ORDER BY fecha_hora_local DESC
    """)
    salida = []
    try:
        resultado = session.execute(query_week)
        resultado = resultado.fetchall()
        for row in resultado:
            registro = {"id": row[0], "fecha_hora_local": row[1], "uid": row[2], "origen_ws": row[3], "nombre_ws": row[4], "localizacion": row[5], "tipo": row[6], "code": row[7], "geolocation": row[8], "localpath": row[9], "shift": row[10], "weekday": row[11]}
            salida.append(registro)
    except Exception as e:
        print(e)
    session.close()
    return salida


def get_inicio_jornada(codigo_driver):
    engine2 = create_engine(conexion).execution_options(autocommit=True)
    sessionMaker = sessionmaker(bind=engine2)
    session = sessionMaker()
    query_week = text("""
        SELECT fd.codigo_app, fd.driver, fd.email, CASE WHEN jwh.id_working_hours IS NULL 
        THEN 0 ELSE jwh.id_working_hours END id_working_hours, CASE WHEN jwh.week_number IS NULL THEN 
        (WITH fecha AS (
			select now()::date - (EXTRACT(DOW FROM now()::date)::INT + 6) % 7 AS valor
		), filas AS (
			SELECT extract(week from valor) as semana, 
			extract(year from valor) as anio, 
			extract(month from valor) as mes FROM fecha
		)
		SELECT CASE WHEN semana = 1 AND mes = 12 
			THEN (to_char(anio + 1 - 2000, 'FM00') || to_char(semana, 'FM00'))::integer 
			ELSE (to_char(anio - 2000, 'FM00') || to_char(semana, 'FM00'))::integer END week_numer FROM filas) 
			ELSE jwh.week_number END week_number FROM facturacion.drivers fd 
			LEFT JOIN (	SELECT id_working_hours, week_number, driver_code, fecha_creacion FROM 
			(SELECT id_working_hours, action_working_hours, week_number, driver_code, fecha_creacion 
			FROM jotform.working_hours WHERE driver_code = :a ORDER BY fecha_creacion DESC LIMIT 1) w 
			WHERE UPPER(action_working_hours) = 'CHECKIN') jwh	ON fd.codigo_app = jwh.driver_code WHERE codigo_app = :a
			LIMIT 1;
        """)
    ## salida = []
    registro = {"success": False, "msg": "Driver code error"}
    try:
        resultado = session.execute(query_week, {"a": codigo_driver})
        resultado = resultado.fetchall()
        for row in resultado:
            tipo = 'CHECKIN'
            if row[3] != 0:
                tipo = 'CHECKOUT'
            registro = {"codigo_app": row[0], "driver": row[1], "email": row[2], "id_working_hours": row[3],
                        "week_number": row[4], "tipo": tipo, "success": True}
            ## salida.append(registro)
    except Exception as e:
        print(e)
    session.close()
    return registro


def ingresa_inicio_jornada(id_working_hours, codigo_driver, driver, week_number, email, longitud, latitud, date_time_driver):
    engine2 = create_engine(conexion).execution_options(autocommit=True)
    sessionMaker = sessionmaker(bind=engine2)
    session = sessionMaker()
    if id_working_hours <= 0:
        check = 'CHECKIN'
        query_week = text("""
                INSERT INTO jotform.working_hours (id_working_hours, fecha_creacion, fecha_hora_local, driver_code, driver, 
                week_number, email, longitud, latitud, date_time_driver, action_working_hours, estado) 
                VALUES ((SELECT CASE WHEN max(id_working_hours) IS NULL THEN 10 ELSE max(id_working_hours) + 1 END AS maximo 
                FROM jotform.working_hours), now(),	
                substring(((now()::timestamp without time zone AT TIME ZONE 'UTC'::text) AT TIME ZONE 
                'America/Los_Angeles'::text)::text, 1, 19)::timestamp without time zone,
                :b, :c, :d, :e, :f, :g, :h, :i, 'NUEVO') RETURNING id_secuencial;
                """)
    else:
        check = 'CHECKOUT'
        query_week = text("""
                INSERT INTO jotform.working_hours (id_working_hours, fecha_creacion, fecha_hora_local, driver_code, driver, 
                week_number, email, longitud, latitud, date_time_driver, action_working_hours, estado) 
                VALUES (:a, now(),	
                substring(((now()::timestamp without time zone AT TIME ZONE 'UTC'::text) AT TIME ZONE 
                'America/Los_Angeles'::text)::text, 1, 19)::timestamp without time zone,
                :b, :c, :d, :e, :f, :g, :h, :i, 'NUEVO') RETURNING id_secuencial;
                """)
    salida = {"success": False, "msg": "Error"}
    print(query_week)
    try:
        resultado = session.execute(query_week, {"a": id_working_hours, "b": codigo_driver, "c": driver,
                                                 "d": week_number, "e": email, "f": longitud, "g": latitud,
                                                 "h": date_time_driver, "i": check})
        resultado = resultado.fetchall()
        for row in resultado:
            print("uno")
            if row[0] > 0:
                print("dos")
                salida = {"success": True, "msg": "Success"}
    except Exception as e:
        print(e)
    session.commit()
    session.close()
    return salida


def formulario_aceptacion(codigo_driver):
    if codigo_driver is None or codigo_driver == "" or codigo_driver == 0 or codigo_driver == "0":
        return []

    ##print("codigo_driver", codigo_driver)
    engine2 = create_engine(conexion).execution_options(autocommit=True)
    sessionMaker = sessionmaker(bind=engine2)
    session = sessionMaker()
    query_week = text("""
        SELECT drivers.*, 'Enabled'::text as status, 
        CASE WHEN da.id_envio IS NULL THEN 
        (SELECT link FROM jotform.links WHERE nombre = 'drayage_aceptacion') 
        ELSE (SELECT link FROM jotform.links WHERE nombre = 'drayage') END as url_form, 
        CASE WHEN da.id_envio IS NULL THEN NULL  
        ELSE (SELECT link FROM jotform.links WHERE nombre = 'drayage_checkout') END as url_checkout FROM 
        (SELECT driver, email, (WITH fecha AS (select now()::date - (EXTRACT(DOW FROM now()::date)::INT + 6) % 7 
        AS valor), filas AS (
			SELECT extract(week from valor) as semana, 
			extract(year from valor) as anio, 
			extract(month from valor) as mes FROM fecha
		)
		SELECT CASE WHEN semana = 1 AND mes = 12 
			THEN (to_char(anio + 1 - 2000, 'FM00') || to_char(semana, 'FM00'))::integer 
			ELSE (to_char(anio - 2000, 'FM00') || to_char(semana, 'FM00'))::integer END week_numer FROM filas) 
			as week_number FROM facturacion.drivers fd WHERE fd.codigo_app = :a) drivers 
			LEFT JOIN (SELECT DISTINCT ON (week_number, email) week_number, email, id_envio 
			FROM (SELECT id_envio, driver, week_number, email FROM jotform.drayage_aceptacion 
			UNION 
			SELECT id_envio, driver, week_number, email FROM jotform.drayage_aceptacion_webhook) as daw	
			ORDER BY week_number, email) da ON drivers.email = da.email 
			AND drivers.week_number = da.week_number LIMIT 1
        """)
    salida = []
    try:
        resultado = session.execute(query_week, {"a": codigo_driver})
        resultado = resultado.fetchall()
        ##if (len(resultado) == 0):
        ##    return []
        for row in resultado:
            print(row)

            url_base = row[4]
            url_checkout = row[5]
            print(url_base)
            params = {
                "typeA": codigo_driver,
                "driver58": row[0],
                "driver48": row[0],
                "email": row[1],
                "weekNumber": row[2],
                "status": row[3],
            }
            full_url_form = url_base + "?" + urlencode(params)
            if url_checkout is not None:
                full_url_checkout = url_checkout + "?" + urlencode(params)
            else:
                full_url_checkout = None
            print(full_url_form)
            registro = {"driver": row[0], "email": row[1], "week_number": row[2], "status": row[3], "full_url_form": full_url_form, "full_url_checkout": full_url_checkout}
            salida.append(registro)
    except Exception as e:
        print(e)
    session.close()
    return salida

def formulario_aceptacion_v2(codigo_driver):
    if codigo_driver is None or codigo_driver == "" or codigo_driver == 0 or codigo_driver == "0":
        return []

    ##print("codigo_driver", codigo_driver)
    engine2 = create_engine(conexion).execution_options(autocommit=True)
    sessionMaker = sessionmaker(bind=engine2)
    session = sessionMaker()
    query_week = text("""
        SELECT d.driver, d.email, d.week_number, d.status, l.link as url_form, l.title  FROM jotform.links l JOIN 
        (SELECT driver, drivers.email, drivers.week_number, 'Enabled'::text as status, CASE WHEN id_envio IS NULL 
        THEN 0 ELSE 1 END as id_envio 
        FROM 
        (SELECT driver, email, (WITH fecha AS (select now()::date - (EXTRACT(DOW FROM now()::date)::INT + 6) % 7 
        AS valor), filas AS (
                        SELECT extract(week from valor) as semana, 
                        extract(year from valor) as anio, 
                        extract(month from valor) as mes FROM fecha
                )
                SELECT CASE WHEN semana = 1 AND mes = 12 
                        THEN (to_char(anio + 1 - 2000, 'FM00') || to_char(semana, 'FM00'))::integer 
                        ELSE (to_char(anio - 2000, 'FM00') || to_char(semana, 'FM00'))::integer END week_number FROM filas) 
                        as week_number FROM facturacion.drivers fd WHERE upper(fd.codigo_app) = upper(:a)) drivers 
                        LEFT JOIN (SELECT DISTINCT ON (week_number, email) week_number, email, id_envio 
                        FROM (SELECT id_envio, driver, week_number, email FROM jotform.drayage_aceptacion 
                        UNION 
                        SELECT id_envio, driver, week_number, email FROM jotform.drayage_aceptacion_webhook) as daw     
                        ORDER BY week_number, email) da ON drivers.email = da.email 
                        AND drivers.week_number = da.week_number LIMIT 1) d 
                        ON l.id_envio = d.id_envio ORDER BY l.id
        """)
    salida = []
    try:
        resultado = session.execute(query_week, {"a": codigo_driver})
        resultado = resultado.fetchall()
        ##if (len(resultado) == 0):
        ##    return []
        for row in resultado:
            print(row)

            url_base = row[4]
            title = row[5]
            print(url_base)
            params = {
                "typeA": codigo_driver,
                "driver58": row[0],
                "driver48": row[0],
                "email": row[1],
                "weekNumber": row[2],
                "status": row[3],
            }
            full_url_form = url_base + "?" + urlencode(params)

            registro = {"driver": row[0], "email": row[1], "week_number": row[2], "status": row[3], "full_url_form": full_url_form, "title": title}
            salida.append(registro)
    except Exception as e:
        print(e)
    session.close()
    return salida


def webhook_drayage_aceptacion(submissionid, weeknumber, email, driver58):
    #Insertar los datos en la tabla drayage_webhook
    engine2 = create_engine(conexion).execution_options(autocommit=True)
    sessionMaker = sessionmaker(bind=engine2)
    session = sessionMaker()
    try:
        query = text("""
        INSERT INTO jotform.drayage_aceptacion_webhook(id_envio, driver, week_number, email) 
        VALUES (:a, :b, :c, :d);
        """)
        session.execute(query, {"a": submissionid, "b": driver58, "c": weeknumber, "d": email})
        session.commit()
        session.close()
        return True
    except Exception as e:
        print(e)
        session.close()
        return False


def es_decimal(s):
    try:
        float(s)
        return True
    except (ValueError, TypeError):
        return False
