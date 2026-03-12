import streamlit as st
import pandas as pd
import os
import secrets
import string
from datetime import date

import psycopg2
import uuid
import logging
import json
from utils import obtener_ahora_chile
from pdf_generator import generar_cotizacion_pdf

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- FUNCIONES DE BASE DE DATOS (MIGRADO DESDE database.py) ---
def conectar_db():
    # 1. Prioridad: Variables de entorno directas (lo más robusto en Docker/Coolify)
    try:
        host = os.environ.get("STREAMLIT_POSTGRES_HOST") or os.environ.get("POSTGRES_HOST")
        if host:
            return psycopg2.connect(
                host=host,
                database=os.environ.get("STREAMLIT_POSTGRES_DATABASE") or os.environ.get("POSTGRES_DATABASE", "db_migracion"),
                user=os.environ.get("STREAMLIT_POSTGRES_USER") or os.environ.get("POSTGRES_USER", "postgres"),
                password=os.environ.get("STREAMLIT_POSTGRES_PASSWORD") or os.environ.get("POSTGRES_PASSWORD"),
                port=os.environ.get("STREAMLIT_POSTGRES_PORT") or os.environ.get("POSTGRES_PORT", "5432"),
                connect_timeout=5
            ), None
    except Exception as e_env:
        # Si falló la env var pero había una, retornamos el error
        if os.environ.get("POSTGRES_HOST") or os.environ.get("STREAMLIT_POSTGRES_HOST"):
            return None, f"Error env var: {str(e_env)}"

    # 2. Intento secundario: st.secrets (Local o Streamlit Cloud)
    try:
        # Usamos getattr o un chequeo manual para evitar la excepción ruidosa de Streamlit
        if hasattr(st, "secrets") and "postgres" in st.secrets:
            params = dict(st.secrets["postgres"])
            if "connect_timeout" not in params: params["connect_timeout"] = 5
            return psycopg2.connect(**params), None
    except Exception:
        pass # Ignoramos errores de secrets si no están presentes

    return None, "No se encontraron credenciales válidas en el sistema."

