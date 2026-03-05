import streamlit as st
import pandas as pd
from fpdf import FPDF
import os
import secrets
import string
import uuid
from datetime import date, datetime
import psycopg2

# 1. Configuración de página y CSS (MANTENIENDO EL DISEÑO PERFECTO CON NUEVOS COLORES)
st.set_page_config(
    page_title="Cotizador Policlínico Tabancura", 
    page_icon="🏥", 
    layout="wide" 
)

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .block-container {
        max-width: 850px !important;
        padding-top: 1.5rem !important;
    }
    .logo-wrapper {
        display: flex;
        justify-content: center;
        margin-bottom: 1rem;
    }
    .exam-card {
        background-color: white;
        border: 1px solid #eef2f6;
        border-radius: 12px;
        padding: 15px 20px;
        margin-bottom: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02), 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    .exam-title {
        font-size: 0.95rem;
        font-weight: 600;
        color: #2d3748;
        margin-bottom: 10px;
        line-height: 1.4;
    }
    span[data-baseweb="tag"] {
        background-color: #0270f9 !important;
    }
    
    /* ESTILO DE BOTONES PRINCIPALES: AZUL CON LETRAS BLANCAS */
    .stButton>button, .stDownloadButton>button, .stLinkButton>a {
        background-color: #0270f9 !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        border: none !important;
        transition: background-color 0.3s;
    }
    
    .stButton>button:hover, .stDownloadButton>button:hover, .stLinkButton>a:hover {
        background-color: #0156c2 !important;
        color: white !important;
    }

    /* Botón Eliminar (Se mantiene rojo para contraste de acción negativa) */
    .btn-del-box > div > button {
        background-color: #ffffff !important;
        color: #ff4b4b !important;
        border: 1px solid #ff4b4b !important;
        height: 38px !important;
        width: 38px !important;
        border-radius: 8px !important;
        font-weight: bold !important;
    }
    .btn-del-box > div > button:hover {
        background-color: #ff4b4b !important;
        color: white !important;
    }
    
    .sucursal-info {
        text-align: center;
        color: #718096;
        font-size: 0.85rem;
        margin-bottom: 2rem;
    }
    .footer-link {
        color: #0270f9 !important;
        text-decoration: none !important;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Funciones Core ---
def calcular_edad(fecha_nacimiento):
    today = date.today()
    return today.year - fecha_nacimiento.year - ((today.month, today.day) < (fecha_nacimiento.month, fecha_nacimiento.day))

PACKS = {
    "Preventivo Hombre": {"items": ["Hemograma", "VHS", "Perfil Lipídico", "Creatinina", "Electrolitos", "Electrocardiograma", "Glucosa", "Hemoglobina glicosilada", "TSH", "VIH", "VDRL", "VHC", "Perfil Hepático", "Hepatitis B"]},
    "Cardiovascular": {"items": ["Electrocardiograma", "Perfil Lipídico", "Glicemia"]},
    "Tercera Edad": {"items": ["Perfil Bioquímico", "Hemograma", "Vitamina D"]},
    "Diabetes/HTA": {"items": ["Hemoglobina Glicosilada", "Microalbuminuria", "Creatinina"]}
}

def conectar_db():
    host = os.environ.get("POSTGRES_HOST")
    if host:
        try:
            return psycopg2.connect(
                host=host, database=os.environ.get("POSTGRES_DATABASE"),
                user=os.environ.get("POSTGRES_USER"), password=os.environ.get("POSTGRES_PASSWORD"),
                port=os.environ.get("POSTGRES_PORT")
            )
        except: return None
    try:
        if "postgres" in st.secrets: return psycopg2.connect(**st.secrets["postgres"])
    except: pass
    return None

def buscar_paciente_historial(doc_id):
    conn = conectar_db()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT folio, nombre_paciente, total_fonasa FROM cotizaciones WHERE documento_id = %s ORDER BY fecha_cotizacion DESC LIMIT 1", (doc_id,))
            res = cur.fetchone(); conn.close(); return res
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
            conn.commit(); conn.close(); return True
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

# --- UI Principal ---
if os.path.exists("logo_vec.svg"):
    st.markdown('<div class="logo-wrapper">', unsafe_allow_html=True)
    st.image("logo_vec.svg", width=100)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center; margin-bottom: 0;'>Cotizador de exámenes</h2>", unsafe_allow_html=True)
st.markdown("""<div class="sucursal-info">Vitacura: Av. Vitacura #8620 | Los Tribunales: Calle Los Tribunales #1268<br><b>Policlínico Tabancura</b></div>""", unsafe_allow_html=True)

if 'paso' not in st.session_state: st.session_state.paso = 'busqueda'
if 'seleccionados' not in st.session_state: st.session_state.seleccionados = []
if 'cantidades' not in st.session_state: st.session_state.cantidades = {}
if 'pdf_generado' not in st.session_state: st.session_state.pdf_generado = False

# PASO 1: BÚSQUEDA
if st.session_state.paso == 'busqueda':
    with st.container():
        st.markdown("##### 🔍 Consulta de Paciente")
        tipo_doc_busq = st.radio("Documento", ["RUT Nacional", "Pasaporte / ID"], horizontal=True)
        doc_id_input = st.text_input("Ingresa tu identificación:")
        if st.button("Ingresar", use_container_width=True):
            if doc_id_input:
                st.session_state.doc_id_sesion = doc_id_input
                st.session_state.tipo_doc_sesion = tipo_doc_busq
                hist = buscar_paciente_historial(doc_id_input)
                if hist:
                    st.session_state.es_paciente_nuevo, st.session_state.nombre_sugerido = False, hist[1]
                    st.session_state.prevision_sugerida = "Fonasa" if hist[2] > 0 else "Particular"
                else:
                    st.session_state.es_paciente_nuevo, st.session_state.nombre_sugerido = True, ""
                    st.session_state.prevision_sugerida = "Seleccione..."
                st.session_state.paso = 'formulario'; st.rerun()

# PASO 2: FORMULARIO
elif st.session_state.paso == 'formulario':
    if not st.session_state.pdf_generado:
        # Botón Volver (Mantenemos estructura azul/blanco)
        st.button("⬅️ Volver", on_click=lambda: st.session_state.update({"paso": "busqueda"}))

    df_aranceles = cargar_datos()
    if df_aranceles is not None:
        with st.container():
            st.markdown("##### 👤 Datos del Paciente")
            nombre_p = st.text_input("Nombre Completo", value=st.session_state.nombre_sugerido, disabled=st.session_state.pdf_generado)
            f1, f2 = st.columns(2)
            fecha_nac = f1.date_input("Fecha de Nacimiento", value=date(1990, 1, 1), disabled=st.session_state.pdf_generado)
            prevision = f2.selectbox("Previsión", ["Seleccione...", "Particular", "Fonasa"], index=(2 if st.session_state.get('prevision_sugerida')=="Fonasa" else (1 if st.session_state.get('prevision_sugerida')=="Particular" else 0)), disabled=st.session_state.pdf_generado)

        if not st.session_state.pdf_generado:
            with st.container():
                st.markdown("##### 📦 Paquetes de exámenes")
                p_cols = st.columns(4)
                for i, (p_name, p_data) in enumerate(PACKS.items()):
                    with p_cols[i]:
                        # Botones de paquetes (Azules/Blancos)
                        if st.button(p_name, key=f"pk_{i}", use_container_width=True):
                            for kw in p_data["items"]:
                                match = df_aranceles[df_aranceles["Nombre"].str.contains(kw, case=False, na=False)]
                                if not match.empty:
                                    it = match.iloc[0]["busqueda"]
                                    if it not in st.session_state.seleccionados:
                                        st.session_state.seleccionados.append(it)
                                        st.session_state.cantidades[it] = 1
                            st.rerun()
                st.session_state.seleccionados = st.multiselect("➕ Selección Individual:", options=df_aranceles["busqueda"].unique().tolist(), default=st.session_state.seleccionados)

        if st.session_state.seleccionados and prevision != "Seleccione...":
            st.markdown("##### 🔢 Ajustar Cantidades")
            for item in list(st.session_state.seleccionados):
                if item not in st.session_state.cantidades: st.session_state.cantidades[item] = 1
                
                with st.container():
                    st.markdown(f'<div class="exam-card"><div class="exam-title">{item}</div>', unsafe_allow_html=True)
                    # MANTENIENDO LA ALINEACIÓN PERFECTA
                    c_sp, c_qty, c_del = st.columns([3, 1.2, 0.4], vertical_alignment="center")
                    with c_qty:
                        st.session_state.cantidades[item] = st.number_input(f"Q_{item}", min_value=1, max_value=20, value=st.session_state.cantidades.get(item, 1), key=f"q_{item}", label_visibility="collapsed", disabled=st.session_state.pdf_generado)
                    with c_del:
                        st.markdown('<div class="btn-del-box">', unsafe_allow_html=True)
                        if st.button("✖", key=f"del_{item}", disabled=st.session_state.pdf_generado):
                            st.session_state.seleccionados.remove(item)
                            if item in st.session_state.cantidades: del st.session_state.cantidades[item]
                            st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

            # Cálculos
            df_sel = df_aranceles[df_aranceles["busqueda"].isin(st.session_state.seleccionados)].copy()
            df_sel["Cant"] = df_sel["busqueda"].map(st.session_state.cantidades).fillna(1).astype(int)
            
            t_f = (df_sel["Valor bono Fonasa"] * df_sel["Cant"]).sum()
            t_c = (df_sel["Valor copago"] * df_sel["Cant"]).sum()
            t_pg = (df_sel["Valor particular General"] * df_sel["Cant"]).sum()
            t_pp = (df_sel["Valor particular preferencial"] * df_sel["Cant"]).sum()

            st.markdown("---")
            df_disp = df_sel.copy()
            res_c = ["Cant", "Nombre", "Valor bono Fonasa", "Valor copago"] if prevision == "Fonasa" else ["Cant", "Nombre", "Valor particular General", "Valor particular preferencial"]
            for col in res_c[2:]: df_disp[col] = df_disp[col] * df_disp["Cant"]
            st.dataframe(df_disp[res_c], use_container_width=True, hide_index=True)

            m1, m2 = st.columns(2)
            if prevision == "Fonasa":
                m1.metric("Total Bono", f"${t_f:,.0f}"); m2.metric("Total Copago a Pagar", f"${t_c:,.0f}")
            else:
                m1.metric("Total P. Gral", f"${t_pg:,.0f}"); m2.metric("Total P. Pref", f"${t_pp:,.0f}")

            if not st.session_state.pdf_generado:
                # ANTES DE GENERAR: Solo botón PDF (Azul/Blanco)
                if st.button("🚀 Generar PDF", use_container_width=True):
                    folio = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
                    if guardar_en_db(folio, nombre_p, st.session_state.tipo_doc_sesion, st.session_state.doc_id_sesion, fecha_nac, t_f, t_c, t_pg, t_pp):
                        timestamp_emision = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                        pdf = FPDF()
                        pdf.add_page()
                        # Restauración de toda la información en el PDF (MANTENIDO)
                        if os.path.exists("logo_vec.svg"): pdf.image("logo_vec.svg", x=10, y=8, w=15)
                        pdf.set_font("Arial", 'B', 10); pdf.cell(0, 10, f"FOLIO: {folio}", ln=1, align='R')
                        pdf.set_font("Arial", 'I', 8); pdf.cell(0, 5, f"Fecha de Emisión: {timestamp_emision}", ln=1, align='R')
                        pdf.set_font("Arial", 'B', 14); pdf.ln(10); pdf.cell(0, 10, "Cotización de exámenes", ln=True, align='C'); pdf.ln(10)
                        
                        pdf.set_font("Arial", 'B', 10); pdf.cell(0, 6, "DATOS DEL PACIENTE:", ln=1); pdf.set_font("Arial", '', 10)
                        pdf.cell(0, 6, f"Nombre: {nombre_p}", ln=1)
                        pdf.cell(0, 6, f"Documento: {st.session_state.doc_id_sesion}", ln=1)
                        pdf.cell(0, 6, f"Edad: {calcular_edad(fecha_nac)} años", ln=1)
                        pdf.cell(0, 6, f"Previsión: {prevision}", ln=1); pdf.ln(5)
                        
                        h3, h4 = ("Bono Tot", "Copago Tot") if prevision == "Fonasa" else ("P. Gral Tot", "P. Pref Tot")
                        pdf.set_fill_color(2, 112, 249); pdf.set_text_color(255); pdf.set_font("Arial", 'B', 8)
                        w = [12, 88, 15, 37.5, 37.5]
                        for i, h in enumerate(["Cant", "Examen", "Cod", h3, h4]): pdf.cell(w[i], 10, h, 1, 0, 'C', True)
                        pdf.ln(); pdf.set_text_color(0); pdf.set_font("Arial", '', 8)
                        for _, r in df_sel.iterrows():
                            pdf.cell(w[0], 8, str(int(r['Cant'])), 1, 0, 'C')
                            pdf.cell(w[1], 8, f" {str(r['Nombre'])[:45]}", 1)
                            pdf.cell(w[2], 8, str(r['Código']), 1, 0, 'C')
                            v1, v2 = (r['Valor bono Fonasa'], r['Valor copago']) if prevision == "Fonasa" else (r['Valor particular General'], r['Valor particular preferencial'])
                            pdf.cell(w[3], 8, f"${(v1*r['Cant']):,.0f}", 1, 0, 'R'); pdf.cell(w[4], 8, f"${(v2*r['Cant']):,.0f}", 1, 1, 'R')
                        
                        pdf.set_font("Arial", 'B', 9); pdf.set_fill_color(240, 240, 240)
                        pdf.cell(w[0]+w[1]+w[2], 10, "TOTAL ESTIMADO A PAGAR", 1, 0, 'R', True)
                        res1, res2 = (t_f, t_c) if prevision == "Fonasa" else (t_pg, t_pp)
                        pdf.cell(w[3], 10, f"${res1:,.0f}", 1, 0, 'R', True); pdf.cell(w[4], 10, f"${res2:,.0f}", 1, 1, 'R', True)
                        
                        pdf.ln(10); pdf.set_font("Arial", 'B', 8); pdf.cell(0, 5, "SUCURSALES Y CONTACTO:", ln=True)
                        pdf.set_font("Arial", '', 7); pdf.cell(0, 4, "- Av. Vitacura #8620 | Calle Los Tribunales #1268", ln=True)
                        pdf.cell(0, 4, "- Sitio Web: www.policlinicotabancura.cl", ln=True)
                        pdf.ln(2); pdf.set_font("Arial", 'B', 8); pdf.cell(0, 5, "INDICACIONES IMPORTANTES:", ln=True)
                        pdf.set_font("Arial", '', 7); pdf.multi_cell(0, 4, f"- Folio: {folio}\n- Validez de la cotización: 30 días.\n- (*) El valor a pagar no considera seguros complementarios.\n- Si el examen cotizado tiene costo $0, el valor del exámen SÓLO se encuentra en previsión Fonasa.\n- El ayuno no debe superar las 12 horas.\n- Para pruebas PTGO (Curva de Glucosa/Insulina): Sólo con agenda previa a las 08:30am.\n- Valores sujetos a confirmación en sucursal al momento de la atención.\n- Si el paciente es diabético, debe notificar en recepción antes de su atención.")
                        
                        path = f"Cot_{folio}.pdf"; pdf.output(path); st.session_state.pdf_path = path; st.session_state.pdf_generado = True; st.rerun()

        if st.session_state.pdf_generado:
            st.success("✅ Cotización finalizada con éxito.")
            # DESPUÉS DE GENERAR: Botón Descargar (Azul/Blanco)
            with open(st.session_state.pdf_path, "rb") as f: st.download_button("🔵 DESCARGAR PDF COTIZACIÓN", f, file_name=f"Cotizacion_{nombre_p}.pdf", use_container_width=True)
            
            # NUEVA UBICACIÓN: Botón Agendamiento debajo de Descargar (Azul/Blanco)
            st.link_button("📅 Agenda Toma de Muestras", "https://ff.healthatom.io/FKV7ZY", use_container_width=True)
            
            st.markdown("---")
            # Botones finales de navegación (Azules/Blancos)
            cf1, cf2, cf3 = st.columns(3)
            with cf1:
                if st.button("🔄 Nueva Cotización", use_container_width=True): st.session_state.update({"seleccionados": [], "cantidades": {}, "pdf_generado": False}); st.rerun()
            with cf2:
                if st.button("🏠 Inicio", use_container_width=True): st.session_state.update({"paso": "busqueda", "pdf_generado": False, "seleccionados": [], "cantidades": {}}); st.rerun()
            with cf3: st.link_button("🌐 policlinicotabancura.cl", "https://www.policlinicotabancura.cl", use_container_width=True)

st.markdown("<br><br>", unsafe_allow_html=True)
f_col1, f_col2, f_col3 = st.columns(3)
with f_col1: st.markdown('<center><a href="#" class="footer-link">📄 Cotizador</a></center>', unsafe_allow_html=True)
with f_col2: st.markdown('<center><a href="https://www.policlinicotabancura.cl" class="footer-link">🌐 Sitio Web</a></center>', unsafe_allow_html=True)
with f_col3: st.markdown('<center><a href="https://www.instagram.com/politabancura/" class="footer-link">📸 Instagram</a></center>', unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #aaa; font-size: 0.8rem; margin-top: 10px;'>© 2026 Policlínico Tabancura</p>", unsafe_allow_html=True)