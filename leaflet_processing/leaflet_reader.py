# leaflet_processing/leaflet_reader.py

import os
import io
from typing import List
from pdf2image import convert_from_path
import gdown

class LeafletReader:
    def __init__(self, pdf_dir: str, download_url: str):
        """
        Initializes the LeafletReader with the directory for PDFs and download URL.

        Parameters:
            pdf_dir (str): Directory to save downloaded PDFs.
            download_url (str): URL of the leaflet folder to download.
        """
        self.pdf_dir = pdf_dir
        self.download_url = download_url

    def download_leaflet(self) -> None:
        """
        Downloads the PDF leaflets from the specified URL and saves them in pdf_dir.
        """
        os.makedirs(self.pdf_dir, exist_ok=True)
        gdown.download_folder(self.download_url, output=self.pdf_dir)
        print("Leaflets downloaded successfully.")

    def split_pdf_to_images(self, pdf_path: str) -> List[io.BytesIO]:
        """
        Splits a PDF into individual images.

        Parameters:
            pdf_path (str): Path to the PDF file.

        Returns:
            List[io.BytesIO]: List of images in BytesIO format.
        """
        images = convert_from_path(pdf_path)
        image_bytes = []

        for image in images:
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            image_bytes.append(img_byte_arr)

        return image_bytes

    def process_leaflets(self, do_download=True) -> List[List[io.BytesIO]]:
        """
        Downloads leaflets and converts each PDF into images.

        Returns:
            List[tuple(str, List[io.BytesIO])]: List of (file name, images) for each PDF.
        """
        if do_download:
            self.download_leaflet()
        all_images = []

        for filename in os.listdir(self.pdf_dir):
            if filename.endswith(".pdf"):
                pdf_path = os.path.join(self.pdf_dir, filename)
                print(f"Processing {filename}...")
                pdf_images = self.split_pdf_to_images(pdf_path)
                all_images.append((os.path.basename(filename), pdf_images))
                print(f"{filename} converted to images.")

        return all_images
