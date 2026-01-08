import streamlit as st
import pandas as pd
from fpdf import FPDF
import os
import secrets
import string
from datetime import date

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Cotiza tu examen", page_icon="🏥", layout="wide")

# --- ESTILO CSS PARA EL COLOR AZUL #0f8fee ---
st.markdown(f"""
    <style>
    span[data-baseweb="tag"] {{
        background-color: #0f8fee !important;
    }}
    span[data-baseweb="tag"] span, span[data-baseweb="tag"] svg {{
        color: white !important;
        fill: white !important;
    }}
    .stButton>button {{
        background-color: #0f8fee;
        color: white;
    }}
    </style>
    """, unsafe_allow_html=True)

# FUNCIÓN PARA GENERAR FOLIO ÚNICO (8 caracteres alfanuméricos)
def generar_folio():
    caracteres = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(caracteres) for i in range(8))

# 2. CARGA DE DATOS DESDE EXCEL
@st.cache_data
def cargar_datos():
    try:
        df = pd.read_excel("aranceles.xlsx")
        # Aseguramos nombres de columnas estándar para la lógica
        df.columns = [
            "Código", "Nombre", "Valor bono Fonasa", 
            "Valor copago", "Valor particular General", "Valor particular preferencial"
        ]
        df = df.fillna(0)
        df["Código"] = df["Código"].astype(str).str.replace(".0", "", regex=False)
        # Columna para el buscador
        df["busqueda"] = df["Código"] + " - " + df["Nombre"]
        return df
    except Exception as e:
        st.error(f"Error al cargar 'aranceles.xlsx': {e}")
        return None

df = cargar_datos()

# 3. INTERFAZ DE USUARIO
if os.path.exists("logo.png"):
    st.image("logo.png", width=200)

st.title("Cotizador de Exámenes")

