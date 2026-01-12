import streamlit as st
import pandas as pd
from fpdf import FPDF
import os
import psycopg2
from datetime import datetime

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Cotizador Policlínico Tabancura", page_icon="🏥", layout="wide")

def conectar_db():
    host = os.getenv("POSTGRES_HOST")
    if not host:
        try:
            db_conf = st.secrets["postgres"]
            host = db_conf["host"]
            database = db_conf["database"]
            user = db_conf["user"]
            password = db_conf["password"]
            port = db_conf["port"]
        except:
            st.error("❌ No hay variables de entorno configuradas.")
            return None
    else:
        database = os.getenv("POSTGRES_DATABASE")
        user = os.getenv("POSTGRES_USER")
        password = os.getenv("POSTGRES_PASSWORD")
        port = os.getenv("POSTGRES_PORT")

    try:
        return psycopg2.connect(
            host=host, database=database, user=user, 
            password=password, port=port, sslmode="require"
        )
    except Exception as e:
        st.error(f"❌ Error de conexión: {e}")
        return None

@st.cache_data
def cargar_aranceles():
    if not os.path.exists("aranceles.xlsx"):
        st.error("❌ Archivo 'aranceles.xlsx' no encontrado.")
        return None
    df = pd.read_excel("aranceles.xlsx")
    # Ajuste de nombres de columnas según tu Excel
    df.columns = ["Código", "Nombre", "Fonasa", "Copago", "Particular_Gral", "Particular_Pref"]
    df["Código"] = df["Código"].astype(str).str.replace(".0", "", regex=False)
    return df

# --- 2. INTERFAZ ---
st.title("Cotizador de Exámenes")
st.subheader("Policlínico Tabancura")

# Formulario de paciente
with st.expander("Datos del Paciente", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("Nombre Completo")
        rut = st.text_input("RUT")
    with col2:
        fecha_nac = st.date_input("Fecha de Nacimiento", min_value=datetime(1920, 1, 1))

# Selección de exámenes
aranceles = cargar_aranceles()

if aranceles is not None:
    examenes_nombres = aranceles["Nombre"].tolist()
    seleccionados = st.multiselect("Seleccione los exámenes a cotizar:", examenes_nombres)
    
    df_seleccionados = aranceles[aranceles["Nombre"].isin(seleccionados)]
    
    if not df_seleccionados.empty:
        st.write("### Resumen de Cotización")
        st.table(df_seleccionados[["Código", "Nombre", "Particular_Gral"]])
        
        total = df_seleccionados["Particular_Gral"].sum()
        st.metric("Total a Pagar (Particular)", f"${total:,.0f}")

        if st.button("Guardar y Generar PDF"):
            conn = conectar_db()
            if conn:
                try:
                    cur = conn.cursor()
                    # Generar un Folio Simple
                    folio_gen = f"COT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    
                    # 1. Guardar en la tabla cotizaciones
                    cur.execute("""
                        INSERT INTO cotizaciones (folio, rut, nombre, fecha_nacimiento, fecha_creacion)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (folio_gen, rut, nombre, fecha_nac, datetime.now()))
                    
                    # 2. Guardar el detalle
                    for cod in df_seleccionados["Código"]:
                        cur.execute("""
                            INSERT INTO detalle_cotizaciones (folio_cotizacion, codigo_examen)
                            VALUES (%s, %s)
                        """, (folio_gen, cod))
                    
                    conn.commit()
                    
                    # 3. Generar PDF con FPDF
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", 'B', 16)
                    pdf.cell(200, 10, "COTIZACIÓN MÉDICA", ln=True, align='C')
                    pdf.set_font("Arial", '', 12)
                    pdf.ln(10)
                    pdf.cell(200, 10, f"Folio: {folio_gen}", ln=True)
                    pdf.cell(200, 10, f"Paciente: {nombre}", ln=True)
                    pdf.cell(200, 10, f"RUT: {rut}", ln=True)
                    pdf.ln(10)
                    
                    for _, row in df_seleccionados.iterrows():
                        pdf.cell(150, 10, f"{row['Nombre']}", 0)
                        pdf.cell(40, 10, f"${row['Particular_Gral']:,.0f}", 0, ln=True, align='R')
                    
                    pdf.ln(10)
                    pdf.set_font("Arial", 'B', 12)
                    pdf.cell(190, 10, f"TOTAL: ${total:,.0f}", ln=True, align='R')
                    
                    nombre_archivo = f"cotizacion_{folio_gen}.pdf"
                    pdf.output(nombre_archivo)
                    
                    st.success(f"✅ Cotización guardada con Folio: {folio_gen}")
                    
                    with open(nombre_archivo, "rb") as f:
                        st.download_button("Descargar PDF", f, file_name=nombre_archivo)
                    
                    cur.close()
                    conn.close()
                except Exception as e:
                    st.error(f"Error al guardar: {e}")
