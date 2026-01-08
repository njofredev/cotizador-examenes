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

# FUNCIÓN PARA GENERAR FOLIO ÚNICO
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

if df is not None:
    st.subheader("Datos del Paciente")
    col_p1, col_p2, col_p3 = st.columns(3)
    nombre_p = col_p1.text_input("Nombre Completo:", placeholder="Ej: Juan Pérez")
    rut_p = col_p2.text_input("RUT:", placeholder="12.345.678-9")
    fecha_nac = col_p3.date_input("Fecha de Nacimiento:", 
                                 value=date(1990, 1, 1),
                                 format="DD/MM/YYYY")

    seleccionados = st.multiselect(
        "Busque y seleccione los exámenes:",
        options=df["busqueda"].unique().tolist(),
        placeholder="Escriba aquí nombre o código..."
    )

    if seleccionados:
        # Filtrar datos seleccionados
        df_sel = df[df["busqueda"].isin(seleccionados)].copy()
        df_display = df_sel.drop(columns=["busqueda"])

        st.write("### Detalle de Cotización")

        # --- LÓGICA PARA SUPER CABECERAS EN LA TABLA WEB ---
        # Creamos un MultiIndex para las columnas
        columnas_multi = pd.MultiIndex.from_tuples([
            ("", "Código"),
            ("", "Nombre"),
            ("Bono Fonasa", "Valor bono Fonasa"),
            ("Bono Fonasa", "Valor copago"),
            ("Particular", "Valor particular General"),
            ("Particular", "Valor particular preferencial")
        ])
        
        df_display.columns = columnas_multi

        # Mostrar tabla con estilo (Pandas Styler permite visualizar el MultiIndex)
        st.table(df_display.style.format(subset=df_display.columns[2:], formatter="${:,.0f}"))
        
        # Totales
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
            codigo_cotizacion = generar_folio()
            pdf = FPDF(orientation='P', unit='mm', format='A4')
            pdf.add_page()
            
            if os.path.exists("logo.png"):
                pdf.image("logo.png", 10, 8, h=12)
            
            pdf.set_font("Arial", 'B', 10)
            pdf.set_text_color(15, 143, 238)
            pdf.cell(0, 5, f"FOLIO: {codigo_cotizacion}", ln=True, align='R')
            pdf.set_text_color(0, 0, 0)

            pdf.ln(10)
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 10, "COTIZACIÓN DE EXÁMENES", ln=True, align='C')
            pdf.ln(3)

            pdf.set_font("Arial", '', 10)
            pdf.cell(0, 6, f"Paciente: {nombre_p}", ln=True)
            pdf.cell(0, 6, f"RUT: {rut_p}", ln=True)
            pdf.cell(0, 6, f"Fecha de Nacimiento: {fecha_nac.strftime('%d/%m/%Y')}", ln=True)
            pdf.cell(0, 6, f"Fecha Cotización: {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')}", ln=True)
            pdf.ln(6)

            # --- CABECERA PDF ---
            pdf.set_fill_color(15, 143, 238)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Arial", 'B', 9)
            
            pdf.cell(18, 10, "", 0, 0) 
            pdf.cell(52, 10, "", 0, 0)
            pdf.cell(60, 10, "Bono Fonasa", 1, 0, 'C', True)
            pdf.cell(60, 10, "Particular", 1, 1, 'C', True)

            pdf.set_font("Arial", 'B', 7)
            pdf.cell(18, 10, "Código", 1, 0, 'C', True)
            pdf.cell(52, 10, " Nombre", 1, 0, 'L', True)
            pdf.cell(30, 10, "Valor Bono", 1, 0, 'C', True)
            pdf.cell(30, 10, "Valor Copago", 1, 0, 'C', True)
            pdf.cell(30, 10, "Part. Gral.", 1, 0, 'C', True)
            pdf.cell(30, 10, "Part. Pref.", 1, 1, 'C', True)

            # Filas con truncado
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Arial", '', 7)
            for _, row in df_sel.iterrows():
                n_raw = str(row['Nombre'])
                n_mostrar = (n_raw[:35] + "..") if len(n_raw) > 38 else n_raw
                pdf.cell(18, 8, str(row['Código']), 1, 0, 'C')
                pdf.cell(52, 8, f" {n_mostrar}", 1, 0, 'L')
                pdf.cell(30, 8, f"${row['Valor bono Fonasa']:,.0f}", 1, 0, 'R')
                pdf.cell(30, 8, f"${row['Valor copago']:,.0f}", 1, 0, 'R')
                pdf.cell(30, 8, f"${row['Valor particular General']:,.0f}", 1, 0, 'R')
                pdf.cell(30, 8, f"${row['Valor particular preferencial']:,.0f}", 1, 1, 'R')

            # Totales
            pdf.set_font("Arial", 'B', 7)
            pdf.set_fill_color(240, 240, 240)
            pdf.cell(70, 10, " TOTALES ACUMULADOS", 1, 0, 'L', True)
            pdf.cell(30, 10, f"${tot_f:,.0f}", 1, 0, 'R', True)
            pdf.cell(30, 10, f"${tot_c:,.0f}", 1, 0, 'R', True)
            pdf.cell(30, 10, f"${tot_pg:,.0f}", 1, 0, 'R', True)
            pdf.cell(30, 10, f"${tot_pp:,.0f}", 1, 1, 'R', True)

            pdf.ln(10)
            pdf.set_font("Arial", 'I', 7)
            pdf.multi_cell(0, 5, f"Folio: {codigo_cotizacion}. Validez 30 días. Valores sujetos a confirmación.")

            pdf.output("cotizacion.pdf")
            with open("cotizacion.pdf", "rb") as f:
                st.download_button("⬇️ Descargar PDF", f, file_name=f"Cotizacion_{codigo_cotizacion}.pdf")
    else:
        st.info("Seleccione exámenes.")
else:
    st.error("Archivo 'aranceles.xlsx' no encontrado.")