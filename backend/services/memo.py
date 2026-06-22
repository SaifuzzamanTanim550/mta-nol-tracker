"""Builds the MTA memorandum PDF from a record and merges the scanned NOL
behind it, returning one properly-named package.
"""
import io
import re
from datetime import datetime, timedelta

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
)
from reportlab.lib.enums import TA_RIGHT
from pypdf import PdfReader, PdfWriter

from .. import memo_config as cfg

MTA_NAVY = colors.HexColor("#003DA5")


def _fmt(d: str) -> str:
    """YYYY-MM-DD → M/D/YYYY (the format the memo uses). Pass through if odd."""
    if not d:
        return ""
    try:
        return datetime.strptime(d, "%Y-%m-%d").strftime("%-m/%-d/%Y")
    except ValueError:
        return d


def _long_date(d: str) -> str:
    try:
        return datetime.strptime(d, "%Y-%m-%d").strftime("%B %-d, %Y")
    except (ValueError, TypeError):
        return d or datetime.now().strftime("%B %-d, %Y")


def memo_defaults(record: dict) -> dict:
    """Derive sensible memo fields from a saved record. The app shows these
    pre-filled and lets staff edit before generating."""
    division = record.get("Division", "")
    violation = record.get("Type_of_Violation", "")
    today = datetime.now()
    return {
        "memo_date": today.strftime("%Y-%m-%d"),
        "submit_by": (today + timedelta(days=7)).strftime("%Y-%m-%d"),
        "to_line": cfg.DIVISION_RECIPIENTS.get(division, ""),
        "from_line": cfg.FROM_LINE,
        "re_line": cfg.VIOLATION_PROGRAMS.get(violation, "CAMERA MONITORING PROGRAM"),
        "depot_code": record.get("Depot_Assigned_To", ""),
        "vehicle_type_short": (record.get("Vehicle_Type") or "BUS").upper(),
        "notice_round": "1ST",
    }


def _violation_slug(violation: str) -> str:
    table = {
        "Speeding": "SCHOOL_ZONE_SPEEDING_CAMERA_VIOLATION",
        "School Bus Safety": "SCHOOL_BUS_SAFETY_CAMERA_VIOLATION",
        "Red Light": "RED_LIGHT_CAMERA_VIOLATION",
        "Bus Lane": "BUS_LANE_CAMERA_VIOLATION",
        "ACE": "ACE_BUS_LANE_VIOLATION",
        "Work Zone Safety": "WORK_ZONE_SPEEDING_CAMERA_VIOLATION",
        "Weigh in Motion": "WEIGH_IN_MOTION_VIOLATION",
        "Courtesy": "COURTESY_VIOLATION",
        "Parking": "PARKING_VIOLATION",
    }
    if violation in table:
        return table[violation]
    base = re.sub(r"[^A-Za-z0-9]+", "_", (violation or "").upper()).strip("_")
    return f"{base}_VIOLATION" if base else "VIOLATION"


def build_filename(record: dict, memo: dict) -> str:
    """e.g. 1ST_NOL_4978950260_FLT_BUS_7310_SCHOOL_ZONE_SPEEDING_CAMERA_VIOLATION.pdf"""
    parts = [
        memo.get("notice_round", "1ST"),
        "NOL",
        record.get("NOL_Number", "UNKNOWN"),
        memo.get("depot_code") or "NA",
        memo.get("vehicle_type_short", "BUS"),
        record.get("Vehicle_Number") or "NA",
        _violation_slug(record.get("Type_of_Violation", "")),
    ]
    name = "_".join(str(p) for p in parts)
    name = re.sub(r"[^A-Za-z0-9_]+", "", name)
    return f"{name}.pdf"


