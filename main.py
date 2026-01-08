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
    .stButton>button {{
        background-color: #0f8fee;
        color: white;
    }}
    </style>
    """, unsafe_allow_html=True)

# 2. CARGA DE DATOS DESDE EXCEL
@st.cache_data
def cargar_datos():
    try:
        # Cargamos el archivo Excel (.xlsx)
        df = pd.read_excel("aranceles.xlsx")
        
        # Ajustamos nombres de columnas (asegúrate que tu Excel tenga 6 columnas)
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
        df["Código"] = df["Código"].astype(str).str.replace(".0", "", regex=False)
        
        # Columna auxiliar para el buscador
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
    # Información del Paciente
    col_p1, col_p2 = st.columns(2)
    nombre_p = col_p1.text_input("Nombre del Paciente:", placeholder="Ej: Juan Pérez")
    rut_p = col_p2.text_input("RUT:", placeholder="12.345.678-9")

    # Buscador Multiselect
    seleccionados = st.multiselect(
        "Busque y seleccione los exámenes (por nombre o código):",
        options=df["busqueda"].unique().tolist(),
        placeholder="Escriba aquí..."
    )

    if seleccionados:
        # Filtramos
        df_sel = df[df["busqueda"].isin(seleccionados)]
        
        st.write("### Detalle de Cotización")
        st.dataframe(df_sel.drop(columns=["busqueda"]), use_container_width=True)
        
        # Totales para métricas y PDF
        tot_f = df_sel["Valor bono Fonasa"].sum()
        tot_c = df_sel["Valor copago"].sum()
        tot_pg = df_sel["Valor particular General"].sum()
        tot_pp = df_sel["Valor particular preferencial"].sum()

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Bono Fonasa", f"${tot_f:,.0f}")
        m2.metric("Total Copago", f"${tot_c:,.0f}")
        m3.metric("Total Part. General", f"${tot_pg:,.0f}")
        m4.metric("Total Part. Preferencial", f"${tot_pp:,.0f}")

        # 4. GENERACIÓN DE PDF CON CABECERAS AGRUPADAS
        if st.button("Generar Cotización en PDF"):
            pdf = FPDF(orientation='L', unit='mm', format='A4')
            pdf.add_page()
            
            # Logo
            if os.path.exists("logo.png"):
                pdf.image("logo.png", 10, 8, h=15)
            
            pdf.ln(20)
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, "COTIZACIÓN DE EXÁMENES", ln=True, align='C')
            pdf.ln(5)

            # Datos Paciente
            pdf.set_font("Arial", '', 11)
            pdf.cell(0, 7, f"Paciente: {nombre_p if nombre_p else '____________________'}", ln=True)
            pdf.cell(0, 7, f"RUT: {rut_p if rut_p else '____________________'}", ln=True)
            pdf.cell(0, 7, f"Fecha: {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')}", ln=True)
            pdf.ln(8)

            # --- CABECERA DE TABLA AGRUPADA ---
            pdf.set_fill_color(15, 143, 238) # #0f8fee
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Arial", 'B', 10)
            
            # Fila 1: Grupos Superiores
            pdf.cell(20, 10, "", 0, 0)       # Vacío sobre Código
            pdf.cell(85, 10, "", 0, 0)       # Vacío sobre Nombre
            pdf.cell(66, 10, "Bono Fonasa", 1, 0, 'C', True)   # Une Fonasa + Copago (33+33)
            pdf.cell(76, 10, "Particular", 1, 1, 'C', True)     # Une Gral + Pref (38+38)

            # Fila 2: Sub-títulos
            pdf.set_font("Arial", 'B', 8)
            pdf.cell(20, 10, "Código", 1, 0, 'C', True)
            pdf.cell(85, 10, " Nombre", 1, 0, 'L', True)
            pdf.cell(33, 10, "Valor Bono", 1, 0, 'C', True)
            pdf.cell(33, 10, "Valor Copago", 1, 0, 'C', True)
            pdf.cell(38, 10, "Particular Gral.", 1, 0, 'C', True)
            pdf.cell(38, 10, "Particular Pref.", 1, 1, 'C', True)

            # Filas de datos
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Arial", '', 8)
            for _, row in df_sel.iterrows():
                pdf.cell(20, 8, str(row['Código']), 1, 0, 'C')
                # Truncar nombre si es muy largo para no romper la tabla
                nombre_examen = str(row['Nombre'])[:55]
                pdf.cell(85, 8, f" {nombre_examen}", 1, 0, 'L')
                pdf.cell(33, 8, f"${row['Valor bono Fonasa']:,.0f}", 1, 0, 'R')
                pdf.cell(33, 8, f"${row['Valor copago']:,.0f}", 1, 0, 'R')
                pdf.cell(38, 8, f"${row['Valor particular General']:,.0f}", 1, 0, 'R')
                pdf.cell(38, 8, f"${row['Valor particular preferencial']:,.0f}", 1, 1, 'R')

            # Totales Finales
            pdf.set_font("Arial", 'B', 8)
            pdf.set_fill_color(240, 240, 240)
            pdf.cell(105, 10, " TOTALES ACUMULADOS", 1, 0, 'L', True)
            pdf.cell(33, 10, f"${tot_f:,.0f}", 1, 0, 'R', True)
            pdf.cell(33, 10, f"${tot_c:,.0f}", 1, 0, 'R', True)
            pdf.cell(38, 10, f"${tot_pg:,.0f}", 1, 0, 'R', True)
            pdf.cell(38, 10, f"${tot_pp:,.0f}", 1, 1, 'R', True)

            # Nota al pie
            pdf.ln(10)
            pdf.set_font("Arial", 'I', 8)
            pdf.multi_cell(0, 5, "Notas:\n- Valores sujetos a confirmación en sucursal.\n- Presupuesto válido por 30 días.\n- Solo aplica para tramos Fonasa B, C y D.")

            # Guardar y ofrecer descarga
            nombre_archivo = "cotizacion_examen.pdf"
            pdf.output(nombre_archivo)
            with open(nombre_archivo, "rb") as f:
                st.download_button(
                    label="⬇️ Descargar Cotización en PDF",
                    data=f,
                    file_name=f"Cotizacion_{rut_p}.pdf",
                    mime="application/pdf"
                )
    else:
        st.info("Seleccione exámenes para comenzar la cotización.")
        st.write("⚠️ *Nota: Valores sujetos a confirmación en sucursal. Vigencia 30 días.*")
else:
    st.error("No se encontró el archivo 'aranceles.xlsx' en el directorio.")