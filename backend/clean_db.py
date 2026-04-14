import os
from sqlalchemy.orm import sessionmaker
from database import engine, Cotizacion, DetalleCotizacion

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    print("Iniciando proceso de limpieza...")
    
    # Nombres a buscar (insensible a mayúsculas y acentos es mejor, o usando like)
    nombres_a_eliminar = ['NICOLÁS JOFRÉ ANDRADE', 'LUCOSO PENETROSO', 'LUCAS PENETROSO']
    
    cotizaciones = db.query(Cotizacion).filter(Cotizacion.nombre_paciente.in_(nombres_a_eliminar)).all()
    
    if not cotizaciones:
        print("No se encontraron cotizaciones para eliminar.")
    else:
        for cot in cotizaciones:
            print(f"Eliminando cotización: {cot.folio} - {cot.nombre_paciente}")
            # Eliminar detalles primero
            db.query(DetalleCotizacion).filter(DetalleCotizacion.folio_cotizacion == cot.folio).delete()
            # Eliminar cotización
            db.delete(cot)
        
        db.commit()
        print(f"Se eliminaron {len(cotizaciones)} cotizaciones con sus respectivos detalles.")

except Exception as e:
    print(f"Error: {e}")
    db.rollback()
finally:
    db.close()
