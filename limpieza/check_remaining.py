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
    
    # Buscar TODO lo que no sea Francisco Madariaga
    cur.execute("""
        SELECT folio, nombre_paciente 
        FROM cotizaciones 
        WHERE nombre_paciente NOT ILIKE '%%Francisco Madariaga%%'
    """)
    rows = cur.fetchall()
    print("--- REGISTROS PARA ELIMINAR ---")
    for r in rows:
        print(f"FOLIO: {r[0]} | PACIENTE: {r[1]}")
        
    cur.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
