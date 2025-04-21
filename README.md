The main.py script is a tool for converting PDF documents into structured Markdown files, leveraging Google Gemini (genai) for OCR and text extraction. The workflow is as follows:

1. PDF Selection: Prompts the user to select a PDF file via a file dialog.
2. Image Extraction: Extracts all images within the PDF, saving them to a designated assets folder in your Obsidian vault.
3. Page Conversion: Converts each page of the PDF into an image.
4. LLM Query: Sends the images and a prompt to the Gemini large language model, instructing it to extract readable text and format it as well-structured Markdown, including correct references to the extracted images.
5. Markdown Output: Saves the resulting Markdown to a specified articles folder in your Obsidian vault, using the original PDF filename.

Your .env file must define the following 3 variables:

```
GENAI_API_KEY = "your_google_gemini_api_key"
OBSIDIAN_ASSETS_FOLDER = "path/to/your/Obsidian/Assets"
OBSIDIAN_ARTICLES_FOLDER = "path/to/your/Obsidian/Articles"
```

Where:

- GENAI_API_KEY: The API key for accessing Google Gemini (genai).
- OBSIDIAN_ASSETS_FOLDER: The directory where images extracted from within the PDF document will be saved.
- OBSIDIAN_ARTICLES_FOLDER: The directory where the converted Markdown files will be saved.

To run the project, type the following in your Terminal:

´´´
uv run main.py
´´´