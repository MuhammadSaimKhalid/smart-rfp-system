from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from io import BytesIO
import datetime

def generate_rfp_pdf(rfp, buffer):
    """
    Generates a PDF for the given RFP object and writes it to the buffer.
    """
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = styles["Title"]
    heading_style = styles["Heading2"]
    normal_style = styles["Normal"]
    
    story = []
    
    # --- Title & Metadata ---
    story.append(Paragraph(rfp.title, title_style))
    story.append(Spacer(1, 12))
    
    meta_data = [
        f"<b>Status:</b> {rfp.status}",
        f"<b>Created Date:</b> {rfp.created_at.strftime('%Y-%m-%d') if rfp.created_at else 'N/A'}",
        f"<b>Deadline:</b> {rfp.deadline or 'N/A'}",
        f"<b>Budget:</b> ${rfp.budget:,.2f}" if rfp.budget else "<b>Budget:</b> TBD"
    ]
    for meta in meta_data:
        story.append(Paragraph(meta, normal_style))
    
    story.append(Spacer(1, 12))
    
    # --- Scope / Description ---
    if rfp.description:
        story.append(Paragraph("Scope of Work", heading_style))
        story.append(Paragraph(rfp.description, normal_style))
        story.append(Spacer(1, 12))
        
    # --- Requirements ---
    if rfp.requirements:
        story.append(Paragraph("Requirements", heading_style))
        req_items = []
        for req in rfp.requirements:
            # req is a dict like {'text': '...', 'source': '...'} or just text
            text = req.get('text', '') if isinstance(req, dict) else str(req)
            req_items.append(ListItem(Paragraph(text, normal_style)))
        
        story.append(ListFlowable(req_items, bulletType='bullet', start='circle'))
        story.append(Spacer(1, 12))

    # --- Proposal Submission Form ---
    if rfp.proposal_form_rows:
        story.append(Paragraph("Proposal Submission Form", heading_style))
        story.append(Paragraph("Vendors must fill out the following unit prices:", normal_style))
        story.append(Spacer(1, 12))
        
        # Table Data
        # Headers
        table_data = [['Section', 'Item', 'Description', 'Unit', 'Qty']]
        
        # Rows
        # Group by section for readability? Or just list. 
        # For PDF table, flat list is okay, maybe color alternate rows.
        for row in rfp.proposal_form_rows:
            section = row.get('section', '') or ''
            item_id = row.get('item_id', '')
            desc = row.get('description', '')
            unit = row.get('unit', '') or ''
            qty = row.get('quantity', '') or ''
            
            # Truncate desc if too long? Paragraph handles wrapping.
            # Using Paragraph in cell allows wrapping.
            table_data.append([
                Paragraph(section, normal_style),
                item_id,
                Paragraph(desc, normal_style),
                unit,
                qty
            ])
            
        # Column Widths
        col_widths = [1.2*inch, 0.6*inch, 2.5*inch, 0.7*inch, 0.7*inch]
        
        t = Table(table_data, colWidths=col_widths)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(t)

    doc.build(story)
