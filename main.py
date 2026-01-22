import streamlit as st
import pandas as pd
from fpdf import FPDF
import os
import secrets
import string
from datetime import date
import locale
import psycopg2

# 1. CONFIGURACIÓN DE PÁGINA E IDIOMA a
st.set_page_config(page_title="Cotizador de Exámenes", page_icon="🏥", layout="wide")

# Intentar forzar el locale a español para el manejo de datos interno
try:
    # Para Linux/Docker (Cloud)
    locale.setlocale(locale.LC_ALL, 'es_ES.utf8')
except:
    try:
        # Para Windows
        locale.setlocale(locale.LC_ALL, 'spanish')
    except:
        pass

# --- CONEXIÓN A BASE DE DATOS ---
def conectar_db():
    host = os.getenv("POSTGRES_HOST")
    if host:
        database = os.getenv("POSTGRES_DATABASE")
        user = os.getenv("POSTGRES_USER")
        password = os.getenv("POSTGRES_PASSWORD")
        port = os.getenv("POSTGRES_PORT")
    else:
        try:
            if "postgres" in st.secrets:
                db_conf = st.secrets["postgres"]
                host = db_conf["host"]
                database = db_conf["database"]
                user = db_conf["user"]
                password = db_conf["password"]
                port = db_conf["port"]
            else:
                return None
        except:
            return None

    try:
        conn = psycopg2.connect(
            host=host,
            database=database,
            user=user,
            password=password,
            port=port,
            sslmode="require"
        )
        return conn
    except Exception as e:
        st.error(f"Error crítico de conexión a DB: {e}")
        return None

def guardar_en_db(folio, nombre, t_doc, doc_id, f_nac, t_f, t_c, t_pg, t_pp, df_examenes):
    conn = conectar_db()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO cotizaciones (folio, nombre_paciente, tipo_documento, documento_id, fecha_nacimiento, total_fonasa, total_copago, total_particular_gral, total_particular_pref)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (folio, nombre, t_doc, doc_id, f_nac, int(t_f), int(t_c), int(t_pg), int(t_pp)))
            
            for _, row in df_examenes.iterrows():
                cur.execute("""
                    INSERT INTO detalle_cotizaciones (folio_cotizacion, codigo_examen, nombre_examen, valor_copago)
                    VALUES (%s, %s, %s, %s)
                """, (folio, str(row['Código']), str(row['Nombre']), int(row['Valor copago'])))
            
            conn.commit()
            cur.close()
            conn.close()
            return True
        except Exception as e:
            st.error(f"Error al guardar datos: {e}")
            return False
    return False

