import streamlit as st
import psycopg2
import pandas as pd

def conectar_db():
    if "postgres" in st.secrets:
        return psycopg2.connect(**st.secrets["postgres"])
    return None

nombre_objetivo = "Nicolás Jofré Andrade"

print(f"Buscando registros para: {nombre_objetivo}")
conn = conectar_db()
if not conn:
    print("No se pudo conectar a la base de datos.")
    exit()

try:
    # 1. Cotizaciones
    df_cot = pd.read_sql("SELECT folio, nombre_paciente FROM cotizaciones WHERE nombre_paciente = %s", conn, params=(nombre_objetivo,))
    folios = df_cot['folio'].tolist()
    
    print(f"\n[COTIZACIONES] Encontradas: {len(df_cot)}")
    print(df_cot)
    
    if folios:
        # 2. Detalles de Cotización
        df_det_cot = pd.read_sql("SELECT count(*) as total FROM detalle_cotizaciones WHERE folio_cotizacion IN %s", conn, params=(tuple(folios),))
        print(f"\n[DETALLES COTIZACION] Registros relacionados: {df_det_cot['total'][0]}")
        
        # 3. Ordenes Clínicas
        df_om = pd.read_sql("SELECT folio_orden, folio_cotizacion_origen FROM ordenes_clinicas WHERE folio_cotizacion_origen IN %s", conn, params=(tuple(folios),))
        folios_om = df_om['folio_orden'].tolist()
        print(f"\n[ORDENES CLINICAS] Encontradas: {len(df_om)}")
        print(df_om)
        
        if folios_om:
            # 4. Detalles de Ordenes
            df_det_om = pd.read_sql("SELECT count(*) as total FROM ordenes_detalles WHERE folio_orden IN %s", conn, params=(tuple(folios_om),))
            print(f"\n[DETALLES ORDENES] Registros relacionados: {df_det_om['total'][0]}")
    else:
        print("\nNo se encontraron folios asociados.")

finally:
    conn.close()
