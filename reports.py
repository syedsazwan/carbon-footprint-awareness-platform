import io
import csv
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import pandas as pd
import streamlit as st
import database as db

def generate_pdf_report(user: dict, month_entry: dict):
    """Generate a clean, beautiful PDF report using ReportLab and return it as bytes."""
    buffer = io.BytesIO()
    
    # Page setup
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    # Custom colors
    PRIMARY_COLOR = colors.HexColor("#0c3b2e")
    SECONDARY_COLOR = colors.HexColor("#6d9773")
    LIGHT_GREEN = colors.HexColor("#f3f9f6")
    TEXT_DARK = colors.HexColor("#2c3e50")
    
    # Custom Paragraph Styles
    title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        textColor=colors.white,
        spaceAfter=15,
        alignment=1 # Center
    )
    
    subtitle_style = ParagraphStyle(
        'ReportSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=10,
        textColor=colors.white,
        alignment=1
    )
    
    h2_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=16,
        textColor=PRIMARY_COLOR,
        spaceBefore=15,
        spaceAfter=8
    )
    
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=10,
        textColor=TEXT_DARK,
        spaceAfter=6,
        leading=14
    )
    
    bullet_style = ParagraphStyle(
        'BulletPoint',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=TEXT_DARK,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4,
        leading=12
    )

    # 1. Header Banner
    banner_data = [
        [Paragraph("CARBON FOOTPRINT REPORT", title_style)],
        [Paragraph(f"Analysis for the Month of {month_entry['month']}", subtitle_style)]
    ]
    banner_table = Table(banner_data, colWidths=[530])
    banner_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), PRIMARY_COLOR),
        ('PADDING', (0,0), (-1,-1), 18),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,1), (-1,1), 12),
    ]))
    story.append(banner_table)
    story.append(Spacer(1, 15))
    
    created_at_val = month_entry.get('created_at', '')
    created_date = created_at_val[:10] if (created_at_val and len(created_at_val) >= 10) else datetime.now().strftime("%Y-%m-%d")
    
    # 2. User & Meta Details Card
    meta_data = [
        [
            Paragraph(f"<b>Name:</b> {user['name']}", body_style),
            Paragraph(f"<b>Date Generated:</b> {created_date}", body_style)
        ],
        [
            Paragraph(f"<b>Username:</b> @{user['username']}", body_style),
            Paragraph(f"<b>Carbon Category:</b> {month_entry['score_category']}", body_style)
        ],
        [
            Paragraph(f"<b>Email:</b> {user['email']}", body_style),
            Paragraph(f"<b>Eco Points Earned:</b> {user['eco_points']}", body_style)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[265, 265])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_GREEN),
        ('PADDING', (0,0), (-1,-1), 8),
        ('BOX', (0,0), (-1,-1), 1, SECONDARY_COLOR),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 15))
    
    # 3. Executive Summary
    story.append(Paragraph("Executive Summary", h2_style))
    score = month_entry['score_category']
    total_em = month_entry['total_emissions']
    
    if score == "Green":
        summary_text = f"Congratulations! Your monthly carbon footprint of <b>{total_em} kg CO₂</b> places you in the <b>Green (Low Emissions)</b> category. Your lifestyle habits are highly sustainable and reflect a strong commitment to environmental conservation. Keep up the fantastic work! Refer to the recommendations below to maintain or further optimize your carbon footprint."
    elif score == "Yellow":
        summary_text = f"Your monthly carbon footprint of <b>{total_em} kg CO₂</b> places you in the <b>Yellow (Moderate Emissions)</b> category. While you are doing better than many, there is significant room for improvement. By making minor changes in your daily travel, electricity conservation, and dining habits, you can transition into the elite Green zone."
    else:
        summary_text = f"Your monthly carbon footprint of <b>{total_em} kg CO₂</b> is in the <b>Red (High Emissions)</b> category. This level of emissions is unsustainable and contributes significantly to climate change. We recommend reviewing the category breakdown below and focusing on immediate carbon reduction strategies, particularly in your highest-emitting activities."
        
    story.append(Paragraph(summary_text, body_style))
    story.append(Spacer(1, 15))
    
    # 4. Emissions Breakdown Table
    story.append(Paragraph("Emissions Breakdown", h2_style))
    
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=colors.white
    )
    
    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=TEXT_DARK
    )
    
    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=TEXT_DARK
    )
    
    def get_pct(val):
        return f"{(val / total_em) * 100:.1f}%" if total_em > 0 else "0%"
        
    breakdown_data = [
        [Paragraph("Category", table_header_style), Paragraph("Emissions (kg CO₂/month)", table_header_style), Paragraph("Contribution (%)", table_header_style)],
        [Paragraph("🚗 Transportation", table_cell_style), Paragraph(str(month_entry['transport']), table_cell_style), Paragraph(get_pct(month_entry['transport']), table_cell_style)],
        [Paragraph("⚡ Electricity", table_cell_style), Paragraph(str(month_entry['electricity']), table_cell_style), Paragraph(get_pct(month_entry['electricity']), table_cell_style)],
        [Paragraph("💧 Water", table_cell_style), Paragraph(str(month_entry['water']), table_cell_style), Paragraph(get_pct(month_entry['water']), table_cell_style)],
        [Paragraph("🥗 Food Habits", table_cell_style), Paragraph(str(month_entry['food']), table_cell_style), Paragraph(get_pct(month_entry['food']), table_cell_style)],
        [Paragraph("♻️ Waste / Trash", table_cell_style), Paragraph(str(month_entry['waste']), table_cell_style), Paragraph(get_pct(month_entry['waste']), table_cell_style)],
        [Paragraph("<b>TOTAL FOOTPRINT</b>", table_cell_bold), Paragraph(f"<b>{total_em}</b>", table_cell_bold), Paragraph("<b>100%</b>", table_cell_bold)]
    ]
    
    em_table = Table(breakdown_data, colWidths=[200, 180, 150])
    em_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY_COLOR),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#dddddd")),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, LIGHT_GREEN]),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#eef2f0")), # Highlight total row
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(em_table)
    story.append(Spacer(1, 15))
    
    # 5. Targeted Recommendations
    story.append(Paragraph("Personalized Recommendations for Reduction", h2_style))
    
    recs = []
    if month_entry['transport'] > 150:
        recs.append("<b>Transportation:</b> Adopt active transport (walking/cycling) for short trips. Swap to public transit, carpool, or investigate electric vehicle options to decrease transport emissions.")
    if month_entry['electricity'] > 100:
        recs.append("<b>Electricity:</b> Swap house bulbs to LEDs. Turn off wall switches to eliminate phantom power loads, and look into solar installations or carbon offsets.")
    if month_entry['water'] > 20:
        recs.append("<b>Water:</b> Keep showers under 5 minutes. Regularly inspect plumbing for leaks, and install water-saving showerheads and aerators.")
    if month_entry['food'] > 150:
        recs.append("<b>Diet:</b> Introduce 'Meatless Mondays' and gradually increase plant-based meals. Livestock farming generates high amounts of greenhouse gases.")
    if month_entry['waste'] > 25:
        recs.append("<b>Waste:</b> Start composting organic food waste to avoid landfill methane release. Strictly avoid single-use plastics and recycle metals, glass, and paper.")
        
    if not recs:
        recs = [
            "Maintain your excellent routines and encourage neighbors to adopt eco-friendly habits.",
            "Install a home energy audit system to track real-time power leakage.",
            "Support local carbon-neutral businesses and purchase locally sourced food items."
        ]
        
    for rec in recs:
        story.append(Paragraph(f"• {rec}", bullet_style))
        
    story.append(Spacer(1, 20))
    
    # 6. Footer disclaimer
    disclaimer = Paragraph(
        "<font size=8 color='#7f8c8d'>This document is generated by the Carbon Footprint Awareness Platform. Calculations are estimates based on standard international greenhouse gas emission coefficients. Together, we can build a carbon-neutral planet! 🌍</font>",
        ParagraphStyle('Footer', parent=styles['Normal'], alignment=1)
    )
    story.append(disclaimer)
    
    # Build Document
    doc.build(story)
    
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

