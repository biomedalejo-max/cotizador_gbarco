import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT

def formato_cop(valor: float) -> str:
    return f"$ {valor:,.0f}".replace(",", ".")

def generar_documento_pdf(datos_oferta: dict, productos: list, ruta_pdf: str):
    # Márgenes de 24 puntos para ganar espacio horizontal
    doc = SimpleDocTemplate(
        ruta_pdf,
        pagesize=letter,
        leftMargin=24,
        rightMargin=24,
        topMargin=26,
        bottomMargin=26
    )

    estilos = getSampleStyleSheet()
    
    style_oferta = ParagraphStyle('Oferta', parent=estilos['Normal'], fontName='Helvetica-Bold', fontSize=12, textColor=colors.HexColor('#003366'), alignment=TA_RIGHT)
    style_fecha = ParagraphStyle('Fecha', parent=estilos['Normal'], fontName='Helvetica', fontSize=9.5, alignment=TA_LEFT)
    style_cliente = ParagraphStyle('Cliente', parent=estilos['Normal'], fontName='Helvetica', fontSize=9, leading=13)
    style_saludo = ParagraphStyle('Saludo', parent=estilos['Normal'], fontName='Helvetica', fontSize=8.5, leading=12)
    
    # Encabezados de tabla: sin partir palabras
    style_th = ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white, alignment=TA_CENTER)
    style_td = ParagraphStyle('TD', fontName='Helvetica', fontSize=7.5, leading=10, alignment=TA_LEFT)
    style_td_c = ParagraphStyle('TDC', fontName='Helvetica', fontSize=7.5, leading=10, alignment=TA_CENTER)
    style_td_bold = ParagraphStyle('TDBold', fontName='Helvetica-Bold', fontSize=8, alignment=TA_CENTER)
    
    style_clausula_t = ParagraphStyle('CT', fontName='Helvetica-Bold', fontSize=8.5, leading=12, textColor=colors.HexColor('#003366'))
    style_clausula_p = ParagraphStyle('CP', fontName='Helvetica', fontSize=8, leading=11)
    style_firma = ParagraphStyle('Firma', fontName='Helvetica', fontSize=8.5, leading=12)

    story = []
# 1. ENCABEZADO
    story.append(Paragraph(f"Oferta: {datos_oferta.get('numero_oferta', 'BMZL201449')}", style_oferta))
    story.append(Spacer(1, 10))  # <-- Espacio entre Oferta y Fecha
    story.append(Paragraph(datos_oferta.get("ciudad_fecha", "Manizales"), style_fecha))
    
    # 👇 1. ESPACIO ENTRE LA FECHA Y LOS DATOS DEL CLIENTE:
    # Cámbialo de 12 a 25 (o 30 si quieres aún más aire)
    story.append(Spacer(1, 25))

    # 2. CLIENTE
    texto_cliente = f"""
    <b>SEÑORES:</b><br/>
    <b>{datos_oferta.get('cliente', '').upper()}</b><br/>
    Nit: {datos_oferta.get('nit', '')}<br/>
    {datos_oferta.get('contacto', '')}<br/>
    {datos_oferta.get('ciudad_cliente', 'La Ciudad')}
    """
    story.append(Paragraph(texto_cliente, style_cliente))

    # 👇 2. ESPACIO ENTRE DATOS DEL CLIENTE Y EL SIGUIENTE BLOQUE (Saludo):
    # Cámbialo de 10 a 20 (o 25 si lo quieres más separado)
    story.append(Spacer(1, 20))
    """
    story.append(Paragraph(texto_cliente, style_cliente))
    story.append(Spacer(1, 10))

    story.append(Paragraph(
        "Estimado Cliente,<br/>"
        "Atendiendo a su amable solicitud, en <b>G. BARCO S.A.</b> nos complace presentar a su "
        "consideración nuestra propuesta comercial para la adquisición de los siguientes equipos:", 
        style_saludo
    ))
    story.append(Spacer(1, 12))

    # 3. TABLA DE PRODUCTOS (ANCHO OPTIMIZADO)
    story.append(Paragraph("<b>Descripción de los productos:</b>", style_clausula_t))
    story.append(Spacer(1, 6))

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

        img_celda = Paragraph("[Sin foto]", style_td_c)
        img_p = prod.get("imagen_path")
        if img_p and os.path.exists(img_p):
            try:
                # Foto más amplia y proporcionada
                img_celda = RLImage(img_p, width=48, height=44)
            except Exception:
                pass

        fila = [
            img_celda,
            Paragraph(str(idx), style_td_c),
            Paragraph(str(prod.get("referencia", "")), style_td_c),
            Paragraph(str(prod.get("descripcion", "")), style_td),
            Paragraph(str(cant), style_td_c),
            Paragraph(formato_cop(p_u), style_td_c),
            Paragraph(formato_cop(iva), style_td_c),
            Paragraph(formato_cop(sub), style_td_c),
            Paragraph(str(prod.get("garantia", "12 meses")), style_td_c),
            Paragraph(str(prod.get("visitas", "2/año")), style_td_c)
        ]
        data_tabla.append(fila)

    # Ancho total: 564 puntos (aprovecha la hoja completa sin partir palabras)
    # [Imagen, Ítem, Referencia, Descripción, Cant, P. Unit, IVA, Subtotal, Garantía, Visitas]
    col_widths = [54, 24, 70, 142, 28, 64, 58, 66, 48, 40]
    
    tabla_pdf = Table(data_tabla, colWidths=col_widths, repeatRows=1)
    tabla_pdf.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#B0C4DE')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(tabla_pdf)
    story.append(Spacer(1, 14))

    # 4. TABLA DE RESUMEN
    data_resumen = [
        [Paragraph("<b>SUBTOTAL:</b>", style_td), Paragraph(formato_cop(subtotal_gral), style_td_c)],
        [Paragraph("<b>IVA (19%):</b>", style_td), Paragraph(formato_cop(iva_gral), style_td_c)],
        [Paragraph("<b>TOTAL OFERTA:</b>", style_td), Paragraph(f"<b>{formato_cop(subtotal_gral + iva_gral)}</b>", style_td_bold)]
    ]
    t_resumen = Table(data_resumen, colWidths=[100, 95], hAlign='RIGHT')
    t_resumen.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),
        ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#EBF3FB')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_resumen)
    story.append(Spacer(1, 16))

    # 5. CONDICIONES COMERCIALES (CON MEJOR ESPACIADO)
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
        story.append(Spacer(1, 4))

    # 6. FIRMA FORMAL CON LÍNEA Y ESPACIO SUFICIENTE
    story.append(Spacer(1, 28))
    
    bloque_firma = []
    bloque_firma.append(Paragraph("Cordialmente,", style_firma))
    bloque_firma.append(Spacer(1, 35))  # Espacio amplio para firmar a mano o sello digital
    bloque_firma.append(Paragraph("________________________________________________", style_firma))
    bloque_firma.append(Paragraph("<b>ALEJANDRO VALENCIA VARGAS</b>", style_firma))
    bloque_firma.append(Paragraph("Representante de Ventas 360", style_firma))
    bloque_firma.append(Paragraph("<b>G. BARCO S.A.</b> | Cel: 3117662264", style_firma))
    
    # KeepTogether asegura que la firma no quede huérfana en otra página si cabe aquí
    story.append(KeepTogether(bloque_firma))

    doc.build(story)
