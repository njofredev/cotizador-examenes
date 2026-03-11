from datetime import date, datetime
import pytz

def obtener_ahora_chile():
    tz = pytz.timezone('America/Santiago')
    return datetime.now(tz)

def calcular_edad(fecha_nacimiento):
    today = date.today()
    return today.year - fecha_nacimiento.year - ((today.month, today.day) < (fecha_nacimiento.month, fecha_nacimiento.day))

PACKS = {
    "Chequeo General": {
        "items": {
            "Hemoglobina glicada A1c": 1,
            "Perfil lipídico": 1,
            "Perfil Bioquímico": 1,
            "Orina Completa": 1,
            "Creatinina en sangre": 1,
            "Hemograma": 1,
            "Venosa en adulto": 1,
            "vitamina D": 1,
            "Vitamina B12": 1,
            "Electrolitos plasmáticos": 3,
            "Tiroestimulante (TSH)": 1,
            "Tiroxina o tetrayodotironina (T4)": 1,
            "Triyodotironina (T3)": 1,
            "Perfil Hepático": 1,
            "Electrocardiograma": 1
        }
    },
    "Chequeo preventivo adulto mayor +65": {
        "items": {
            "Hemoglobina glicada A1c": 1,
            "Perfil lipídico": 1,
            "Perfil Bioquímico": 1,
            "Orina Completa": 1,
            "Creatinina en sangre": 1,
            "Hemograma": 1,
            "V.D.R.L.": 1,
            "Venosa en adulto": 1,
            "Electrocardiograma": 1
        }
    },
    "Chequeo preventivo diabetes e hipertensión": {
        "items": {
            "Hemoglobina glicada A1c": 1,
            "Perfil lipídico": 1,
            "Perfil Bioquímico": 1,
            "Orina Completa": 1,
            "Creatinina en sangre": 1,
            "Hemograma": 1,
            "Venosa en adulto": 1,
            "Electrolitos plasmáticos": 3,
            "Tiroestimulante (TSH)": 1,
            "Tiroxina o tetrayodotironina (T4)": 1,
            "Triyodotironina (T3)": 1,
            "Perfil Hepático": 1,
            "Electrocardiograma": 1,
            "PROTEINA C REACTIVA": 1,
            "Acido úrico": 1,
            "MICROALBUMINURIA": 1,
            "Creatinina cuantitativa": 1,
            "Nitrógeno ureico": 1
        }
    },
    "Detección Diabetes e Insulino Resistencia": {
        "items": {
            "Hemoglobina glicada A1c": 1,
            "Glucosa, Prueba de Tolerancia": 1,
            "Frasco de Glucosa": 1,
            "Venosa en adulto": 1,
            "Glicemia basal": 1,
            "Orina Completa": 1,
            "Perfil lipídico": 1,
            "Acido úrico": 1,
            "PROTEINA C REACTIVA": 1,
            "HOMA": 1
        }
    },
    "Chequeo preventivo mujer menos de 30 años": {
        "items": {
            "Creatinina en sangre": 1,
            "Hemograma": 1,
            "V.D.R.L.": 1,
            "Venosa en adulto": 1,
            "Hemoglobina glicada A1c": 1,
            "Perfil lipídico": 1,
            "Electrolitos plasmáticos": 3,
            "Tiroestimulante (TSH)": 1,
            "Tiroxina o tetrayodotironina (T4)": 1,
            "Triyodotironina (T3)": 1,
            "Perfil Hepático": 1,
            "Anticuerpos virales, determ. de H.I.V.": 1,
            "Perfil Bioquímico": 1,
            "vitamina D": 1,
            "Vitamina B12": 1,
            "Orina Completa": 1,
            "Electrocardiograma": 1
        }
    },
    "Chequeo preventivo mujer mas de 40 años": {
        "items": {
            "Creatinina en sangre": 1,
            "Hemograma": 1,
            "V.D.R.L.": 1,
            "Venosa en adulto": 1,
            "Hemoglobina glicada A1c": 1,
            "Perfil lipídico": 1,
            "Electrolitos plasmáticos": 3,
            "Tiroestimulante (TSH)": 1,
            "Tiroxina o tetrayodotironina (T4)": 1,
            "Triyodotironina (T3)": 1,
            "Hormona luteinizante": 1,
            "Estradiol": 1,
            "Perfil Hepático": 1,
            "Perfil Bioquímico": 1,
            "vitamina D": 1,
            "Vitamina B12": 1,
            "Orina Completa": 1,
            "Electrocardiograma": 1
        }
    },
    "Chequeo preventivo hombre menos de 45 años": {
        "items": {
            "Creatinina en sangre": 1,
            "Hemograma": 1,
            "V.D.R.L.": 1,
            "Venosa en adulto": 1,
            "Hemoglobina glicada A1c": 1,
            "Perfil lipídico": 1,
            "Electrolitos plasmáticos": 3,
            "Tiroestimulante (TSH)": 1,
            "Tiroxina o tetrayodotironina (T4)": 1,
            "Triyodotironina (T3)": 1,
            "Perfil Hepático": 1,
            "Anticuerpos virales, determ. de H.I.V.": 1,
            "Perfil Bioquímico": 1,
            "vitamina D": 1,
            "Vitamina B12": 1,
            "Orina Completa": 1,
            "Electrocardiograma": 1
        }
    },
    "Chequeo preventivo hombre mas de 45 años": {
        "items": {
            "Creatinina en sangre": 1,
            "Hemograma": 1,
            "V.D.R.L.": 1,
            "Venosa en adulto": 1,
            "Hemoglobina glicada A1c": 1,
            "Perfil lipídico": 1,
            "Electrolitos plasmáticos": 3,
            "Tiroestimulante (TSH)": 1,
            "Tiroxina o tetrayodotironina (T4)": 1,
            "Triyodotironina (T3)": 1,
            "Perfil Hepático": 1,
            "Anticuerpos virales, determ. de H.I.V.": 1,
            "Perfil Bioquímico": 1,
            "vitamina D": 1,
            "Vitamina B12": 1,
            "Orina Completa": 1,
            "Electrocardiograma": 1,
            "Antigeno prostático": 2,
            "Testosterona libre": 1,
            "Testosterona en sangre": 1
        }
    },
    "Detección de anemia": {
        "items": {
            "Fierro": 1,
            "Hemograma": 1
        }
    }
}
