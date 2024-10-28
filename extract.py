import gdown
import io
import pdf2image
import os

from openai_api import OpenAIClient


# Usage:
# Create a folder in Google Drive
# Share -> Share
# Change to "anyone with the link"
URL = "https://drive.google.com/drive/folders/1AR2_592V_x4EF97FHv4UPN5zdLTXpVB3"
PDF_DIR = "pdf-files"
API_KEY_PATH = "openai_api_key.txt"
gdown.download_folder(URL, output=PDF_DIR)

with open(API_KEY_PATH, 'r') as file:
    api_key = file.readline().strip()
openai_client = OpenAIClient(api_key=api_key)

for filename in os.listdir(PDF_DIR):
    if filename.endswith(".pdf"):
        file_path = os.path.join(PDF_DIR, filename)
        print("Converting...")
        pdf_images = pdf2image.convert_from_path(file_path)
        print("Done")
        for i, image in enumerate(pdf_images):
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            print("Calling ChatGPT...")
            response = openai_client.extract(img_byte_arr)
            print(response.message.content)
