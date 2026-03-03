import streamlit as st
import pandas as pd
from fpdf import FPDF
import os
import secrets
import string
import uuid
from datetime import date, datetime
import psycopg2

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="Cotizador Policlínico Tabancura", 
    page_icon="🏥", 
    layout="centered" 
)

# --- ESTILO CSS ---
st.markdown(f"""
    <style>
    .main {{ background-color: #f8f9fa; }}
    span[data-baseweb="tag"] {{ background-color: #0270f9 !important; }}
    div.stBlock {{
        padding: 1.5rem;
        border-radius: 12px;
        background-color: white;
        border: 1px solid #e1e4e8;
        margin-bottom: 1rem;
    }}
    .stButton>button {{
        width: 100%;
        border-radius: 8px;
        height: 3.5em;
        background-color: #0270f9;
        color: white;
        font-weight: bold;
        border: none;
    }}
    .sucursal-info {{
        text-align: center;
        color: #555;
        font-size: 0.9rem;
        margin-bottom: 20px;
        line-height: 1.4;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE BASE DE DATOS ---
def conectar_db():
    try:
        if "postgres" in st.secrets:
            db_conf = st.secrets["postgres"]
            return psycopg2.connect(
                host=db_conf["host"], database=db_conf["database"], 
                user=db_conf["user"], password=db_conf["password"], 
                port=db_conf["port"], sslmode="disable"
            )
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

def guardar_en_db(folio, nombre, t_doc, doc_id, f_nac, t_f, t_c, t_pg, t_pp, df_examenes):
    conn = conectar_db()
    if conn:
        try:
            cur = conn.cursor()
            cotizacion_id = str(uuid.uuid4())
            fecha_ahora = datetime.now()
            
            # 1. Insertar en tabla cotizaciones
            cur.execute("""
                INSERT INTO cotizaciones (
                    id, folio, nombre_paciente, tipo_documento, documento_id, 
                    fecha_nacimiento, fecha_cotizacion, total_fonasa, 
                    total_copago, total_particular_gral, total_particular_pref
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                cotizacion_id, folio, nombre, t_doc, doc_id, 
                f_nac, fecha_ahora, int(t_f), int(t_c), int(t_pg), int(t_pp)
            ))
            
            # 2. Insertar detalles
            for _, row in df_examenes.iterrows():
                detalle_id = str(uuid.uuid4())
                cur.execute("""
                    INSERT INTO detalle_cotizaciones (
                        id, folio_cotizacion, codigo_examen, nombre_examen, valor_copago
                    ) VALUES (%s, %s, %s, %s, %s)
                """, (
                    detalle_id, folio, str(row['Código']), 
                    str(row['Nombre']), int(row['Valor copago'])
                ))
            
            conn.commit()
            cur.close()
            conn.close()
            return True
        except Exception as e:
            st.error(f"Error al guardar: {e}")
            return False
    return False

# --- UTILIDADES ---
def generar_folio():
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for i in range(8))

@st.cache_data
def cargar_datos():
    try:
        df = pd.read_excel("aranceles.xlsx")
        df.columns = ["Código", "Nombre", "Valor bono Fonasa", "Valor copago", "Valor particular General", "Valor particular preferencial"]
        df = df.fillna(0)
        df["Código"] = df["Código"].astype(str).str.replace(".0", "", regex=False)
        df["busqueda"] = df["Código"] + " - " + df["Nombre"]
        return df
    except: return None

# --- INTERFAZ ---
df = cargar_datos()

if os.path.exists("logo.png"):
    col_l1, col_l2, col_l3 = st.columns([1.5, 1, 1.5])
    with col_l2: st.image("logo.png", width=110)

st.markdown("<h2 style='text-align: center; margin-bottom: 0;'>Cotizador de exámenes</h2>", unsafe_allow_html=True)
st.markdown("""
    <div class="sucursal-info">
        <b>Vitacura:</b> Av. Vitacura #8620, Vitacura | tel: +56229336740<br>
        <b>Los Tribunales:</b> Calle Los Tribunales #1268, Santiago | tel: +5622172635
    </div>
    """, unsafe_allow_html=True)

