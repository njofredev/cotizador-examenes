import streamlit as st
import pandas as pd
from fpdf import FPDF
import os
import psycopg2
from datetime import datetime

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Revisión de Exámenes", page_icon="🔍", layout="wide")

def conectar_db():
    import os
    # Intentamos obtener variables de entorno de Coolify (Production)
    host = os.environ.get("POSTGRES_HOST")
    database = os.environ.get("POSTGRES_DATABASE")
    user = os.environ.get("POSTGRES_USER")
    password = os.environ.get("POSTGRES_PASSWORD")
    port = os.environ.get("POSTGRES_PORT")

    # Si no existen en el entorno, intentamos st.secrets (Local/Streamlit Cloud)
    if not host:
        try:
            db_conf = st.secrets["postgres"]
            host, database, user, password, port = db_conf["host"], db_conf["database"], db_conf["user"], db_conf["password"], db_conf["port"]
        except:
            pass

    if not host:
        st.error("❌ Error: No se encontraron credenciales de base de datos en el servidor.")
        return None

    try:
        return psycopg2.connect(host=host, database=database, user=user, password=password, port=port, sslmode="require")
    except Exception as e:
        st.error(f"❌ Error de conexión física: {e}")
        return None

@st.cache_data
def cargar_aranceles():
    if not os.path.exists("aranceles.xlsx"):
        st.error("❌ Archivo 'aranceles.xlsx' no encontrado.")
        return None
    df = pd.read_excel("aranceles.xlsx")
    df.columns = ["Código", "Nombre", "Valor bono Fonasa", "Valor copago", "Valor particular General", "Valor particular preferencial"]
    df["Código"] = df["Código"].astype(str).str.replace(".0", "", regex=False)
    return df

# --- INTERFAZ ---
if os.path.exists("logo.png"): st.image("logo.png")
st.title("Revisión de Cotizaciones Realizadas")

folio_busqueda = st.text_input("Ingrese el Folio (8 caracteres):").upper().strip()

if st.button("Buscar Cotización"):
    if not folio_busqueda:
        st.warning("⚠️ Ingrese un folio.")
    else:
        conn = conectar_db()
        if conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM cotizaciones WHERE folio = %s", (folio_busqueda,))
            maestro = cur.fetchone()
            
            if maestro:
                cur.execute("SELECT codigo_examen FROM detalle_cotizaciones WHERE folio_cotizacion = %s", (folio_busqueda,))
                codigos_db = [row[0] for row in cur.fetchall()]
                df_precios = cargar_aranceles()
                
                if df_precios is not None:
                    df_final = df_precios[df_precios["Código"].isin(codigos_db)].copy()
                    st.success(f"✅ Cotización encontrada para: {maestro[2]}")
                    
                    # TABLA WEB
                    st.table(df_final.style.format("${:,.0f}", subset=["Valor bono Fonasa", "Valor copago", "Valor particular General", "Valor particular preferencial"]))
                    
                    # --- PDF CON CABEZALES AGRUPADOS ---
                    pdf = FPDF(); pdf.add_page()
                    if os.path.exists("logo.png"): pdf.image("logo.png", 10, 8, h=12)
                    pdf.set_font("Arial", 'B', 10); pdf.set_text_color(15, 143, 238); pdf.cell(0, 5, f"FOLIO: {maestro[1]}", ln=True, align='R')
                    pdf.set_text_color(0, 0, 0); pdf.ln(10); pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, "Exámenes de Laboratorio", ln=True, align='C'); pdf.ln(3)

                    pdf.set_font("Arial", 'B', 9); pdf.set_fill_color(15, 143, 238); pdf.set_text_color(255, 255, 255)
                    pdf.cell(18, 10, "", 0, 0); pdf.cell(52, 10, "", 0, 0); pdf.cell(60, 10, "Bono Fonasa", 1, 0, 'C', True); pdf.cell(60, 10, "Arancel particular", 1, 1, 'C', True)
                    
                    pdf.set_font("Arial", 'B', 7); pdf.cell(18, 10, "Código", 1, 0, 'C', True); pdf.cell(52, 10, " Nombre", 1, 0, 'L', True); pdf.cell(30, 10, "Valor Bono", 1, 0, 'C', True); pdf.cell(30, 10, "Valor a pagar(*)", 1, 0, 'C', True); pdf.cell(30, 10, "Valor general", 1, 0, 'C', True); pdf.cell(30, 10, "Valor preferencial", 1, 1, 'C', True)

                    pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", '', 7)
                    for _, row in df_final.iterrows():
                        n_mostrar = (str(row['Nombre'])[:35] + "..") if len(str(row['Nombre'])) > 37 else str(row['Nombre'])
                        pdf.cell(18, 8, str(row['Código']), 1, 0, 'C'); pdf.cell(52, 8, f" {n_mostrar}", 1, 0, 'L'); pdf.cell(30, 8, f"${row['Valor bono Fonasa']:,.0f}", 1, 0, 'R'); pdf.cell(30, 8, f"${row['Valor copago']:,.0f}", 1, 0, 'R'); pdf.cell(30, 8, f"${row['Valor particular General']:,.0f}", 1, 0, 'R'); pdf.cell(30, 8, f"${row['Valor particular preferencial']:,.0f}", 1, 1, 'R')

                    pdf.set_font("Arial", 'B', 7); pdf.set_fill_color(240, 240, 240); pdf.cell(70, 10, " TOTALES REIMPRESOS", 1, 0, 'L', True); pdf.cell(30, 10, f"${maestro[7]:,.0f}", 1, 0, 'R', True); pdf.cell(30, 10, f"${maestro[8]:,.0f}", 1, 0, 'R', True); pdf.cell(30, 10, f"${maestro[9]:,.0f}", 1, 0, 'R', True); pdf.cell(30, 10, f"${maestro[10]:,.0f}", 1, 1, 'R', True)

                    pdf_name = f"Reimpresion_{maestro[1]}.pdf"
                    pdf.output(pdf_name)
                    with open(pdf_name, "rb") as f:
                        st.download_button("🔵 Descargar PDF Reimpreso", data=f, file_name=pdf_name, mime="application/pdf")
            else:
                st.error("❌ Folio no encontrado.")
            cur.close(); conn.close()
