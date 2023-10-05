from fpdf import FPDF

def pdf_to_bytes(pdf_path):
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    return pdf_bytes

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

def merge_pdfs(pdf_list, output_filename):
  
  pdf = FPDF()

  for pdf_file in pdf_list:

    # Open each PDF file
    with open(pdf_file, 'rb') as f:
      pdf_content = f.read()

    # Add a page
    pdf.add_page() 

    # Write PDF content
    pdf.write(8, pdf_content)

  # Save merged file
  pdf.output(output_filename, 'F')

if __name__ == "__main__":
    # input_file = "input.txt"  # Replace with the path to your text file
    # output_pdf = "output.pdf"  # Replace with the desired output PDF file name
    # text_to_pdf(input_file, output_pdf)

    # pdf_path = "test.pdf"
    # pdf_bytes = pdf_to_bytes(pdf_path)
    # bytes_to_pdf(pdf_bytes, "test2.pdf")

    merge_pdfs(["test.pdf", "test2.pdf"], "output.pdf")