import psycopg2

creds = {
    "host": "181.42.232.26",
    "database": "db_migracion",
    "user": "postgres",
    "password": "oIZEFdX4TwqvCqoRurMkEOBjLxXRpwfwNMRzwrTyaH5OhUNINqv9lNqAzmD4fLeV",
    "port": "5432"
}

target_folios = ['CMAZ0604', 'C7S6YWQJ', 'UZNC4KA5', 'FM8FEIV4', 'VQ0CSD1B', '7YYJNNVP', 'QL06OFKD']

try:
    conn = psycopg2.connect(**creds)
    cur = conn.cursor()
    
    print(f"Iniciando limpieza de {len(target_folios)} folios de prueba...")

    # 1. Obtener folios de órdenes relacionadas
    cur.execute("SELECT folio_orden FROM ordenes_clinicas WHERE folio_cotizacion_origen IN %s", (tuple(target_folios),))
    ords_rows = cur.fetchall()
    folios_om = [r[0] for r in ords_rows]

    # --- ELIMINACION EN ORDEN ---
    
    # a. Detalles de Órdenes
    if folios_om:
        cur.execute("DELETE FROM ordenes_detalles WHERE folio_orden IN %s", (tuple(folios_om),))
        print(f"- Eliminados detalles de {len(folios_om)} órdenes médicas.")

    # b. Órdenes Clínicas
    cur.execute("DELETE FROM ordenes_clinicas WHERE folio_cotizacion_origen IN %s", (tuple(target_folios),))
    print(f"- Eliminadas {len(target_folios)} órdenes médicas.")

    # c. Detalles de Cotizaciones
    cur.execute("DELETE FROM detalle_cotizaciones WHERE folio_cotizacion IN %s", (tuple(target_folios),))
    print(f"- Eliminados detalles de {len(target_folios)} cotizaciones.")

    # d. Cotizaciones
    cur.execute("DELETE FROM cotizaciones WHERE folio IN %s", (tuple(target_folios),))
    print(f"- Eliminadas {len(target_folios)} cotizaciones principales.")

    conn.commit()
    print("\n✅ LIMPIEZA COMPLETADA EXITOSAMENTE.")
    
    cur.close()
    conn.close()
except Exception as e:
    if conn: conn.rollback()
    print(f"❌ ERROR durante la limpieza: {e}")
