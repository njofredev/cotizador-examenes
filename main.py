import streamlit as st
import pandas as pd
from fpdf import FPDF
import os
import secrets
import string
from datetime import date
import locale

# 1. CONFIGURACIÓN DE PÁGINA E IDIOMA
st.set_page_config(page_title="Cotiza tu examen", page_icon="🏥", layout="wide")

# Configuración de idioma para que el calendario aparezca en español
try:
    locale.setlocale(locale.LC_ALL, 'es_CL.UTF-8') 
except:
    try:
        locale.setlocale(locale.LC_ALL, 'spanish')
    except:
        pass

# --- ESTILO CSS PARA BOTONES Y HOVER ---
st.markdown(f"""
    <style>
    span[data-baseweb="tag"] {{
        background-color: #0f8fee !important;
    }}
    .stButton>button {{
        background-color: #0f8fee;
        color: white;
        border: none;
        transition: all 0.3s ease;
    }}
    .stButton>button:hover {{
        background-color: #0d79ca !important;
        color: white !important;
        border: none !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# Función para generar el Folio Único
def generar_folio():
    caracteres = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(caracteres) for i in range(8))

# 2. CARGA DE DATOS
@st.cache_data
def cargar_datos():
    try:
        df = pd.read_excel("aranceles.xlsx")
        df.columns = [
            "Código", "Nombre", "Valor bono Fonasa", 
            "Valor copago", "Valor particular General", "Valor particular preferencial"
        ]
        df = df.fillna(0)
        df["Código"] = df["Código"].astype(str).str.replace(".0", "", regex=False)
        df["busqueda"] = df["Código"] + " - " + df["Nombre"]
        return df
    except Exception as e:
        st.error(f"Error al cargar 'aranceles.xlsx': {e}")
        return None

df = cargar_datos()

# 3. INTERFAZ DE USUARIO
if os.path.exists("logo.png"):
    st.image("logo.png")

st.title("Cotizador de Exámenes")

# Botón Limpiar Formulario (Lógica corregida para evitar el error de rerun)
col_title, col_clear = st.columns([0.85, 0.15])
with col_clear:
    if st.button("🗑️ Limpiar Formulario"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()

if df is not None:
    st.subheader("Datos del Paciente")
    col_p1, col_p2, col_p3 = st.columns(3)
    
    # Asignamos llaves (keys) para que puedan ser reseteadas por el botón de limpieza
    nombre_p = col_p1.text_input("Nombre Completo:", placeholder="Ej: Juan Pérez", key="nombre_key")
    rut_p = col_p2.text_input("RUT:", placeholder="12.345.678-9", key="rut_key")
    fecha_nac = col_p3.date_input("Fecha de Nacimiento:", value=date(1990, 1, 1), format="DD/MM/YYYY", key="fecha_key")

    # Buscador de exámenes
    seleccionados = st.multiselect(
        "Busque y seleccione los exámenes:",
        options=df["busqueda"].unique().tolist(),
        placeholder="Escriba aquí el nombre o código...",
        key="examenes_key"
    )

    if seleccionados:
        df_sel = df[df["busqueda"].isin(seleccionados)].copy()
        
        st.write("### Detalle de Cotización")
        
        # Mostramos la tabla simple sin super-cabezales en la web
        df_web = df_sel.drop(columns=["busqueda"])
        st.table(df_web.style.format({
            "Valor bono Fonasa": "${:,.0f}",
            "Valor copago": "${:,.0f}",
            "Valor particular General": "${:,.0f}",
            "Valor particular preferencial": "${:,.0f}"
        }))
        
        # Cálculo de totales
        tot_f = df_sel["Valor bono Fonasa"].sum()
        tot_c = df_sel["Valor copago"].sum()
        tot_pg = df_sel["Valor particular General"].sum()
        tot_pp = df_sel["Valor particular preferencial"].sum()

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Fonasa", f"${tot_f:,.0f}")
        m2.metric("Total Copago", f"${tot_c:,.0f}")
        m3.metric("Total Part. Gral", f"${tot_pg:,.0f}")
        m4.metric("Total Part. Pref", f"${tot_pp:,.0f}")

        # 4. GENERACIÓN DE PDF
        if st.button("Generar Cotización en PDF"):
            codigo_folio = generar_folio()
            pdf = FPDF(orientation='P', unit='mm', format='A4')
            pdf.add_page()
            
            if os.path.exists("logo.png"):
                pdf.image("logo.png", 10, 8, h=12)
            
            pdf.set_font("Arial", 'B', 10)
            pdf.set_text_color(15, 143, 238)
            pdf.cell(0, 5, f"FOLIO: {codigo_folio}", ln=True, align='R')
            pdf.set_text_color(0, 0, 0)

            pdf.ln(10)
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 10, "Exámenes de Laboratorio", ln=True, align='C')
            pdf.ln(3)

            pdf.set_font("Arial", '', 10)
            pdf.cell(0, 6, f"Paciente: {nombre_p}", ln=True)
            pdf.cell(0, 6, f"RUT: {rut_p}", ln=True)
            pdf.cell(0, 6, f"Fecha de Nacimiento: {fecha_nac.strftime('%d/%m/%Y')}", ln=True)
            pdf.cell(0, 6, f"Fecha Cotización: {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')}", ln=True)
            pdf.ln(6)

            # --- CABECERA PDF CON SUPER-CABEZALES ---
            pdf.set_fill_color(15, 143, 238)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Arial", 'B', 9)
            
            pdf.cell(18, 10, "", 0, 0) 
            pdf.cell(52, 10, "", 0, 0)
            pdf.cell(60, 10, "Bono Fonasa", 1, 0, 'C', True)
            pdf.cell(60, 10, "Arancel particular", 1, 1, 'C', True)

            # Fila de columnas secundaria
            pdf.set_font("Arial", 'B', 7)
            pdf.cell(18, 10, "Código", 1, 0, 'C', True)
            pdf.cell(52, 10, " Nombre", 1, 0, 'L', True)
            pdf.cell(30, 10, "Valor Bono", 1, 0, 'C', True)
            pdf.cell(30, 10, "Valor a pagar(*)", 1, 0, 'C', True) 
            pdf.cell(30, 10, "Valor general", 1, 0, 'C', True) 
            pdf.cell(30, 10, "Valor preferencial", 1, 1, 'C', True)

            # Filas de datos
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Arial", '', 7)
            for _, row in df_sel.iterrows():
                n_raw = str(row['Nombre'])
                n_mostrar = (n_raw[:35] + "..") if len(n_raw) > 37 else n_raw
                pdf.cell(18, 8, str(row['Código']), 1, 0, 'C')
                pdf.cell(52, 8, f" {n_mostrar}", 1, 0, 'L')
                pdf.cell(30, 8, f"${row['Valor bono Fonasa']:,.0f}", 1, 0, 'R')
                pdf.cell(30, 8, f"${row['Valor copago']:,.0f}", 1, 0, 'R')
                pdf.cell(30, 8, f"${row['Valor particular General']:,.0f}", 1, 0, 'R')
                pdf.cell(30, 8, f"${row['Valor particular preferencial']:,.0f}", 1, 1, 'R')

            # Fila de Totales
            pdf.set_font("Arial", 'B', 7)
            pdf.set_fill_color(240, 240, 240)
            pdf.cell(70, 10, " TOTALES ACUMULADOS", 1, 0, 'L', True)
            pdf.cell(30, 10, f"${tot_f:,.0f}", 1, 0, 'R', True)
            pdf.cell(30, 10, f"${tot_c:,.0f}", 1, 0, 'R', True)
            pdf.cell(30, 10, f"${tot_pg:,.0f}", 1, 0, 'R', True)
            pdf.cell(30, 10, f"${tot_pp:,.0f}", 1, 1, 'R', True)

            # --- PIE DE PÁGINA ---
            pdf.ln(10)
            pdf.set_font("Arial", 'B', 8)
            pdf.cell(0, 5, "INFORMACIÓN IMPORTANTE:", ln=True)
            pdf.set_font("Arial", '', 7)
            notas_texto = (
                f"- Folio único de atención: {codigo_folio}\n"
                "(*) Este valor no considera seguros complementarios.\n"
                "- Horario de atención de la toma de muestras: Lun- Vier desde las 08:30am a las 11:00am.\n"
                "- Ayuno no puede superar las 12hrs.\n"
                "- Para pruebas PTGO, SÓLO se puede tomar agendando a las 08:30am.\n"
                "- Si es diabético, debe notificar.\n"
                "- Las horas de ayuno dependen del examen.\n"
                "- Existen exámenes sin necesidad de ayuno.\n"
                "- Consultar por los plazos de entregas individuales de cada examen.\n"
                "- Esta cotización tiene una validez de 30 días. Valores sujetos a confirmación en sucursal."
            )
            pdf.multi_cell(0, 4, notas_texto)

            # Descarga del archivo
            nombre_pdf = f"Cotizacion_{codigo_folio}.pdf"