if df is not None:
    # --- FORMULARIO DE PACIENTE ---
    st.subheader("Datos del Paciente")
    col_p1, col_p2, col_p3 = st.columns(3)
    nombre_p = col_p1.text_input("Nombre Completo:", placeholder="Ej: Juan Pérez")
    rut_p = col_p2.text_input("RUT:", placeholder="12.345.678-9")
    fecha_nac = col_p3.date_input(
        "Fecha de Nacimiento:", 
        value=date(1990, 1, 1),
        format="DD/MM/YYYY"
    )

    # Buscador Multiselect
    seleccionados = st.multiselect(
        "Busque y seleccione los exámenes:",
        options=df["busqueda"].unique().tolist(),
        placeholder="Escriba aquí el nombre o código del examen..."
    )

    if seleccionados:
        # Filtrar datos
        df_sel = df[df["busqueda"].isin(seleccionados)].copy()
        
        st.write("### Detalle de Cotización")
        
        # --- TABLA WEB CON CABECERAS AGRUPADAS ---
        df_display = df_sel.drop(columns=["busqueda"])
        columnas_multi = pd.MultiIndex.from_tuples([
            ("", "Código"),
            ("", "Nombre"),
            ("Bono Fonasa", "Valor bono Fonasa"),
            ("Bono Fonasa", "Valor copago"),
            ("Particular", "Valor particular General"),
            ("Particular", "Valor particular preferencial")
        ])
        df_display.columns = columnas_multi
        
        # Mostramos tabla formateada con $ y puntos
        st.table(df_display.style.format(subset=df_display.columns[2:], formatter="${:,.0f}"))
        
        # Totales para métricas
        tot_f = df_sel["Valor bono Fonasa"].sum()
        tot_c = df_sel["Valor copago"].sum()
        tot_pg = df_sel["Valor particular General"].sum()
        tot_pp = df_sel["Valor particular preferencial"].sum()

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Fonasa", f"${tot_f:,.0f}")
        m2.metric("Total Copago", f"${tot_c:,.0f}")
        m3.metric("Total Part. Gral", f"${tot_pg:,.0f}")
        m4.metric("Total Part. Pref", f"${tot_pp:,.0f}")

        # 4. GENERACIÓN DE PDF VERTICAL
        if st.button("Generar Cotización en PDF"):
            codigo_folio = generar_folio()
            
            # 'P' = Portrait (Vertical)
            pdf = FPDF(orientation='P', unit='mm', format='A4')
            pdf.add_page()
            
            # Logo y Folio
            if os.path.exists("logo.png"):
                pdf.image("logo.png", 10, 8, h=12)
            
            pdf.set_font("Arial", 'B', 10)
            pdf.set_text_color(15, 143, 238) # Azul
            pdf.cell(0, 5, f"FOLIO: {codigo_folio}", ln=True, align='R')
            pdf.set_text_color(0, 0, 0) # Volver a negro

            pdf.ln(10)
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 10, "COTIZACIÓN DE EXÁMENES", ln=True, align='C')
            pdf.ln(3)

            # Datos Paciente (Formato Chileno)
            pdf.set_font("Arial", '', 10)
            pdf.cell(0, 6, f"Paciente: {nombre_p if nombre_p else '____________________'}", ln=True)
            pdf.cell(0, 6, f"RUT: {rut_p if rut_p else '____________________'}", ln=True)
            pdf.cell(0, 6, f"Fecha de Nacimiento: {fecha_nac.strftime('%d/%m/%Y')}", ln=True)
            pdf.cell(0, 6, f"Fecha Cotización: {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')}", ln=True)
            pdf.ln(6)

            # --- CABECERA AGRUPADA PDF ---
            pdf.set_fill_color(15, 143, 238)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Arial", 'B', 9)
            
            # Fila 1: Super-cabeceras
            pdf.cell(18, 10, "", 0, 0) 
            pdf.cell(52, 10, "", 0, 0)
            pdf.cell(60, 10, "Bono Fonasa", 1, 0, 'C', True)
            pdf.cell(60, 10, "Particular", 1, 1, 'C', True)

            # Fila 2: Sub-cabeceras
            pdf.set_font("Arial", 'B', 7)
            pdf.cell(18, 10, "Código", 1, 0, 'C', True)
            pdf.cell(52, 10, " Nombre", 1, 0, 'L', True)
            pdf.cell(30, 10, "Valor Bono", 1, 0, 'C', True)
            pdf.cell(30, 10, "Valor Copago", 1, 0, 'C', True)
            pdf.cell(30, 10, "Part. Gral.", 1, 0, 'C', True)
            pdf.cell(30, 10, "Part. Pref.", 1, 1, 'C', True)

            # --- FILAS CON TRUNCADO DE NOMBRE ---
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Arial", '', 7)
            for _, row in df_sel.iterrows():
                nombre_raw = str(row['Nombre'])
                # Truncado para no pisar otras celdas
                nombre_mostrar = (nombre_raw[:35] + "..") if len(nombre_raw) > 37 else nombre_raw
                
                pdf.cell(18, 8, str(row['Código']), 1, 0, 'C')
                pdf.cell(52, 8, f" {nombre_mostrar}", 1, 0, 'L')
                pdf.cell(30, 8, f"${row['Valor bono Fonasa']:,.0f}", 1, 0, 'R')
                pdf.cell(30, 8, f"${row['Valor copago']:,.0f}", 1, 0, 'R')
                pdf.cell(30, 8, f"${row['Valor particular General']:,.0f}", 1, 0, 'R')
                pdf.cell(30, 8, f"${row['Valor particular preferencial']:,.0f}", 1, 1, 'R')

            # --- TOTALES ---
            pdf.set_font("Arial", 'B', 7)
            pdf.set_fill_color(240, 240, 240)
            pdf.cell(70, 10, " TOTALES ACUMULADOS", 1, 0, 'L', True)
            pdf.cell(30, 10, f"${tot_f:,.0f}", 1, 0, 'R', True)
            pdf.cell(30, 10, f"${tot_c:,.0f}", 1, 0, 'R', True)
            pdf.cell(30, 10, f"${tot_pg:,.0f}", 1, 0, 'R', True)
            pdf.cell(30, 10, f"${tot_pp:,.0f}", 1, 1, 'R', True)

            # --- PIE DE PÁGINA CON NOTAS ---
            pdf.ln(10)
            pdf.set_font("Arial", 'B', 8)
            pdf.cell(0, 5, "INFORMACIÓN IMPORTANTE:", ln=True)
            
            pdf.set_font("Arial", '', 7)
            notas_texto = (
                f"- Folio único de atención: {codigo_folio}\n"
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

            # Generar archivo
            nombre_archivo = f"Cotizacion_{codigo_folio}.pdf"
            pdf.output(nombre_archivo)
            with open(nombre_archivo, "rb") as f:
                st.download_button(
                    label="⬇️ Descargar PDF",
                    data=f,
                    file_name=f"Cotizacion_{nombre_p}_{codigo_folio}.pdf",
                    mime="application/pdf"
                )
    else:
        st.info("Por favor, seleccione uno o más exámenes para generar la cotización.")
else:
    st.error("No se pudo cargar el archivo 'aranceles.xlsx'. Verifique que el archivo esté en la misma carpeta que este script.")