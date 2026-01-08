import streamlit as st
import pandas as pd
from fpdf import FPDF
import os

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
    </style>
    """, unsafe_allow_html=True)

# 2. CARGA DE DATOS DESDE EXCEL
@st.cache_data
def cargar_datos():
    try:
        # Cargamos el archivo Excel (.xlsx)
        df = pd.read_excel("aranceles.xlsx")
        
        # CAMBIO DE NOMBRES DE COLUMNAS SEGÚN SOLICITUD
        df.columns = [
            "Código", 
            "Nombre", 
            "Valor bono Fonasa", 
            "Valor copago", 
            "Valor particular General", 
            "Valor particular preferencial"
        ]
        
        # Limpieza de datos
        df = df.fillna(0)
        # Convertimos el código a string limpio
        df["Código"] = df["Código"].astype(str).str.replace(".0", "", regex=False)
        
        # Columna auxiliar para el buscador (Código + Nombre)
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

st.markdown("""
Busque sus exámenes aquí:  
*(Puede buscar por **Nombre** o por **Código**)*
""")

if df is not None:
    # Información del Paciente
    col_p1, col_p2 = st.columns(2)
    nombre_p = col_p1.text_input("Nombre del Paciente:", placeholder="Ej: Juan Pérez")
    rut_p = col_p2.text_input("RUT:", placeholder="12.345.678-9")

    # Buscador Multiselect
    seleccionados = st.multiselect(
        "Seleccione los exámenes:",
        options=df["busqueda"].unique().tolist(),
        placeholder="Escriba el nombre o código aquí..."
    )

    if seleccionados:
        # Filtramos usando la columna auxiliar
        df_sel = df[df["busqueda"].isin(seleccionados)]
        
        # Tabla en pantalla (quitamos la columna de búsqueda para la vista)
        st.write("### Detalle de Cotización")
        st.dataframe(df_sel.drop(columns=["busqueda"]), use_container_width=True)
        
        # Totales
        tot_f = df_sel["Valor bono Fonasa"].sum()
        tot_c = df_sel["Valor copago"].sum()
        tot_pg = df_sel["Valor particular General"].sum()
        tot_pp = df_sel["Valor particular preferencial"].sum()

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Bono Fonasa", f"${tot_f:,.0f}")
        m2.metric("Total Copago", f"${tot_c:,.0f}")
        m3.metric("Total Part. General", f"${tot_pg:,.0f}")
        m4.metric("Total Part. Preferencial", f"${tot_pp:,.0f}")

        # 4. GENERACIÓN DE PDF
        if st.button("Generar Cotización en PDF"):
            pdf = FPDF(orientation='L', unit='mm', format='A4')
            pdf.add_page()
            
            if os.path.exists("logo.png"):
                pdf.image("logo.png", 10, 8, w=0)
            
            pdf.ln(25)
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, "PRESUPUESTO MÉDICO", ln=True, align='C')
            pdf.ln(5)

            pdf.set_font("Arial", '', 11)
            pdf.cell(0, 7, f"Paciente: {nombre_p if nombre_p else '____________________'}", ln=True)
            pdf.cell(0, 7, f"RUT: {rut_p if rut_p else '____________________'}", ln=True)
            pdf.cell(0, 7, f"Fecha: {pd.Timestamp.now().strftime('%d/%m/%Y')}", ln=True)
            pdf.ln(8)

            # Cabecera Tabla con nuevos nombres
            pdf.set_fill_color(15, 143, 238) # Azul corporativo
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Arial", 'B', 8)
            
            pdf.cell(20, 10, "Código", 1, 0, 'C', True)
            pdf.cell(85, 10, " Nombre", 1, 0, 'L', True)
            pdf.cell(33, 10, "Val. Bono Fonasa", 1, 0, 'C', True)
            pdf.cell(33, 10, "Valor Copago", 1, 0, 'C', True)
            pdf.cell(38, 10, "Val. Part. General", 1, 0, 'C', True)
            pdf.cell(38, 10, "Val. Part. Pref.", 1, 1, 'C', True)

            # Filas
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Arial", '', 8)
            for _, row in df_sel.iterrows():
                pdf.cell(20, 8, str(row['Código']), 1, 0, 'C')
                pdf.cell(85, 8, f" {str(row['Nombre'])[:50]}", 1)
                pdf.cell(33, 8, f"${row['Valor bono Fonasa']:,.0f}", 1, 0, 'R')
                pdf.cell(33, 8, f"${row['Valor copago']:,.0f}", 1, 0, 'R')
                pdf.cell(38, 8, f"${row['Valor particular General']:,.0f}", 1, 0, 'R')
                pdf.cell(38, 8, f"${row['Valor particular preferencial']:,.0f}", 1, 1, 'R')

            # Totales
            pdf.set_font("Arial", 'B', 8)
            pdf.set_fill_color(240, 240, 240)
            pdf.cell(105, 10, " TOTALES ACUMULADOS", 1, 0, 'L', True)
            pdf.cell(33, 10, f"${tot_f:,.0f}", 1, 0, 'R', True)
            pdf.cell(33, 10, f"${tot_c:,.0f}", 1, 0, 'R', True)
            pdf.cell(38, 10, f"${tot_pg:,.0f}", 1, 0, 'R', True)
            pdf.cell(38, 10, f"${tot_pp:,.0f}", 1, 1, 'R', True)

            pdf.output("cotizacion.pdf")
            with open("cotizacion.pdf", "rb") as f:
                st.download_button("⬇️ Descargar PDF", f, file_name="cotizacion_tabancura.pdf")
    else:
        st.info("Seleccione exámenes para cotizar.")
else:
    st.error("Archivo 'aranceles.xlsx' no encontrado.")