import pandas as pd
from fpdf import FPDF
import io
import csv
from io import BytesIO
from io import StringIO
import os

# def flashcards_to_csv(flashcards):
#     df = pd.DataFrame(flashcards)
#     return df.to_csv(index=False).encode('utf-8')

def flashcards_to_csv(flashcards):
    output = StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_ALL)
    writer.writerow(["Question", "Answer"])
    for card in flashcards:
        writer.writerow([card['question'], card['answer']])
    return output.getvalue()

def flashcards_to_tsv(flashcards):
    df = pd.DataFrame(flashcards)
    return df.to_csv(index=False, sep='\t').encode('utf-8')


def flashcards_to_pdf(flashcards):
    pdf = FPDF()
    pdf.add_page()

    font_folder = "fonts"
    pdf.add_font("NotoSans", "", os.path.join(font_folder, "NotoSans-Regular.ttf"), uni=True)
    pdf.add_font("NotoSans", "B", os.path.join(font_folder, "NotoSans-Bold.ttf"), uni=True)

    page_width = pdf.w - 2 * pdf.l_margin

    for i, card in enumerate(flashcards, start=1):
        pdf.set_font("NotoSans", style='B', size=14)
        pdf.multi_cell(page_width, 10, f"Q{i}: {card['question']}")
        pdf.ln(2)

        pdf.set_font("NotoSans", size=12)
        pdf.multi_cell(page_width, 10, f"A: {card['answer']}")
        pdf.ln(8)

    pdf_bytes = pdf.output(dest='S')  # Already a byte stream
    return BytesIO(pdf_bytes)

