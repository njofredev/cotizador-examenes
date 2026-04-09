import os
import uvicorn
import pandas as pd
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
import uuid
from datetime import datetime

from database import SessionLocal, get_db, Arancel, Paquete, PaqueteExamen, Cotizacion, DetalleCotizacion
from schemas import ExamenSchema, PaqueteSchema, CotizacionRequest
from pdf_generator import generar_cotizacion_pdf
from utils import obtener_ahora_chile

app = FastAPI(title="Cotizador Policlínico Tabancura API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/examenes", response_model=List[ExamenSchema])
def get_examenes(db: Session = Depends(get_db)):
    try:
        return db.query(Arancel).order_by(Arancel.nombre.asc()).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener exámenes: {e}")

@app.get("/api/paquetes", response_model=List[PaqueteSchema])
def get_paquetes(db: Session = Depends(get_db)):
    try:
        return db.query(Paquete).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener paquetes: {e}")

@app.get("/api/paciente/{doc_id}")
def get_paciente(doc_id: str, db: Session = Depends(get_db)):
    try:
        res = db.query(Cotizacion).filter(Cotizacion.documento_id == doc_id).order_by(desc(Cotizacion.fecha_cotizacion)).first()
        if res:
            return {
                "nombre": res.nombre_paciente,
                "fecha_nacimiento": res.fecha_nacimiento.strftime("%Y-%m-%d") if res.fecha_nacimiento else None,
                "prevision": res.prevision
            }
        return {"nombre": None}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al buscar paciente: {e}")

@app.post("/api/cotizar")
def post_cotizar(request: CotizacionRequest, db: Session = Depends(get_db)):
    try:
        folio_cot = str(uuid.uuid4())[:8].upper()
        folio_om = str(uuid.uuid4())[:8].upper()
        ahora = obtener_ahora_chile()
        
        is_fonasa = request.prevision.lower() == "fonasa"
        examenes_list = []
        t_f, t_c, t_pg, t_pp = 0, 0, 0, 0
        
        for item in request.examenes:
            # Determinamos el copago según la lógica de negocio (Sincronizado con frontend)
            if is_fonasa:
                copago_unidad = item.valor_copago if item.valor_bono_fonasa > 0 else item.valor_particular_general
            else:
                copago_unidad = item.valor_particular_preferencial

            # Sincronizar nombres de columnas con lo que espera pdf_generator.py
            examenes_list.append({
                "Código": item.codigo,
                "Nombre": item.nombre,
                "Cant": item.cantidad,
                "Valor bono Fonasa": item.valor_bono_fonasa,
                "Valor copago": item.valor_copago,
                "Valor particular General": item.valor_particular_general,
                "Valor particular preferencial": item.valor_particular_preferencial,
                "Copago Calculado": copago_unidad # Campo para trazabilidad
            })
            
            t_f += item.valor_bono_fonasa * item.cantidad
            t_c += copago_unidad * item.cantidad
            t_pg += item.valor_particular_general * item.cantidad
            t_pp += item.valor_particular_preferencial * item.cantidad

        # Persistir en Base de Datos con los totales RECALCULADOS
        nueva_cot = Cotizacion(
            id=str(uuid.uuid4()),
            folio=folio_cot,
            nombre_paciente=request.nombre_paciente,
            tipo_documento="RUT Nacional" if "-" in request.documento_id else "Pasaporte",
            documento_id=request.documento_id,
            fecha_nacimiento=datetime.strptime(request.fecha_nacimiento, "%Y-%m-%d") if request.fecha_nacimiento else None,
            fecha_cotizacion=ahora,
            total_fonasa=int(t_f),
            total_copago=int(t_c),
            total_particular_gral=int(t_pg),
            total_particular_pref=int(t_pp),
            prevision=request.prevision
        )
        db.add(nueva_cot)
        
        for ex in examenes_list:
            db.add(DetalleCotizacion(
                id=str(uuid.uuid4()),
                folio_cotizacion=folio_cot,
                codigo_examen=ex["Código"],
                nombre_examen=ex["Nombre"],
                valor_copago=ex["Copago Calculado"] # Guardamos el copago real cobrado
            ))
        db.commit()

        # Preparar data para el generador
        f_nac_dt = datetime.strptime(request.fecha_nacimiento, "%Y-%m-%d") if request.fecha_nacimiento else None
        df_sel = pd.DataFrame(examenes_list)

        # Generar PDF usando el generador histórico con los totales CORRECTOS
        generar_cotizacion_pdf(
            folio_cot, folio_om, ahora.strftime("%d/%m/%Y %H:%M:%S"),
            request.nombre_paciente, request.documento_id, 
            f_nac_dt, request.prevision,
            df_sel, int(t_f), int(t_c), int(t_pg), int(t_pp),
            pack_nombre=request.pack_activo, incluir_om=(request.pack_activo is not None)
        )
        
        filename = f"Cot_{folio_cot}.pdf"
        
        return {
            "success": True,
            "folio": folio_cot,
            "pdf_url": f"/api/pdf/{filename}"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error en el proceso de cotización: {e}")

from fastapi.responses import FileResponse
@app.get("/api/pdf/{filename}")
def get_pdf(filename: str):
    file_path = os.path.join(os.path.dirname(__file__), filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type='application/pdf', filename=filename)
    raise HTTPException(status_code=404, detail="Archivo PDF no encontrado")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
