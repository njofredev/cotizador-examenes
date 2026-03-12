from fpdf import FPDF
import os
from utils import calcular_edad

def generar_cotizacion_pdf(folio, timestamp_emision, nombre_p, doc_id, fecha_nac, prevision, df_sel, t_f, t_c, t_pg, t_pp, pack_nombre=None):
    pdf = FPDF()
    pdf.add_page()
    if os.path.exists("logo_vec.svg"): 
        pdf.image("logo_vec.svg", x=10, y=8, w=15)
    
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 10, f"FOLIO: {folio}", ln=1, align='R')
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(0, 5, f"Fecha de Emisión: {timestamp_emision}", ln=1, align='R')
    
    pdf.set_font("Arial", 'B', 14)
    pdf.ln(10)
    pdf.cell(0, 10, "COTIZACIÓN DIGITAL DE EXÁMENES", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 6, "DATOS DEL PACIENTE:", ln=1)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 6, f"Nombre: {nombre_p}", ln=1)
    pdf.cell(0, 6, f"Documento: {doc_id}", ln=1)
    pdf.cell(0, 6, f"Edad: {calcular_edad(fecha_nac)} años", ln=1)
    pdf.cell(0, 6, f"Previsión: {prevision}", ln=1)
    pdf.ln(5)

    if pack_nombre:
        pdf.set_text_color(120, 120, 120)
        pdf.set_font("Arial", 'I', 8)
        pdf.cell(0, 5, f"Pack seleccionado: {pack_nombre}", ln=1, align='L')
        pdf.set_text_color(0)
    
    h3, h4 = ("Valor Fonasa", "Copago o Valor a pagar") if prevision == "Fonasa" else ("Valor Gral.", "Valor Pref.")
    pdf.set_fill_color(2, 112, 249)
    pdf.set_text_color(255)
    pdf.set_font("Arial", 'B', 8)
    
    w = [20, 80, 15, 37.5, 37.5]
    headers = ["Cod", "Examen", "Cant", h3, h4]
    for i, h in enumerate(headers):
        pdf.cell(w[i], 10, h, 1, 0, 'C', True)
    
    pdf.ln()
    pdf.set_text_color(0)
    pdf.set_font("Arial", '', 8)
    
    for _, r in df_sel.iterrows():
        pdf.cell(w[0], 8, str(r['Código']), 1, 0, 'C')
        # Truncado de nombre para evitar desborde en Hoja 1
        nombre_pdf = str(r['Nombre'])
        if len(nombre_pdf) > 45: nombre_pdf = nombre_pdf[:42] + "..."
        pdf.cell(w[1], 8, f" {nombre_pdf}", 1)
        pdf.cell(w[2], 8, str(int(r['Cant'])), 1, 0, 'C')
        
        v1, v2 = (r['Valor bono Fonasa'], r['Valor copago'] if r['Valor bono Fonasa'] > 0 else r['Valor particular General']) if prevision == "Fonasa" else (r['Valor particular General'], r['Valor particular preferencial'])
        pdf.cell(w[3], 8, f"${(v1*r['Cant']):,.0f}", 1, 0, 'R')
        pdf.cell(w[4], 8, f"${(v2*r['Cant']):,.0f}", 1, 1, 'R')
    
    pdf.set_font("Arial", 'I', 8)
    pdf.set_fill_color(255, 255, 255)
    total_items = int(df_sel['Cant'].sum())
    pdf.cell(w[0]+w[1]+w[2], 6, f"TOTAL DE EXÁMENES COTIZADOS: {total_items}", 0, 0, 'R')
    pdf.ln(6)
    
    pdf.set_font("Arial", 'B', 9)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(w[0]+w[1]+w[2], 10, "TOTAL ESTIMADO A PAGAR", 1, 0, 'R', True)
    res1, res2 = (t_f, t_c) if prevision == "Fonasa" else (t_pg, t_pp)
    pdf.cell(w[3], 10, f"${res1:,.0f}", 1, 0, 'R', True)
    pdf.cell(w[4], 10, f"${res2:,.0f}", 1, 1, 'R', True)
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 8)
    pdf.cell(0, 5, "SUCURSAL LABORATORIO TOMA DE MUESTRAS:", ln=True)
    pdf.set_font("Arial", '', 8)
    pdf.cell(0, 4, "- Av. Vitacura #8620, Comuna de Vitacura.", ln=True)
    pdf.cell(0, 4, "- Sitio Web: www.policlinicotabancura.cl", ln=True)
    
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 8)
    pdf.cell(0, 5, "INDICACIONES IMPORTANTES:", ln=True)
    pdf.set_font("Arial", '', 7)
    pdf.multi_cell(0, 4, f"- Folio: {folio}\n- Validez de la cotización: 30 días.\n- (*) El valor a pagar no considera seguros complementarios. \n- El ayuno no debe superar las 12 horas.\n- Para pruebas PTGO (Curva de Glucosa/Insulina): Sólo con agenda previa a las 08:30am.\n- Valores sujetos a confirmación en sucursal al momento de la atención.\n- Si el paciente es diabético, debe notificar en recepción antes de su atención.\n- Si el examen no es cubierto por Fonasa, aparecerá el valor a pagar en la columna copago.\n- Obtén claridad sobre tus resultados con la evaluación experta de nuestro equipo de medicina general.")

    # --- HOJA 2: ORDEN MÉDICA ---
    pdf.add_page()
    if os.path.exists("logo_vec.svg"): 
        pdf.image("logo_vec.svg", x=10, y=8, w=15)
        
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 10, f"FOLIO: {folio}", ln=1, align='R')
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(0, 5, f"Fecha de Emisión: {timestamp_emision}", ln=1, align='R')

    pdf.set_font("Arial", 'B', 14)
    pdf.ln(10)
    pdf.cell(0, 10, "ORDEN MÉDICA DE EXÁMENES", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 6, "DATOS DEL PACIENTE:", ln=1)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 6, f"Nombre: {nombre_p}", ln=1)
    pdf.cell(0, 6, f"Documento: {doc_id}", ln=1)
    pdf.cell(0, 6, f"Edad: {calcular_edad(fecha_nac)} años", ln=1)
    pdf.ln(10)

    # Tabla simplificada (sin precios)
    pdf.set_fill_color(2, 112, 249)
    pdf.set_text_color(255)
    pdf.set_font("Arial", 'B', 9)
    
    w_om = [30, 130, 30]
    headers_om = ["Código", "Examen Solicitado", "Cant"]
    for i, h in enumerate(headers_om):
        pdf.cell(w_om[i], 10, h, 1, 0, 'C', True)
    
    pdf.ln()
    pdf.set_text_color(0)
    pdf.set_font("Arial", '', 9)
    
    for _, r in df_sel.iterrows():
        pdf.cell(w_om[0], 10, str(r['Código']), 1, 0, 'C')
        # Truncado de nombre para evitar desborde en Hoja 2
        nombre_om = str(r['Nombre'])
        if len(nombre_om) > 70: nombre_om = nombre_om[:67] + "..."
        pdf.cell(w_om[1], 10, f" {nombre_om}", 1)
        pdf.cell(w_om[2], 10, str(int(r['Cant'])), 1, 1, 'C')

    # Firma del Doctor (Centrada al final)
    if os.path.exists("firma_prado.png"):
        current_y = pdf.get_y()
        if current_y > 220:
            pdf.add_page()
        
        pdf.set_y(-65) # 6.5 cm desde el final
        
        # Imagen centrada: Ancho pagina 210, imagen aprox 60
        img_w = 60
        pdf.image("firma_prado.png", x=(210-img_w)/2, w=img_w)
        
        pdf.set_y(-35)
        pdf.set_font("Arial", 'B', 9)
        pdf.cell(0, 4, "Dr. Cristian Prado Jara", ln=1, align='C')
        pdf.set_font("Arial", '', 9)
        pdf.cell(0, 4, "Medicina General", ln=1, align='C')
        pdf.cell(0, 4, "10363519-5", ln=1, align='C')

    path = f"Cot_{folio}.pdf"
    pdf.output(path)
    return path
