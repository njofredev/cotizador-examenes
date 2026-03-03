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

def buscar_paciente_historial(doc_id):
    conn = conectar_db()
    if conn:
        try:
            query = "SELECT folio, fecha_cotizacion, nombre_paciente, total_copago FROM cotizaciones WHERE documento_id = %s ORDER BY fecha_cotizacion DESC"
            df_historial = pd.read_sql(query, conn, params=(doc_id,))
            conn.close()
            return df_historial
        except: return None
    return None

def guardar_en_db(folio, nombre, t_doc, doc_id, f_nac, t_f, t_c, t_pg, t_pp, df_examenes):
    conn = conectar_db()
    if conn:
        try:
            cur = conn.cursor()
            cotizacion_id = str(uuid.uuid4())
            fecha_ahora = datetime.now()
            cur.execute("""
                INSERT INTO cotizaciones (id, folio, nombre_paciente, tipo_documento, documento_id, 
                fecha_nacimiento, fecha_cotizacion, total_fonasa, total_copago, total_particular_gral, total_particular_pref
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (cotizacion_id, folio, nombre, t_doc, doc_id, f_nac, fecha_ahora, int(t_f), int(t_c), int(t_pg), int(t_pp)))
            for _, row in df_examenes.iterrows():
                cur.execute("INSERT INTO detalle_cotizaciones (id, folio_cotizacion, codigo_examen, nombre_examen, valor_copago) VALUES (%s, %s, %s, %s, %s)",
                            (str(uuid.uuid4()), folio, str(row['Código']), str(row['Nombre']), int(row['Valor copago'])))
            conn.commit(); cur.close(); conn.close()
            return True
        except: return False
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

# --- ESTADOS DE SESIÓN ---
if 'paso' not in st.session_state: st.session_state.paso = 'busqueda'
if 'doc_id_sesion' not in st.session_state: st.session_state.doc_id_sesion = ''
if 'nombre_sugerido' not in st.session_state: st.session_state.nombre_sugerido = ''
if 'pdf_generado' not in st.session_state: st.session_state.pdf_generado = False

# --- HEADER ---
if os.path.exists("logo.png"):
    col_l1, col_l2, col_l3 = st.columns([1.5, 1, 1.5])
    with col_l2: st.image("logo.png", width=110)

st.markdown("<h2 style='text-align: center; margin-bottom: 0;'>Cotizador de exámenes</h2>", unsafe_allow_html=True)
st.markdown("""
    <div class="sucursal-info">
        <b>Vitacura:</b> Av. Vitacura #8620 | <b>Los Tribunales:</b> Calle Los Tribunales #1268<br>
        Policlínico Tabancura S.A.
    </div>
    """, unsafe_allow_html=True)

# --- PASO 1: BÚSQUEDA ---
if st.session_state.paso == 'busqueda':
    with st.container():
        st.markdown("##### 🔍 Consulta de Paciente")
        c1, c2 = st.columns([1, 2])
        tipo_doc_busq = c1.radio("Documento", ["RUT Nacional", "Pasaporte / ID"], horizontal=True)
        doc_id_input = c2.text_input("Número de Documento")
        
        if st.button("Consultar o Iniciar"):
            if doc_id_input:
                st.session_state.doc_id_sesion = doc_id_input
                st.session_state.tipo_doc_sesion = tipo_doc_busq
                hist = buscar_paciente_historial(doc_id_input)
                if hist is not None and not hist.empty:
                    st.info(f"Paciente con historial ({len(hist)} registros).")
                    st.session_state.nombre_sugerido = hist.iloc[0]['nombre_paciente']
                    st.dataframe(hist, use_container_width=True, hide_index=True)
                st.session_state.paso = 'formulario'
                st.rerun()
            else:
                st.error("Ingrese un documento.")

# --- PASO 2: FORMULARIO ---
elif st.session_state.paso == 'formulario':
    if not st.session_state.pdf_generado:
        if st.button("⬅️ Volver a buscar"):
            st.session_state.paso = 'busqueda'
            st.rerun()

    df_aranceles = cargar_datos()
    if df_aranceles is not None:
        with st.container():
            st.markdown("##### 👤 Datos del Paciente")
            st.write(f"**Documento:** {st.session_state.doc_id_sesion} ({st.session_state.tipo_doc_sesion})")
            nombre_p = st.text_input("Nombre Completo", value=st.session_state.nombre_sugerido, disabled=st.session_state.pdf_generado)
            
            c_f1, c_f2 = st.columns(2)
            fecha_nac = c_f1.date_input("Fecha de Nacimiento", value=date(1990, 1, 1), min_value=date(1900, 1, 1), max_value=date.today(), disabled=st.session_state.pdf_generado)
            prevision = c_f2.selectbox("Previsión", ["Particular", "Fonasa"], disabled=st.session_state.pdf_generado)

        if not st.session_state.pdf_generado:
            with st.container():
                st.markdown("##### 🧪 Selección de Exámenes")
                seleccionados = st.multiselect("Busque exámenes por nombre o código:", options=df_aranceles["busqueda"].unique().tolist())

            if seleccionados:
                df_sel = df_aranceles[df_aranceles["busqueda"].isin(seleccionados)].copy()
                
                if prevision == "Fonasa":
                    cols_v = ["Código", "Nombre", "Valor bono Fonasa", "Valor copago"]
                    nombres_display = {"Valor bono Fonasa": "Bono", "Valor copago": "Copago"}
                else:
                    cols_v = ["Código", "Nombre", "Valor particular General", "Valor particular preferencial"]
                    nombres_display = {"Valor particular General": "P. Gral", "Valor particular preferencial": "P. Pref"}
                
                st.dataframe(df_sel[cols_v].rename(columns=nombres_display), use_container_width=True, hide_index=True)

                t_f, t_c, t_pg, t_pp = df_sel["Valor bono Fonasa"].sum(), df_sel["Valor copago"].sum(), df_sel["Valor particular General"].sum(), df_sel["Valor particular preferencial"].sum()
                
                m1, m2 = st.columns(2)
                if prevision == "Fonasa":
                    m1.metric("Total Bono Fonasa", f"${t_f:,.0f}")
                    m2.metric("Total Copago", f"${t_c:,.0f}")
                else:
                    m1.metric("Total Part. General", f"${t_pg:,.0f}")
                    m2.metric("Total Part. Pref", f"${t_pp:,.0f}")

                if st.button("🚀 Guardar y Generar PDF"):
                    if nombre_p:
                        folio = generar_folio()
                        if guardar_en_db(folio, nombre_p, st.session_state.tipo_doc_sesion, st.session_state.doc_id_sesion, fecha_nac, t_f, t_c, t_pg, t_pp, df_sel):
                            
                            # --- LÓGICA DE PDF ---
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
                            pdf.cell(0, 6, f"Documento: {st.session_state.doc_id_sesion}", ln=True)
                            pdf.cell(0, 6, f"Previsión: {prevision}", ln=True)
                            pdf.cell(0, 6, f"Fecha: {date.today().strftime('%d/%m/%Y')}", ln=True); pdf.ln(5)

                            # Definir nombres de columnas dinámicos para el PDF
                            if prevision == "Fonasa":
                                col3_label = "Bono Fonasa"
                                col4_label = "Copago"
                            else:
                                col3_label = "P. General"
                                col4_label = "P. Preferencial"

                            # Tabla - Encabezados
                            pdf.set_fill_color(2, 112, 249); pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", 'B', 8)
                            w = [25, 75, 45, 45]
                            headers = ["Código", "Examen", col3_label, col4_label]
                            for i in range(len(headers)): pdf.cell(w[i], 10, headers[i], 1, 0, 'C', True)
                            pdf.ln()

                            # Tabla - Filas
                            pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", '', 8)
                            for _, r in df_sel.iterrows():
                                pdf.cell(w[0], 8, str(r['Código']), 1, 0, 'C')
                                pdf.cell(w[1], 8, f" {str(r['Nombre'])[:40]}", 1, 0, 'L')
                                if prevision == "Fonasa":
                                    pdf.cell(w[2], 8, f"${r['Valor bono Fonasa']:,.0f}", 1, 0, 'R')
                                    pdf.cell(w[3], 8, f"${r['Valor copago']:,.0f}", 1, 1, 'R')
                                else:
                                    pdf.cell(w[2], 8, f"${r['Valor particular General']:,.0f}", 1, 0, 'R')
                                    pdf.cell(w[3], 8, f"${r['Valor particular preferencial']:,.0f}", 1, 1, 'R')

                            # Fila de Totales
                            pdf.set_font("Arial", 'B', 9); pdf.set_fill_color(240, 240, 240)
                            pdf.cell(w[0] + w[1], 10, "TOTAL ESTIMADO", 1, 0, 'R', True)
                            if prevision == "Fonasa":
                                pdf.cell(w[2], 10, f"${t_f:,.0f}", 1, 0, 'R', True)
                                pdf.cell(w[3], 10, f"${t_c:,.0f}", 1, 1, 'R', True)
                            else:
                                pdf.cell(w[2], 10, f"${t_pg:,.0f}", 1, 0, 'R', True)
                                pdf.cell(w[3], 10, f"${t_pp:,.0f}", 1, 1, 'R', True)

                            # Notas
                            pdf.ln(10); pdf.set_font("Arial", 'B', 8); pdf.cell(0, 5, "NOTAS E INFORMACIÓN:", ln=True)
                            pdf.set_font("Arial", '', 7)
                            pdf.multi_cell(0, 4, "- Toma de muestras: Lunes a Viernes de 08:30 a 11:00 hrs.\n- El ayuno requerido es de 8 a 12 horas máximo.\n- Esta cotización es referencial y tiene validez por 30 días.")

                            path = f"Cot_{folio}.pdf"
                            pdf.output(path)
                            st.session_state['pdf_path'] = path
                            st.session_state.pdf_generado = True
                            st.rerun()
                    else: st.error("Falta el nombre del paciente.")

        if st.session_state.pdf_generado:
            with st.container():
                st.success("Cotización generada.")
                if 'pdf_path' in st.session_state:
                    with open(st.session_state['pdf_path'], "rb") as f:
                        st.download_button("🔵 DESCARGAR PDF", f, file_name=f"Cotizacion_{nombre_p}.pdf")
                
                st.markdown("---")
                c_opt1, c_opt2 = st.columns(2)
                if c_opt1.button("🔄 Nueva Cotización (Mismo Paciente)"):
                    st.session_state.pdf_generado = False
                    st.rerun()
                if c_opt2.button("🏠 Volver al Inicio"):
                    st.session_state.paso = 'busqueda'
                    st.session_state.pdf_generado = False
                    st.session_state.nombre_sugerido = ''
                    st.session_state.doc_id_sesion = ''
                    st.rerun()

st.markdown("<br><p style='text-align: center; color: #aaa; font-size: 0.8rem;'>© 2026 Policlínico Tabancura</p>", unsafe_allow_html=True)