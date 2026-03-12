from datetime import date, datetime
import pytz

def obtener_ahora_chile():
    tz = pytz.timezone('America/Santiago')
    return datetime.now(tz)

def calcular_edad(fecha_nacimiento):
    today = date.today()
    return today.year - fecha_nacimiento.year - ((today.month, today.day) < (fecha_nacimiento.month, fecha_nacimiento.day))

# Los packs ahora se cargan desde pack.json en la aplicación principal.
