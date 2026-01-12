import streamlit as st
import pandas as pd
from fpdf import FPDF
import os
import psycopg2
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# --- 1. CONFIGURACIÓN Y CONEXIÓN ---
st.set_page_config(page_title="Cotizador Policlínico Tabancura", page_icon="🏥", layout="wide")

def conectar_db():
    host = os.getenv("POSTGRES_HOST")
    if not host:
        try:
            db_conf = st.secrets["postgres"]
            host, database, user, password, port = db_conf["host"], db_conf["database"], db_conf["user"], db_conf["password"], db_conf["port"]
        except:
            st.error("❌ Error de configuración: Faltan variables de entorno.")
            return None
    else:
        database, user, password, port = os.getenv("POSTGRES_DATABASE"), os.getenv("POSTGRES_USER"), os.getenv("POSTGRES_PASSWORD"), os.getenv("POSTGRES_PORT")

    try:
        return psycopg2.connect(host=host, database=database, user=user, password=password, port=port, sslmode="require")
    except Exception as e:
        st.error(f"❌ Error de conexión: {e}")
        return None

@st.cache_data
def cargar_aranceles():
    if not os.path.exists("aranceles.xlsx"):
        st.error("❌ Archivo 'aranceles.xlsx' no encontrado.")
        return None
    df = pd.read_excel("aranceles.xlsx")
    # Ajustamos nombres de columnas según tu archivo
    df.columns = ["Código", "Nombre", "Fonasa", "Copago", "Particular_Gral", "Particular_Pref"]
    df["Código"] = df["Código"].astype(str).str.replace(".0", "", regex=False)
    return df

# --- 2. FUNCIONES DE LÓGICA (PDF Y EMAIL) ---

def generar_pdf(nombre, rut, fecha_nac, email, examenes_df, folio):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "COTIZACIÓN DE EXÁMENES - POLICLÍNICO TABANCURA", ln=True, align='C')
    
    pdf.set_font("Arial", '', 12)
    pdf.ln(10)
    pdf.cell(200, 10, f"Folio: {folio}", ln=True)
    pdf.cell(200, 10, f"Paciente: {nombre} | RUT: {rut}", ln=True)
    pdf.cell(200, 10, f"Fecha Nacimiento: {fecha_nac}", ln=True)
    pdf.cell(200, 10, f"Email: {email}", ln=True)
    pdf.cell(200, 10, f"Fecha Emisión: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True)
    pdf.ln(10)

    # Cabecera de tabla
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(30, 10, "Código", 1)
    pdf.cell(100, 10, "Examen", 1)
    pdf.cell(40, 10, "Precio (Part.)", 1)
    pdf.ln()

    # Contenido de tabla
    pdf.set_font("Arial", '', 10)
    total = 0
    for _, row in examenes_df.iterrows():
        pdf.cell(30, 10, str(row['Código']), 1)
        pdf.cell(100, 10, str(row['Nombre'])[:50], 1)
        pdf.cell(40, 10, f"${row['Particular_Gral']:,.0f}", 1)
        total += row['Particular_Gral']
        pdf.ln()

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, f"TOTAL A PAGAR: ${total:,.0f}", ln=True, align='R')
    
    filename = f"cotizacion_{folio}.pdf"
    pdf.output(filename)
    return filename

def enviar_correo(destinatario, archivo_pdf, nombre_paciente):
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", 465))
    
    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = destinatario
    msg['Subject'] = f"Tu Cotización Médica - Policlínico Tabancura"

    body = f"Hola {nombre_paciente},\n\nAdjuntamos la cotización de exámenes solicitada en Policlínico Tabancura.\n\nAtentamente,\nEquipo Policlínico Tabancura."
    msg.attach(MIMEText(body, 'plain'))

    with open(archivo_pdf, "rb") as f:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename={archivo_pdf}")
        msg.attach(part)

    try:
        # USAMOS SMTP_SSL PARA PUERTO 465
        server = smtplib.SMTP_SSL(smtp_host, smtp_port)
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Error al enviar email: {e}")
        return False

