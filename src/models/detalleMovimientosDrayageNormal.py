from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import declarative_base
from src.config.db_config import esquema

Base = declarative_base()


class DetalleMovimientoDrayageNormal(Base):
    __tablename__ = 'detalle_movimientos_drayage_normal'
    __table_args__ = {'schema': esquema}
    id = Column(Integer, primary_key=True)
    date_time_local = Column(String)
    driver = Column(String)
    movement = Column(String)
    date_local = Column(String)
    week_number = Column(Integer)
