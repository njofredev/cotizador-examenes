import streamlit as st
import pandas as pd
from fpdf import FPDF
import os
import secrets
import string
import uuid
from datetime import date, datetime
import psycopg2

# 1. Configuración de página y CSS
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
        padding-top: 2rem !important;
    }
    .logo-wrapper {
        display: flex;
        justify-content: center;
        margin-bottom: 1rem;
        padding-top: 2rem;
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

    .nota-fonasa {
        color: #718096;
        font-size: 0.85rem;
        font-style: italic;
        margin-top: -10px;
        margin-bottom: 15px;
    }

    [data-testid="stDataFrame"] td:nth-child(2) p {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 350px;
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
    col_l, col_c, col_r = st.columns([1, 0.4, 1])
    with col_c:
        st.markdown('<div class="logo-wrapper">', unsafe_allow_html=True)
        st.image("logo_vec.svg", width=100)
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center; margin-bottom: 0;'>Cotizador digital de exámenes</h2>", unsafe_allow_html=True)
st.divider()

if 'paso' not in st.session_state: st.session_state.paso = 'busqueda'
if 'seleccionados' not in st.session_state: st.session_state.seleccionados = []
if 'cantidades' not in st.session_state: st.session_state.cantidades = {}
if 'pdf_generado' not in st.session_state: st.session_state.pdf_generado = False
if 'ms_key' not in st.session_state: st.session_state.ms_key = 0

# PASO 1: BÚSQUEDA
if st.session_state.paso == 'busqueda':
    with st.container():
        st.markdown("##### 🔍 Ingresa tu rut o documento extranjero")
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
        st.button("⬅️ Volver", on_click=lambda: st.session_state.update({"paso": "busqueda"}))

    df_aranceles = cargar_datos()
    if df_aranceles is not None:
        df_filtrado = df_aranceles.copy()

        with st.container():
            st.markdown("#### 👤 Datos del Paciente")
            nombre_p = st.text_input("Nombre Completo", value=st.session_state.nombre_sugerido, disabled=st.session_state.pdf_generado)
            f1, f2 = st.columns(2)
            fecha_nac = f1.date_input("Fecha de Nacimiento", value=date(1990, 1, 1), disabled=st.session_state.pdf_generado)
            prevision = f2.selectbox("Previsión", ["Seleccione...", "Particular", "Fonasa"], index=(2 if st.session_state.get('prevision_sugerida')=="Fonasa" else (1 if st.session_state.get('prevision_sugerida')=="Particular" else 0)), disabled=st.session_state.pdf_generado)

        if not st.session_state.pdf_generado:
            with st.container():
                st.markdown("#### 📦 Paquetes de exámenes")
                p_cols = st.columns(4)
                for i, (p_name, p_data) in enumerate(PACKS.items()):
                    with p_cols[i]:
                        if st.button(p_name, key=f"pk_{i}", use_container_width=True):
                            for kw in p_data["items"]:
                                match = df_filtrado[df_filtrado["Nombre"].str.contains(kw, case=False, na=False)]
                                if not match.empty:
                                    it = match.iloc[0]["busqueda"]
                                    if it not in st.session_state.seleccionados:
                                        st.session_state.seleccionados.append(it)
                                        st.session_state.cantidades[it] = 1
                            st.session_state.ms_key += 1
                            st.rerun()
                
                def on_ms_change():
                    st.session_state.seleccionados = st.session_state[f"ms_{st.session_state.ms_key}"]

                st.multiselect(
                    "➕ Aquí puedes agregar o quitar exámenes de manera individual:", 
                    options=df_filtrado["busqueda"].unique().tolist(), 
                    default=[s for s in st.session_state.seleccionados if s in df_filtrado["busqueda"].values],
                    key=f"ms_{st.session_state.ms_key}",
                    on_change=on_ms_change
                )

        if st.session_state.seleccionados and prevision != "Seleccione...":
            st.markdown("#### 🔢 Exámenes seleccionados para cotizar")
            st.markdown("##### 🔎 Puedes agregar o quitar exámenes")
            for item in list(st.session_state.seleccionados):
                if item not in st.session_state.cantidades: st.session_state.cantidades[item] = 1
                
                with st.container():
                    st.markdown(f'<div class="exam-card"><div class="exam-title">{item}</div>', unsafe_allow_html=True)
                    c_sp, c_qty, c_del = st.columns([3, 1.2, 0.4], vertical_alignment="center")
                    with c_qty:
                        st.session_state.cantidades[item] = st.number_input(f"Q_{item}", min_value=1, max_value=20, value=st.session_state.cantidades.get(item, 1), key=f"q_{item}", label_visibility="collapsed", disabled=st.session_state.pdf_generado)
                    with c_del:
                        st.markdown('<div class="btn-del-box">', unsafe_allow_html=True)
                        if st.button("✖", key=f"del_{item}", disabled=st.session_state.pdf_generado):
                            st.session_state.seleccionados.remove(item)
                            if item in st.session_state.cantidades: del st.session_state.cantidades[item]
                            st.session_state.ms_key += 1
                            st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

            # --- Lógica de Negocio (Fallback) ---
            df_sel = df_filtrado[df_filtrado["busqueda"].isin(st.session_state.seleccionados)].copy()
            df_sel["Cant"] = df_sel["busqueda"].map(st.session_state.cantidades).fillna(1).astype(int)
            
            df_sel["Valor Fonasa Final"] = df_sel["Valor bono Fonasa"]
            df_sel["Valor Copago Final"] = df_sel.apply(lambda r: r["Valor copago"] if r["Valor bono Fonasa"] > 0 else r["Valor particular General"], axis=1)
            
            t_f = (df_sel["Valor Fonasa Final"] * df_sel["Cant"]).sum()
            t_c = (df_sel["Valor Copago Final"] * df_sel["Cant"]).sum()
            t_pg = (df_sel["Valor particular General"] * df_sel["Cant"]).sum()
            t_pp = (df_sel["Valor particular preferencial"] * df_sel["Cant"]).sum()

            st.markdown("---")
            df_disp = df_sel.copy()
            res_c = ["Cant", "Nombre", "Fonasa (Tot)", "Copago (Tot)"] if prevision == "Fonasa" else ["Cant", "Nombre", "P.Gral (Tot)", "P.Pref (Tot)"]
            
            if prevision == "Fonasa":
                df_disp["Fonasa (Tot)"] = df_disp["Valor Fonasa Final"] * df_disp["Cant"]
                df_disp["Copago (Tot)"] = df_disp["Valor Copago Final"] * df_disp["Cant"]
            else:
                df_disp["P.Gral (Tot)"] = df_disp["Valor particular General"] * df_disp["Cant"]
                df_disp["P.Pref (Tot)"] = df_disp["Valor particular preferencial"] * df_disp["Cant"]

            st.dataframe(
                df_disp[res_c], 
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "Cant": st.column_config.NumberColumn(width="small"),
                    "Nombre": st.column_config.TextColumn(width="large"),
                    res_c[2]: st.column_config.NumberColumn(format="$%d", width="medium"),
                    res_c[3]: st.column_config.NumberColumn(format="$%d", width="medium")
                }
            )

            m1, m2 = st.columns(2)
            if prevision == "Fonasa":
                m1.metric("Total Bono", f"${t_f:,.0f}"); m2.metric("Total Copago a Pagar", f"${t_c:,.0f}")
                # NUEVA NOTA SOLICITADA
                st.markdown('<p class="nota-fonasa">Si el exámen cotizado no es cubierto por Fonasa, el valor a pagar corresponde a la segunda columna de Total calculada.</p>', unsafe_allow_html=True)
            else:
                m1.metric("Total P. Gral", f"${t_pg:,.0f}"); m2.metric("Total P. Pref", f"${t_pp:,.0f}")

            if not st.session_state.pdf_generado:
                if st.button("🚀 Generar PDF", use_container_width=True):
                    folio = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
                    if guardar_en_db(folio, nombre_p, st.session_state.tipo_doc_sesion, st.session_state.doc_id_sesion, fecha_nac, t_f, t_c, t_pg, t_pp):
                        timestamp_emision = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                        pdf = FPDF()
                        pdf.add_page()
                        if os.path.exists("logo_vec.svg"): pdf.image("logo_vec.svg", x=10, y=8, w=15)
                        pdf.set_font("Arial", 'B', 10); pdf.cell(0, 10, f"FOLIO: {folio}", ln=1, align='R')
                        pdf.set_font("Arial", 'I', 8); pdf.cell(0, 5, f"Fecha de Emisión: {timestamp_emision}", ln=1, align='R')
                        pdf.set_font("Arial", 'B', 14); pdf.ln(10); pdf.cell(0, 10, "Cotización digital de exámenes", ln=True, align='C'); pdf.ln(10)
                        
                        pdf.set_font("Arial", 'B', 10); pdf.cell(0, 6, "DATOS DEL PACIENTE:", ln=1); pdf.set_font("Arial", '', 10)
                        pdf.cell(0, 6, f"Nombre: {nombre_p}", ln=1)
                        pdf.cell(0, 6, f"Documento: {st.session_state.doc_id_sesion}", ln=1)
                        pdf.cell(0, 6, f"Edad: {calcular_edad(fecha_nac)} años", ln=1)
                        pdf.cell(0, 6, f"Previsión: {prevision}", ln=1); pdf.ln(5)
                        
                        h3, h4 = ("Valor Fonasa", "Copago o Valor a pagar") if prevision == "Fonasa" else ("Valor Gral.", "Valor Pref.")
                        pdf.set_fill_color(2, 112, 249); pdf.set_text_color(255); pdf.set_font("Arial", 'B', 8)
                        w = [20, 80, 15, 37.5, 37.5]
                        for i, h in enumerate(["Cod", "Examen", "Cant", h3, h4]): pdf.cell(w[i], 10, h, 1, 0, 'C', True)
                        pdf.ln(); pdf.set_text_color(0); pdf.set_font("Arial", '', 8)
                        
                        for _, r in df_sel.iterrows():
                            pdf.cell(w[0], 8, str(r['Código']), 1, 0, 'C')
                            nombre_pdf = str(r['Nombre'])
                            if len(nombre_pdf) > 42: nombre_pdf = nombre_pdf[:40] + "..."
                            pdf.cell(w[1], 8, f" {nombre_pdf}", 1)
                            pdf.cell(w[2], 8, str(int(r['Cant'])), 1, 0, 'C')
                            
                            v1, v2 = (r['Valor Fonasa Final'], r['Valor Copago Final']) if prevision == "Fonasa" else (r['Valor particular General'], r['Valor particular preferencial'])
                            pdf.cell(w[3], 8, f"${(v1*r['Cant']):,.0f}", 1, 0, 'R'); pdf.cell(w[4], 8, f"${(v2*r['Cant']):,.0f}", 1, 1, 'R')
                        
                        pdf.set_font("Arial", 'B', 9); pdf.set_fill_color(240, 240, 240)
                        pdf.cell(w[0]+w[1]+w[2], 10, "TOTAL ESTIMADO A PAGAR", 1, 0, 'R', True)
                        res1, res2 = (t_f, t_c) if prevision == "Fonasa" else (t_pg, t_pp)
                        pdf.cell(w[3], 10, f"${res1:,.0f}", 1, 0, 'R', True); pdf.cell(w[4], 10, f"${res2:,.0f}", 1, 1, 'R', True)
                        
                        pdf.ln(10); pdf.set_font("Arial", 'B', 8); pdf.cell(0, 5, "SUCURSAL LABORATORIO TOMA DE MUESTRAS:", ln=True)
                        pdf.set_font("Arial", '', 7); pdf.cell(0, 4, "- Av. Vitacura #8620, Comuna de Vitacura.", ln=True)
                        pdf.cell(0, 4, "- Sitio Web: www.policlinicotabancura.cl", ln=True)
                        pdf.ln(2); pdf.set_font("Arial", 'B', 8); pdf.cell(0, 5, "INDICACIONES IMPORTANTES:", ln=True)
                        pdf.set_font("Arial", '', 7); pdf.multi_cell(0, 4, f"- Folio: {folio}\n- Validez de la cotización: 30 días.\n- (*) El valor a pagar no considera seguros complementarios. \n- El ayuno no debe superar las 12 horas.\n- Para pruebas PTGO (Curva de Glucosa/Insulina): Sólo con agenda previa a las 08:30am.\n- Valores sujetos a confirmación en sucursal al momento de la atención.\n- Si el paciente es diabético, debe notificar en recepción antes de su atención.\n- Si el examen no es cubierto por Fonasa, aparecerá el valor a pagar en la columna copago.\n- Tu salud es lo primero. Asegura un diagnóstico preciso revisando tus exámenes con nuestro médico general.")
                        
                        path = f"Cot_{folio}.pdf"; pdf.output(path); st.session_state.pdf_path = path; st.session_state.pdf_generado = True; st.rerun()

        if st.session_state.pdf_generado:
            st.success("✅ Cotización finalizada con éxito.")
            with open(st.session_state.pdf_path, "rb") as f: st.download_button("🔵 Descarga aquí tu cotización", f, file_name=f"Cotizacion_{nombre_p}.pdf", use_container_width=True)
            st.link_button("📅 Agenda Toma de Muestras", "https://ff.healthatom.io/FKV7ZY", use_container_width=True)
            st.markdown("---")
            cf1, cf2, cf3 = st.columns(3)
            with cf1:
                if st.button("🔄 Nueva Cotización", use_container_width=True): st.session_state.update({"seleccionados": [], "cantidades": {}, "pdf_generado": False, "ms_key": st.session_state.ms_key + 1}); st.rerun()
            with cf2:
                if st.button("🏠 Inicio", use_container_width=True): st.session_state.update({"paso": "busqueda", "pdf_generado": False, "seleccionados": [], "cantidades": {}, "ms_key": st.session_state.ms_key + 1}); st.rerun()
            with cf3:
                st.link_button("🌐 policlinicotabancura.cl", "https://www.policlinicotabancura.cl", use_container_width=True)

st.markdown("<br><br>", unsafe_allow_html=True)
f_col1, f_col2, f_col3 = st.columns(3)
with f_col1: st.markdown('<center><a href="#" class="footer-link">📄 Cotizador</a></center>', unsafe_allow_html=True)
with f_col2: st.markdown('<center><a href="https://www.policlinicotabancura.cl" class="footer-link">🌐 Sitio Web</a></center>', unsafe_allow_html=True)
with f_col3: st.markdown('<center><a href="https://www.instagram.com/politabancura/" class="footer-link">📸 Instagram</a></center>', unsafe_allow_html=True)
st.divider()
st.markdown("""<div class="sucursal-info"><b>Policlínico Tabancura - Área de toma de muestras</b></br>Sucursal Vitacura: Av. Vitacura #8620 <br> +569 6578 1253 - +569 2933 6740</br></div>""", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #aaa; font-size: 0.8rem; margin-top: 10px;'>© 2026 Policlínico Tabancura</p>", unsafe_allow_html=True)