import streamlit as st
import pandas as pd
import psycopg2
import os
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from pdf_generator import generar_cotizacion_pdf
from utils import obtener_ahora_chile

# Configuración de página
st.set_page_config(page_title="Gestión Lab - Dashboard", layout="wide", page_icon="🏥")

# --- CONEXIÓN DB ---
def conectar_db():
    try:
        if "postgres" in st.secrets:
            creds = dict(st.secrets["postgres"])
            creds["client_encoding"] = "utf8"
            return psycopg2.connect(**creds)
        return None
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

def get_data(query, params=None):
    conn = conectar_db()
    if conn:
        try:
            df = pd.read_sql(query, conn, params=params)
            conn.close()
            return df
        except Exception as e:
            st.error(f"Error en consulta: {e}")
            conn.close()
    return pd.DataFrame()

# --- FILTROS SIDEBAR ---
with st.sidebar:
    if os.path.exists("logo_vec.svg"):
        st.image("logo_vec.svg", width=180)
    st.title("🎛️ Filtros de Control")
    st.markdown("---")
    
    # Rango de fechas más profesional
    hoy = obtener_ahora_chile().date()
    hace_mes = hoy - timedelta(days=30)
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        start_date = st.date_input("Desde", hace_mes)
    with col_f2:
        end_date = st.date_input("Hasta", hoy)
    
    st.markdown("---")
    # Filtro de Previsión Directo
    prevision_opt = st.multiselect("Previsión", ["Fonasa", "Particular"], default=["Fonasa", "Particular"])
    
    st.markdown("---")
    st.info("💡 Sugerencia: Filtra por Previsión para ver el comportamiento de ingresos específicos.")

# --- CARGA DE DATOS ---
# Cargamos todo para manejar los filtros localmente con Pandas (más reactivo)
df_cot_raw = get_data("SELECT * FROM cotizaciones ORDER BY fecha_cotizacion DESC")
df_om_raw = get_data("SELECT * FROM ordenes_clinicas ORDER BY fecha_creacion DESC")
df_detalles = get_data("SELECT * FROM detalle_cotizaciones")

# --- PROCESAMIENTO ---
if df_cot_raw.empty:
    st.warning("No hay datos cargados en el sistema.")
    st.stop()

# Conversión de fechas
df_cot_raw['fecha_dt'] = pd.to_datetime(df_cot_raw['fecha_cotizacion']).dt.date
df_om_raw['fecha_dt'] = pd.to_datetime(df_om_raw['fecha_creacion']).dt.date if not df_om_raw.empty else None

# Aplicar Filtros
mask_cot = (df_cot_raw['fecha_dt'] >= start_date) & (df_cot_raw['fecha_dt'] <= end_date) & (df_cot_raw['prevision'].isin(prevision_opt))
df_cot = df_cot_raw.loc[mask_cot].copy()

if not df_om_raw.empty:
    mask_om = (df_om_raw['fecha_dt'] >= start_date) & (df_om_raw['fecha_dt'] <= end_date)
    # También filtrar OM por la previsión de su cotización de origen
    om_with_prev = df_om_raw.merge(df_cot_raw[['folio', 'prevision']], left_on='folio_cotizacion_origen', right_on='folio', how='left')
    mask_om_prev = om_with_prev['prevision'].isin(prevision_opt)
    df_om = df_om_raw.loc[mask_om & mask_om_prev].copy()
else:
    df_om = pd.DataFrame()

# --- HEADER ---
st.title("🏥 Dashboard de Gestión - Cotizador Digital")
st.caption(f"Visualizando datos desde {start_date.strftime('%d/%m/%Y')} hasta {end_date.strftime('%d/%m/%Y')}")
st.markdown("---")

# --- TABS PRINCIPALES ---
tab_resumen, tab_examenes, tab_busqueda = st.tabs(["📊 Resumen de Gestión", "🧬 Análisis de Exámenes", "🔍 Localizador & Auditoría"])

