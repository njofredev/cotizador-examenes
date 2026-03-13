from fpdf import FPDF
import os
from utils import calcular_edad

class PDF(FPDF):
    def __init__(self, folio_cot, folio_om, timestamp_emision):
        super().__init__()
        self.folio_cot = folio_cot
        self.folio_om = folio_om
        self.timestamp_emision = timestamp_emision
        self.seccion_actual = "COTIZACIÓN"
        self.paginas_por_seccion = {"COTIZACIÓN": [], "ORDEN MÉDICA": []}
        self.total_paginas_seccion = {"COTIZACIÓN": 0, "ORDEN MÉDICA": 0}

    def header(self):
        if os.path.exists("logo_vec.svg"):
            self.image("logo_vec.svg", x=10, y=8, w=15)
        
        folio = self.folio_cot if self.seccion_actual == "COTIZACIÓN" else self.folio_om
        
        self.set_font("Arial", 'B', 8)
        self.cell(0, 5, f"FOLIO: {folio}", ln=1, align='R')
        self.set_font("Arial", 'I', 7)
        self.cell(0, 4, f"Fecha: {self.timestamp_emision}", ln=1, align='R')
        
        # Registrar página en la sección si no está (evita ValueError)
        if self.page_no() not in self.paginas_por_seccion[self.seccion_actual]:
            self.paginas_por_seccion[self.seccion_actual].append(self.page_no())
        
        pagina_relativa = self.paginas_por_seccion[self.seccion_actual].index(self.page_no()) + 1
        total_relativo = self.total_paginas_seccion[self.seccion_actual]
        
        # Si por alguna razón nos pasamos del estimado, ajustamos el total mostrado
        if pagina_relativa > total_relativo: 
            total_relativo = pagina_relativa
            self.total_paginas_seccion[self.seccion_actual] = total_relativo
        
        self.cell(0, 4, f"Página {pagina_relativa} de {total_relativo}", ln=1, align='R')
        self.ln(5)