# --- ESTILO CSS ---
st.markdown("""
    <style>
    span[data-baseweb="tag"] { background-color: #0f8fee !important; }
    .stButton>button { 
        background-color: #0f8fee; color: white; border: none; 
        transition: all 0.3s ease; width: 100%;
    }
    .stButton>button:hover { background-color: #0d79ca !important; }
    div[data-testid="stTable"] { overflow-x: auto !important; display: block !important; }
    div[data-testid="stTable"] table { min-width: 600px !important; width: 100% !important; }
    div[data-testid="stRadio"] > div { flex-direction: row; gap: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES AUXILIARES ---
def generar_folio():
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for i in range(8))

def formatear_rut(rut_raw):
    if not rut_raw: return ""
    limpio = "".join(filter(str.isalnum, rut_raw)).upper()
    if len(limpio) < 2: return limpio
    cuerpo = limpio[:-1]; dv = limpio[-1]
    reverso = cuerpo[::-1]; con_puntos = ""
    for i in range(len(reverso)):
        if i > 0 and i % 3 == 0: con_puntos += "."
        con_puntos += reverso[i]
    return con_puntos[::-1] + "-" + dv

@st.cache_data
def cargar_datos():
    try:
        df = pd.read_excel("aranceles.xlsx")
        df.columns = ["Código", "Nombre", "Valor bono Fonasa", "Valor copago", "Valor particular General", "Valor particular preferencial"]
        df = df.fillna(0)
        df["Código"] = df["Código"].astype(str).str.replace(".0", "", regex=False)
        df["busqueda"] = df["Código"] + " - " + df["Nombre"]
        return df
    except Exception as e:
        st.error(f"Error al cargar aranceles.xlsx: {e}")
        return None

df = cargar_datos()

# --- INTERFAZ ---
if os.path.exists("logo.png"):
    st.image("logo.png")

st.title("Cotizador de Exámenes")

if df is not None:
    st.subheader("Datos del Paciente")
    
    col_tipo, col_num = st.columns([1, 2])
    with col_tipo:
        tipo_doc = st.radio("Tipo de Documento:", ["RUT Nacional", "Extranjero / Pasaporte"], horizontal=True)
    with col_num:
        if tipo_doc == "RUT Nacional":
            rut_input = st.text_input("Número de RUT:", placeholder="Ej: 12345678K")
            documento_final = formatear_rut(rut_input)
            if rut_input: st.caption(f"Formato: {documento_final}")
        else:
            documento_final = st.text_input("Número de Documento Extranjero:", placeholder="Pasaporte o ID")

    col_nom, col_fec = st.columns([2, 1])
    nombre_p = col_nom.text_input("Nombre Completo:", placeholder="Ej: Juan Pérez")
    
    # Selector de fecha con rango desde 1930
    fecha_nac = col_fec.date_input(
        "Fecha de Nacimiento:", 
        value=date(1990, 1, 1),
        min_value=date(1930, 1, 1),
        max_value=date.today(),
        format="DD/MM/YYYY" # Esto fuerza el formato visual día/mes/año
    )

    st.markdown("---")

    seleccionados = st.multiselect(
        "Agregue uno o más exámenes a cotizar", 
        options=df["busqueda"].unique().tolist(),
        placeholder="Escriba aquí el nombre o código..."
    )

    if seleccionados:
        df_sel = df[df["busqueda"].isin(seleccionados)].copy()
        st.write("### Detalle de Cotización")
        
        df_web = df_sel.drop(columns=["busqueda"]).rename(columns={
            "Valor bono Fonasa": "Bono Fonasa",
            "Valor copago": "Copago",
            "Valor particular General": "Part. Gral",
            "Valor particular preferencial": "Part. Pref"
        })
        st.table(df_web.style.format("${:,.0f}", subset=["Bono Fonasa", "Copago", "Part. Gral", "Part. Pref"]))
        
        tot_f = df_sel["Valor bono Fonasa"].sum()
        tot_c = df_sel["Valor copago"].sum()
        tot_pg = df_sel["Valor particular General"].sum()
        tot_pp = df_sel["Valor particular preferencial"].sum()

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Fonasa", f"${tot_f:,.0f}")
        m2.metric("Total Copago", f"${tot_c:,.0f}")
        m3.metric("Total Part. Gral", f"${tot_pg:,.0f}")
        m4.metric("Total Part. Pref", f"${tot_pp:,.0f}")

        if st.button("Generar Cotización y Guardar"):
            if not nombre_p or not documento_final:
                st.warning("⚠️ Complete los datos del paciente.")
            else:
                folio = generar_folio()
                
                if guardar_en_db(folio, nombre_p, tipo_doc, documento_final, fecha_nac, tot_f, tot_c, tot_pg, tot_pp, df_sel):
                    st.success(f"✅ Registrado exitosamente (Folio: {folio})")

                # --- PDF ---
                pdf = FPDF(orientation='P', unit='mm', format='A4')
                pdf.add_page()
                if os.path.exists("logo.png"): pdf.image("logo.png", 10, 8, h=12)
                
                pdf.set_font("Arial", 'B', 10); pdf.set_text_color(15, 143, 238)
                pdf.cell(0, 5, f"FOLIO: {folio}", ln=True, align='R')
                pdf.set_text_color(0, 0, 0); pdf.ln(10)
                
                pdf.set_font("Arial", 'B', 14)
                pdf.cell(0, 10, "Exámenes de Laboratorio", ln=True, align='C'); pdf.ln(3)

                pdf.set_font("Arial", '', 10)
                pdf.cell(0, 6, f"Paciente: {nombre_p}", ln=True)
                pdf.cell(0, 6, f"{tipo_doc}: {documento_final}", ln=True)
                pdf.cell(0, 6, f"F. Nacimiento: {fecha_nac.strftime('%d/%m/%Y')}", ln=True)
                pdf.cell(0, 6, f"Fecha Cotización: {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')}", ln=True); pdf.ln(6)

                # Cabecera tabla PDF
                pdf.set_fill_color(15, 143, 238); pdf.set_text_color(255, 255, 255)
                pdf.set_font("Arial", 'B', 9)
                pdf.cell(18, 10, "", 0, 0) 
                pdf.cell(52, 10, "", 0, 0)
                pdf.cell(60, 10, "Bono Fonasa", 1, 0, 'C', True)
                pdf.cell(60, 10, "Arancel particular", 1, 1, 'C', True)

                pdf.set_font("Arial", 'B', 7)
                pdf.cell(18, 10, "Código", 1, 0, 'C', True)
                pdf.cell(52, 10, " Nombre", 1, 0, 'L', True)
                pdf.cell(30, 10, "Valor Bono", 1, 0, 'C', True)
                pdf.cell(30, 10, "Valor a pagar(*)", 1, 0, 'C', True) 
                pdf.cell(30, 10, "Valor general", 1, 0, 'C', True) 
                pdf.cell(30, 10, "Valor preferencial", 1, 1, 'C', True)

                pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", '', 7)
                for _, row in df_sel.iterrows():
                    n_raw = str(row['Nombre'])
                    n_mostrar = (n_raw[:35] + "..") if len(n_raw) > 37 else n_raw
                    pdf.cell(18, 8, str(row['Código']), 1, 0, 'C')
                    pdf.cell(52, 8, f" {n_mostrar}", 1, 0, 'L')
                    pdf.cell(30, 8, f"${row['Valor bono Fonasa']:,.0f}", 1, 0, 'R')
                    pdf.cell(30, 8, f"${row['Valor copago']:,.0f}", 1, 0, 'R')
                    pdf.cell(30, 8, f"${row['Valor particular General']:,.0f}", 1, 0, 'R')
                    pdf.cell(30, 8, f"${row['Valor particular preferencial']:,.0f}", 1, 1, 'R')

                pdf.set_font("Arial", 'B', 7); pdf.set_fill_color(240, 240, 240)
                pdf.cell(70, 10, " TOTALES ACUMULADOS", 1, 0, 'L', True)
                pdf.cell(30, 10, f"${tot_f:,.0f}", 1, 0, 'R', True)
                pdf.cell(30, 10, f"${tot_c:,.0f}", 1, 0, 'R', True)
                pdf.cell(30, 10, f"${tot_pg:,.0f}", 1, 0, 'R', True)
                pdf.cell(30, 10, f"${tot_pp:,.0f}", 1, 1, 'R', True)

                pdf.ln(10); pdf.set_font("Arial", 'B', 8); pdf.cell(0, 5, "INFORMACIÓN IMPORTANTE:", ln=True)
                pdf.set_font("Arial", '', 7)
                notas = (
                    f"- Folio único de atención: {folio}\n"
                    "(*) Este valor no considera seguros complementarios.\n"
                    "- Horario de atención de la toma de muestras: Lun- Vier desde las 08:30am a las 11:00am.\n"
                    "- Ayuno no puede superar las 12hrs.\n"
                    "- Para pruebas PTGO, SÓLO se puede tomar agendando a las 08:30am.\n"
                    "- Si es diabético, debe notificar en recepción.\n"
                    "- Las horas de ayuno dependen del examen.\n"
                    "- Existen exámenes sin necesidad de ayuno.\n"
                    "- Consultar por los plazos de entregas individuales de cada examen.\n"
                    "- Esta cotización tiene una validez de 30 días. Valores sujetos a confirmación en sucursal."
                )
                pdf.multi_cell(0, 4, notas)

                pdf_name = f"Cotizacion_{folio}.pdf"
                pdf.output(pdf_name)
                with open(pdf_name, "rb") as f:
                    st.download_button("🔵 Descargar PDF Cotización", data=f, file_name=f"Cotizacion_{nombre_p}.pdf", mime="application/pdf")
    else:
        st.info("Agregue uno o más exámenes a cotizar")
else:
    st.error("Archivo 'aranceles.xlsx' no encontrado.")
