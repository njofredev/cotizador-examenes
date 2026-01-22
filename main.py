import streamlit as st
import pandas as pd
from fpdf import FPDF
import os
import psycopg2
from datetime import datetime

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Revisión de Cotizaciones", page_icon="🔍", layout="wide")

def conectar_db():
    # DIAGNÓSTICO: Verificamos si Coolify está entregando las variables
    host = os.getenv("POSTGRES_HOST")
    if not host:
        st.warning("⚠️ El sistema no detecta variables de entorno de Coolify. Buscando st.secrets...")
        try:
            db_conf = st.secrets["postgres"]
            host = db_conf["host"]
            database = db_conf["database"]
            user = db_conf["user"]
            password = db_conf["password"]
            port = db_conf["port"]
            sslmode="disable"
        except:
            st.error("❌ No hay variables de entorno ni st.secrets configurados.")
            return None
    else:
        database = os.getenv("POSTGRES_DATABASE")
        user = os.getenv("POSTGRES_USER")
        password = os.getenv("POSTGRES_PASSWORD")
        port = os.getenv("POSTGRES_PORT")
        sslmode="disable"

    try:
        return psycopg2.connect(
            host=host, database=database, user=user, 
            password=password, port=port, sslmode="require",
            connect_timeout=10 # Evita que se quede pegado si no conecta
        )
    except Exception as e:
        st.error(f"❌ Error de conexión física: {e}")
        return None

@st.cache_data
def cargar_aranceles():
    if not os.path.exists("aranceles.xlsx"):
        st.error("❌ Archivo 'aranceles.xlsx' no encontrado en el repositorio.")
        return None
    return pd.read_excel("aranceles.xlsx")

# --- INTERFAZ ---
st.title("Revisión de Cotizaciones")

folio_input = st.text_input("Ingrese Folio:").upper().strip()

if st.button("Buscar Cotización"):
    st.info(f"🔎 Iniciando búsqueda para el folio: {folio_input}...")
    
    conn = conectar_db()
    if conn:
        st.success("📡 Conexión a la base de datos establecida.")
        try:
            cur = conn.cursor()
            
            # Buscamos en la tabla maestra
            st.write("🛰️ Consultando tabla 'cotizaciones'...")
            cur.execute("SELECT * FROM cotizaciones WHERE folio = %s", (folio_input,))
            maestro = cur.fetchone()
            
            if maestro:
                st.success(f"✅ Paciente encontrado: {maestro[2]}")
                
                # Buscamos los exámenes vinculados
                st.write("🛰️ Consultando tabla 'detalle_cotizaciones'...")
                cur.execute("SELECT codigo_examen FROM detalle_cotizaciones WHERE folio_cotizacion = %s", (folio_input,))
                filas_detalle = cur.fetchall()
                codigos = [r[0] for r in filas_detalle]
                
                if codigos:
                    st.write(f"📋 Se encontraron {len(codigos)} exámenes.")
                    
                    # Cargar Excel y filtrar
                    df_excel = cargar_aranceles()
                    if df_excel is not None:
                        df_excel.columns = ["Código", "Nombre", "Valor bono Fonasa", "Valor copago", "Valor particular General", "Valor particular preferencial"]
                        df_excel["Código"] = df_excel["Código"].astype(str).str.replace(".0", "", regex=False)
                        
                        df_resultado = df_excel[df_excel["Código"].isin(codigos)]
                        st.table(df_resultado)
                        
                        # Botón para descargar (Generación simplificada para probar)
                        st.write("📄 Generando vista previa del documento...")
                        # ... (Aquí iría tu lógica de FPDF que ya tenemos)
                        st.success("Proceso completado.")
                else:
                    st.warning("⚠️ El folio existe, pero no tiene exámenes registrados en el detalle.")
            else:
                st.error(f"❌ El folio '{folio_input}' no existe en la base de datos.")
            
            cur.close()
            conn.close()
        except Exception as e:
            st.error(f"💥 Error durante la ejecución del SQL: {e}")