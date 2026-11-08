import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def formato_cop(valor: float) -> str:
    """Formatea valores en pesos colombianos."""
    return f"$ {valor:,.0f}".replace(",", ".")

def aplicar_estilo_encabezado(celda, texto):
    celda.text = texto
    shading = parse_xml(r'<w:shd {} w:fill="003366"/>'.format(nsdecls('w')))
    celda._tc.get_or_add_tcPr().append(shading)
    p = celda.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in p.runs:
        run.font.bold = True
        run.font.size = Pt(8.5)
        run.font.color.rgb = RGBColor(255, 255, 255)
        run.font.name = "Arial"

def fijar_bordes_tabla(tabla):
    tblPr = tabla._tbl.tblPr
    borders = parse_xml(
        r'<w:tblBorders {} >'
        r'<w:top w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/>'
        r'<w:left w:val="none"/>'
        r'<w:bottom w:val="single" w:sz="6" w:space="0" w:color="003366"/>'
        r'<w:right w:val="none"/>'
        r'<w:insideH w:val="single" w:sz="4" w:space="0" w:color="E0E0E0"/>'
        r'<w:insideV w:val="none"/>'
        r'</w:tblBorders>'.format(nsdecls('w'))
    )
    tblPr.append(borders)

def generar_documento_oferta(datos_oferta: dict, productos: list, ruta_salida: str):
    doc = Document()
    
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.7)
        section.right_margin = Inches(0.7)

    # Encabezado
    p_oferta = doc.add_paragraph()
    p_oferta.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run_oferta = p_oferta.add_run(f"Oferta: {datos_oferta.get('numero_oferta', 'BMZL201449')}")
    run_oferta.bold = True
    run_oferta.font.size = Pt(12)
    run_oferta.font.color.rgb = RGBColor(0, 51, 102)

    p_fecha = doc.add_paragraph(datos_oferta.get("ciudad_fecha", "Manizales"))
    p_fecha.paragraph_format.space_after = Pt(14)

    # Cliente
    p_cliente = doc.add_paragraph()
    p_cliente.add_run("SEÑORES:\n").bold = True
    p_cliente.add_run(f"{datos_oferta.get('cliente', '').upper()}\n").bold = True
    p_cliente.add_run(f"Nit: {datos_oferta.get('nit', '')}\n")
    p_cliente.add_run(f"{datos_oferta.get('contacto', '')}\n")
    p_cliente.add_run(f"{datos_oferta.get('ciudad_cliente', 'La Ciudad')},\n")
    p_cliente.paragraph_format.space_after = Pt(12)

    p_saludo = doc.add_paragraph(
        "Estimado Cliente,\n\n"
        "Atendiendo a su amable solicitud, en G. BARCO S.A. nos complace presentar a su "
        "consideración nuestra propuesta comercial para la adquisición de los siguientes equipos."
    )
    p_saludo.paragraph_format.space_after = Pt(12)

    # Tabla productos
    doc.add_heading("Descripción de los productos:", level=3)
    columnas = ["Imagen", "Ítem", "Referencia", "Descripción / Características", "Cant.", "Precio Unitario", "IVA 19%", "Subtotal", "Garantía", "Visitas/Año"]
    tabla = doc.add_table(rows=1, cols=len(columnas))
    tabla.alignment = WD_TABLE_ALIGNMENT.CENTER
    fijar_bordes_tabla(tabla)

    for i, col in enumerate(columnas):
        aplicar_estilo_encabezado(tabla.rows[0].cells[i], col)

    subtotal_general = 0.0
    iva_general = 0.0

    for idx, prod in enumerate(productos, start=1):
        cant = prod.get("cantidad", 1)
        p_unit = prod.get("precio_unitario", 0.0)
        subtotal_item = cant * p_unit
        iva_item = subtotal_item * 0.19
        subtotal_general += subtotal_item
        iva_general += iva_item

        row = tabla.add_row().cells
        img_path = prod.get("imagen_path")
        if img_path and os.path.exists(img_path):
            try:
                p_img = row[0].paragraphs[0]
                p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_img.add_run().add_picture(img_path, width=Inches(0.85))
            except Exception:
                row[0].text = "[Sin Imagen]"
        else:
            row[0].text = "[Sin Imagen]"

        row[1].text = str(idx)
        row[2].text = str(prod.get("referencia", ""))
        row[3].text = str(prod.get("descripcion", ""))
        row[4].text = str(cant)
        row[5].text = formato_cop(p_unit)
        row[6].text = formato_cop(iva_item)
        row[7].text = formato_cop(subtotal_item)
        row[8].text = str(prod.get("garantia", "12 meses"))
        row[9].text = str(prod.get("visitas", "2 visitas/año"))

        for c in row:
            c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            for par in c.paragraphs:
                for r in par.runs:
                    r.font.size = Pt(8)
                    r.font.name = "Arial"

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # Resumen
    doc.add_heading("Resumen de la oferta:", level=3)
    tabla_res = doc.add_table(rows=3, cols=2)
    tabla_res.alignment = WD_TABLE_ALIGNMENT.RIGHT
    fijar_bordes_tabla(tabla_res)

    res_data = [
        ("SUBTOTAL:", formato_cop(subtotal_general)),
        ("IVA (19%):", formato_cop(iva_general)),
        ("TOTAL OFERTA:", formato_cop(subtotal_general + iva_general))
    ]

    for i, (k, v) in enumerate(res_data):
        c0, c1 = tabla_res.rows[i].cells[0], tabla_res.rows[i].cells[1]
        c0.text, c1.text = k, v
        c0.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
        c1.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
        if i == 2:
            c0.paragraphs[0].runs[0].font.bold = True
            c1.paragraphs[0].runs[0].font.bold = True

    doc.add_paragraph().paragraph_format.space_after = Pt(14)

    # Cláusulas legales
    condiciones = [
        ("MONEDA DE NEGOCIACIÓN / VALIDEZ DE LA OFERTA", datos_oferta.get("validez", "Pesos colombianos / Hasta 30 días.")),
        ("PLAZO DE ENTREGA", datos_oferta.get("entrega", "Cinco (5) días salvo previa venta.")),
        ("FORMA DE PAGO", datos_oferta.get("forma_pago", "90 días.")),
        ("GARANTÍA", "Doce (12) meses contra defectos de fabricación exclusivamente."),
        ("INSTALACIÓN", "Los equipos se entregarán instalados y funcionando a entera satisfacción en la ciudad de compra."),
        ("MANTENIMIENTO PREVENTIVO", "Dos (2) visitas anuales durante los 12 meses de garantía."),
        ("MANTENIMIENTO CORRECTIVO", "Ilimitado durante la vigencia de la garantía."),
        ("ENTRENAMIENTO Y CAPACITACIÓN", "Ilimitada durante la vida útil del equipo.")
    ]

    for tit, cont in condiciones:
        p_t = doc.add_paragraph()
        p_t.add_run(tit).bold = True
        doc.add_paragraph(cont)

    # Firma
    doc.add_paragraph("\nCordialmente,\n\n")
    p_f = doc.add_paragraph()
    p_f.add_run("ALEJANDRO VALENCIA VARGAS\n").bold = True
    p_f.add_run("REPRESENTANTE DE VENTAS 360\n")
    p_f.add_run("G BARCO S.A\n")
    p_f.add_run("CEL: 3117662264")

    doc.save(ruta_salida)