# leaflet_processing/leaflet_reader.py

import gdown
import glob
import io
import os
import streamlit as st

from natsort import natsorted
from typing import List
import pypdfium2 as pdfium
from PyPDF2 import PdfReader


class LeafletReader:

    def __init__(self, download_url: str,do_download=True):

        """
        Initializes the LeafletReader with the directory for PDFs and download URL.

        Parameters:
            download_url (str): URL of the leaflet folder to download.
        """
        self.download_url = download_url

        # if do_download:
        #     self.download_leaflet()

        # self.all_files = os.listdir(self.pdf_dir)
        # self.selected_files = os.listdir(self.pdf_dir)

    def download_leaflets(self, pdf_dir: str) -> None:
        """
        Downloads the PDF leaflets from the specified URL and saves them in pdf_dir.
        """
        # TODO: this should check for duplicates and not re-download them
        # but no need to do it now as we probably won't use Google Drive for the final solution
        os.makedirs(pdf_dir, exist_ok=True)
        gdown.download_folder(self.download_url, output=pdf_dir)
        print("Leaflets downloaded successfully.")

    def convert_pdf_to_images(self, pdf_path, output_dir: str, overwrite_images = False) -> List[str]:
        """
        Splits a PDF into individual images.

        Parameters:
            pdf_path (str): Path to the PDF file.
            output_dir (str): Path to where the images will be written.
            overwrite_images (bool): If False, skips the conversion to images, if enough images are found.

        Returns:
            List[str]: List of image paths.
        """
        # FIXME: this no longer works for the non-UI code path, fix that
        if not overwrite_images:
            reader = PdfReader(io.BytesIO(pdf_path.read()))
            png_files = glob.glob(f"{output_dir}/*.png")
            png_files = [os.path.basename(f) for f in png_files]
            pdf_name, _ = os.path.splitext(os.path.basename(pdf_path.name))


            expected_image_names = set([f"{pdf_name}_{i+1}.png" for i in range(len(reader.pages))])
            if len(expected_image_names - set(png_files)) == 0:
                print(f"Found PNG images for {pdf_path}. Skipping conversion from PDF to images.")
                return natsorted(png_files)

        print(f"Converting {pdf_path} to images.")
        os.makedirs(output_dir, exist_ok=True)

        pdf_path.seek(0)
        pdf_doc = pdfium.PdfDocument(pdf_path.read())
        paths = []

        for i in range(len(pdf_doc)):
            page = pdf_doc[i]
            image = page.render(scale=4).to_pil()
            output_filename = os.path.join(output_dir, f"{pdf_name}_{i+1}.png")
            image.save(output_filename, format='PNG')
            paths.append(output_filename)
            st.write(f"Wrote image [{i}].")

        return natsorted(paths)