def generate_csv_report(history: list):
    """Compile user carbon calculation logs history into CSV format bytes."""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write Headers
    writer.writerow([
        "Month", "Transport (kg CO2)", "Electricity (kg CO2)", 
        "Water (kg CO2)", "Food (kg CO2)", "Waste (kg CO2)", 
        "Total Emissions (kg CO2)", "Score Category", "Logged Date"
    ])
    
    # Write Rows
    for entry in history:
        writer.writerow([
            entry.get("month"),
            entry.get("transport"),
            entry.get("electricity"),
            entry.get("water"),
            entry.get("food"),
            entry.get("waste"),
            entry.get("total_emissions"),
            entry.get("score_category"),
            entry.get("created_at")
        ])
        
    csv_bytes = output.getvalue().encode('utf-8')
    output.close()
    return csv_bytes

def render_reports_page():
    """Render the premium PDF/CSV export report page."""
    user = st.session_state.user

    st.markdown("""
        <div style="margin-bottom:24px;">
            <h2 style="color:#111827;margin:0 0 6px;font-size:1.7rem;">📄 Export Sustainability Reports</h2>
            <p style="color:#6B7280;font-size:14px;margin:0;">Download your monthly carbon footprint analysis as a premium PDF or export your full history to CSV.</p>
        </div>
    """, unsafe_allow_html=True)

    history = db.get_carbon_history(user['id'])

    if not history:
        st.markdown("""
            <div class="eco-card" style="text-align:center;padding:48px;">
                <div style="font-size:48px;margin-bottom:16px;">📄</div>
                <h3 style="color:#111827;margin:0 0 8px;">No Data Available</h3>
                <p style="color:#6B7280;">Please log your carbon footprint in the <b>Calculator</b> tab first!</p>
            </div>
        """, unsafe_allow_html=True)
        return

    sorted_history = sorted(history, key=lambda x: x['month'], reverse=True)
    months = [entry['month'] for entry in sorted_history]
    selected_month = months[0]
    selected_entry = sorted_history[0]

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown("""
            <div class="eco-card" style="border-top:4px solid #22C55E;">
                <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;">
                    <div style="width:44px;height:44px;background:#DCFCE7;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:22px;">📋</div>
                    <div>
                        <h4 style="color:#111827;margin:0;">PDF Report</h4>
                        <p style="color:#6B7280;margin:0;font-size:12px;">Detailed monthly analysis</p>
                    </div>
                </div>
                <p style="color:#6B7280;font-size:13px;margin-bottom:16px;">Export a printable PDF with category breakdowns, score analysis, and personalized sustainability tips.</p>
            </div>
        """, unsafe_allow_html=True)
        selected_month = st.selectbox("Select Month", months, key="report_pdf_month")
        selected_entry = next(e for e in sorted_history if e['month'] == selected_month)
        pdf_bytes = generate_pdf_report(user, selected_entry)
        st.download_button(
            label="📥 Download PDF Report",
            data=pdf_bytes,
            file_name=f"carbon_report_{user['username']}_{selected_month}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    with col2:
        st.markdown("""
            <div class="eco-card" style="border-top:4px solid #3B82F6;">
                <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;">
                    <div style="width:44px;height:44px;background:#DBEAFE;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:22px;">📊</div>
                    <div>
                        <h4 style="color:#111827;margin:0;">CSV Export</h4>
                        <p style="color:#6B7280;margin:0;font-size:12px;">All-time historical data</p>
                    </div>
                </div>
                <p style="color:#6B7280;font-size:13px;margin-bottom:16px;">Download your complete carbon calculation history in CSV format for spreadsheet analysis or custom plotting.</p>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("<div style='height:58px'></div>", unsafe_allow_html=True)
        csv_bytes = generate_csv_report(history)
        st.download_button(
            label="📥 Download All-Time CSV",
            data=csv_bytes,
            file_name=f"carbon_history_{user['username']}.csv",
            mime="text/csv",
            use_container_width=True
        )

    # Preview section
    st.markdown(f"""
        <div style="margin-top:32px;margin-bottom:12px;">
            <h3 style="color:#111827;margin:0 0 4px;">🔍 Preview: {selected_month} Summary</h3>
            <p style="color:#6B7280;font-size:13px;margin:0;">Quick overview of the selected month's emissions</p>
        </div>
    """, unsafe_allow_html=True)

    score = selected_entry['score_category']
    score_color = {"Green": "#22C55E", "Yellow": "#FBBF24", "Red": "#EF4444"}[score]
    score_bg = {"Green": "#F0FDF4", "Yellow": "#FFFBEB", "Red": "#FEF2F2"}[score]

    p1, p2, p3, p4, p5 = st.columns(5)
    metrics = [
        (p1, "🚗 Transport", f"{selected_entry['transport']} kg", "#3B82F6", "#DBEAFE"),
        (p2, "⚡ Electricity", f"{selected_entry['electricity']} kg", "#FBBF24", "#FEF3C7"),
        (p3, "💧 Water", f"{selected_entry['water']} kg", "#06B6D4", "#CFFAFE"),
        (p4, "🥗 Food", f"{selected_entry['food']} kg", "#22C55E", "#DCFCE7"),
        (p5, "♻️ Waste", f"{selected_entry['waste']} kg", "#A78BFA", "#EDE9FE"),
    ]
    for col, label, val, color, bg in metrics:
        with col:
            st.markdown(f"""
                <div style="background:#FFFFFF;border:1px solid #E5E7EB;border-radius:16px;padding:14px;text-align:center;box-shadow:0 1px 4px rgba(0,0,0,0.05);">
                    <div style="width:32px;height:32px;background:{bg};border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:16px;margin:0 auto 8px;">{label.split()[0]}</div>
                    <div style="font-size:10px;color:#6B7280;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;">{label.split(None,1)[1]}</div>
                    <div style="font-size:16px;font-weight:800;color:{color};margin-top:4px;">{val}</div>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    total = selected_entry['total_emissions']
    st.markdown(f"""
        <div style="background:{score_bg};border:1.5px solid {score_color};border-radius:16px;padding:16px 24px;display:flex;align-items:center;justify-content:space-between;">
            <div>
                <div style="font-size:12px;color:#6B7280;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;">Total Emissions</div>
                <div style="font-size:26px;font-weight:800;color:#111827;">{total} <span style="font-size:14px;font-weight:500;color:#6B7280;">kg CO₂</span></div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:12px;color:#6B7280;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;">Carbon Score</div>
                <div style="font-size:20px;font-weight:800;color:{score_color};">{score}</div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:12px;color:#6B7280;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;">Eco Points</div>
                <div style="font-size:20px;font-weight:800;color:#FBBF24;">🪙 {user['eco_points']}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
  
    st.markdown('</div>', unsafe_allow_html=True)
