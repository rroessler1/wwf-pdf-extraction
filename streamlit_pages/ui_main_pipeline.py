import glob
import os
import pandas as pd
import streamlit as st
from datetime import datetime
from natsort import natsorted

from categorization.product_categorizer import ProductCategorizer
from leaflet_processing.leaflet_reader import LeafletReader
from openai_integration.openai_client import OpenAIClient
from result_handling.result_saver import ResultSaver

from settings import settings


PDF_DIR = settings.PDF_DIR
API_KEY_PATH = settings.API_KEY_PATH
URL = settings.URL

st.markdown("""
            <style>
                .stMarkdown > div {
                    padding-left: 4px; 
                    background-color: LightGray;
                    margin-top: 1px;
                    margin-bottom: 1px;
                    margin-right: 1px;
                    margin-left: 1px;
                }
            </style>
            """, unsafe_allow_html=True)


# Load API key
def load_api_key(api_key_path: str) -> str:
    with open(api_key_path, 'r') as file:
        return file.readline().strip()

# Append metadata
def append_metadata(df: pd.DataFrame):
    df['date_collected'] = datetime.now().strftime('%Y-%m-%d')
    df['calendar_week'] = datetime.now().isocalendar()[1]

# Get all image paths
def get_all_image_paths(directory: str):
    paths = []
    for ext in ["png", "PNG", "jpg", "jpeg", "JPG", "JPEG"]:
        paths.extend(glob.glob(f"{directory}/*.{ext}"))
    return natsorted(paths)

# Process directory
def process_directory(directory: str, output_dir: str, openai_client, categorizer, result_saver):
    if result_saver.results_exist(output_dir):
        st.write(f"Results already exist for {directory}, skipping...")
        return pd.DataFrame()
    
    image_paths = get_all_image_paths(directory)
    all_products = []
    
    progress_bar = st.progress(0)
    total_directories = len(image_paths)
    
    for i,image_path in enumerate(image_paths):
        with open(image_path, "rb") as image_file:
            st.write(f"Extracting data from {image_path}")
            response = openai_client.extract(image_file.read())
            for product in response.all_products:
                product_as_dict = product.model_dump()
                product_as_dict['folder'] = os.path.basename(directory)
                product_as_dict['page_number'] = os.path.basename(image_path)
                all_products.append(product_as_dict)
        progress_bar.progress((i + 1) / total_directories)

    if all_products:
        product_df = pd.DataFrame(all_products)
        st.write(f"{len(all_products)} products detected for categorization.")
        
        # Categorize products
        categorized_df = categorizer.categorize_products(None, product_df, openai_client)
        append_metadata(categorized_df)
        
        return categorized_df
    else:
        st.write(f"No products found to save from {directory}.")
        return pd.DataFrame()

