# leaflet_processing/leaflet_reader.py

import gdown
import glob
import os

from natsort import natsorted
from typing import List
from pdf2image import convert_from_path
from PyPDF2 import PdfReader


class LeafletReader:
    def __init__(self, download_url: str):
        """
        Initializes the LeafletReader with the directory for PDFs and download URL.

        Parameters:
            download_url (str): URL of the leaflet folder to download.
        """
        self.download_url = download_url

    def download_leaflets(self, pdf_dir: str) -> None:
        """
        Downloads the PDF leaflets from the specified URL and saves them in pdf_dir.
        """
        # TODO: this should check for duplicates and not re-download them
        # but no need to do it now as we probably won't use Google Drive for the final solution
        os.makedirs(pdf_dir, exist_ok=True)
        gdown.download_folder(self.download_url, output=pdf_dir)
        print("Leaflets downloaded successfully.")

    def convert_pdf_to_images(self, pdf_path: str, output_dir: str, overwrite_images = False) -> List[str]:
        """
        Splits a PDF into individual images.

        Parameters:
            pdf_path (str): Path to the PDF file.
            output_dir (str): Path to where the images will be written.
            overwrite_images (bool): If False, skips the conversion to images, if enough images are found.

        Returns:
            List[str]: List of image paths.
        """
        if not overwrite_images:
            reader = PdfReader(pdf_path)
            png_files = glob.glob(f"{output_dir}/*.png")
            expected_image_names = set([f"{i+1}.png" for i in range(len(reader.pages))])
            if len(expected_image_names - set(png_files)) == 0:
                print(f"Found PNG images for {pdf_path}. Skipping conversion from PDF to images.")
                return natsorted(png_files)

        os.makedirs(output_dir, exist_ok=True)
        images = convert_from_path(pdf_path)
        paths = []

        for i, image in enumerate(images):
            output_filename = os.path.join(output_dir, f"{i+1}.png")
            image.save(output_filename, format='PNG')
            paths.append(output_filename)

        return natsorted(paths)
