import os
import pandas as pd

from categorization.product_categorizer import ProductCategorizer
from datetime import datetime
from leaflet_processing.leaflet_reader import LeafletReader
from openai_integration.openai_client import OpenAIClient
from result_handling.result_saver import ResultSaver
from typing import List


PDF_DIR = "pdf-files"
API_KEY_PATH = "openai_api_key.txt"
URL = "https://drive.google.com/drive/folders/1AR2_592V_x4EF97FHv4UPN5zdLTXpVB3"
DO_DOWNLOAD = False # just used for testing, saves time

def load_api_key(api_key_path: str) -> str:
    with open(api_key_path, 'r') as file:
        return file.readline().strip()

def append_metadata(df: pd.DataFrame):
    df['date_collected'] = datetime.now().strftime('%Y-%m-%d')
    df['calendar_week'] = datetime.now().isocalendar().week

def main():
    api_key = load_api_key(API_KEY_PATH)
    leaflet_reader = LeafletReader(download_url=URL)
    openai_client = OpenAIClient(api_key=api_key)
    result_saver = ResultSaver()
    categorizer = ProductCategorizer()

    # Next Steps:
    # Misc images should be in their own folder
    # Check PDF length, don't process if we already have all the images
    # Don't process if we already have the results

    if DO_DOWNLOAD:
        leaflet_reader.download_leaflets(PDF_DIR)

    for filename in os.listdir(PDF_DIR):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(PDF_DIR, filename)
            pdf_name, _ = os.path.splitext(os.path.basename(filename))
            output_dir = os.path.join(PDF_DIR, pdf_name)
            if result_saver.results_exist(output_dir):
                print(f"Already have results for {filename}, skipping...")
                continue

            image_paths: List[str] = leaflet_reader.convert_pdf_to_images(pdf_path, output_dir)
            all_products = []
            # Call LLMs for all images for one PDF at a time
            for image_path in image_paths:
                with open(image_path, "rb") as image_file:
                    print(f"Extracting data from {image_path}")
                    response = openai_client.extract(image_file.read())
                    for product in response.all_products:
                        product_as_dict = product.model_dump()
                        product_as_dict['pdf_name'] = os.path.basename(filename)
                        product_as_dict['page_number'] = os.path.basename(image_path)
                        all_products.append(product_as_dict)

            # Convert all_products to DataFrame for categorization
            if all_products:
                product_df = pd.DataFrame(all_products)

                # Categorize products
                print(f"Categorizing products for {filename}")
                categorized_df = categorizer.categorize_products(None, product_df, openai_client)
                append_metadata(categorized_df)

                # Save categorized products to an Excel file
                output_path = result_saver.save(categorized_df, output_dir)
                print(f"Categorized results from {filename} saved at: {output_path}")
            else:
                print(f"No products found to save from {filename}.")

if __name__ == "__main__":
    main()
