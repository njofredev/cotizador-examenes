import os
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Conexión persistente
DATABASE_URL = "postgresql://{user}:{password}@{host}:{port}/{database}".format(
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    host=os.getenv("POSTGRES_HOST"),
    port=os.getenv("POSTGRES_PORT"),
    database=os.getenv("POSTGRES_DATABASE")
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Arancel(Base):
    __tablename__ = "aranceles"
    codigo = Column(String, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    valor_bono_fonasa = Column(Integer, default=0)
    valor_copago = Column(Integer, default=0)
    valor_particular_general = Column(Integer, default=0)
    valor_particular_preferencial = Column(Integer, default=0)
    busqueda = Column(String)

class Paquete(Base):
    __tablename__ = "paquetes"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, nullable=False)
    examenes = relationship("PaqueteExamen", back_populates="paquete")

class PaqueteExamen(Base):
    __tablename__ = "paquete_examenes"
    id = Column(Integer, primary_key=True, index=True)
    paquete_id = Column(Integer, ForeignKey("paquetes.id"))
    examen_codigo = Column(String)
    examen_nombre = Column(String, nullable=False)
    cantidad = Column(Integer, default=1)
    
    paquete = relationship("Paquete", back_populates="examenes")

class Cotizacion(Base):
    __tablename__ = "cotizaciones"
    id = Column(String, primary_key=True, index=True)
    folio = Column(String, unique=True, index=True)
    nombre_paciente = Column(String)
    tipo_documento = Column(String)
    documento_id = Column(String, index=True)
    fecha_nacimiento = Column(DateTime)
    fecha_cotizacion = Column(DateTime, default=datetime.now)
    total_fonasa = Column(Integer)
    total_copago = Column(Integer)
    total_particular_gral = Column(Integer)
    total_particular_pref = Column(Integer)
    prevision = Column(String)

class DetalleCotizacion(Base):
    __tablename__ = "detalle_cotizaciones"
    id = Column(String, primary_key=True, index=True)
    folio_cotizacion = Column(String, ForeignKey("cotizaciones.folio"))
    codigo_examen = Column(String)
    nombre_examen = Column(String)
    valor_copago = Column(Integer)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
