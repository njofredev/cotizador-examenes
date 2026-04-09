import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        database=os.getenv("POSTGRES_DATABASE"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        port=os.getenv("POSTGRES_PORT")
    )

def cleanup():
    conn = get_connection()
    cur = conn.cursor()
    
    names = ["NICOLÁS JOFRÉ ANDRADE", "FELIPE IGNACIO JOFRE ANDRADE", "JOHN DOE"]
    
    # 1. Get folios
    cur.execute("SELECT folio FROM cotizaciones WHERE nombre_paciente IN %s", (tuple(names),))
    folios = [row[0] for row in cur.fetchall()]
    
    if not folios:
        print("No records found for specified names.")
        conn.close()
        return

    print(f"Folios to delete: {folios}")
    
    # 2. Check related tables and delete
    # detalle_cotizaciones has folio_cotizacion
    # ordenes_clinicas might have folio_cotizacion or nombre_paciente
    # ordenes_detalles might have folio_cotizacion
    
    tables_to_clean = []
    
    # Check what tables actually exist and have the columns
    all_tables = ['detalle_cotizaciones', 'ordenes_clinicas', 'ordenes_detalles']
    for table in all_tables:
        cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name='{table}'")
        cols = [c[0] for c in cur.fetchall()]
        if not cols:
            continue
            
        if 'folio_cotizacion' in cols:
            cur.execute(f"DELETE FROM {table} WHERE folio_cotizacion IN %s", (tuple(folios),))
            print(f"Deleted from {table} by folio_cotizacion.")
        
        if 'nombre_paciente' in cols:
            cur.execute(f"DELETE FROM {table} WHERE nombre_paciente IN %s", (tuple(names),))
            print(f"Deleted from {table} by nombre_paciente.")

    # 3. Finally delete from cotizaciones
    cur.execute("DELETE FROM cotizaciones WHERE nombre_paciente IN %s", (tuple(names),))
    print("Deleted from cotizaciones.")
    
    conn.commit()
    conn.close()
    print("Cleanup completed successfully.")

if __name__ == "__main__":
    cleanup()
