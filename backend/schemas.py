from pydantic import BaseModel, Field
from typing import List, Optional

class ExamenSchema(BaseModel):
    codigo: str
    nombre: str
    valor_bono_fonasa: int
    valor_copago: int
    valor_particular_general: int
    valor_particular_preferencial: int

    class Config:
        from_attributes = True

class PaqueteExamenSchema(BaseModel):
    # Usamos validation_alias para leer de la DB (examen_codigo)
    # y el nombre del campo (codigo) para la salida JSON al frontend.
    codigo: Optional[str] = Field(None, validation_alias="examen_codigo")
    nombre: str = Field(..., validation_alias="examen_nombre")
    cantidad: int

    class Config:
        from_attributes = True

class PaqueteSchema(BaseModel):
    id: int
    nombre: str
    examenes: List[PaqueteExamenSchema]

    class Config:
        from_attributes = True

class CotizacionExamen(BaseModel):
    codigo: str
    nombre: str
    cantidad: int
    valor_bono_fonasa: int
    valor_copago: int
    valor_particular_general: int
    valor_particular_preferencial: int

class CotizacionRequest(BaseModel):
    nombre_paciente: str
    fecha_nacimiento: str
    tipo_documento: str
    documento_id: str
    prevision: str
    es_publico: Optional[bool] = False
    pack_activo: Optional[str] = None
    examenes: List[CotizacionExamen]

class LoginRequest(BaseModel):
    username: str
    password: str

class AdminStats(BaseModel):
    total_cotizaciones: int
    total_hoy: int
    monto_fonasa: int
    monto_particular: int
    top_examenes: List[dict]
    trend_data: List[dict]

class UpdatePriceRequest(BaseModel):
    valor_bono_fonasa: int
    valor_copago: int
    valor_particular_general: int
    valor_particular_preferencial: int