def generar_cotizacion_pdf(folio_cot, folio_om, timestamp_emision, nombre_p, doc_id, fecha_nac, prevision, df_sel, t_f, t_c, t_pg, t_pp, pack_nombre=None, incluir_om=False):
    
    def renderizar_contenido(pdf_obj, fase_conteo=False):
        """Función interna para renderizar el contenido. Se llama dos veces."""
        # --- SECCIÓN: COTIZACIÓN ---
        pdf_obj.seccion_actual = "COTIZACIÓN"
        pdf_obj.add_page()
        
        pdf_obj.set_font("Arial", 'B', 14)
        pdf_obj.ln(3)
        pdf_obj.cell(0, 8, "COTIZACIÓN DIGITAL DE EXÁMENES", ln=True, align='C')
        pdf_obj.ln(2)
        
        # Bloque de datos del paciente - FORMATO HORIZONTAL
        pdf_obj.set_font("Arial", 'B', 9)
        pdf_obj.cell(0, 5, "DATOS DEL PACIENTE:", ln=1)
        pdf_obj.set_font("Arial", '', 9)
        
        # Fila 1: Nombre y Documento
        pdf_obj.cell(100, 5, f"Nombre: {nombre_p}", 0, 0)
        pdf_obj.cell(90, 5, f"Documento: {doc_id}", 0, 1)
        
        # Fila 2: Edad y Previsión
        pdf_obj.cell(100, 5, f"Edad: {calcular_edad(fecha_nac)} años", 0, 0)
        pdf_obj.cell(90, 5, f"Previsión: {prevision}", 0, 1)
        
        if pack_nombre:
            pdf_obj.set_text_color(100, 100, 100)
            pdf_obj.set_font("Arial", 'I', 8)
            pdf_obj.cell(0, 5, f"Pack: {pack_nombre}", ln=1, align='L')
            pdf_obj.set_text_color(0)
        
        pdf_obj.ln(2)
        
        # Cabecera de tabla
        h3, h4 = ("Valor Fonasa", "Copago o Valor a pagar") if prevision == "Fonasa" else ("Valor Gral.", "Valor Pref.")
        pdf_obj.set_fill_color(2, 112, 249)
        pdf_obj.set_text_color(255)
        pdf_obj.set_font("Arial", 'B', 8)
        
        w = [20, 80, 15, 37.5, 37.5]
        headers = ["Cod", "Examen", "Cant", h3, h4]
        for i, h in enumerate(headers):
            pdf_obj.cell(w[i], 8, h, 1, 0, 'C', True)
        
        pdf_obj.ln()
        pdf_obj.set_text_color(0)
        pdf_obj.set_font("Arial", '', 8)
        
        # Filas de exámenes - ALTURA REDUCIDA A 6mm
        for _, r in df_sel.iterrows():
            if pdf_obj.get_y() > 265:
                pdf_obj.add_page()
                pdf_obj.set_fill_color(2, 112, 249)
                pdf_obj.set_text_color(255)
                pdf_obj.set_font("Arial", 'B', 8)
                for i, h in enumerate(headers):
                    pdf_obj.cell(w[i], 8, h, 1, 0, 'C', True)
                pdf_obj.ln()
                pdf_obj.set_text_color(0)
                pdf_obj.set_font("Arial", '', 8)

            pdf_obj.cell(w[0], 6, str(r['Código']), 1, 0, 'C')
            nombre_pdf = str(r['Nombre'])
            if len(nombre_pdf) > 48: nombre_pdf = nombre_pdf[:45] + "..."
            pdf_obj.cell(w[1], 6, f" {nombre_pdf}", 1)
            pdf_obj.cell(w[2], 6, str(int(r['Cant'])), 1, 0, 'C')
            
            v1, v2 = (r['Valor bono Fonasa'], r['Valor copago'] if r['Valor bono Fonasa'] > 0 else r['Valor particular General']) if prevision == "Fonasa" else (r['Valor particular General'], r['Valor particular preferencial'])
            pdf_obj.cell(w[3], 6, f"${(v1*r['Cant']):,.0f}", 1, 0, 'R')
            pdf_obj.cell(w[4], 6, f"${(v2*r['Cant']):,.0f}", 1, 1, 'R')
        
        # Bloque de Totales
        if pdf_obj.get_y() > 225: pdf_obj.add_page()
        pdf_obj.ln(1)
        pdf_obj.set_font("Arial", 'B', 9)
        pdf_obj.set_fill_color(240, 240, 240)
        pdf_obj.cell(w[0]+w[1]+w[2], 8, "Total estimado a pagar", 1, 0, 'R', True)
        res1, res2 = (t_f, t_c) if prevision == "Fonasa" else (t_pg, t_pp)
        pdf_obj.cell(w[3], 8, f"${res1:,.0f}", 1, 0, 'R', True)
        pdf_obj.cell(w[4], 8, f"${res2:,.0f}", 1, 1, 'R', True)

        pdf_obj.set_font("Arial", 'I', 8)
        pdf_obj.cell(w[0]+w[1]+w[2], 5, f"Total exámenes cotizados: {int(df_sel['Cant'].sum())}", 0, 1, 'R')
        
        pdf_obj.ln(2)
        pdf_obj.set_font("Arial", 'B', 8)
        pdf_obj.cell(0, 4, "SUCURSAL LABORATORIO TOMA DE MUESTRAS:", ln=True)
        pdf_obj.set_font("Arial", '', 8)
        pdf_obj.cell(0, 4, "- Av. Vitacura #8620, Comuna de Vitacura | www.policlinicotabancura.cl", ln=True)
        
        pdf_obj.ln(2)
        pdf_obj.set_font("Arial", 'B', 8)
        pdf_obj.cell(0, 4, "INDICACIONES IMPORTANTES:", ln=True)
        pdf_obj.set_font("Arial", '', 7.5)
        pdf_obj.multi_cell(0, 3.5, f"- Folio Cotización: {folio_cot} | Validez: 30 días.\n- (*) El valor a pagar no considera seguros complementarios. Ayuno máximo 12 horas.\n- Pruebas PTGO (Curva Glucosa/Insulina): Sólo agenda previa 08:30am.\n- Valores sujetos a confirmación en sucursal. Notificar diabetes antes de atención.\n- Si el examen no es cubierto por Fonasa, aplica valor en columna copago.\n- Evaluación experta disponible con nuestro equipo de medicina general.")

        # --- SECCIÓN: ORDEN MÉDICA ---
        if incluir_om:
            pdf_obj.seccion_actual = "ORDEN MÉDICA"
            pdf_obj.add_page()
            
            pdf_obj.set_font("Arial", 'B', 14)
            pdf_obj.ln(3)
            pdf_obj.cell(0, 8, "ORDEN MÉDICA DE EXÁMENES", ln=True, align='C')
            pdf_obj.ln(3)

            pdf_obj.set_font("Arial", 'B', 9)
            pdf_obj.cell(0, 5, "DATOS DEL PACIENTE:", ln=1)
            pdf_obj.set_font("Arial", '', 9)
            
            # Fila 1: Nombre y Documento
            pdf_obj.cell(100, 5, f"Nombre: {nombre_p}", 0, 0)
            pdf_obj.cell(90, 5, f"Documento: {doc_id}", 0, 1)
            
            # Fila 2: Edad
            pdf_obj.cell(0, 5, f"Edad: {calcular_edad(fecha_nac)} años", 0, 1)
            pdf_obj.ln(3)

            pdf_obj.set_fill_color(2, 112, 249)
            pdf_obj.set_text_color(255)
            pdf_obj.set_font("Arial", 'B', 9)
            w_om = [30, 130, 30]
            headers_om = ["Código", "Examen Solicitado", "Cant"]
            for i, h in enumerate(headers_om):
                pdf_obj.cell(w_om[i], 8, h, 1, 0, 'C', True)
            
            pdf_obj.ln()
            pdf_obj.set_text_color(0)
            pdf_obj.set_font("Arial", '', 9)
            
            # Filas de OM - ALTURA REDUCIDA A 7mm
            for _, r in df_sel.iterrows():
                if pdf_obj.get_y() > 260:
                    pdf_obj.add_page()
                    pdf_obj.set_fill_color(2, 112, 249)
                    pdf_obj.set_text_color(255)
                    pdf_obj.set_font("Arial", 'B', 9)
                    for i, h in enumerate(headers_om):
                        pdf_obj.cell(w_om[i], 8, h, 1, 0, 'C', True)
                    pdf_obj.ln()
                    pdf_obj.set_text_color(0)
                    pdf_obj.set_font("Arial", '', 9)

                pdf_obj.cell(w_om[0], 7, str(r['Código']), 1, 0, 'C')
                pdf_obj.cell(w_om[1], 7, f" {str(r['Nombre'])[:75]}", 1)
                pdf_obj.cell(w_om[2], 7, str(int(r['Cant'])), 1, 1, 'C')

            if os.path.exists("firma_prado.png"):
                if pdf_obj.get_y() > 230: pdf_obj.add_page()
                pdf_obj.ln(10)
                curr_y = pdf_obj.get_y()
                pdf_obj.image("firma_prado.png", x=77.5, y=curr_y, w=50)
                pdf_obj.set_y(curr_y + 22)
                pdf_obj.set_font("Arial", 'B', 8.5)
                pdf_obj.cell(0, 4, "Dr. Cristian Prado Jara", ln=1, align='C')
                pdf_obj.set_font("Arial", '', 8.5)
                pdf_obj.cell(0, 4, "Medicina General / 10363519-5", ln=1, align='C')

    # PASO 1: Conteo
    pdf_count = PDF(folio_cot, folio_om, timestamp_emision)
    renderizar_contenido(pdf_count, fase_conteo=True)
    
    # Extraer conteos
    final_counts = {sec: len(paginas) for sec, paginas in pdf_count.paginas_por_seccion.items()}
    
    # PASO 2: Generación Real
    pdf_real = PDF(folio_cot, folio_om, timestamp_emision)
    pdf_real.total_paginas_seccion = final_counts
    renderizar_contenido(pdf_real, fase_conteo=False)

    path = f"Cot_{folio_cot}.pdf"
    pdf_real.output(path)
    return path

    return path
