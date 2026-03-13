import psycopg2
import pandas as pd

creds = {
    "host": "181.42.232.26",
    "database": "db_migracion",
    "user": "postgres",
    "password": "oIZEFdX4TwqvCqoRurMkEOBjLxXRpwfwNMRzwrTyaH5OhUNINqv9lNqAzmD4fLeV",
    "port": "5432"
}

nombre_objetivo = "Nicolás Jofré Andrade"

try:
    conn = psycopg2.connect(**creds)
    cur = conn.cursor()
    
    # 1. Cotizaciones
    df_cot = pd.read_sql("SELECT folio, nombre_paciente, fecha_cotizacion FROM cotizaciones WHERE nombre_paciente = %s", conn, params=(nombre_objetivo,))
    folios = df_cot['folio'].tolist()
    
    print(f"--- REPORTE DE REGISTROS PARA ELIMINAR ---")
    print(f"Paciente: {nombre_objetivo}")
    print(f"Cotizaciones encontradas: {len(df_cot)}")
    print(df_cot)
    
    if folios:
        # 2. Ordenes Clínicas
        df_om = pd.read_sql("SELECT folio_orden, folio_cotizacion_origen FROM ordenes_clinicas WHERE folio_cotizacion_origen IN %s", conn, params=(tuple(folios),))
        folios_om = [str(f) for f in df_om['folio_orden'].tolist()]
        print(f"\nOrdenes Clínicas encontradas: {len(df_om)}")
        print(df_om)
        
        # 3. Datos de auditoría (si existen)
        df_aud = pd.read_sql("SELECT id, folio_origen FROM auditoria_examenes WHERE nombre_paciente = %s", conn, params=(nombre_objetivo,))
        print(f"\nRegistros en auditoria_examenes: {len(df_aud)}")
        print(df_aud)

    cur.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
