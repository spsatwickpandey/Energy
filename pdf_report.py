import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table,
    TableStyle, HRFlowable, KeepTogether, PageBreak
)
from reportlab.lib import colors

# ── Palette ──────────────────────────────────────────────────────────────────
GOLD        = HexColor('#FFD600')
GOLD_DARK   = HexColor('#C9A800')
DARK        = HexColor('#1A1914')
DARK_NAVY   = HexColor('#0D1B2A')
DARK_NAVY2  = HexColor('#162232')
LIGHT_BG    = HexColor('#F4F6F8')
MEDIUM_BG   = HexColor('#E8ECF0')
BORDER      = HexColor('#C8D0D8')
TEXT_DARK   = HexColor('#1A1A2E')
TEXT_GRAY   = HexColor('#5A6A7A')
TEXT_LIGHT  = HexColor('#8A9BAB')
GREEN       = HexColor('#00C853')
GREEN_LIGHT = HexColor('#E8F5E9')
BLUE        = HexColor('#0288D1')
BLUE_LIGHT  = HexColor('#E1F5FE')
ORANGE      = HexColor('#FF8F00')
ORANGE_LIGHT= HexColor('#FFF3E0')
RED         = HexColor('#D32F2F')
RED_LIGHT   = HexColor('#FFEBEE')
WHITE       = white


def _style(base, **kw):
    s = ParagraphStyle('_', parent=base)
    for k, v in kw.items():
        setattr(s, k, v)
    return s