def guardar_en_db(folio, nombre, t_doc, doc_id, f_nac, t_f, t_c, t_pg, t_pp, df_detalle, prevision):
    conn, err = conectar_db()
    if not conn:
        st.error(f"❌ Error de conexión: {err}")
        st.info("💡 Asegúrate de configurar las variables de entorno (POSTGRES_HOST, etc.) en el panel de Coolify.")
        return False
        
    try:
        cur = conn.cursor()
        ahora = obtener_ahora_chile()
        cotizacion_uuid = str(uuid.uuid4())
        
        # 1. Insertar cabecera de cotización
        cur.execute("""INSERT INTO cotizaciones (id, folio, nombre_paciente, tipo_documento, documento_id, 
                    fecha_nacimiento, fecha_cotizacion, total_fonasa, total_copago, total_particular_gral, total_particular_pref, prevision)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", 
                    (cotizacion_uuid, folio, nombre, t_doc, doc_id, f_nac, ahora, int(t_f), int(t_c), int(t_pg), int(t_pp), prevision))
        
        # 2. Insertar detalles
        filas_insertadas = 0
        if df_detalle is not None and not df_detalle.empty:
            for _, row in df_detalle.iterrows():
                try:
                    cant = int(row.get('Cant', 1))
                    if prevision == "Fonasa":
                        val_u = int(row.get('V. Copago', 0) / cant)
                    else:
                        val_u = int(row.get('P. Gral', 0) / cant)
                except Exception:
                    val_u = 0

                cur.execute("""INSERT INTO detalle_cotizaciones (id, folio_cotizacion, codigo_examen, nombre_examen, valor_copago)
                            VALUES (%s, %s, %s, %s, %s)""",
                            (str(uuid.uuid4()), folio, str(row.get('Código', 'n/a')), str(row.get('Nombre', 'Examen')), val_u))
                filas_insertadas += 1
        
        conn.commit()
        logger.info(f"💾 Cotización {folio} guardada exitosamente.")
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        if conn: conn.rollback()
        logger.error(f"Error crítico al guardar en BD: {e}")
        st.error(f"Error al guardar en base de datos: {e}")
        return False

def obtener_datos_paciente(doc_id):
    conn, err = conectar_db()
    if not conn: return None
    try:
        cur = conn.cursor()
        cur.execute("""SELECT nombre_paciente, fecha_nacimiento, prevision 
                    FROM cotizaciones 
                    WHERE documento_id = %s 
                    ORDER BY fecha_cotizacion DESC 
                    LIMIT 1""", (doc_id,))
        res = cur.fetchone()
        cur.close(); conn.close()
        if res:
            return {"nombre": res[0], "fecha_nacimiento": res[1], "prevision": res[2]}
    except Exception as e:
        logger.error(f"Error al buscar paciente: {e}")
    return None
# -------------------------------------------------------------

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
        max-width: 1200px !important;
        padding-top: 2rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    .logo-wrapper {
        display: flex;
        justify-content: center;
        margin-bottom: 1rem;
        padding-top: 1rem;
    }
    
    .exam-row-compact {
        background-color: white;
        border: 1px solid #eef2f6;
        border-radius: 8px;
        padding: 10px 15px;
        margin-bottom: 5px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
        display: flex;
        align-items: center;
    }
    .exam-row-title {
        font-size: 0.9rem;
        font-weight: 600;
        color: #2d3748;
        flex-grow: 1;
        margin-right: 10px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    div[data-testid="stNumberInput"] {
        width: 130px !important;
    }
    div[data-testid="stNumberInput"] button {
        display: flex !important;
    }
    
    span[data-baseweb="tag"] {
        background-color: #0270f9 !important;
    }
    
    .stButton>button, .stDownloadButton>button, .stLinkButton>a {
        background-color: #0270f9;
        color: white !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        border: none !important;
    }
    
    .stButton>button:hover, .stDownloadButton>button:hover, .stLinkButton>a:hover {
        background-color: #0156c2;
    }

    /* Botones de Paquetes de Exámenes (Uniformidad y Alineación) */
    div.stButton button[kind="primary"] {
        min-height: 85px !important;
        padding: 5px 10px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        line-height: 1.2 !important;
        font-size: 0.95rem !important;
        white-space: normal !important;
        word-wrap: break-word !important;
    }

    /* Botón de eliminar en lista de exámenes */
    .btn-del-box button {
        background-color: white !important;
        color: #ff4b4b !important;
        border: 1px solid #ff4b4b !important;
        border-radius: 8px !important;
    }
    .btn-del-box button:hover {
        background-color: #ff4b4b !important;
        color: white !important;
    }

    /* Colores específicos para botones finales (Alta especificidad) */
    div.stButton button[aria-label*="ditar"], 
    div.stButton button[aria-label*="Editar"] {
        background-color: #ff9800 !important;
    }
    
    div.stDownloadButton button[aria-label*="escargar"],
    div.stDownloadButton button[aria-label*="Descargar"] {
        background-color: #28a745 !important;
    }
    
    div.stButton button[aria-label*="nueva"] {
        background-color: #6c757d !important;
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
    
    /* Responsive Adjustments for Mobile */
    @media (max-width: 768px) {
        .block-container {
            padding-top: 1rem !important;
        }
        h2 {
            font-size: 1.5rem !important;
        }
        button[kind="primary"] {
            min-height: 60px !important;
            font-size: 0.85rem !important;
        }
        .exam-row-compact {
            flex-direction: column;
            align-items: flex-start;
        }
        .exam-row-title {
            margin-bottom: 10px;
            white-space: normal;
        }
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def cargar_datos():
    try:
        df = pd.read_excel("aranceles.xlsx")
        df.columns = ["Código", "Nombre", "Valor bono Fonasa", "Valor copago", "Valor particular General", "Valor particular preferencial"]
        df = df.fillna(0)
        df["Código"] = df["Código"].astype(str).str.replace(".0", "", regex=False)
        df["busqueda"] = df["Código"] + " - " + df["Nombre"]
        return df
    except Exception as e: 
        st.error(f"Error cargando los datos: {e}")
        return None

def aplicar_pack(pack, df_filtrado):
    st.session_state.seleccionados = []
    st.session_state.cantidades = {}
    st.session_state.pack_activo = pack["nombre"]
    
    for p_item in pack["examenes"]:
        cod = str(p_item["codigo"]) if p_item["codigo"] else None
        nom = p_item["nombre"]
        qty = p_item["cantidad"]
        
        match = pd.DataFrame()
        if cod and cod != "HOMA":
            match = df_filtrado[df_filtrado["Código"] == cod]
        
        if match.empty:
            match = df_filtrado[df_filtrado["Nombre"].str.contains(nom, case=False, na=False)]
        
        if not match.empty:
            it = match.iloc[0]["busqueda"]
            if it not in st.session_state.seleccionados: st.session_state.seleccionados.append(it)
            st.session_state.cantidades[it] = qty
        else:
            logger.warning(f"No se encontró el examen del pack: {nom} ({cod})")
    
    st.session_state.ms_key += 1
    st.rerun()

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
if 'pack_activo' not in st.session_state: st.session_state.pack_activo = None

# Función para detectar si es móvil desde el servidor
def es_mobile():
    try:
        # Usamos st.context.headers que es la forma moderna y recomendada
        headers = st.context.headers
        if headers:
            ua = headers.get("User-Agent", "").lower()
            return any(m in ua for m in ["android", "iphone", "ipad", "mobile"])
    except:
        pass
    return False

# Cargar packs desde JSON

# Cargar packs desde JSON
if 'packs_json' not in st.session_state:
    try:
        with open("pack.json", "r", encoding="utf-8") as f:
            st.session_state.packs_json = json.load(f)["packs_examenes"]
    except Exception as e:
        st.error(f"Error cargando pack.json: {e}")
        st.session_state.packs_json = []

# Inicialización de datos de paciente para auto-rellenado
if 'p_nombre' not in st.session_state: st.session_state.p_nombre = ""
if 'p_fecha_nac' not in st.session_state: st.session_state.p_fecha_nac = date(1990, 1, 1)
if 'p_prevision' not in st.session_state: st.session_state.p_prevision = "Seleccione..."

if st.session_state.paso == 'busqueda':
    with st.container():
        st.markdown("##### 🔍 Ingresa tu rut o documento extranjero")
        tipo_doc_busq = st.radio("Documento", ["RUT Nacional", "Pasaporte / ID"], horizontal=True, help="Selecciona si tienes RUT chileno o Pasaporte extranjero.")
        doc_id_input = st.text_input("Ingresa tu identificación:", help="Ingresa tu documento (ej: 12345678-9). Si ingresas un RUT existente se cargarán tus datos históricos.")
        if st.button("Ingresar", width="stretch"):
            if doc_id_input:
                st.session_state.doc_id_sesion, st.session_state.tipo_doc_sesion = doc_id_input, tipo_doc_busq
                
                # Intentar recuperar datos del paciente
                datos = obtener_datos_paciente(doc_id_input)
                if datos:
                    st.session_state.p_nombre = datos["nombre"] or ""
                    st.session_state.p_fecha_nac = datos["fecha_nacimiento"] or date(1990, 1, 1)
                    st.session_state.p_prevision = datos["prevision"] if datos["prevision"] in ["Particular", "Fonasa"] else "Seleccione..."
                else:
                    # Resetear si es nuevo o no se encuentra
                    st.session_state.p_nombre = ""
                    st.session_state.p_fecha_nac = date(1990, 1, 1)
                    st.session_state.p_prevision = "Seleccione..."

                st.session_state.paso = 'formulario'; st.rerun()

elif st.session_state.paso == 'formulario':
    if not st.session_state.pdf_generado:
        st.button("⬅️ Volver", on_click=lambda: st.session_state.update({
            "paso": "busqueda", 
            "seleccionados": [], 
            "cantidades": {}, 
            "pack_activo": None
        }))

    df_aranceles = cargar_datos()
    if df_aranceles is not None:
        df_filtrado = df_aranceles.copy()
        
        st.markdown("#### 👤 Datos del paciente")
        st.caption("📝 Por favor completa tu información personal básica antes de seleccionar exámenes.")
        
        nombre_p = st.text_input("Nombre Completo", value=st.session_state.p_nombre, disabled=st.session_state.pdf_generado, help="Ingresa el nombre completo del paciente que se realizará los exámenes.")
        f1, f2 = st.columns(2)
        
        # Sincronizamos con session_state para que persistan los cambios manuales
        fecha_nac = f1.date_input("Fecha de Nacimiento", value=st.session_state.p_fecha_nac, min_value=date(1900, 1, 1), max_value=date(2026, 12, 31), disabled=st.session_state.pdf_generado, help="Esta fecha nos ayuda a calcular tu edad para cotizar exámenes que influyen según el rango etario.")
        
        # Calcular el indice de la prevision
        prev_options = ["Seleccione...", "Particular", "Fonasa"]
        try:
            prev_index = prev_options.index(st.session_state.p_prevision)
        except ValueError:
            prev_index = 0
            
        prevision = f2.selectbox("Previsión", prev_options, index=prev_index, disabled=st.session_state.pdf_generado, help="Selecciona tu previsión de salud actual para calcular correctamente la bonificación o copago.")

        if not st.session_state.pdf_generado:
            # Validacion para mostrar o no los examenes
            if not nombre_p.strip() or prevision == "Seleccione...":
                st.warning("⚠️ Debes rellenar tu Nombre Completo y seleccionar tu Previsión antes de comenzar a cotizar exámenes.")
            else:
                st.markdown("#### 📦 Paquetes de exámenes")
                st.caption("👈 Selecciona uno de nuestros paquetes preventivos para cargar los exámenes automáticamente.")
                
                # Renderizado Responsivo (Lado del Servidor)
                if es_mobile():
                    # Versión Mobile (Dropdown)
                    pack_names = ["Seleccione un paquete..."] + [p["nombre"] for p in st.session_state.packs_json]
                    def_idx = 0
                    if st.session_state.pack_activo:
                        try:
                            def_idx = pack_names.index(st.session_state.pack_activo)
                        except:
                            def_idx = 0
                    
                    selected_p = st.selectbox("Elige un paquete preventivo:", pack_names, index=def_idx, key="mobile_pack_sel")
                    
                    if selected_p != "Seleccione un paquete..." and selected_p != st.session_state.pack_activo:
                        pack_data = next(p for p in st.session_state.packs_json if p["nombre"] == selected_p)
                        aplicar_pack(pack_data, df_filtrado)
                else:
                    # Versión Desktop (Botones)
                    p_cols = st.columns(4)
                    for i, pack in enumerate(st.session_state.packs_json):
                        p_name = pack["nombre"]
                        with p_cols[i % 4]:
                            if st.button(p_name, key=f"pk_desk_{i}", width="stretch", type="primary"):
                                aplicar_pack(pack, df_filtrado)

                # Solo mostramos buscador individual si NO hay un pack activo
                if not st.session_state.pack_activo:
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown("#### 🔍 Exámenes individuales")
                    st.multiselect(
                        "➕ Agregar o quitar exámenes individualmente:", 
                        options=df_filtrado["busqueda"].unique().tolist(), 
                        default=[s for s in st.session_state.seleccionados if s in df_filtrado["busqueda"].values], 
                        key=f"ms_{st.session_state.ms_key}", 
                        max_selections=60,
                        on_change=lambda: st.session_state.update({"seleccionados": st.session_state[f"ms_{st.session_state.ms_key}"], "pack_activo": None}), 
                        help="Escribe el nombre del examen o el código Fonasa para buscar agregarlo a la cotización actual. (Máximo 60 exámenes)"
                    )

        if st.session_state.seleccionados:
            # Solo mostramos la lista de seleccionados (con opción de borrar/cantidad) si NO hay un pack activo
            if not st.session_state.pack_activo:
                st.markdown("#### 🔢 Exámenes seleccionados")
                for item in list(st.session_state.seleccionados):
                    if item not in st.session_state.cantidades: st.session_state.cantidades[item] = 1
                    c_txt, c_qty, c_del = st.columns([5, 1.8, 0.5], vertical_alignment="center")
                    with c_txt: st.markdown(f'<div class="exam-row-compact"><div class="exam-row-title">{item}</div></div>', unsafe_allow_html=True)
                    with c_qty:
                        st.session_state.cantidades[item] = st.number_input(f"Q_{item}", min_value=1, max_value=20, value=st.session_state.cantidades.get(item, 1), key=f"q_{item}", label_visibility="collapsed", disabled=st.session_state.pdf_generado)
                    with c_del:
                        st.markdown('<div class="btn-del-box">', unsafe_allow_html=True)
                        if st.button("✖", key=f"del_{item}", disabled=st.session_state.pdf_generado):
                            st.session_state.seleccionados.remove(item)
                            if f"q_{item}" in st.session_state: del st.session_state[f"q_{item}"]
                            st.session_state.pack_activo = None
                            st.session_state.ms_key += 1; st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)

            df_sel = df_filtrado[df_filtrado["busqueda"].isin(st.session_state.seleccionados)].copy()
            df_sel["Cant"] = df_sel["busqueda"].map(st.session_state.cantidades).fillna(1).astype(int)
            df_sel["V. Bono"] = df_sel["Valor bono Fonasa"] * df_sel["Cant"]
            df_sel["V. Copago"] = df_sel.apply(lambda r: r["Valor copago"] if r["Valor bono Fonasa"] > 0 else r["Valor particular General"], axis=1) * df_sel["Cant"]
            df_sel["P. Gral"] = df_sel["Valor particular General"] * df_sel["Cant"]
            df_sel["P. Pref"] = df_sel["Valor particular preferencial"] * df_sel["Cant"]
            
            t_f, t_c, t_pg, t_pp = df_sel["V. Bono"].sum(), df_sel["V. Copago"].sum(), df_sel["P. Gral"].sum(), df_sel["P. Pref"].sum()

            st.markdown("---")
            if prevision != "Seleccione...":
                st.markdown("#### 📋 Vista previa de la cotización")
                res_c = ["Cant", "Nombre", "Fonasa (Tot)", "Copago (Tot)"] if prevision == "Fonasa" else ["Cant", "Nombre", "P.Gral (Tot)", "P.Pref (Tot)"]
                df_disp = df_sel.copy()
                if prevision == "Fonasa":
                    df_disp["Fonasa (Tot)"], df_disp["Copago (Tot)"] = df_sel["V. Bono"], df_sel["V. Copago"]
                else:
                    df_disp["P.Gral (Tot)"], df_disp["P.Pref (Tot)"] = df_sel["P. Gral"], df_sel["P. Pref"]
                st.dataframe(
                    df_disp[res_c], 
                    width="stretch", 
                    hide_index=True,
                    column_config={
                        "Cant": st.column_config.NumberColumn("Cant", width="small"),
                        "Nombre": st.column_config.TextColumn("Nombre", width="large"),
                        "Fonasa (Tot)": st.column_config.NumberColumn("Fonasa (Tot)", width="medium"),
                        "Copago (Tot)": st.column_config.NumberColumn("Copago (Tot)", width="medium"),
                        "P.Gral (Tot)": st.column_config.NumberColumn("P.Gral (Tot)", width="medium"),
                        "P.Pref (Tot)": st.column_config.NumberColumn("P.Pref (Tot)", width="medium")
                    }
                )
                
                m1, m2 = st.columns(2)
                if prevision == "Fonasa":
                    m1.metric("Total Bono", f"${t_f:,.0f}"); m2.metric("Total Copago", f"${t_c:,.0f}")
                else:
                    m1.metric("Total P. Gral", f"${t_pg:,.0f}"); m2.metric("Total P. Pref", f"${t_pp:,.0f}")

                if not st.session_state.pdf_generado:
                    if st.button("🚀 Generar PDF", width="stretch"):
                        folio = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
                        ahora_chile = obtener_ahora_chile()
                        timestamp_emision = ahora_chile.strftime("%d/%m/%Y %H:%M:%S")

                        if guardar_en_db(folio, nombre_p, st.session_state.tipo_doc_sesion, st.session_state.doc_id_sesion, fecha_nac, t_f, t_c, t_pg, t_pp, df_sel, prevision):
                            
                            path = generar_cotizacion_pdf(
                                folio, timestamp_emision, nombre_p, 
                                st.session_state.doc_id_sesion, fecha_nac, prevision, 
                                df_sel, t_f, t_c, t_pg, t_pp, st.session_state.pack_activo
                            )
                            
                            st.session_state.pdf_path, st.session_state.pdf_generado = path, True
                            st.rerun()

        if st.session_state.pdf_generado:
            st.success("✅ Cotización finalizada con éxito.")
            
            with open(st.session_state.pdf_path, "rb") as f:
                st.download_button("🔵 Descargar cotización y orden médica", f, file_name=f"Cotizacion_{nombre_p}.pdf", width="stretch")

            if st.button("✏️ Editar cotización", width="stretch"):
                st.session_state.pdf_generado = False
                st.rerun()
            
            st.markdown("---")
            
            if st.button("🔄 Generar nueva cotización", width="stretch"):
                st.session_state.update({"seleccionados": [], "cantidades": {}, "pdf_generado": False, "ms_key": st.session_state.ms_key + 1, "pack_activo": None})
                st.rerun()

            st.markdown("---")

            st.link_button("📅 Agendar hora Toma de muestras", "https://ff.healthatom.io/FKV7ZY", width="stretch")

# FOOTER
st.markdown("<br><br>", unsafe_allow_html=True)
f_col1, f_col2, f_col3 = st.columns(3)
with f_col1: st.markdown('<center><a href="#" class="footer-link">📄 Cotizador</a></center>', unsafe_allow_html=True)
with f_col2: st.markdown('<center><a href="https://www.policlinicotabancura.cl" class="footer-link">🌐 Sitio Web</a></center>', unsafe_allow_html=True)
with f_col3: st.markdown('<center><a href="https://www.instagram.com/politabancura/" class="footer-link">📸 Instagram</a></center>', unsafe_allow_html=True)
st.divider()
st.markdown("""<div class="sucursal-info">Sucursal Vitacura: Av. Vitacura #8620 <br><b>Área toma de muestras - Policlínico Tabancura</b><br>+562 2933 6740 - +569 6578 1253</div>""", unsafe_allow_html=True)
