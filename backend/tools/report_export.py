from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from docx import Document
from docx.shared import Inches
from openpyxl import Workbook
import pandas as pd
import matplotlib.pyplot as plt
import os
from agents import function_tool


# ------------------------- Visualization Tool -------------------------
@function_tool
def visualize_data(data: list, filename: str = "visualization.png"):
    """
    Generate a bar chart from given data and save as PNG.

    Args:
        data (list): [{"name": "AI Tools", "score": 95}, ...]
        filename (str): Output image filename

    Returns:
        str: Path of saved chart image
    """
    names = [d["name"] for d in data]
    values = [d["score"] for d in data]

    plt.figure(figsize=(6, 4))
    plt.bar(names, values, color="orange")
    plt.title("Data Visualization")
    plt.ylabel("Score")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()
    return filename


# ------------------------- Helper: Chart Generator -------------------------
def create_chart(trends, filename="trend_chart.png"):
    """
    Internal helper for charts (used by export_report/export_pitchdeck).
    """
    names = [d["name"] for d in trends]
    values = [d["score"] for d in trends]

    plt.figure(figsize=(6, 4))
    plt.bar(names, values, color="skyblue")
    plt.title("Trends / Market Analysis")
    plt.ylabel("Score")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()
    return filename


# ------------------------- Export Trends Report -------------------------
@function_tool
def export_report(trends: list, format_type: str = "pdf", output_name: str = None):
    """
    Export trends report in PDF, Word, or Excel.

    Args:
        trends (list): [{"name": "AI Tools", "score": 95}, ...]
        format_type (str): "pdf", "word", or "excel"
        output_name (str): output file name without extension
    """
    if output_name is None:
        output_name = "trend_report"

    chart_file = create_chart(trends)

    if format_type == "pdf":
        report_file = f"{output_name}.pdf"
        c = canvas.Canvas(report_file, pagesize=A4)
        c.setFont("Helvetica-Bold", 18)
        c.drawString(50, 800, "Trending Market Topics Report")
        if os.path.exists(chart_file):
            c.drawImage(chart_file, 50, 450, width=500, height=300)
        c.save()
        return report_file

    elif format_type == "word":
        report_file = f"{output_name}.docx"
        doc = Document()
        doc.add_heading("Trending Market Topics Report", 0)

        table = doc.add_table(rows=1, cols=2)
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = "Topic"
        hdr_cells[1].text = "Score"

        for t in trends:
            row_cells = table.add_row().cells
            row_cells[0].text = t["name"]
            row_cells[1].text = str(t["score"])

        if os.path.exists(chart_file):
            doc.add_picture(chart_file, width=Inches(5))

        doc.save(report_file)
        return report_file

    elif format_type == "excel":
        report_file = f"{output_name}.xlsx"
        df = pd.DataFrame(trends)
        df.to_excel(report_file, index=False)
        return report_file

    else:
        raise ValueError("Invalid format_type! Choose 'pdf', 'word', or 'excel'.")


# ------------------------- Export Pitch Deck -------------------------
@function_tool
def export_pitchdeck(data: list, format_type: str = "pdf", filename: str = "PitchDeck"):
    """
    Export pitch deck (slides with title + bullets + optional chart).
    Example data: [{"title": "Slide 1", "bullets": ["point1", "point2"], "chart": True}]
    """
    chart_file = None
    if any(slide.get("chart") for slide in data):
        chart_file = create_chart([{"name": "Demo", "score": 100}])

    format_type = format_type.lower()

    if format_type == "pdf":
        c = canvas.Canvas(f"{filename}.pdf", pagesize=A4)
        width, height = A4
        y = height - 50

        for slide in data:
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, y, slide["title"])
            y -= 30
            c.setFont("Helvetica", 12)

            for bullet in slide.get("bullets", []):
                c.drawString(70, y, f"* {bullet}")
                y -= 20
                if y < 100:
                    c.showPage()
                    y = height - 50

            if slide.get("chart", False) and chart_file and os.path.exists(chart_file):
                c.drawImage(chart_file, 50, y - 200, width=400, height=200)
                y -= 220

            c.showPage()
            y = height - 50

        c.save()
        return f"{filename}.pdf"

    elif format_type == "word":
        doc = Document()
        for slide in data:
            doc.add_heading(slide["title"], level=1)
            for bullet in slide.get("bullets", []):
                doc.add_paragraph(f"{bullet}", style="ListBullet")
            doc.add_paragraph("")

            if slide.get("chart", False) and chart_file and os.path.exists(chart_file):
                doc.add_picture(chart_file, width=Inches(5))

        doc.save(f"{filename}.docx")
        return f"{filename}.docx"

    elif format_type == "excel":
        wb = Workbook()
        ws = wb.active
        ws.title = "Pitch Deck"

        row = 1
        for slide in data:
            ws.cell(row=row, column=1, value=slide["title"])
            row += 1
            for bullet in slide.get("bullets", []):
                ws.cell(row=row, column=2, value=bullet)
                row += 1
            row += 2

        wb.save(f"{filename}.xlsx")
        return f"{filename}.xlsx"

    else:
        raise ValueError("Unsupported format_type! Use 'pdf', 'word', or 'excel'.")
