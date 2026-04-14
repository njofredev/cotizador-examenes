import os
import uvicorn
import pandas as pd
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
import uuid
from datetime import datetime

from database import SessionLocal, get_db, Arancel, Paquete, PaqueteExamen, Cotizacion, DetalleCotizacion
from schemas import ExamenSchema, PaqueteSchema, CotizacionRequest, LoginRequest, AdminStats, UpdatePriceRequest
from utils import obtener_ahora_chile
from sqlalchemy import func, case
from pdf_generator import generar_cotizacion_pdf

# Configuración de directorios
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_OUTPUT_DIR = os.path.join(BASE_DIR, "generated_pdfs")
os.makedirs(PDF_OUTPUT_DIR, exist_ok=True)

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
        pdf_path = generar_cotizacion_pdf(
            folio_cot, folio_om, ahora.strftime("%d/%m/%Y %H:%M:%S"),
            request.nombre_paciente, request.documento_id, 
            f_nac_dt, request.prevision,
            df_sel, int(t_f), int(t_c), int(t_pg), int(t_pp),
            pack_nombre=request.pack_activo, incluir_om=(request.pack_activo is not None),
            output_dir=PDF_OUTPUT_DIR
        )
        
        filename = os.path.basename(pdf_path)
        
        return {
            "success": True,
            "folio": folio_cot,
            "pdf_url": f"/api/pdf/{filename}"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error en el proceso de cotización: {e}")

# --- RUTAS ADMINISTRATIVAS ---

def check_admin_auth(password: Optional[str] = Header(None)):
    # En producción esto sería un JWT, aquí validamos contra el .env para simplicidad
    valid_pass = os.getenv("ADMIN_PASSWORD", "Tabancura2026!")
    if password != valid_pass:
        raise HTTPException(status_code=401, detail="No autorizado")
    return True

@app.post("/api/admin/login")
def admin_login(request: LoginRequest):
    valid_user = os.getenv("ADMIN_USER", "admin")
    valid_pass = os.getenv("ADMIN_PASSWORD", "Tabancura2026!")
    
    if request.username == valid_user and request.password == valid_pass:
        return {"success": True, "token": valid_pass} # Usamos el pass como token simple
    raise HTTPException(status_code=401, detail="Credenciales incorrectas")

@app.get("/api/admin/stats", response_model=AdminStats)
def get_admin_stats(db: Session = Depends(get_db), auth=Depends(check_admin_auth)):
    try:
        ahora = obtener_ahora_chile()
        inicio_hoy = ahora.replace(hour=0, minute=0, second=0, microsecond=0)
        
        total_cots = db.query(func.count(Cotizacion.id)).scalar()
        total_hoy = db.query(func.count(Cotizacion.id)).filter(Cotizacion.fecha_cotizacion >= inicio_hoy).scalar()
        
        # Montos acumulados (Copagos reales)
        monto_f = db.query(func.sum(Cotizacion.total_copago)).filter(Cotizacion.prevision.ilike('fonasa')).scalar() or 0
        monto_p = db.query(func.sum(Cotizacion.total_particular_pref)).filter(Cotizacion.prevision.ilike('particular')).scalar() or 0
        
        # Top 5 Exámenes (desde DetalleCotizacion)
        top_ex = db.query(
            DetalleCotizacion.nombre_examen, 
            func.count(DetalleCotizacion.id).label('total')
        ).group_by(DetalleCotizacion.nombre_examen).order_by(desc('total')).limit(5).all()
        
        top_list = [{"nombre": r[0], "cantidad": r[1]} for r in top_ex]
        
        # Datos de tendencia (Últimos 15 días)
        # Nota: Usamos func.date para agrupar por día (compatibilidad SQLite/Postgres varía un poco, corregimos para Postgres)
        trend_results = db.query(
            func.date(Cotizacion.fecha_cotizacion).label('fecha'),
            func.count(Cotizacion.id).label('cantidad')
        ).filter(Cotizacion.fecha_cotizacion >= ahora.replace(day=ahora.day-15 if ahora.day > 15 else 1)) \
         .group_by('fecha').order_by('fecha').all()
        
        # Formateo robusto de fechas (maneja datetime.date y strings de SQLite)
        trend_list = []
        for r in trend_results:
            fecha_val = r[0]
            if hasattr(fecha_val, 'strftime'):
                fecha_str = fecha_val.strftime("%d/%m")
            else:
                # Si es string (SQLite), intentamos parsear o lo usamos directo
                try:
                    fecha_str = datetime.strptime(str(fecha_val), "%Y-%m-%d").strftime("%d/%m")
                except:
                    fecha_str = str(fecha_val)
            trend_list.append({"fecha": fecha_str, "cantidad": r[1]})
        
        return {
            "total_cotizaciones": total_cots,
            "total_hoy": total_hoy,
            "monto_fonasa": int(monto_f),
            "monto_particular": int(monto_p),
            "top_examenes": top_list,
            "trend_data": trend_list
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al calcular estadísticas: {e}")

@app.get("/api/admin/history")
def get_history(db: Session = Depends(get_db), auth=Depends(check_admin_auth)):
    try:
        results = db.query(Cotizacion).order_by(desc(Cotizacion.fecha_cotizacion)).limit(100).all()
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener historial: {e}")

@app.put("/api/admin/aranceles/{codigo}")
def update_arancel(codigo: str, request: UpdatePriceRequest, db: Session = Depends(get_db), auth=Depends(check_admin_auth)):
    try:
        item = db.query(Arancel).filter(Arancel.codigo == codigo).first()
        if not item:
            raise HTTPException(status_code=404, detail="Examen no encontrado")
        
        item.valor_bono_fonasa = request.valor_bono_fonasa
        item.valor_copago = request.valor_copago
        item.valor_particular_general = request.valor_particular_general
        item.valor_particular_preferencial = request.valor_particular_preferencial
        
        db.commit()
        return {"success": True, "message": f"Precios de {codigo} actualizados"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar arancel: {e}")

from fastapi.responses import FileResponse
@app.get("/api/pdf/{filename}")
def get_pdf(filename: str):
    file_path = os.path.join(PDF_OUTPUT_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type='application/pdf', filename=filename)
    raise HTTPException(status_code=404, detail=f"Archivo PDF no encontrado en {file_path}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