with tab_resumen:
    # KPIs SUPERIORES
    c1, c2, c3, c4 = st.columns(4)
    total_cot = len(df_cot)
    total_om = len(df_om)
    conv_rate = (total_om / total_cot * 100) if total_cot > 0 else 0
    ingresos = df_cot['total_copago'].sum() if not df_cot.empty else 0
    
    c1.metric("Cotizaciones Realizadas", f"{total_cot}", delta=None)
    c2.metric("Órdenes Generadas", f"{total_om}", delta=None)
    c3.metric("Tasa de Conversión", f"{conv_rate:.1f}%", help="Porcentaje de cotizaciones que se convirtieron en órdenes médicas")
    c4.metric("Ingreso Proyectado (Copago)", f"${ingresos:,.0f}")

    st.markdown("---")
    
    # GRÁFICOS DE RESUMEN
    g1, g2 = st.columns([2, 1])
    
    with g1:
        st.subheader("📈 Evolución de Demanda")
        if not df_cot.empty:
            df_ev = df_cot.groupby('fecha_dt').size().reset_index(name='cuant')
            fig_ev = px.area(df_ev, x='fecha_dt', y='cuant', 
                             labels={'cuant': 'Cantidad', 'fecha_dt': 'Fecha'},
                             color_discrete_sequence=['#0270F9'])
            fig_ev.update_layout(hovermode="x unified", margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig_ev, use_container_width=True)
            
    with g2:
        st.subheader("💰 Distribución de Ingresos")
        if not df_cot.empty:
            df_pie = df_cot.groupby('prevision')['total_copago'].sum().reset_index()
            fig_pie = px.pie(df_pie, values='total_copago', names='prevision', 
                             hole=0.4, color_discrete_sequence=['#85C1E9', '#0270F9'])
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("---")
    st.subheader("📜 Historial Reciente Recortado")
    if not df_cot.empty:
        df_mini = df_cot[['fecha_cotizacion', 'folio', 'nombre_paciente', 'prevision', 'total_copago']].head(10).copy()
        df_mini.columns = ["Fecha", "Folio", "Paciente", "Previsión", "Total ($)"]
        df_mini["Fecha"] = pd.to_datetime(df_mini["Fecha"]).dt.strftime("%d/%m/%Y %H:%M")
        df_mini["Total ($)"] = df_mini["Total ($)"].apply(lambda x: f"${x:,.0f}")
        st.dataframe(df_mini, use_container_width=True, hide_index=True)

with tab_examenes:
    st.subheader("🔬 Top 15 Exámenes más Cotizados")
    if not df_detalles.empty and not df_cot.empty:
        # Filtrar detalles por los folios de las cotizaciones filtradas
        df_det_filt = df_detalles[df_detalles['folio_cotizacion'].isin(df_cot['folio'])]
        if not df_det_filt.empty:
            top_ex = df_det_filt['nombre_examen'].value_counts().head(15).reset_index()
            top_ex.columns = ['Examen', 'Frecuencia']
            fig_bar = px.bar(top_ex, x='Frecuencia', y='Examen', orientation='h',
                             color='Frecuencia', color_continuous_scale='Blues')
            fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No hay detalles suficientes para este periodo.")
    
    st.markdown("---")
    c_p1, c_p2 = st.columns(2)
    with c_p1:
        st.subheader("📦 Uso de Packs Preventivos")
        if 'nombre_pack' in df_cot.columns:
            df_pk = df_cot[df_cot['nombre_pack'].notna()]['nombre_pack'].value_counts().reset_index()
            if not df_pk.empty:
                df_pk.columns = ['Pack', 'Uso']
                fig_pk = px.bar(df_pk, x='Uso', y='Pack', orientation='h', color_discrete_sequence=['#5DADE2'])
                st.plotly_chart(fig_pk, use_container_width=True)
            else:
                st.write("Sin uso de packs en este periodo.")
    with c_p2:
        st.subheader("👥 Perfil de Pacientes")
        if 'tipo_documento' in df_cot.columns:
            df_doc = df_cot['tipo_documento'].value_counts().reset_index()
            df_doc.columns = ['Tipo', 'Cant']
            fig_doc = px.pie(df_doc, values='Cant', names='Tipo', color_discrete_sequence=['#AED6F1', '#2E86C1'])
            st.plotly_chart(fig_doc, use_container_width=True)

