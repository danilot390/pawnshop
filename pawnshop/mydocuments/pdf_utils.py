from reportlab.lib.pagesizes import legal
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_RIGHT
from reportlab.platypus import PageBreak, SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import cm

import io

def build_pdf(response, title, body, sellers_sign=None, buyers_sign=None, date=None):
    """
    This function generates a PDF document using ReportLab, combining multiuple sections
    of titles, bodies, and optional signer information. It constructs paragraphs with
    specified styles, handles page breack between sections, and includes signatory 
    details if provided. The generated PDF is streamed directly to the provided
    HttpResponse objedct 'response'.
    """
    def signers (sign1, sign2):
        elements.append(Spacer(1,36))
        data = [
            [Paragraph(sign1['name'], custom_center_style), 
             Paragraph(sign2['name'], custom_center_style),],
            [Paragraph(sign1['ci'], custom_center_style), 
             Paragraph(sign2['ci'], custom_center_style),],
            [Paragraph(sign1['foot'], custom_center_style), 
             Paragraph(sign2['foot'], custom_center_style),],
        ]
        table = Table(data, colWidths=[doc.width/2.0]*2)
        table.setStyle(TableStyle([
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
            ('TOPPADDING',(0,0),(-1,-1),0),
        ]))
        elements.append(table)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=legal,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=3*cm,
        bottomMargin=2*cm,
    )

    styles = getSampleStyleSheet()
    normal_style = styles['Normal']
    title_style = styles['Title']

    custom_title_style = ParagraphStyle(
        'CustomTitle',
        parent=title_style,
        fontName='Times-Roman',
        fontSize=13,
        leading=15,
        spacerAfter=17,
    )
    custom_body_style= ParagraphStyle(
        'CustomBody',
        parent=normal_style,
        fontName='Times-Roman',
        fontSize=11,
        leading=16,
        spacerAfter=12,
        alignment=TA_JUSTIFY,
    )
    custom_center_style= ParagraphStyle(
        'CustomCenter',
        parent=normal_style,
        fontName='Times-Roman',
        fontSize=11,
        leading=12,
        alignment=TA_CENTER,
    )
    custom_right_style =ParagraphStyle(
        'CustomRight',
        parent=normal_style,
        fontName='Times-Roman',
        fontSize=11,
        leading=12,
        alignment=TA_RIGHT,
    )

    elements = []
    for i in range(len(title)):
        if i != 0:
            elements.append(PageBreak())
        elements.append(Paragraph(title[i], custom_title_style))
        elements.append(Spacer(1,12))

        paragraphs = str(body[i]).split('\n')
        for para in paragraphs:
            elements.append(Paragraph(para.strip(), custom_body_style))
            elements.append(Spacer(1,12))

        if date is not None:
            elements.append(Spacer(1,12))
            elements.append(Paragraph(str(date[i]), custom_right_style))

        if sellers_sign is not None:
            signers(sellers_sign, buyers_sign)

    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)

    return response