def _build_memo_pdf(record: dict, memo: dict) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=letter,
        leftMargin=0.9 * inch, rightMargin=0.9 * inch,
        topMargin=0.7 * inch, bottomMargin=0.7 * inch,
    )
    ss = getSampleStyleSheet()
    body = ParagraphStyle("body", parent=ss["Normal"], fontName="Helvetica",
                          fontSize=10.5, leading=15, spaceAfter=10)
    org = ParagraphStyle("org", parent=ss["Normal"], fontName="Helvetica-Bold",
                         fontSize=9.5, leading=12, textColor=MTA_NAVY)
    title = ParagraphStyle("title", parent=ss["Normal"], fontName="Helvetica-Bold",
                          fontSize=22, alignment=TA_RIGHT)
    meta = ParagraphStyle("meta", parent=ss["Normal"], fontName="Helvetica",
                         fontSize=10.5, leading=15)

    agency = record.get("Enforcement_Agency", "")
    agency_full = cfg.AGENCY_FULL.get(agency, agency or "the issuing agency")

    story = []

    # Header band: org block on the left, "Memorandum" on the right.
    header = Table(
        [[Paragraph("Metropolitan Transportation Authority<br/>"
                    "NYCT Department of Buses<br/>MTA Bus Company", org),
          Paragraph("Memorandum", title)]],
        colWidths=[3.4 * inch, 3.3 * inch],
    )
    header.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LINEBELOW", (0, 0), (-1, -1), 1.2, MTA_NAVY),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story += [header, Spacer(1, 14)]

    # Date / To / From / Re
    for label, value in [
        ("Date:", _long_date(memo.get("memo_date"))),
        ("To:", memo.get("to_line", "")),
        ("From:", memo.get("from_line", cfg.FROM_LINE)),
        ("Re:", memo.get("re_line", "")),
    ]:
        story.append(Paragraph(f"<b>{label}</b>&nbsp;&nbsp;{value}", meta))
    story.append(Spacer(1, 10))

    # Body
    story.append(Paragraph(
        f"On {_fmt(record.get('Violation_Date',''))}, Vehicle #{record.get('Vehicle_Number','')} "
        f"assigned to your department was photographed by the {agency_full} ({agency}) "
        f"for the following violation:", body))
    story.append(Paragraph(
        "The operator in charge of this vehicle, when the photographs were taken, must be "
        "informed that New York City Transit will not assume responsibility for payment of the "
        "fine. Furthermore, the employee is also subject to disciplinary action by New York City "
        "Transit Department of Buses.", body))
    story.append(Paragraph(
        "To avoid additional penalties the operator must pay or contest the fine following the "
        "procedure described on the back of the Notice of Liability violation within 7 days "
        "receipt of the Notice of Liability.", body))
    story.append(Paragraph(
        f"Please submit proof of violation dismissal (not guilty) or payment including operator "
        f"name and payroll # to {cfg.SUBMIT_TO} by {_fmt(memo.get('submit_by',''))}.", body))
    story.append(Paragraph("Thank you for your assistance in this matter.", body))
    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>Attachments</b>", body))
    story.append(Spacer(1, 10))

    # Violation table
    headers = ["VIOLATION\nDATE", "NOL #", "VIOLATION", "VEHICLE\nTYPE",
               "VEHICLE #", "LICENSE\nPLATE #", "LOCATION/\nASSIGNED TO", "FINE"]
    row = [
        _fmt(record.get("Violation_Date", "")),
        record.get("NOL_Number", ""),
        (record.get("Type_of_Violation", "") or "").upper(),
        memo.get("vehicle_type_short", "BUS"),
        record.get("Vehicle_Number", ""),
        record.get("License_Plate_Number", ""),
        memo.get("depot_code", "") or record.get("Depot_Assigned_To", ""),
        f"${record.get('Fine_Amount','')}" if record.get("Fine_Amount") else "",
    ]
    tbl = Table([headers, row],
                colWidths=[0.78*inch, 1.0*inch, 1.0*inch, 0.72*inch,
                           0.72*inch, 0.78*inch, 0.95*inch, 0.6*inch])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F0F3F9")),
        ("TEXTCOLOR", (0, 0), (-1, 0), MTA_NAVY),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, 1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("GRID", (0, 0), (-1, -1), 0.6, colors.HexColor("#9AA7BD")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(tbl)

    doc.build(story)
    buf.seek(0)
    return buf.getvalue()


def build_package(record: dict, memo: dict, scan_bytes: bytes) -> bytes:
    """Memo PDF first, then the scanned NOL pages appended."""
    memo_pdf = _build_memo_pdf(record, memo)
    writer = PdfWriter()
    for page in PdfReader(io.BytesIO(memo_pdf)).pages:
        writer.add_page(page)
    if scan_bytes:
        try:
            for page in PdfReader(io.BytesIO(scan_bytes)).pages:
                writer.add_page(page)
        except Exception:
            pass  # if the scan can't be read, still return the memo
    out = io.BytesIO()
    writer.write(out)
    out.seek(0)
    return out.getvalue()
