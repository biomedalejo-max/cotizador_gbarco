import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image as RLImage,
    KeepTogether
)
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)
from reportlab.lib.enums import (
    TA_RIGHT,
    TA_CENTER,
    TA_LEFT
)

def formato_cop(valor: float) -> str:
    return f"$ {valor:,.0f}".replace(",", ".")

def generar_documento_pdf(
    datos_oferta: dict,
    productos: list,
    ruta_pdf: str
):
    doc = SimpleDocTemplate(
        ruta_pdf,
        pagesize=letter,
        leftMargin=24,
        rightMargin=24,
        topMargin=26,
        bottomMargin=26
    )

    estilos = getSampleStyleSheet()
    
    style_oferta = ParagraphStyle(
        'Oferta',
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=colors.HexColor('#003366'),
        alignment=TA_RIGHT
    )
    style_fecha = ParagraphStyle(
        'Fecha',
        fontName='Helvetica',
        fontSize=9.5,
        alignment=TA_LEFT
    )
    style_cliente = ParagraphStyle(
        'Cliente',
        fontName='Helvetica',
        fontSize=9,
        leading=13
    )
    style_saludo = ParagraphStyle(
        'Saludo',
        fontName='Helvetica',
        fontSize=8.5,
        leading=12
    )
    style_th = ParagraphStyle(
        'TH',
        fontName='Helvetica-Bold',
        fontSize=8,
        textColor=colors.white,
        alignment=TA_CENTER
    )
    style_td = ParagraphStyle(
        'TD',
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        alignment=TA_LEFT
    )
    style_td_c = ParagraphStyle(
        'TDC',
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        alignment=TA_CENTER
    )
    style_td_bold = ParagraphStyle(
        'TDBold',
        fontName='Helvetica-Bold',
        fontSize=8,
        alignment=TA_CENTER
    )
    style_clausula_t = ParagraphStyle(
        'CT',
        fontName='Helvetica-Bold',
        fontSize=8.5,
        lead
