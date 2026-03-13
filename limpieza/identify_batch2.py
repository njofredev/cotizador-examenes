import psycopg2

creds = {
    "host": "181.42.232.26",
    "database": "db_migracion",
    "user": "postgres",
    "password": "oIZEFdX4TwqvCqoRurMkEOBjLxXRpwfwNMRzwrTyaH5OhUNINqv9lNqAzmD4fLeV",
    "port": "5432"
}

try:
    conn = psycopg2.connect(**creds)
    cur = conn.cursor()
    
    # Buscar folios para Javiera y Testingextranjero
    cur.execute("""
        SELECT folio, nombre_paciente, fecha_cotizacion 
        FROM cotizaciones 
        WHERE nombre_paciente ILIKE '%%Javiera Marchant%%' 
           OR nombre_paciente ILIKE '%%Testingextranjero%%'
    """)
    rows = cur.fetchall()
    print("--- REGISTROS IDENTIFICADOS ---")
    for r in rows:
        print(f"FOLIO: {r[0]} | PACIENTE: {r[1]} | FECHA: {r[2]}")
        
    cur.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
