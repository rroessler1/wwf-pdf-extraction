from datetime import datetime
import pandas as pd

from leaflet_processing.leaflet_reader import LeafletReader
from openai_integration.openai_client import OpenAIClient
from result_handling.result_saver import ResultSaver
from categorization.product_categorizer import ProductCategorizer
from confirmation.price_validation import price_valudator


PDF_DIR = "pdf-files"
API_KEY_PATH = "openai_api_key.txt"
URL = "https://drive.google.com/drive/folders/1AR2_592V_x4EF97FHv4UPN5zdLTXpVB3"

def load_api_key(api_key_path: str) -> str:
    with open(api_key_path, 'r') as file:
        return file.readline().strip()

def append_metadata(df: pd.DataFrame):
    df['date_collected'] = datetime.now().strftime('%Y-%m-%d')
    df['calendar_week'] = datetime.now().isocalendar().week

def main():
    api_key = load_api_key(API_KEY_PATH)
    leaflet_reader = LeafletReader(pdf_dir=PDF_DIR, download_url=URL)
    openai_client = OpenAIClient(api_key=api_key)
    result_saver = ResultSaver(output_dir="results")
    categorizer = ProductCategorizer()

    all_pdf_images = leaflet_reader.process_leaflets(do_download=False)
    all_products = []

    for pdf_name, pdf_images in all_pdf_images:
        for i, image_data in enumerate(pdf_images):
            response = openai_client.extract(image_data.getvalue())
            for product in response.all_products:
                product_as_dict = product.model_dump()
                product_as_dict['pdf_name'] = pdf_name
                product_as_dict['page_number'] = i + 1 # this is i + 1 so it's one-indexed
                all_products.append(product_as_dict)

    # Convert all_products to DataFrame for categorization
    if all_products:
        product_df = pd.DataFrame(all_products)

        # Categorize products
        categorized_df = categorizer.categorize_products(None, product_df, openai_client)
        categorized_df['price_check'] = price_valudator(categorized_df)
        append_metadata(categorized_df)

        # Save categorized products to an Excel file
        output_path = result_saver.save_to_excel(categorized_df)
        print(f"Categorized results saved at: {output_path}")
    else:
        print("No products found to save.")

if __name__ == "__main__":
    main()