# --- 3. INTERFAZ DE USUARIO ---

tab1, tab2 = st.tabs(["🆕 Nueva Cotización", "🔍 Buscar Folio"])

with tab1:
    st.header("Generar Nueva Cotización")
    col1, col2 = st.columns(2)
    with col1:
        nombre_pax = st.text_input("Nombre Completo")
        rut_pax = st.text_input("RUT (ej: 12.345.678-9)")
    with col2:
        fecha_nac_pax = st.date_input("Fecha de Nacimiento", min_value=datetime(1920,1,1))
        email_pax = st.text_input("Correo Electrónico del Paciente")

    aranceles = cargar_aranceles()
    if aranceles is not None:
        seleccion = st.multiselect("Busque y seleccione los exámenes:", aranceles["Nombre"].tolist())
        df_seleccionados = aranceles[aranceles["Nombre"].isin(seleccion)]
        
        if not df_seleccionados.empty:
            st.table(df_seleccionados[["Código", "Nombre", "Particular_Gral"]])
            
            if st.button("Finalizar, Guardar y Enviar"):
                if not email_pax or "@" not in email_pax or not nombre_pax:
                    st.warning("⚠️ Complete todos los campos y asegúrese de que el correo sea válido.")
                else:
                    conn = conectar_db()
                    if conn:
                        try:
                            cur = conn.cursor()
                            folio_gen = f"COT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                            
                            # 1. Guardar en tabla Maestra
                            cur.execute("""
                                INSERT INTO cotizaciones (folio, rut, nombre, fecha_nacimiento, email, fecha_creacion) 
                                VALUES (%s, %s, %s, %s, %s, %s)
                                """, (folio_gen, rut_pax, nombre_pax, fecha_nac_pax, email_pax, datetime.now()))
                            
                            # 2. Guardar en Detalle
                            for cod in df_seleccionados["Código"]:
                                cur.execute("INSERT INTO detalle_cotizaciones (folio_cotizacion, codigo_examen) VALUES (%s, %s)", (folio_gen, cod))
                            
                            conn.commit()
                            
                            # 3. PDF y Email
                            with st.spinner("Generando documento y enviando correo..."):
                                pdf_path = generar_pdf(nombre_pax, rut_pax, str(fecha_nac_pax), email_pax, df_seleccionados, folio_gen)
                                if enviar_correo(email_pax, pdf_path, nombre_pax):
                                    st.success(f"✅ ¡Folio {folio_gen} enviado con éxito a {email_pax}!")
                                    with open(pdf_path, "rb") as f:
                                        st.download_button("Descargar Copia PDF", f, file_name=pdf_path)
                            
                            cur.close()
                            conn.close()
                        except Exception as e:
                            st.error(f"Error en la base de datos: {e}")

with tab2:
    st.header("Revisión de Cotizaciones")
    folio_input = st.text_input("Ingrese Folio a buscar (ej: COT-2024...):").upper().strip()

    if st.button("Buscar en Base de Datos"):
        conn = conectar_db()
        if conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM cotizaciones WHERE folio = %s", (folio_input,))
            maestro = cur.fetchone()
            
            if maestro:
                st.info(f"📍 Cotización encontrada")
                st.write(f"**Paciente:** {maestro[2]} | **RUT:** {maestro[1]}")
                st.write(f"**Email registrado:** {maestro[5]}") # Asumiendo que email es la col 5
                
                cur.execute("SELECT codigo_examen FROM detalle_cotizaciones WHERE folio_cotizacion = %s", (folio_input,))
                codigos = [r[0] for r in cur.fetchall()]
                
                aranceles = cargar_aranceles()
                df_res = aranceles[aranceles["Código"].isin(codigos)]
                st.table(df_res[["Código", "Nombre", "Particular_Gral"]])
            else:
                st.error("❌ El folio ingresado no existe.")
            cur.close()
            conn.close()
