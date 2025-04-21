import io
import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image  # Pillow for image processing
from google import genai
import shutil
import pymupdf  # PyMuPDF for PDF processing
from pdf2image import convert_from_path
from dotenv import load_dotenv

# Load the environment variable for the Gemini API key
load_dotenv()
client = genai.Client(os.getenv("GENAI_API_KEY"))
Obsidian_Assets_folder = os.getenv("OBSIDIAN_ASSETS_FOLDER")
if Obsidian_Assets_folder is None:
    raise ValueError("Please set the OBSIDIAN_ASSETS_FOLDER environment variable.")
Obsidian_Articles_folder = os.getenv("OBSIDIAN_ARTICLES_FOLDER")
if Obsidian_Articles_folder is None:
    raise ValueError("Please set the OBSIDIAN_ARTICLES_FOLDER environment variable.")

class PdfToImg:
    """A class to convert PDF files to images using pdf2image."""

    def __init__(
        self,
        dpi: int = 200,
        fmt: str = "jpeg",
        size: tuple = (700, None),
        output_folder: str = "./Output",
    ):

        self.fmt = fmt  # output file format {jpeg, ppm, png}
        self.output_folder = output_folder
        self.paths_only = True  # return only the paths of the images
        self.size = size  # shape of the resulting images
        self.dpi = dpi  # dpi of the resulting images

        # Remove the output folder if it already exists
        if os.path.exists(self.output_folder):
            shutil.rmtree(self.output_folder)

        os.makedirs(self.output_folder, exist_ok=True)

    def convert(self, file_path: str) -> list[str]:
        """Convert a PDF file to images."""

        img_paths = convert_from_path(
            file_path,
            fmt=self.fmt,
            output_folder=self.output_folder,
            paths_only=self.paths_only,
            size=self.size,
            dpi=self.dpi,
        )

        if img_paths is None or len(img_paths) == 0:
            raise ValueError("No images generated.")

        return img_paths

def convert_pdf_to_images(pdf_path):
    pdf2img = PdfToImg()
    return pdf2img.convert(pdf_path)

def extract_images_from_pdf(pdf_path):
    # os.path.join(os.path.dirname(pdf_path), "Assets")
    subfolder = os.path.splitext(os.path.basename(pdf_path))[0]
    assets_folder = os.path.join(Obsidian_Assets_folder, subfolder)
    os.makedirs(assets_folder, exist_ok=True)
    doc = pymupdf.open(pdf_path)
    image_paths = []
    img_count = 0
    for page_num in range(len(doc)):
        page = doc[page_num]
        images = page.get_images(full=True)
        for img_index, img in enumerate(images):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            # Save as JPEG regardless of original format
            img_filename = f"page{page_num+1}_img{img_index+1}.jpg"
            img_path = os.path.join(assets_folder, img_filename)
            with open(img_path, "wb") as img_file:
                # Convert to JPEG if not already
                if image_ext.lower() != "jpg" and image_ext.lower() != "jpeg":
                    pil_img = Image.open(io.BytesIO(image_bytes))
                    pil_img.convert("RGB").save(img_file, "JPEG")
                else:
                    img_file.write(image_bytes)
            image_paths.append(img_path)
            img_count += 1
    print(f"Extracted {img_count} images to {assets_folder}")
    return image_paths

def query_llm_with_images(image_paths, prompt):
    # Use the Gemini multimodal model
    model = "gemini-2.0-flash"
    # Convert image file paths to PIL images
    images = [Image.open(path) for path in image_paths]
    # Send prompt and images
    response = client.models.generate_content(model=model, contents=[images, prompt])
    return response.text

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
    if not pdf_path:
        print("No PDF file selected. Exiting.")
        return
    print(f"Selected PDF: {pdf_path}")
    
    assets = extract_images_from_pdf(pdf_path)
    
    if assets:
        print(f"Extracted {len(assets)} images from the PDF.")
    else:
        print("No images extracted from the PDF.")
    
    images = convert_pdf_to_images(pdf_path)

    if images:
        print(f"Converted {len(images)} pages to images.")
        
        prompt = """Extract all the readable text from these images and format it as structured Markdown. The images are from a PDF document. Please ensure the Markdown is well-structured and easy to read. Finally, reference the extracted images within the Markdown file using relative paths, e.g. ![](./Assets/page1_img1.jpg), where page1 and img1 are the page and image index numbers."""
        
        extracted_text = query_llm_with_images(images, prompt)
        
        # Save with the same name as the PDF but with .md extension
        filename = os.path.splitext(os.path.basename(pdf_path))[0]
        md_path = os.path.join(Obsidian_Articles_folder, f"{filename}.md")
        # md_path = os.path.splitext(pdf_path)[0] + ".md"
        with open(md_path, "w", encoding="utf-8") as md_file:
            md_file.write(extracted_text)
        print(f"\nMarkdown Conversion Complete! Check `{md_path}`.")
    else:
        print("No images found in the PDF.")

if __name__ == "__main__":
    main()
