import psycopg2
import pandas as pd

creds = {
    "host": "181.42.232.26",
    "database": "db_migracion",
    "user": "postgres",
    "password": "oIZEFdX4TwqvCqoRurMkEOBjLxXRpwfwNMRzwrTyaH5OhUNINqv9lNqAzmD4fLeV",
    "port": "5432"
}

try:
    conn = psycopg2.connect(**creds)
    # Buscar cualquier nombre que contenga Nicolas o Jofre
    df = pd.read_sql("""
        SELECT folio, nombre_paciente, documento_id, fecha_cotizacion, prevision 
        FROM cotizaciones 
        WHERE nombre_paciente ILIKE '%%Nicolás%%' 
           OR nombre_paciente ILIKE '%%Jofré%%' 
           OR nombre_paciente ILIKE '%%Jofre%%' 
           OR nombre_paciente ILIKE '%%Andrade%%'
        ORDER BY fecha_cotizacion DESC
    """, conn)
    
    print("\n--- REGISTROS ENCONTRADOS QUE PODRÍAN SER PARA ELIMINAR ---")
    if not df.empty:
        # Ajustar visualización de pandas para ver todo
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)
        print(df)
        
        folios = df['folio'].tolist()
        # Buscar ordenes relacionadas
        df_om = pd.read_sql("SELECT folio_orden, folio_cotizacion_origen FROM ordenes_clinicas WHERE folio_cotizacion_origen IN %s", conn, params=(tuple(folios),))
        print("\n--- ORDENES CLÍNICAS RELACIONADAS ---")
        if not df_om.empty:
            print(df_om)
        else:
            print("No se encontraron órdenes médicas para estos folios.")
    else:
        print("No se encontraron registros.")
    
    conn.close()
except Exception as e:
    print(f"Error: {e}")
