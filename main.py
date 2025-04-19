import io
import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image  # Pillow for image processing
import pymupdf  # PyMuPDF for PDFs
from paddleocr import PaddleOCR
import numpy as np

# This function reads the PDF, converts each page into a high-res image, and stores them in memory as PIL Images
def convert_pdf_to_images(pdf_path):
    images = []
    doc = pymupdf.open(pdf_path)  # Open the PDF
    for page_num in range(len(doc)):
        pix = doc[page_num].get_pixmap()  # Render page to pixel map
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)  # Convert to PIL image
        images.append(img)
    return images

def extract_text_from_images(images, lang='en'):
    ocr = PaddleOCR(use_angle_cls=True, lang=lang)
    all_text = []
    for idx, img in enumerate(images):
        # Convert PIL Image to numpy array
        np_img = np.array(img)
        result = ocr.ocr(np_img, cls=True)
        page_text = []
        for line in result:
            for word_info in line:
                text = word_info[1][0]
                page_text.append(text)
        all_text.append('\n'.join(page_text))
    return '\n\n'.join(all_text)

def select_pdf():
    """Open a dialog window for the user to select a PDF file and return its path."""
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    file_path = filedialog.askopenfilename(
        title="Select a PDF file",
        filetypes=[("PDF files", "*.pdf")],
    )
    root.destroy()
    return file_path

def main():
    print("Hello from pdf2md v0.2.0 (PaddleOCR)!")
    pdf_path = select_pdf()
    images = convert_pdf_to_images(pdf_path)

    if images:
        print(f"Converted {len(images)} pages to images.")
        extracted_text = extract_text_from_images(images)
        # Save with the same name as the PDF but with .md extension
        md_path = os.path.splitext(pdf_path)[0] + ".md"
        with open(md_path, "w", encoding="utf-8") as md_file:
            md_file.write(extracted_text)
        print(f"\nMarkdown Conversion Complete! Check `{md_path}`.")
    else:
        print("No images found in the PDF.")

if __name__ == "__main__":
    main()