# Main function
# Main function
def main():
    st.title("Product Categorization Application")

    # Load API key
    api_key = load_api_key(API_KEY_PATH)
    leaflet_reader = LeafletReader(download_url=URL)
    openai_client = OpenAIClient(api_key=api_key)
    result_saver = ResultSaver()
    categorizer = ProductCategorizer()

    # Initialize session state variables if not set
    if 'cat_df' not in st.session_state:
        st.session_state.cat_df = pd.DataFrame()
    if 'unique_categories' not in st.session_state:
        st.session_state.unique_categories = []

    # Step 1: Ask if user wants to download files
    if st.button("Download Files"):
        leaflet_reader.download_leaflets(PDF_DIR)
        st.write("Files downloaded from the server.")

    # Step 2: Check if results file exists
    if result_saver.results_exist(PDF_DIR):
        st.write("Results file already exists. To create new results, delete the existing file and rerun.")
        return

    # Step 3: List available files and allow selection
    files = [f for f in os.listdir(PDF_DIR) if f.endswith(".pdf")]
    
    #################
    # Initialize session state for selected files if not set
    if 'selected_files' not in st.session_state:
        st.session_state.selected_files = []
    
    
    with st.container():
        # Checkbox for "Select All"
        select_all_checkbox = st.checkbox("Select All")
        deselect_all_checkbox = st.checkbox("Deselect All")
        
        file_df = pd.DataFrame({
            'PDF File':files,
            'Select': [False]*len(files)
        })
        
        # Table headers
        df_edited = st.data_editor(
            file_df,
            column_config={
                'Select': st.column_config.CheckboxColumn(
                    "Select?",
                    help="Select your **favorite** files",
                    default=False,
                )
            },
            disabled=["PDF File"],
            hide_index=True,
        )
        
        
        # Update the session state with selected files
        st.session_state.selected_files = df_edited[([not deselect_all_checkbox]*len(df_edited['Select']))*(df_edited['Select'])+[select_all_checkbox ]*len(df_edited['Select'])]["PDF File"].to_list()

        # Display selected files for validation (optional)
    st.write("Selected files:", st.session_state.selected_files)

    #################
    
    
    # st.session_state.selected_files = st.multiselect("Select PDF files to process", files)
    if st.button("Next - Process Selected Files") and st.session_state.selected_files:
        for filename in st.session_state.selected_files:
            pdf_path = os.path.join(PDF_DIR, filename)
            pdf_name, _ = os.path.splitext(filename)
            output_dir = os.path.join(PDF_DIR, pdf_name)
            if result_saver.results_exist(output_dir):
                st.write(f"Already have results for {filename}, skipping...")
            else:
                leaflet_reader.convert_pdf_to_images(pdf_path, output_dir)
        st.write("PDF files processed and converted to images.")

    # Step 4: Process each selected directory and store results in session state
    if st.button("Process Directories"):
        all_directories = [os.path.join(PDF_DIR, f).replace('.pdf','') for f in selected_files]
        
        
        for i, directory in enumerate(all_directories):
            cat_df = process_directory(directory, directory, openai_client, categorizer, result_saver)
            if not cat_df.empty:
                st.session_state.cat_df = pd.concat([st.session_state.cat_df, cat_df])
                st.session_state.unique_categories = st.session_state.cat_df['Category'].unique()
            
        
        st.success("Processing completed for all directories!")

    # Display unique categories for selection
    
    ####################
    if 'selected_categories' not in st.session_state:
        st.session_state.selected_categories = []

    # Checkbox for "Select All"
    select_all_checkbox_cat = st.checkbox("Select All Categories")
    deselect_all_checkbox_cat = st.checkbox("Deselect All categories")
    
    # Table headers
    col1, col2 = st.columns([0.1, 0.9])
    col1.write("Select")
    col2.write("File Name")
    
    # Table rows for each file
    selected_categories = []
    for category in st.session_state.unique_categories:
        # Display each file with a checkbox in two columns
        col1, col2 = st.columns([0.05, 0.9])

        # If "Select All" is checked, all individual checkboxes are set to True
        checked = (select_all_checkbox_cat or st.session_state.get(f"checkbox_{category}", False)) and not deselect_all_checkbox_cat
        
        # Create checkbox for each file
        checked = col1.checkbox("", key=f"checkbox_{category}", value=checked)
        col2.write(category)
        
        # Add the file to selected list if checkbox is checked
        if checked:
            selected_categories.append(category)
    

    # Update the session state with selected files
    st.session_state.selected_categories = selected_categories

    # Display selected files for validation (optional)
    st.write("Selected files:", st.session_state.selected_categories)

    ####################
    
    # st.session_state.selected_categories = st.multiselect("Select categories to include", st.session_state.unique_categories)
    
    # Step 5: Filter selected categories and save results
    if st.button("Next - Filter Categories") and selected_categories:
        filtered_df = st.session_state.cat_df[st.session_state.cat_df['Category'].isin(selected_categories)]
        st.write(f"{len(filtered_df)} products selected.")
        
        # Save filtered results
        output_path = result_saver.save(filtered_df, PDF_DIR)
        st.write(f"Filtered results saved at: {output_path}")

    # Step 6: Combine and save final results
    if st.button("Combine and Save Results"):
        combined_results = result_saver.combine_results_from_all_subdirectories(PDF_DIR)
        combined_results_filename = result_saver.save(combined_results, PDF_DIR)
        st.write(f"Combined results saved at: {combined_results_filename}")

# Run main function
if __name__ == "__main__":
    main()
