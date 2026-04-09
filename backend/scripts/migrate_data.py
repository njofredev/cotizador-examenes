import os
import pandas as pd
import json
import psycopg2
from psycopg2.extras import execute_values
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Reutilizar misma lógica de conexión
def conectar_db():
    try:
        host = os.environ.get("POSTGRES_HOST") or os.environ.get("STREAMLIT_POSTGRES_HOST", "localhost")
        return psycopg2.connect(
            host=host,
            database=os.environ.get("POSTGRES_DATABASE", "db_migracion") or os.environ.get("STREAMLIT_POSTGRES_DATABASE", "db_migracion"),
            user=os.environ.get("POSTGRES_USER", "postgres") or os.environ.get("STREAMLIT_POSTGRES_USER", "postgres"),
            password=os.environ.get("POSTGRES_PASSWORD") or os.environ.get("STREAMLIT_POSTGRES_PASSWORD", "postgres"),
            port=os.environ.get("POSTGRES_PORT", "5432") or os.environ.get("STREAMLIT_POSTGRES_PORT", "5432"),
            connect_timeout=5
        )
    except Exception as e:
        logger.error(f"Error de conexión: {e}")
        return None

def init_db():
    conn = conectar_db()
    if not conn:
        logger.error("No se pudo conectar a la base de datos.")
        return
    
    cur = conn.cursor()
    
    # Crear tablas
    # 1. aranceles
    cur.execute("""
        CREATE TABLE IF NOT EXISTS aranceles (
            codigo VARCHAR(255) PRIMARY KEY,
            nombre VARCHAR(255) NOT NULL,
            valor_bono_fonasa INTEGER DEFAULT 0,
            valor_copago INTEGER DEFAULT 0,
            valor_particular_general INTEGER DEFAULT 0,
            valor_particular_preferencial INTEGER DEFAULT 0,
            busqueda VARCHAR(500)
        )
    """)
    
    # 2. paquetes
    cur.execute("""
        CREATE TABLE IF NOT EXISTS paquetes (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(255) UNIQUE NOT NULL
        )
    """)

    # 3. paquete_examenes
    cur.execute("""
        CREATE TABLE IF NOT EXISTS paquete_examenes (
            id SERIAL PRIMARY KEY,
            paquete_id INTEGER REFERENCES paquetes(id) ON DELETE CASCADE,
            examen_codigo VARCHAR(255),
            examen_nombre VARCHAR(255) NOT NULL,
            cantidad INTEGER DEFAULT 1
        )
    """)

    conn.commit()
    return conn

def migrar_aranceles(conn):
    try:
        df = pd.read_excel("aranceles.xlsx")
        df.columns = ["Código", "Nombre", "Valor bono Fonasa", "Valor copago", "Valor particular General", "Valor particular preferencial"]
        df = df.fillna(0)
        df["Código"] = df["Código"].astype(str).str.replace(".0", "", regex=False)
        df["busqueda"] = df["Código"] + " - " + df["Nombre"]
        
        # Eliminar duplicados si hay por código
        df = df.drop_duplicates(subset=["Código"])
        
        datos = []
        def clean_val(val):
            if isinstance(val, str):
                val = val.replace(',', '').replace('.', '')
            try:
                return int(float(val))
            except:
                return 0

        for _, row in df.iterrows():
            datos.append((
                row["Código"],
                row["Nombre"],
                clean_val(row.get("Valor bono Fonasa", 0)),
                clean_val(row.get("Valor copago", 0)),
                clean_val(row.get("Valor particular General", 0)),
                clean_val(row.get("Valor particular preferencial", 0)),
                row["busqueda"]
            ))
            
        cur = conn.cursor()
        # Truncate o Insert (upsert)
        cur.execute("TRUNCATE TABLE aranceles CASCADE")
        insert_query = """
            INSERT INTO aranceles (codigo, nombre, valor_bono_fonasa, valor_copago, valor_particular_general, valor_particular_preferencial, busqueda)
            VALUES %s
        """
        execute_values(cur, insert_query, datos)
        conn.commit()
        logger.info(f"Se insertaron {len(datos)} aranceles exitosamente.")
    except Exception as e:
        logger.error(f"Error migrando aranceles: {e}")

def migrar_paquetes(conn):
    try:
        with open("pack.json", "r", encoding="utf-8") as f:
            data = json.load(f)["packs_examenes"]
            
        cur = conn.cursor()
        cur.execute("TRUNCATE TABLE paquetes CASCADE")
        
        for pack in data:
            nombre = pack["nombre"]
            cur.execute("INSERT INTO paquetes (nombre) VALUES (%s) RETURNING id", (nombre,))
            paquete_id = cur.fetchone()[0]
            
            examenes = pack.get("examenes", [])
            datos_examenes = []
            for ex in examenes:
                datos_examenes.append((
                    paquete_id,
                    str(ex.get("codigo")) if ex.get("codigo") else None,
                    ex["nombre"],
                    int(ex.get("cantidad", 1))
                ))
            
            insert_query = "INSERT INTO paquete_examenes (paquete_id, examen_codigo, examen_nombre, cantidad) VALUES %s"
            execute_values(cur, insert_query, datos_examenes)
        
        conn.commit()
        logger.info(f"Se insertaron {len(data)} paquetes exitosamente.")
    except Exception as e:
        logger.error(f"Error migrando paquetes: {e}")

if __name__ == "__main__":
    conn = init_db()
    if conn:
        migrar_aranceles(conn)
        migrar_paquetes(conn)
        conn.close()