with tab_busqueda:
    st.subheader("🔍 Localizador de Documentos")
    folio_search = st.text_input("Ingrese FOLIO completo:").strip().upper()
    
    if folio_search:
        # Búsqueda local primero por velocidad si ya tenemos los datos cargados
        res_cot = df_cot_raw[df_cot_raw['folio'] == folio_search]
        
        if not res_cot.empty:
            st.success(f"✅ Cotización Encontrada: {folio_search}")
            c = res_cot.iloc[0]
            # Mostrar datos
            col_d1, col_d2, col_d3 = st.columns(3)
            with col_d1:
                st.markdown(f"**Paciente:** {c['nombre_paciente']}")
                st.markdown(f"**Documento:** {c['documento_id']}")
            with col_d2:
                st.markdown(f"**Previsión:** {c['prevision']}")
                st.markdown(f"**Fecha:** {c['fecha_dt']}")
            with col_d3:
                st.markdown(f"**Total Copago:** ${c['total_copago']:,.0f}")
                st.markdown(f"**Total Particular:** ${c['total_particular_gral']:,.0f}")
            
            # Detalles enriquecidos con Aranceles actuales para mostrar ambos valores
            df_det_b = df_detalles[df_detalles['folio_cotizacion'] == folio_search]
            if not df_det_b.empty:
                # Intentar cargar aranceles
                try:
                    df_aranceles = pd.read_excel("aranceles.xlsx")
                    df_aranceles['Código'] = df_aranceles['Código'].astype(str)
                    df_det_b = df_det_b.merge(
                        df_aranceles[['Código', 'V. Copago', 'P. Gral']], 
                        left_on='codigo_examen', 
                        right_on='Código', 
                        how='left'
                    )
                    df_det_b['V. Fonasa'] = df_det_b['V. Copago'].fillna(df_det_b['valor_copago'] if c['prevision'] == 'Fonasa' else 0)
                    df_det_b['V. Particular'] = df_det_b['P. Gral'].fillna(df_det_b['valor_copago'] if c['prevision'] != 'Fonasa' else 0)
                except:
                    es_fonasa = (c['prevision'] == 'Fonasa')
                    df_det_b['V. Fonasa'] = df_det_b['valor_copago'] if es_fonasa else 0
                    df_det_b['V. Particular'] = df_det_b['valor_copago'] if not es_fonasa else 0

                st.write("**Detalle de Exámenes:**")
                
                # Columnas condicionales: Solo mostramos la que corresponde a la previsión
                if c['prevision'] == "Fonasa":
                    display_cols = ['codigo_examen', 'nombre_examen', 'V. Fonasa']
                    renames = {'codigo_examen': 'Código', 'nombre_examen': 'Examen', 'V. Fonasa': 'Valor Copago Fonasa ($)'}
                else:
                    display_cols = ['codigo_examen', 'nombre_examen', 'V. Particular']
                    renames = {'codigo_examen': 'Código', 'nombre_examen': 'Examen', 'V. Particular': 'Valor Particular ($)'}

                st.dataframe(df_det_b[display_cols].rename(columns=renames), use_container_width=True, hide_index=True)
                
                # Totales debajo de la tabla, alineados a la derecha
                col_t1, col_t2 = st.columns([3, 1])
                with col_t2:
                    st.markdown(f"""
                    <div style='text-align: right; border-top: 2px solid #eee; padding-top: 10px;'>
                        <p style='margin:0; color:#666;'>Total Fonasa: <b>${c.get('total_fonasa', 0):,.0f}</b></p>
                        <p style='margin:0; font-size: 1.2rem; color: #0270F9;'>Total Copago: <b>${c.get('total_copago', 0):,.0f}</b></p>
                        <p style='margin:0; color:#666;'>Total Particular: <b>${c.get('total_particular_gral', 0):,.0f}</b></p>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🖨️ Reimprimir PDF"):
                    df_pdf = df_det_b.copy()
                    df_pdf.rename(columns={"codigo_examen":"Código","nombre_examen":"Nombre","valor_copago":"Valor copago"}, inplace=True)
                    df_pdf["Cant"] = 1
                    
                    # Asignación robusta para PDF
                    if c['prevision'] == "Fonasa":
                        df_pdf["Valor bono Fonasa"] = df_pdf["Valor copago"]
                        df_pdf["Valor particular General"] = 0
                        df_pdf["Valor particular preferencial"] = 0
                    else:
                        df_pdf["Valor bono Fonasa"] = 0
                        df_pdf["Valor particular General"] = df_pdf["Valor copago"]
                        df_pdf["Valor particular preferencial"] = df_pdf["Valor copago"]
                    
                    try:
                        ts = pd.to_datetime(c['fecha_cotizacion']).strftime("%d/%m/%Y %H:%M:%S")
                        archivo = generar_cotizacion_pdf(
                            folio_cot=c['folio'], folio_om="", timestamp_emision=ts,
                            nombre_p=c['nombre_paciente'], doc_id=c['documento_id'],
                            fecha_nac=c['fecha_nacimiento'], prevision=c['prevision'],
                            df_sel=df_pdf,
                            t_f=c['total_fonasa'], t_c=c['total_copago'],
                            t_pg=c['total_particular_gral'], t_pp=c['total_particular_pref'],
                            incluir_om=False
                        )
                        with open(archivo, "rb") as f:
                            st.download_button("📩 Descargar PDF", f, file_name=archivo, mime="application/pdf")
                    except Exception as e:
                        st.error(f"Error al generar PDF: {e}")
        else:
            # Buscar en OM si no está en COT (o si es folio de orden)
            res_om_b = df_om_raw[df_om_raw['folio_orden'].astype(str) == folio_search] if not df_om_raw.empty else pd.DataFrame()
            if not res_om_b.empty:
                o = res_om_b.iloc[0]
                st.success(f"✅ Orden Médica Identificada: {folio_search}")
                st.info(f"Asociada a la cotización original: **{o['folio_cotizacion_origen']}**")
                if st.button("Ir a Cotización de Origen"):
                    st.session_state["nav_folio"] = o['folio_cotizacion_origen']
                    st.rerun()
            else:
                st.warning("No se encontró el folio ingresado en los registros activos.")

st.markdown("---")
st.caption("Dashboard de Gestión v2.0 | Laboratorio Policlínico Tabancura")
