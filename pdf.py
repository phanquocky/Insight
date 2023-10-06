from fpdf import FPDF
from PyPDF2 import PdfMerger

#Oke
def pdf_to_bytes(pdf_path):
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    return pdf_bytes

# Oke
def bytes_to_pdf(pdf_bytes, output_file):
  with open(output_file, "wb") as f:
      f.write(pdf_bytes)

# Oke with English
def text_to_pdf(input_file, output_pdf):
  # Read text file and store content in a variable
  with open(input_file, encoding='utf-8') as f:
    text = f.read()

  # Initialize a new PDF 
  pdf = FPDF()

  # Add a page
  pdf.add_page() 

  # Set font to arial, 12pt
  pdf.set_font("Arial", size = 12)

  # Insert the text from the text file
  pdf.multi_cell(200, 10, txt = text) 

  # Save the PDF with name filename.pdf
  pdf.output(output_pdf)

# Oke 
def merge_pdfs(input_files, output_stream):
  merger = PdfMerger()

  for(pdf_path) in input_files:
    merger.append( open(pdf_path, "rb") )
  
  with open(output_stream, "wb") as fout:
    merger.write(fout)

if __name__ == "__main__":
    input_file = "./assets/test_file/input.txt"  # Replace with the path to your text file
    output_pdf = "./assets/test_file/test1.pdf"  # Replace with the desired output PDF file name
    text_to_pdf(input_file, output_pdf)

    pdf_path = "./assets/test_file/test.pdf"
    pdf_bytes = pdf_to_bytes(pdf_path)
    bytes_to_pdf(pdf_bytes, "./assets/test_file/test2.pdf")

    merge_pdfs(["./assets/test_file/test1.pdf", "./assets/test_file/test2.pdf"], "./assets/test_file/output.pdf")