import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT

def formato_cop(valor: float) -> str:
    return f"$ {valor:,.0f}".replace(",", ".")

def generar_documento_pdf(datos_oferta: dict, productos: list, ruta_pdf: str):
    doc = SimpleDocTemplate(
        ruta_pdf,
        pagesize=letter,
        leftMargin=30,
        rightMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    estilos = getSampleStyleSheet()
    
    style_oferta = ParagraphStyle('Oferta', parent=estilos['Normal'], fontName='Helvetica-Bold', fontSize=11, textColor=colors.HexColor('#003366'), alignment=TA_RIGHT)
    style_fecha = ParagraphStyle('Fecha', parent=estilos['Normal'], fontName='Helvetica', fontSize=9, alignment=TA_LEFT)
    style_cliente = ParagraphStyle('Cliente', parent=estilos['Normal'], fontName='Helvetica', fontSize=9, leading=12)
    style_th = ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=7.5, textColor=colors.white, alignment=TA_CENTER)
    style_td = ParagraphStyle('TD', fontName='Helvetica', fontSize=7, leading=9, alignment=TA_LEFT)
    style_td_c = ParagraphStyle('TDC', fontName='Helvetica', fontSize=7, leading=9, alignment=TA_CENTER)
    style_clausula_t = ParagraphStyle('CT', fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=colors.HexColor('#003366'))
    style_clausula_p = ParagraphStyle('CP', fontName='Helvetica', fontSize=7.5, leading=10)

    story = []

    # 1. Encabezado
    story.append(Paragraph(f"Oferta: {datos_oferta.get('numero_oferta', 'BMZL201449')}", style_oferta))
    story.append(Spacer(1, 4))
    story.append(Paragraph(datos_oferta.get("ciudad_fecha", "Manizales"), style_fecha))
    story.append(Spacer(1, 10))

    # 2. Cliente
    texto_cliente = f"""
    <b>SEÑORES:</b><br/>
    <b>{datos_oferta.get('cliente', '').upper()}</b><br/>
    Nit: {datos_oferta.get('nit', '')}<br/>
    {datos_oferta.get('contacto', '')}<br/>
    {datos_oferta.get('ciudad_cliente', 'La Ciudad')}
    """
    story.append(Paragraph(texto_cliente, style_cliente))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Estimado Cliente,<br/>Atendiendo a su amable solicitud, en G. BARCO S.A. nos complace presentar a su consideración nuestra propuesta comercial.", style_clausula_p))
    story.append(Spacer(1, 10))

    # 3. Tabla de Productos
    story.append(Paragraph("<b>Descripción de los productos:</b>", style_clausula_t))
    story.append(Spacer(1, 5))

    encabezados = [
        Paragraph("Imagen", style_th),
        Paragraph("Ítem", style_th),
        Paragraph("Referencia", style_th),
        Paragraph("Descripción", style_th),
        Paragraph("Cant.", style_th),
        Paragraph("P. Unitario", style_th),
        Paragraph("IVA 19%", style_th),
        Paragraph("Subtotal", style_th),
        Paragraph("Garantía", style_th),
        Paragraph("Visitas", style_th)
    ]
    
    data_tabla = [encabezados]
    subtotal_gral = 0.0
    iva_gral = 0.0

    for idx, prod in enumerate(productos, start=1):
        cant = prod.get("cantidad", 1)
        p_u = prod.get("precio_unitario", 0.0)
        sub = cant * p_u
        iva = sub * 0.19
        subtotal_gral += sub
        iva_gral += iva

        # Cargar imagen en celda
        img_celda = Paragraph("[Sin foto]", style_td_c)
        img_p = prod.get("imagen_path")
        if img_p and os.path.exists(img_p):
            try:
                img_celda = RLImage(img_p, width=42, height=42)
            except Exception:
                pass

        fila = [
            img_celda,
            Paragraph(str(idx), style_td_c),
            Paragraph(str(prod.get("referencia", "")), style_td),
            Paragraph(str(prod.get("descripcion", "")), style_td),
            Paragraph(str(cant), style_td_c),
            Paragraph(formato_cop(p_u), style_td_c),
            Paragraph(formato_cop(iva), style_td_c),
            Paragraph(formato_cop(sub), style_td_c),
            Paragraph(str(prod.get("garantia", "12 meses")), style_td_c),
            Paragraph(str(prod.get("visitas", "2/año")), style_td_c)
        ]
        data_tabla.append(fila)

    # Anchos de columna exactos para hoja Carta
    col_widths = [45, 18, 55, 135, 24, 60, 52, 62, 50, 45]
    tabla_pdf = Table(data_tabla, colWidths=col_widths, repeatRows=1)
    tabla_pdf.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(tabla_pdf)
    story.append(Spacer(1, 10))

    # 4. Tabla de Resumen
    data_resumen = [
        [Paragraph("<b>SUBTOTAL:</b>", style_td), Paragraph(formato_cop(subtotal_gral), style_td_c)],
        [Paragraph("<b>IVA (19%):</b>", style_td), Paragraph(formato_cop(iva_gral), style_td_c)],
        [Paragraph("<b>TOTAL OFERTA:</b>", style_td), Paragraph(f"<b>{formato_cop(subtotal_gral + iva_gral)}</b>", style_td_c)]
    ]
    t_resumen = Table(data_resumen, colWidths=[90, 85], hAlign='RIGHT')
    t_resumen.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),
        ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#F2F2F2')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t_resumen)
    story.append(Spacer(1, 12))

    # 5. Cláusulas
    condiciones = [
        ("MONEDA / VALIDEZ", datos_oferta.get("validez", "Pesos colombianos / Hasta 30 días.")),
        ("PLAZO DE ENTREGA", datos_oferta.get("entrega", "Cinco (5) días salvo previa venta.")),
        ("FORMA DE PAGO", datos_oferta.get("forma_pago", "90 días.")),
        ("GARANTÍA", "Doce (12) meses contra defectos de fabricación exclusivamente."),
        ("INSTALACIÓN", "Los equipos se entregarán instalados y funcionando en la ciudad de compra."),
        ("MANTENIMIENTO", "Dos (2) visitas de mantenimiento preventivo durante la garantía."),
        ("CAPACITACIÓN", "Ilimitada durante la vida útil del equipo.")
    ]

    for tit, cont in condiciones:
        story.append(Paragraph(f"<b>{tit}:</b> {cont}", style_clausula_p))
        story.append(Spacer(1, 3))

    # 6. Firma
    story.append(Spacer(1, 10))
    firma_txt = """
    Cordialmente,<br/><br/>
    <b>ALEJANDRO VALENCIA VARGAS</b><br/>
    REPRESENTANTE DE VENTAS 360<br/>
    G BARCO S.A - CEL: 3117662264
    """
    story.append(Paragraph(firma_txt, style_cliente))

    doc.build(story)
