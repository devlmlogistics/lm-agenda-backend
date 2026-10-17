from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import declarative_base
from src.config.db_config import esquema

Base = declarative_base()


class ResumenDriverSemanaDrayage(Base):
    __tablename__ = 'resumen_semanal_drayage'
    __table_args__ = {'schema': esquema}
    id = Column(Integer, primary_key=True)
    driver = Column(String)
    last_movement = Column(String)
    day = Column(String)
    range = Column(String)
    events = Column(String)
    week_number = Column(Integer)
    dia = Column(Integer)
