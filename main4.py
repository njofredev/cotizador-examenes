import streamlit as st
import pandas as pd
from fpdf import FPDF
import os
import secrets
import string
import uuid
from datetime import date, datetime
import psycopg2

st.set_page_config(
    page_title="Cotizador Policlínico Tabancura", 
    page_icon="🏥", 
    layout="centered" 
)

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    span[data-baseweb="tag"] { background-color: #0270f9 !important; }
    
    div.stBlock {
        padding: 1.5rem;
        border-radius: 12px;
        background-color: white;
        border: 1px solid #e1e4e8;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }

    /* NORMALIZACIÓN TOTAL DE BOTONES (Download, Normal y Link) */
    .stButton>button, .stDownloadButton>button, .stLinkButton>a {
        width: 100% !important;
        height: 3.5em !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        font-size: 14px !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        text-decoration: none !important;
        transition: all 0.2s ease !important;
        margin: 0 !important;
        border: none !important;
    }

    .stButton>button, .stDownloadButton>button {
        background-color: #0270f9 !important;
        color: white !important;
    }

    .stButton>button:hover, .stDownloadButton>button:hover {
        background-color: #0156c2 !important;
    }

    .stLinkButton>a {
        background-color: white !important;
        color: #0270f9 !important;
        border: 1px solid #0270f9 !important;
        line-height: normal !important;
    }

    .stLinkButton>a:hover {
        background-color: #f0f7ff !important;
        border: 1px solid #0156c2 !important;
        color: #0156c2 !important;
    }

    .pill-button > div > button {
        background-color: #f0f2f6 !important;
        color: #31333F !important;
        border: 1px solid #d1d5db !important;
        height: 2.2em !important;
        padding: 0px 15px !important;
        border-radius: 15px !important;
        font-size: 0.85rem !important;
    }

    .sucursal-info {
        text-align: center;
        color: #555;
        font-size: 0.9rem;
        margin-bottom: 20px;
        line-height: 1.4;
    }

    .footer-link {
        text-align: center;
        font-size: 0.85rem;
        color: #0270f9 !important;
        text-decoration: none !important;
        font-weight: 500;
    }
    </style>
    """, unsafe_allow_html=True)

def calcular_edad(fecha_nacimiento):
    today = date.today()
    return today.year - fecha_nacimiento.year - ((today.month, today.day) < (fecha_nacimiento.month, fecha_nacimiento.day))

PACKS = {
    "Preventivo Hombre": {"items": ["Hemograma", "VHS", "Perfil Lipídico", "Creatinina", "Electrolitos", "Electrocardiograma", "Glucosa", "Hemoglobina glicosilada", "TSH", "VIH", "VDRL", "VHC", "Perfil Hepático", "Hepatitis B"], "help": "Control Preventivo Hombre 18 a 29 años."},
    "Cardiovascular": {"items": ["Electrocardiograma", "Perfil Lipídico", "Glicemia"], "help": "Riesgo coronario."},
    "Tercera Edad": {"items": ["Perfil Bioquímico", "Hemograma", "Vitamina D"], "help": "Adulto mayor."},
    "Diabetes/HTA": {"items": ["Hemoglobina Glicosilada", "Microalbuminuria", "Creatinina"], "help": "Pacientes crónicos."}
}

def conectar_db():
    try:
        if "postgres" in st.secrets:
            return psycopg2.connect(**st.secrets["postgres"])
    except: return None

def buscar_paciente_historial(doc_id):
    conn = conectar_db()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT folio, nombre_paciente, total_fonasa FROM cotizaciones WHERE documento_id = %s ORDER BY fecha_cotizacion DESC LIMIT 1", (doc_id,))
            res = cur.fetchone()
            conn.close()
            return res
        except: return None
    return None

def guardar_en_db(folio, nombre, t_doc, doc_id, f_nac, t_f, t_c, t_pg, t_pp):
    conn = conectar_db()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO cotizaciones (id, folio, nombre_paciente, tipo_documento, documento_id, 
                fecha_nacimiento, fecha_cotizacion, total_fonasa, total_copago, total_particular_gral, total_particular_pref
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (str(uuid.uuid4()), folio, nombre, t_doc, doc_id, f_nac, datetime.now(), int(t_f), int(t_c), int(t_pg), int(t_pp)))
            conn.commit(); conn.close()
            return True
        except: return False
    return False

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

if os.path.exists("logo_vec.svg"):
    c1, c2, c3 = st.columns([1.5, 1, 1.5])
    with c2: st.image("logo_vec.svg", width=90)

st.markdown("<h2 style='text-align: center; margin-bottom: 0;'>Cotizador de exámenes</h2>", unsafe_allow_html=True)
st.markdown("""<div class="sucursal-info"><b>Vitacura:</b> Av. Vitacura #8620 | <b>Los Tribunales:</b> Calle Los Tribunales #1268<br>Policlínico Tabancura - Área de toma de muestras</div>""", unsafe_allow_html=True)

if 'paso' not in st.session_state: st.session_state.paso = 'busqueda'
if 'seleccionados' not in st.session_state: st.session_state.seleccionados = []
if 'pdf_generado' not in st.session_state: st.session_state.pdf_generado = False

if st.session_state.paso == 'busqueda':
    with st.container():
        st.markdown("##### 🔍 Consulta de Paciente")
        col_doc1, col_doc2 = st.columns([1, 2])
        tipo_doc_busq = col_doc1.radio("Documento", ["RUT Nacional", "Pasaporte / ID"], horizontal=True)
        doc_id_input = col_doc2.text_input("Ingresa tu rut (12345678-k): ")
        if st.button("Ingreso"):
            if doc_id_input:
                st.session_state.doc_id_sesion = doc_id_input
                st.session_state.tipo_doc_sesion = tipo_doc_busq
                hist = buscar_paciente_historial(doc_id_input)
                if hist:
                    st.session_state.es_paciente_nuevo = False
                    st.session_state.nombre_sugerido = hist[1]
                    st.session_state.prevision_sugerida = "Fonasa" if hist[2] > 0 else "Particular"
                else:
                    st.session_state.es_paciente_nuevo = True
                    st.session_state.nombre_sugerido = ""
                    st.session_state.prevision_sugerida = "Seleccione..."
                st.session_state.paso = 'formulario'
                st.rerun()

elif st.session_state.paso == 'formulario':
    if not st.session_state.pdf_generado:
        st.button("⬅️ Volver", on_click=lambda: st.session_state.update({"paso": "busqueda"}))

    if st.session_state.es_paciente_nuevo: st.warning("🆕 Paciente Nuevo")
    else: st.success("✅ Ya te encuentras registrado en nuestra base de datos.")

    df_aranceles = cargar_datos()
    if df_aranceles is not None:
        with st.container():
            st.markdown("##### 👤 Datos del Paciente")
            nombre_p = st.text_input("Nombre Completo", value=st.session_state.nombre_sugerido, disabled=st.session_state.pdf_generado)
            f1, f2 = st.columns(2)
            fecha_nac = f1.date_input("Fecha de Nacimiento", value=date(1990, 1, 1), min_value=date(1900, 1, 1), disabled=st.session_state.pdf_generado)
            edad_actual = calcular_edad(fecha_nac)
            st.info(f"Edad: {edad_actual} años")
            prevision = f2.selectbox("Previsión", ["Seleccione...", "Particular", "Fonasa"], index=(2 if st.session_state.get('prevision_sugerida')=="Fonasa" else (1 if st.session_state.get('prevision_sugerida')=="Particular" else 0)), disabled=st.session_state.pdf_generado)

        if not st.session_state.pdf_generado:
            with st.container():
                st.markdown("##### 📦 Selecciona un paquete de exámenes:")
                p_cols = st.columns(4)
                for i, (p_name, p_data) in enumerate(PACKS.items()):
                    with p_cols[i]:
                        st.markdown('<div class="pill-button">', unsafe_allow_html=True)
                        if st.button(p_name, key=f"pk_{i}"):
                            actuales = list(st.session_state.seleccionados)
                            for kw in p_data["items"]:
                                match = df_aranceles[df_aranceles["Nombre"].str.contains(kw, case=False, na=False)]
                                if not match.empty:
                                    it = match.iloc[0]["busqueda"]
                                    if it not in actuales: actuales.append(it)
                            st.session_state.seleccionados = actuales
                            st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown("##### ➕ o selecciona exámenes de manera individual: ")
                st.session_state.seleccionados = st.multiselect("Añadir individualmente:", options=df_aranceles["busqueda"].unique().tolist(), default=st.session_state.seleccionados)

        if st.session_state.seleccionados and prevision != "Seleccione...":
            df_sel = df_aranceles[df_aranceles["busqueda"].isin(st.session_state.seleccionados)].copy()
            t_f, t_c, t_pg, t_pp = df_sel["Valor bono Fonasa"].sum(), df_sel["Valor copago"].sum(), df_sel["Valor particular General"].sum(), df_sel["Valor particular preferencial"].sum()
            
            st.markdown("---")
            res_c = ["Código", "Nombre", "Valor bono Fonasa", "Valor copago"] if prevision == "Fonasa" else ["Código", "Nombre", "Valor particular General", "Valor particular preferencial"]
            ren_c = {"Valor bono Fonasa": "Bono", "Valor copago": "Copago"} if prevision == "Fonasa" else {"Valor particular General": "P. Gral", "Valor particular preferencial": "P. Pref"}
            st.dataframe(df_sel[res_c].rename(columns=ren_c), use_container_width=True, hide_index=True)

            m1, m2 = st.columns(2)
            if prevision == "Fonasa":
                m1.metric("Total Bono Fonasa", f"${t_f:,.0f}"); m2.metric("Total Copago a Pagar", f"${t_c:,.0f}")
            else:
                m1.metric("Total Particular General", f"${t_pg:,.0f}"); m2.metric("Total Particular Preferencial", f"${t_pp:,.0f}")

            if not st.session_state.pdf_generado:
                c_acc1, c_acc2 = st.columns(2)
                with c_acc1:
                    if st.button("🚀 Guardar y Generar PDF"):
                        folio = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
                        if guardar_en_db(folio, nombre_p, st.session_state.tipo_doc_sesion, st.session_state.doc_id_sesion, fecha_nac, t_f, t_c, t_pg, t_pp):
                            timestamp_emision = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                            pdf = FPDF()
                            pdf.add_page()
                            
                            if os.path.exists("logo_vec.svg"):
                                pdf.image("logo_vec.svg", x=10, y=8, w=30)
                            
                            pdf.set_font("Arial", 'B', 10); pdf.cell(0, 10, f"FOLIO: {folio}", ln=1, align='R')
                            pdf.set_font("Arial", 'I', 8); pdf.cell(0, 5, f"Fecha de Emisión: {timestamp_emision}", ln=1, align='R') # Timestamp añadido
                            
                            pdf.set_text_color(0); pdf.set_font("Arial", 'B', 14); pdf.ln(10)
                            pdf.cell(0, 10, "Cotización de exámenes de Toma de muestras", ln=True, align='C'); pdf.ln(10)
                            
                            pdf.set_font("Arial", '', 10)
                            pdf.cell(0, 6, f"Paciente: {nombre_p}", ln=1)
                            pdf.cell(0, 6, f"Documento: {st.session_state.doc_id_sesion} | Edad: {edad_actual} años", ln=1)
                            pdf.cell(0, 6, f"Previsión: {prevision}", ln=1); pdf.ln(5)
                            
                            h3, h4 = ("Bono Fonasa", "Copago") if prevision == "Fonasa" else ("P. General", "P. Pref")
                            pdf.set_fill_color(2, 112, 249); pdf.set_text_color(255); pdf.set_font("Arial", 'B', 8)
                            w = [25, 75, 45, 45]
                            for i, h in enumerate(["Código", "Examen", h3, h4]): pdf.cell(w[i], 10, h, 1, 0, 'C', True)
                            pdf.ln(); pdf.set_text_color(0); pdf.set_font("Arial", '', 8)
                            for _, r in df_sel.iterrows():
                                pdf.cell(w[0], 8, str(r['Código']), 1, 0, 'C')
                                pdf.cell(w[1], 8, f" {str(r['Nombre'])[:40]}", 1)
                                v1, v2 = (r['Valor bono Fonasa'], r['Valor copago']) if prevision == "Fonasa" else (r['Valor particular General'], r['Valor particular preferencial'])
                                pdf.cell(w[2], 8, f"${v1:,.0f}", 1, 0, 'R'); pdf.cell(w[3], 8, f"${v2:,.0f}", 1, 1, 'R')
                            
                            pdf.set_font("Arial", 'B', 9); pdf.set_fill_color(240, 240, 240)
                            pdf.cell(w[0]+w[1], 10, "TOTAL ESTIMADO", 1, 0, 'R', True)
                            res1, res2 = (t_f, t_c) if prevision == "Fonasa" else (t_pg, t_pp)
                            pdf.cell(w[2], 10, f"${res1:,.0f}", 1, 0, 'R', True); pdf.cell(w[3], 10, f"${res2:,.0f}", 1, 1, 'R', True)

                            pdf.ln(10); pdf.set_font("Arial", 'B', 8); pdf.cell(0, 5, "SUCURSALES Y HORARIOS:", ln=True)
                            pdf.set_font("Arial", '', 7)
                            pdf.cell(0, 4, "- Vitacura: Av. Vitacura #8620. | - Los Tribunales: Calle Los Tribunales #1268.", ln=True)
                            pdf.cell(0, 4, "- Horario toma de muestras: Lunes a Viernes de 08:30 a 11:00 hrs.", ln=True)
                            pdf.ln(2); pdf.set_font("Arial", 'B', 8); pdf.cell(0, 5, "INDICACIONES IMPORTANTES:", ln=True)
                            pdf.set_font("Arial", '', 7); pdf.multi_cell(0, 4, f"- Folio: {folio}\n- Validez: 30 días.\n- (*) El valor total a pagar es estimado.\n- El ayuno no debe superar las 12 horas.\n- PTGO: Con agenda previa.\n- Valores sujetos a confirmación en sucursal al momento de la atención.")

                            path = f"Cot_{folio}.pdf"; pdf.output(path); st.session_state.pdf_path = path; st.session_state.pdf_generado = True; st.rerun()
                with c_acc2:
                    st.link_button("📅 Agendar Hora de Toma", "https://ff.healthatom.io/FKV7ZY")

        if st.session_state.pdf_generado:
            with st.container():
                st.success("✅ Cotización finalizada con éxito.")
                with open(st.session_state.pdf_path, "rb") as f:
                    st.download_button("🔵 DESCARGAR PDF COTIZACIÓN", f, file_name=f"Cotizacion_{nombre_p}.pdf")
                st.markdown("---")
                cf1, cf2, cf3 = st.columns(3)
                with cf1:
                    if st.button("🔄 Nueva Cotización"): 
                        st.session_state.seleccionados = []; st.session_state.pdf_generado = False; st.rerun()
                with cf2:
                    if st.button("🏠 Inicio"):
                        st.session_state.update({"paso": "busqueda", "pdf_generado": False, "seleccionados": [], "nombre_sugerido": ""})
                        st.rerun()
                with cf3:
                    st.link_button("🌐 policlinicotabancura.cl", "https://www.policlinicotabancura.cl")

st.markdown("<br><br>", unsafe_allow_html=True)
f_col1, f_col2, f_col3 = st.columns(3)
with f_col1:
    st.markdown('<center><a href="javascript:window.location.reload();" class="footer-link">📄 Cotizador</a></center>', unsafe_allow_html=True)
with f_col2:
    st.markdown('<center><a href="https://www.policlinicotabancura.cl" target="_blank" class="footer-link">🌐 Sitio Web</a></center>', unsafe_allow_html=True)
with f_col3:
    st.markdown('<center><a href="https://www.instagram.com/policlinicotabancura/" target="_blank" class="footer-link">📸 Instagram</a></center>', unsafe_allow_html=True)

st.markdown("<p style='text-align: center; color: #aaa; font-size: 0.8rem; margin-top: 10px;'>© 2026 Policlínico Tabancura</p>", unsafe_allow_html=True)