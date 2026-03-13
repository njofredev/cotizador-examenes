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
    cur.execute("""
        SELECT folio, nombre_paciente, fecha_cotizacion 
        FROM cotizaciones 
        WHERE nombre_paciente ILIKE '%%Nicolás%%' 
           OR nombre_paciente ILIKE '%%Jofré%%' 
           OR nombre_paciente ILIKE '%%Jofre%%' 
           OR nombre_paciente ILIKE '%%Andrade%%'
        ORDER BY fecha_cotizacion DESC
    """)
    rows = cur.fetchall()
    print("--- REGISTROS DETECTADOS ---")
    for r in rows:
        print(f"FOLIO: {r[0]} | PACIENTE: {r[1]} | DATA: {r[2]}")
    
    # Buscar ordenes
    if rows:
        folios = [r[0] for r in rows]
        cur.execute("SELECT folio_orden, folio_cotizacion_origen FROM ordenes_clinicas WHERE folio_cotizacion_origen IN %s", (tuple(folios),))
        ords = cur.fetchall()
        print("\n--- ÓRDENES CLÍNICAS RELACIONADAS ---")
        for o in ords:
            print(f"ORDEN: {o[0]} | ORIGEN (COT): {o[1]}")
    
    cur.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
