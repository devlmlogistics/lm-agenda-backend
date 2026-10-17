from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import declarative_base
from src.config.db_config import esquema

Base = declarative_base()


class MovimientosContainer(Base):
    __tablename__ = 'movimientos_container'
    __table_args__ = {'schema': esquema}
    id_envio = Column(Integer, primary_key=True)
    fecha_hora_local = Column(String)
    driver = Column(String)
    tipo_operacion = Column(String)
    week_number = Column(Integer)
    ubicacion = Column(String)
    container_code = Column(String)
    code = Column(String)