if df is not None:
    # 1. DATOS PACIENTE
    with st.container():
        st.markdown("##### 👤 Datos del Paciente")
        c1, c2 = st.columns([1, 2])
        tipo_doc = c1.radio("Documento", ["RUT Nacional", "Pasaporte / ID"], horizontal=True)
        doc_id = c2.text_input("Número de Documento")
        nombre_p = st.text_input("Nombre Completo")
        fecha_nac = st.date_input("Fecha de Nacimiento", value=date(1990, 1, 1))

    # 2. SELECCIÓN DE EXÁMENES
    with st.container():
        st.markdown("##### 🧪 Selección de Exámenes")
        seleccionados = st.multiselect("Busque exámenes por nombre o código:", options=df["busqueda"].unique().tolist())

    if seleccionados:
        df_sel = df[df["busqueda"].isin(seleccionados)].copy()
        
        df_display = df_sel[["Código", "Nombre", "Valor bono Fonasa", "Valor copago", "Valor particular General", "Valor particular preferencial"]].rename(columns={
            "Valor bono Fonasa": "Bono Fonasa", "Valor copago": "Copago",
            "Valor particular General": "Part. Gral", "Valor particular preferencial": "Part. Pref"
        })
        
        st.dataframe(
            df_display.style.format("${:,.0f}", subset=["Bono Fonasa", "Copago", "Part. Gral", "Part. Pref"]),
            use_container_width=True, hide_index=True
        )

        t_f, t_c, t_pg, t_pp = df_sel["Valor bono Fonasa"].sum(), df_sel["Valor copago"].sum(), df_sel["Valor particular General"].sum(), df_sel["Valor particular preferencial"].sum()
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Bono Fonasa", f"${t_f:,.0f}")
        m2.metric("Total Copago", f"${t_c:,.0f}")
        m3.metric("Part. General", f"${t_pg:,.0f}")
        m4.metric("Part. Pref", f"${t_pp:,.0f}")

        if st.button("🚀 Guardar y Generar PDF"):
            if not nombre_p or not doc_id:
                st.error("⚠️ Complete los datos del paciente.")
            else:
                folio = generar_folio()
                if guardar_en_db(folio, nombre_p, tipo_doc, doc_id, fecha_nac, t_f, t_c, t_pg, t_pp, df_sel):
                    
                    pdf = FPDF()
                    pdf.set_compression(True)
                    pdf.add_page()
                    
                    # Encabezado
                    pdf.set_font("Arial", 'B', 12); pdf.set_text_color(2, 112, 249)
                    pdf.cell(100, 10, "POLICLÍNICO TABANCURA", ln=0)
                    pdf.set_font("Arial", 'B', 10); pdf.cell(0, 10, f"FOLIO: {folio}", ln=1, align='R')
                    
                    pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", 'B', 14); pdf.ln(5)
                    pdf.cell(0, 10, "Cotización de Exámenes de Laboratorio", ln=True, align='C'); pdf.ln(5)
                    
                    pdf.set_font("Arial", '', 10)
                    pdf.cell(0, 6, f"Paciente: {nombre_p}", ln=True)
                    pdf.cell(0, 6, f"Documento: {doc_id} ({tipo_doc})", ln=True)
                    pdf.cell(0, 6, f"F. Nacimiento: {fecha_nac.strftime('%d/%m/%Y')}", ln=True)
                    pdf.cell(0, 6, f"Fecha: {date.today().strftime('%d/%m/%Y')}", ln=True); pdf.ln(5)

                    # Tabla PDF
                    pdf.set_fill_color(2, 112, 249); pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", 'B', 8)
                    w = [18, 52, 30, 30, 30, 30]
                    headers = ["Código", "Nombre", "Bono Fonasa", "Copago", "P. Gral", "P. Pref"]
                    for i in range(len(headers)): pdf.cell(w[i], 10, headers[i], 1, 0, 'C', True)
                    pdf.ln()

                    pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", '', 7)
                    for _, r in df_sel.iterrows():
                        pdf.cell(w[0], 8, str(r['Código']), 1, 0, 'C')
                        pdf.cell(w[1], 8, f" {str(r['Nombre'])[:35]}", 1, 0, 'L')
                        pdf.cell(w[2], 8, f"${r['Valor bono Fonasa']:,.0f}", 1, 0, 'R')
                        pdf.cell(w[3], 8, f"${r['Valor copago']:,.0f}", 1, 0, 'R')
                        pdf.cell(w[4], 8, f"${r['Valor particular General']:,.0f}", 1, 0, 'R')
                        pdf.cell(w[5], 8, f"${r['Valor particular preferencial']:,.0f}", 1, 1, 'R')

                    # Totales
                    pdf.set_font("Arial", 'B', 7); pdf.set_fill_color(240, 240, 240)
                    pdf.cell(w[0]+w[1], 10, " TOTALES ACUMULADOS", 1, 0, 'L', True)
                    pdf.cell(w[2], 10, f"${t_f:,.0f}", 1, 0, 'R', True)
                    pdf.cell(w[3], 10, f"${t_c:,.0f}", 1, 0, 'R', True)
                    pdf.cell(w[4], 10, f"${t_pg:,.0f}", 1, 0, 'R', True)
                    pdf.cell(w[5], 10, f"${t_pp:,.0f}", 1, 1, 'R', True)

                    pdf.ln(8)
                    pdf.set_font("Arial", 'B', 8)
                    pdf.cell(0, 5, "INFORMACIÓN IMPORTANTE:", ln=True)
                    pdf.set_font("Arial", '', 7)
                    notas = (
                        f"- Folio único de atención: {folio}\n"
                        "- (*) El valor a pagar no considera seguros complementarios.\n"
                        "- Horario toma de muestras: Lunes a Viernes de 08:30am a 11:00am.\n"
                        "- El ayuno no debe superar las 12 horas.\n"
                        "- Para pruebas PTGO (Curva de glucosa/Insulina): Solo con agenda previa a las 08:30am.\n"
                        "- Si es paciente diabético, debe notificar en recepción antes de su atención.\n"
                        "- Esta cotización tiene una validez de 30 días corridos.\n"
                        "- Valores sujetos a confirmación en sucursal al momento de la atención."
                    )
                    pdf.multi_cell(0, 4, notas)

                    path = f"Cot_{folio}.pdf"
                    pdf.output(path)
                    st.session_state['pdf_path'] = path
                    st.success(f"✅ Cotización guardada con Folio: **{folio}**. Presione el botón de descarga.")

        if 'pdf_path' in st.session_state:
            with open(st.session_state['pdf_path'], "rb") as f:
                st.download_button("🔵 DESCARGAR PDF COTIZACIÓN", f, file_name=f"Cotizacion_{nombre_p}.pdf", mime="application/pdf")
    else:
        st.info("Seleccione uno o más exámenes para comenzar.")
else:
    st.error("Archivo 'aranceles.xlsx' no encontrado.")