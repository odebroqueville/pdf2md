# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "ollama",
#     "pillow",
#     "pymupdf",
# ]
# ///

import io
import os
import tkinter as tk
from tkinter import filedialog
import ollama
from PIL import Image  # Pillow for image processing
import pymupdf  # PyMuPDF for PDFs

# This function reads the PDF, converts each page into a high-res image, and stores them in memory as raw PNG bytes
def convert_pdf_to_images(pdf_path):
    images = []
    doc = pymupdf.open(pdf_path)  # Open the PDF
    for page_num in range(len(doc)):
        pix = doc[page_num].get_pixmap()  # Render page to pixel map
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)  # Convert to PIL image
        img_buffer = io.BytesIO()
        img.save(img_buffer, format="PNG")  # Save as in-memory PNG
        images.append(img_buffer.getvalue())  # Raw PNG bytes
    return images

prompt = "Extract all readable text from these images and format it as structured Markdown."
def query_gemma3_with_images(image_bytes_list, model="gemma3:12b", prompt=prompt):
    response = ollama.chat(
        model=model,
        messages=[{
            "role": "user",
            "content": prompt,
            "images": image_bytes_list
        }]
    )
    return response["message"]["content"]

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
    print("Hello from pdf2md!")
    pdf_path = select_pdf()  # Replace with your PDF file
    images = convert_pdf_to_images(pdf_path)

    if images:
        print(f"Converted {len(images)} pages to images.")
        
        extracted_text = query_gemma3_with_images(images)
        
        # Save with the same name as the PDF but with .md extension
        md_path = os.path.splitext(pdf_path)[0] + ".md"
        with open(md_path, "w", encoding="utf-8") as md_file:
            md_file.write(extracted_text)
        print(f"\nMarkdown Conversion Complete! Check `{md_path}`.")
    else:
        print("No images found in the PDF.")


if __name__ == "__main__":
    main()
