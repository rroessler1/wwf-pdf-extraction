import glob
import os
import pandas as pd

from categorization.product_categorizer import ProductCategorizer
from datetime import datetime
from leaflet_processing.leaflet_reader import LeafletReader
from natsort import natsorted
from openai_integration.openai_client import OpenAIClient
from result_handling.result_saver import ResultSaver


PDF_DIR = "pdf-files"
API_KEY_PATH = "openai_api_key.txt"
URL = "https://drive.google.com/drive/folders/1AR2_592V_x4EF97FHv4UPN5zdLTXpVB3"
DO_DOWNLOAD = False # just used for testing, saves time

def load_api_key(api_key_path: str) -> str:
    with open(api_key_path, 'r') as file:
        return file.readline().strip()

def append_metadata(df: pd.DataFrame):
    df['date_collected'] = datetime.now().strftime('%Y-%m-%d')
    try:
        df['calendar_week'] = datetime.now().isocalendar().week
    except:
        df['calendar_week'] = datetime.now().isocalendar()[1] # now().isocalendar().week Didn't work for Darya so I changed it in this way

def main():
    api_key = load_api_key(API_KEY_PATH)
    leaflet_reader = LeafletReader(download_url=URL)
    openai_client = OpenAIClient(api_key=api_key)
    result_saver = ResultSaver()
    categorizer = ProductCategorizer()

    if DO_DOWNLOAD:
        leaflet_reader.download_leaflets(PDF_DIR)

    if result_saver.results_exist(PDF_DIR):
        print(f"Already found a results file: [{os.path.join(PDF_DIR, result_saver.output_file_name)}], nothing to do.")
        print("If you'd like new results, delete or rename the results file and rerun the script.")
        return

    for filename in os.listdir(PDF_DIR):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(PDF_DIR, filename)
            pdf_name, _ = os.path.splitext(os.path.basename(filename))
            output_dir = os.path.join(PDF_DIR, pdf_name)
            if result_saver.results_exist(output_dir):
                print(f"Already have results for {filename}, skipping...")
                continue
            else:
                leaflet_reader.convert_pdf_to_images(pdf_path, output_dir)

    all_directories = [entry.path for entry in os.scandir(PDF_DIR) if entry.is_dir()]
    for directory in all_directories:
            process_directory(directory, directory, openai_client, categorizer, result_saver)

    combined_results = result_saver.combine_results_from_all_subdirectories(PDF_DIR)
    combined_results_filename = result_saver.save(combined_results, PDF_DIR)
    print(f"Combined results from all files in {PDF_DIR} saved at: {combined_results_filename}")


def get_all_image_paths(directory: str):
    paths = []
    for ext in ["png", "PNG", "jpg", "jpeg", "JPG", "JPEG"]:
        paths.extend(glob.glob(f"{directory}/*.{ext}"))
    return natsorted(paths)


def process_directory(directory: str, output_dir: str, openai_client, categorizer, result_saver):
    if result_saver.results_exist(output_dir):
        print(f"Already have results for {directory}, skipping...")
        return

    image_paths = get_all_image_paths(directory)
    all_products = []
    # Call LLMs for all images for one PDF at a time
    for image_path in image_paths:
        with open(image_path, "rb") as image_file:
            print(f"Extracting data from {image_path}")
            response = openai_client.extract(image_file.read())
            for product in response.all_products:
                product_as_dict = product.model_dump()
                # TODO: might need a better way to identify this than just folder
                # or at least, make sure the folder isn't just "Denner", but has a date or calendar week
                product_as_dict['folder'] = os.path.basename(directory)
                product_as_dict['page_number'] = os.path.basename(image_path)
                all_products.append(product_as_dict)

    # Convert all_products to DataFrame for categorization
    if all_products:
        product_df = pd.DataFrame(all_products)

        # Categorize products
        print(f"Categorizing products for {directory}")
        categorized_df = categorizer.categorize_products(None, product_df, openai_client)
        append_metadata(categorized_df)

        # Save categorized products to an Excel file
        output_path = result_saver.save(categorized_df, output_dir)
        print(f"Categorized results from {directory} saved at: {output_path}")
    else:
        print(f"No products found to save from {directory}.")


if __name__ == "__main__":
    main()
