import psycopg2

creds = {
    "host": "181.42.232.26",
    "database": "db_migracion",
    "user": "postgres",
    "password": "oIZEFdX4TwqvCqoRurMkEOBjLxXRpwfwNMRzwrTyaH5OhUNINqv9lNqAzmD4fLeV",
    "port": "5432"
}

# Folios detectados en el último chequeo
target_folios = ['953P2BU5', 'SUO53209', 'WJPWFWXD', 'SNYIA8U4', 'CU6VKC7A']

try:
    conn = psycopg2.connect(**creds)
    cur = conn.cursor()
    
    print(f"Borrando los últimos {len(target_folios)} folios de Javiera...")

    # 1. Obtener folios de órdenes
    cur.execute("SELECT folio_orden FROM ordenes_clinicas WHERE folio_cotizacion_origen IN %s", (tuple(target_folios),))
    ords = cur.fetchall()
    f_om = [r[0] for r in ords]

    if f_om:
        cur.execute("DELETE FROM ordenes_detalles WHERE folio_orden IN %s", (tuple(f_om),))
        print("- Detalles de órdenes eliminados.")

    cur.execute("DELETE FROM ordenes_clinicas WHERE folio_cotizacion_origen IN %s", (tuple(target_folios),))
    print("- Órdenes médicas eliminadas.")

    cur.execute("DELETE FROM detalle_cotizaciones WHERE folio_cotizacion IN %s", (tuple(target_folios),))
    print("- Detalles de cotizaciones eliminados.")

    cur.execute("DELETE FROM cotizaciones WHERE folio IN %s", (tuple(target_folios),))
    print("- Cotizaciones principales eliminadas.")

    conn.commit()
    print("\n✅ LIMPIEZA TOTAL COMPLETADA. Sólo queda Francisco Madariaga.")
    
    cur.close()
    conn.close()
except Exception as e:
    if conn: conn.rollback()
    print(f"❌ Error: {e}")