def generate_report_pdf(session_data: dict, user_name: str = '', user_email: str = '') -> io.BytesIO:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        rightMargin=1.8 * cm, leftMargin=1.8 * cm,
        topMargin=2.0 * cm, bottomMargin=2.0 * cm,
        title="Smart Energy Optimizer — Analysis Report",
        author=user_name
    )

    base    = getSampleStyleSheet()['Normal']
    heading = getSampleStyleSheet()['Heading1']
    story   = []

    # ─────────────────────────────────────────────────────────────────────────
    #  COVER HEADER
    # ─────────────────────────────────────────────────────────────────────────
    # Dark navy header banner
    header_data = [[
        Paragraph(
            "<b>⚡  Smart Energy Optimizer</b>",
            _style(base, fontSize=20, textColor=GOLD, fontName='Helvetica-Bold', alignment=TA_CENTER)
        )
    ]]
    header_tbl = Table(header_data, colWidths=[doc.width])
    header_tbl.setStyle(TableStyle([
        ('BACKGROUND',  (0, 0), (-1, -1), DARK_NAVY),
        ('TOPPADDING',  (0, 0), (-1, -1), 18),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 18),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('ROUNDEDCORNERS', [8, 8, 8, 8]),
    ]))
    story.append(header_tbl)
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph(
        "Complete Energy Analysis Report",
        _style(base, fontSize=13, textColor=TEXT_GRAY, alignment=TA_CENTER, spaceAfter=2)
    ))
    story.append(Paragraph(
        f"Generated: {datetime.now().strftime('%B %d, %Y  ·  %I:%M %p')}",
        _style(base, fontSize=9, textColor=TEXT_LIGHT, alignment=TA_CENTER, spaceAfter=2)
    ))
    if user_name:
        story.append(Paragraph(
            f"Prepared for:  <b>{user_name}</b>  ·  {user_email}",
            _style(base, fontSize=9, textColor=TEXT_GRAY, alignment=TA_CENTER, spaceAfter=8)
        ))
    story.append(HRFlowable(width='100%', thickness=2, color=GOLD, spaceAfter=14))

    # ─────────────────────────────────────────────────────────────────────────
    #  EXECUTIVE SUMMARY — 3 KPI boxes
    # ─────────────────────────────────────────────────────────────────────────
    results = session_data.get('results', {})

    # Handle both MongoDB doc (nested under 'results') and flat payload
    if not results:
        results = session_data

    bill  = results.get('bill_details', {})
    total_consumption = results.get('total_consumption', 0) or 0
    total_load        = results.get('total_load_kw', 0) or 0
    total_bill        = bill.get('total_bill', 0) or 0

    def kpi_cell(label, value, unit='', bg=DARK_NAVY, val_color=GOLD):
        return [
            Paragraph(label, _style(base, fontSize=8, textColor=TEXT_LIGHT, alignment=TA_CENTER)),
            Paragraph(
                f"<b>{value}</b>",
                _style(base, fontSize=22, textColor=val_color, fontName='Helvetica-Bold', alignment=TA_CENTER)
            ),
            Paragraph(unit, _style(base, fontSize=8, textColor=TEXT_LIGHT, alignment=TA_CENTER)),
        ]

    kpi_col = (doc.width - 12) / 3

    kpi_row = [
        kpi_cell("Monthly Consumption", f"{total_consumption:.1f}", "units (kWh)"),
        kpi_cell("Connected Load",      f"{total_load:.2f}",        "kilowatts"),
        kpi_cell("Estimated Bill",      f"₹{total_bill:.0f}",       "per month", val_color=GREEN),
    ]
    kpi_tbl = Table([kpi_row], colWidths=[kpi_col, kpi_col, kpi_col])
    kpi_tbl.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, -1), DARK_NAVY),
        ('BACKGROUND',    (2, 0), (2,  0),  DARK_NAVY2),
        ('TOPPADDING',    (0, 0), (-1, -1), 14),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 14),
        ('LEFTPADDING',   (0, 0), (-1, -1), 6),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 6),
        ('LINEAFTER',     (0, 0), (1,  0),   1, HexColor('#2A3B50')),
        ('BOX',           (0, 0), (-1, -1),  1, HexColor('#2A3B50')),
    ]))
    story.append(KeepTogether([kpi_tbl]))
    story.append(Spacer(1, 0.5 * cm))

    # ─────────────────────────────────────────────────────────────────────────
    #  Helper functions
    # ─────────────────────────────────────────────────────────────────────────
    def section_header(text, emoji=''):
        story.append(Spacer(1, 0.25 * cm))
        banner = [[Paragraph(
            f"<b>{emoji}  {text}</b>" if emoji else f"<b>{text}</b>",
            _style(base, fontSize=11, textColor=WHITE, fontName='Helvetica-Bold', alignment=TA_LEFT)
        )]]
        tbl = Table(banner, colWidths=[doc.width])
        tbl.setStyle(TableStyle([
            ('BACKGROUND',   (0, 0), (-1, -1), DARK),
            ('TOPPADDING',   (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING',(0, 0), (-1, -1), 8),
            ('LEFTPADDING',  (0, 0), (-1, -1), 12),
            ('LINEBELOW',    (0, 0), (-1, -1), 2, GOLD),
        ]))
        story.append(tbl)
        story.append(Spacer(1, 0.2 * cm))

    def sub_heading(text):
        story.append(Paragraph(
            f"<b>{text}</b>",
            _style(base, fontSize=10, textColor=TEXT_DARK, spaceBefore=8, spaceAfter=4)
        ))

    def note_text(text):
        story.append(Paragraph(
            text,
            _style(base, fontSize=8, textColor=TEXT_GRAY, spaceAfter=6)
        ))

    # ─────────────────────────────────────────────────────────────────────────
    #  SECTION 1 — HOUSEHOLD PROFILE
    # ─────────────────────────────────────────────────────────────────────────
    section_header("Household Profile", "👥")

    family = session_data.get('family_details', {})
    if not family and 'family_details' not in session_data:
        family = {}

    profile_items = [
        ("Total Members",   str(family.get('totalMembers',   '—'))),
        ("Household Type",  str(family.get('householdType',  '—')).title()),
        ("Male Members",    str(family.get('maleMembers',    '—'))),
        ("Female Members",  str(family.get('femaleMembers',  '—'))),
        ("Children",        str(family.get('children',       '—'))),
    ]

    col_w = doc.width / 2 - 3
    profile_rows = []
    for i in range(0, len(profile_items), 2):
        row = []
        for j in range(2):
            if i + j < len(profile_items):
                label, val = profile_items[i + j]
                cell = Paragraph(
                    f'<font color="#8A9BAB" size="8">{label}</font><br/>'
                    f'<font color="#1A1A2E" size="11"><b>{val}</b></font>',
                    _style(base, alignment=TA_CENTER)
                )
            else:
                cell = Paragraph('', base)
            row.append(cell)
        profile_rows.append(row)

    profile_tbl = Table(profile_rows, colWidths=[col_w, col_w])
    profile_tbl.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, -1), LIGHT_BG),
        ('ROWBACKGROUNDS',(0, 0), (-1, -1), [LIGHT_BG, MEDIUM_BG]),
        ('TOPPADDING',    (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING',   (0, 0), (-1, -1), 14),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 14),
        ('GRID',          (0, 0), (-1, -1), 0.4, BORDER),
    ]))
    story.append(KeepTogether([profile_tbl]))

    # ─────────────────────────────────────────────────────────────────────────
    #  SECTION 2 — APPLIANCE DETAILS
    # ─────────────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.4 * cm))
    section_header("Appliance Details", "🔌")

    appliances = results.get('appliance_predictions', [])

    # Try flat session_data if not found under 'results'
    if not appliances:
        appliances = []

    if appliances:
        # Header row
        app_header = [
            Paragraph("<b>Appliance</b>",      _style(base, fontSize=8, textColor=WHITE, fontName='Helvetica-Bold', alignment=TA_CENTER)),
            Paragraph("<b>Brand / Model</b>",  _style(base, fontSize=8, textColor=WHITE, fontName='Helvetica-Bold', alignment=TA_CENTER)),
            Paragraph("<b>Qty</b>",            _style(base, fontSize=8, textColor=WHITE, fontName='Helvetica-Bold', alignment=TA_CENTER)),
            Paragraph("<b>Load (kW)</b>",      _style(base, fontSize=8, textColor=WHITE, fontName='Helvetica-Bold', alignment=TA_CENTER)),
            Paragraph("<b>Units/mo</b>",       _style(base, fontSize=8, textColor=WHITE, fontName='Helvetica-Bold', alignment=TA_CENTER)),
            Paragraph("<b>Cost (₹/mo)</b>",    _style(base, fontSize=8, textColor=WHITE, fontName='Helvetica-Bold', alignment=TA_CENTER)),
            Paragraph("<b>% of Bill</b>",      _style(base, fontSize=8, textColor=WHITE, fontName='Helvetica-Bold', alignment=TA_CENTER)),
        ]
        app_data = [app_header]

        for a in appliances:
            brand_model = a.get('brand', '')
            if a.get('model'):
                brand_model += f"\n{a.get('model', '')}"
            cons_pct = a.get('consumption_percentage', 0)
            pct_color = GREEN if cons_pct < 20 else (ORANGE if cons_pct < 40 else RED)

            app_data.append([
                Paragraph(a.get('type', '—'),    _style(base, fontSize=8, textColor=TEXT_DARK)),
                Paragraph(brand_model,            _style(base, fontSize=7, textColor=TEXT_GRAY)),
                Paragraph(str(a.get('quantity', 1)), _style(base, fontSize=8, textColor=TEXT_DARK, alignment=TA_CENTER)),
                Paragraph(f"{a.get('load_kw', 0):.3f}", _style(base, fontSize=8, textColor=BLUE, alignment=TA_CENTER)),
                Paragraph(f"{a.get('consumption', 0):.2f}", _style(base, fontSize=8, textColor=TEXT_DARK, alignment=TA_CENTER)),
                Paragraph(f"₹{a.get('total_charges', 0):.2f}", _style(base, fontSize=8, textColor=GREEN, alignment=TA_CENTER, fontName='Helvetica-Bold')),
                Paragraph(f"{cons_pct:.1f}%", _style(base, fontSize=8, textColor=pct_color, alignment=TA_CENTER, fontName='Helvetica-Bold')),
            ])

        col_widths = [3.0*cm, 3.4*cm, 0.9*cm, 1.6*cm, 1.7*cm, 2.0*cm, 1.6*cm]
        app_tbl = Table(app_data, colWidths=col_widths, repeatRows=1)
        app_tbl.setStyle(TableStyle([
            ('BACKGROUND',    (0, 0), (-1, 0),  DARK),
            ('TEXTCOLOR',     (0, 0), (-1, 0),  WHITE),
            ('FONTSIZE',      (0, 0), (-1, -1), 8),
            ('TOPPADDING',    (0, 0), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
            ('LEFTPADDING',   (0, 0), (-1, -1), 5),
            ('RIGHTPADDING',  (0, 0), (-1, -1), 5),
            ('GRID',          (0, 0), (-1, -1), 0.4, BORDER),
            ('ROWBACKGROUNDS',(0, 1), (-1, -1), [WHITE, LIGHT_BG]),
            ('LINEABOVE',     (0, 1), (-1, 1),  1,  BORDER),
            ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(app_tbl)
        note_text("* % of Bill shows each appliance's share of total monthly electricity cost.")
    else:
        story.append(Paragraph("No appliance data available.", _style(base, fontSize=9, textColor=TEXT_GRAY)))

    # ─────────────────────────────────────────────────────────────────────────
    #  SECTION 3 — BILL BREAKDOWN
    # ─────────────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.4 * cm))
    section_header("Electricity Bill Breakdown", "💡")

    slabs = bill.get('consumption_slabs', {})

    # Slab table
    sub_heading("Consumption Slabs (Progressive Tariff)")
    slab_header = [
        Paragraph("<b>Slab</b>",       _style(base, fontSize=9, textColor=WHITE, fontName='Helvetica-Bold')),
        Paragraph("<b>Units</b>",      _style(base, fontSize=9, textColor=WHITE, fontName='Helvetica-Bold', alignment=TA_CENTER)),
        Paragraph("<b>Rate /unit</b>", _style(base, fontSize=9, textColor=WHITE, fontName='Helvetica-Bold', alignment=TA_CENTER)),
        Paragraph("<b>Amount</b>",     _style(base, fontSize=9, textColor=WHITE, fontName='Helvetica-Bold', alignment=TA_CENTER)),
    ]
    u1 = float(slabs.get('0-150',    0))
    u2 = float(slabs.get('151-300',  0))
    u3 = float(slabs.get('above_300',0))
    slab_data = [
        slab_header,
        [Paragraph("0 – 150 units",   _style(base, fontSize=9, textColor=TEXT_DARK)),
         Paragraph(f"{u1:.2f}",       _style(base, fontSize=9, textColor=BLUE, alignment=TA_CENTER)),
         Paragraph("₹ 5.50",          _style(base, fontSize=9, textColor=TEXT_GRAY, alignment=TA_CENTER)),
         Paragraph(f"₹ {u1*5.50:.2f}",_style(base, fontSize=9, textColor=GREEN, alignment=TA_CENTER, fontName='Helvetica-Bold'))],
        [Paragraph("151 – 300 units", _style(base, fontSize=9, textColor=TEXT_DARK)),
         Paragraph(f"{u2:.2f}",       _style(base, fontSize=9, textColor=BLUE, alignment=TA_CENTER)),
         Paragraph("₹ 6.00",          _style(base, fontSize=9, textColor=TEXT_GRAY, alignment=TA_CENTER)),
         Paragraph(f"₹ {u2*6.00:.2f}",_style(base, fontSize=9, textColor=GREEN, alignment=TA_CENTER, fontName='Helvetica-Bold'))],
        [Paragraph("Above 300 units", _style(base, fontSize=9, textColor=TEXT_DARK)),
         Paragraph(f"{u3:.2f}",       _style(base, fontSize=9, textColor=BLUE, alignment=TA_CENTER)),
         Paragraph("₹ 6.50",          _style(base, fontSize=9, textColor=TEXT_GRAY, alignment=TA_CENTER)),
         Paragraph(f"₹ {u3*6.50:.2f}",_style(base, fontSize=9, textColor=GREEN, alignment=TA_CENTER, fontName='Helvetica-Bold'))],
    ]
    slab_tbl = Table(slab_data, colWidths=[6*cm, 2.5*cm, 2.8*cm, 3.2*cm])
    slab_tbl.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, 0),  DARK),
        ('TEXTCOLOR',     (0, 0), (-1, 0),  WHITE),
        ('FONTSIZE',      (0, 0), (-1, -1), 9),
        ('TOPPADDING',    (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 9),
        ('LEFTPADDING',   (0, 0), (-1, -1), 8),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 8),
        ('GRID',          (0, 0), (-1, -1), 0.4, BORDER),
        ('ROWBACKGROUNDS',(0, 1), (-1, -1), [WHITE, LIGHT_BG]),
    ]))
    story.append(slab_tbl)
    story.append(Spacer(1, 0.25 * cm))

    # Charges summary table
    sub_heading("Charges Summary")
    charges_data = [
        [Paragraph("<b>Charge Component</b>",   _style(base, fontSize=9, textColor=WHITE, fontName='Helvetica-Bold')),
         Paragraph("<b>Amount</b>",              _style(base, fontSize=9, textColor=WHITE, fontName='Helvetica-Bold', alignment=TA_CENTER))],
        [Paragraph("Fixed Charges (₹110 × contracted kW)",  _style(base, fontSize=9, textColor=TEXT_DARK)),
         Paragraph(f"₹ {bill.get('fixed_charges', 0):.2f}",  _style(base, fontSize=9, textColor=TEXT_DARK, alignment=TA_CENTER))],
        [Paragraph("Energy Charges (slab-based)",            _style(base, fontSize=9, textColor=TEXT_DARK)),
         Paragraph(f"₹ {bill.get('energy_charges', 0):.2f}", _style(base, fontSize=9, textColor=TEXT_DARK, alignment=TA_CENTER))],
        [Paragraph("Electricity Duty (6%)",                  _style(base, fontSize=9, textColor=TEXT_DARK)),
         Paragraph(f"₹ {bill.get('electricity_duty', 0):.2f}",_style(base, fontSize=9, textColor=TEXT_DARK, alignment=TA_CENTER))],
        [Paragraph("<b>TOTAL MONTHLY BILL</b>",              _style(base, fontSize=11, textColor=WHITE, fontName='Helvetica-Bold')),
         Paragraph(f"<b>₹ {bill.get('total_bill', 0):.2f}</b>",_style(base, fontSize=13, textColor=GOLD, fontName='Helvetica-Bold', alignment=TA_CENTER))],
    ]
    ch_tbl = Table(charges_data, colWidths=[10*cm, 4.5*cm])
    ch_tbl.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0),  (-1, 0),  DARK),
        ('BACKGROUND',    (0, -1), (-1, -1), DARK_NAVY),
        ('FONTSIZE',      (0, 0),  (-1, -1), 9),
        ('TOPPADDING',    (0, 0),  (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0),  (-1, -1), 10),
        ('LEFTPADDING',   (0, 0),  (-1, -1), 12),
        ('RIGHTPADDING',  (0, 0),  (-1, -1), 12),
        ('GRID',          (0, 0),  (-1, -1), 0.4, BORDER),
        ('ROWBACKGROUNDS',(0, 1),  (-1, -2), [WHITE, LIGHT_BG]),
        ('LINEABOVE',     (0, -1), (-1, -1), 2, GOLD),
    ]))
    story.append(KeepTogether([ch_tbl]))

    # ─────────────────────────────────────────────────────────────────────────
    #  SECTION 4 — AI RECOMMENDATIONS
    # ─────────────────────────────────────────────────────────────────────────
    ai = session_data.get('ai_recommendations')

    # Also look in flat data
    if not ai and isinstance(session_data.get('ai_recommendations'), dict):
        ai = session_data.get('ai_recommendations')

    if ai and isinstance(ai, dict) and any(
        ai.get(k) for k in ['priority_actions', 'usage_optimization', 'behavioral_changes', 'long_term_investments']
    ):
        story.append(PageBreak())
        section_header("AI-Powered Energy Recommendations", "🤖")
        note_text(
            "Generated by Groq LLaMA-3 based on your specific appliances, brands, usage patterns, and monthly costs. "
            "All bill and savings figures are monthly estimates."
        )

        def render_rec_section(title, emoji, items, main_key, accent_color=GOLD, bg_color=LIGHT_BG):
            if not items:
                return
            sub_heading(f"{emoji}  {title}")
            for i, item in enumerate(items, 1):
                action = item.get(main_key) or item.get('action') or item.get('change') or item.get('investment') or ''

                # Build detail lines
                details = []
                if item.get('reason'):          details.append(f"<b>Reason:</b> {item['reason']}")
                if item.get('recommended_usage'):details.append(f"<b>Recom. Usage:</b> {item['recommended_usage']}")
                if item.get('current_usage'):   details.append(f"<b>Current Usage:</b> {item['current_usage']}")
                if item.get('potential_savings'):details.append(f"<b>Savings:</b> {item['potential_savings']}")
                if item.get('savings'):         details.append(f"<b>Savings:</b> {item['savings']}")
                if item.get('tips'):            details.append(f"<b>Tip:</b> {item['tips']}")
                if item.get('impact'):          details.append(f"<b>Impact:</b> {item['impact']}")
                if item.get('difficulty'):      details.append(f"<b>Difficulty:</b> {item['difficulty']}")
                if item.get('urgency'):         details.append(f"<b>Urgency:</b> {item['urgency']}")
                if item.get('payback_period'):  details.append(f"<b>Payback:</b> {item['payback_period']}")
                if item.get('cost'):            details.append(f"<b>Cost:</b> {item['cost']}")
                if item.get('annual_savings'):  details.append(f"<b>Annual Savings:</b> {item['annual_savings']}")
                if item.get('roi_period'):      details.append(f"<b>ROI:</b> {item['roi_period']}")

                # Build cell content
                cell_content = [
                    Paragraph(
                        f"<font color='#1A1914'><b>{i}.</b></font>  {action}",
                        _style(base, fontSize=9, textColor=TEXT_DARK, fontName='Helvetica-Bold', spaceAfter=3)
                    )
                ]
                if details:
                    cell_content.append(Paragraph(
                        "   " + "  ·  ".join(details),
                        _style(base, fontSize=8, textColor=TEXT_GRAY, spaceAfter=0)
                    ))

                row = [[cell_content]]
                rec_tbl = Table(row, colWidths=[doc.width])
                rec_tbl.setStyle(TableStyle([
                    ('BACKGROUND',   (0, 0), (-1, -1), bg_color),
                    ('BOX',          (0, 0), (-1, -1), 0.4, BORDER),
                    ('LINEABOVE',    (0, 0), (-1, 0),  2.5, accent_color),
                    ('TOPPADDING',   (0, 0), (-1, -1), 8),
                    ('BOTTOMPADDING',(0, 0), (-1, -1), 8),
                    ('LEFTPADDING',  (0, 0), (-1, -1), 10),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ]))
                story.append(KeepTogether([rec_tbl, Spacer(1, 0.12 * cm)]))

        render_rec_section("Quick Wins / Priority Actions", "⚡", ai.get('priority_actions', []),     'action',     accent_color=RED,    bg_color=RED_LIGHT)
        render_rec_section("Usage Optimization",            "🔧", ai.get('usage_optimization', []),   'appliance',  accent_color=BLUE,   bg_color=BLUE_LIGHT)
        render_rec_section("Behavioral Changes",            "💡", ai.get('behavioral_changes', []),   'change',     accent_color=ORANGE, bg_color=ORANGE_LIGHT)
        render_rec_section("Long-Term Investments",         "📈", ai.get('long_term_investments', []),'investment', accent_color=GREEN,  bg_color=GREEN_LIGHT)
        if ai.get('personalized_tips'):
            render_rec_section("Personalized Tips",         "🌟", ai.get('personalized_tips', []),    'action',     accent_color=GOLD,   bg_color=LIGHT_BG)

    # ─────────────────────────────────────────────────────────────────────────
    #  FOOTER
    # ─────────────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.6 * cm))
    story.append(HRFlowable(width='100%', thickness=0.8, color=BORDER))
    story.append(Spacer(1, 0.15 * cm))
    footer_row = [[
        Paragraph(
            "This report was generated automatically by <b>Smart Energy Optimizer</b>. "
            "Bill calculations follow standard progressive tariff slabs.",
            _style(base, fontSize=7, textColor=TEXT_LIGHT, alignment=TA_LEFT)
        ),
        Paragraph(
            f"Generated: {datetime.now().strftime('%d %b %Y')}",
            _style(base, fontSize=7, textColor=TEXT_LIGHT, alignment=TA_RIGHT)
        )
    ]]
    footer_tbl = Table(footer_row, colWidths=[doc.width * 0.7, doc.width * 0.3])
    footer_tbl.setStyle(TableStyle([
        ('TOPPADDING',    (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('VALIGN',        (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(footer_tbl)

    doc.build(story)
    buf.seek(0)
    return buf
