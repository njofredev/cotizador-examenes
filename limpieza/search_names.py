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
    df = pd.read_sql("SELECT folio, nombre_paciente, documento_id, fecha_cotizacion FROM cotizaciones WHERE nombre_paciente ILIKE '%%Nicolás%%' OR nombre_paciente ILIKE '%%Jofré%%' OR nombre_paciente ILIKE '%%Jofre%%'", conn)
    print("--- REGISTROS ENCONTRADOS ---")
    print(df)
    conn.close()
except Exception as e:
    print(f"Error: {e}")
