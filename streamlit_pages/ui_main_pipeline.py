import io
import os
import pandas as pd
import streamlit as st
import tempfile
import zipfile

from natsort import natsorted

from categorization.product_categorizer import ProductCategorizer
from leaflet_processing.leaflet_reader import LeafletReader
from openai_integration.mock_client import MockLLM
from openai_integration.openai_client import OpenAIClient
from result_handling.result_saver import ResultSaver
import main_pipeline
from settings import settings
from settings.constants import PROCESSABLE_FILE_EXTENSIONS


PDF_DIR = settings.PDF_DIR
URL = settings.URL
USE_TEST_LLM_CLIENT = False


# Load API key
def load_api_key(api_key_path: str) -> str:
    with open(api_key_path, 'r') as file:
        return file.readline().strip()



# Process directory
def process_directory(directory: str, output_dir: str, openai_client, categorizer, result_saver):
    bool=False
    bool,categorized_df =  main_pipeline.process_directory(directory, output_dir, openai_client, categorizer, result_saver,displaymood=True)
    if bool:
        return categorized_df
    else:
        st.write(f"No products found to save from {directory}.")
        return pd.DataFrame()


def get_processable_directories_in_zip(uploaded_zipfile):
    processable_directories = []
    with zipfile.ZipFile(io.BytesIO(uploaded_zipfile.read())) as zf:
        file_list = zf.namelist()
        processable_directories = [os.path.dirname(f) for f in file_list if can_process_file(f)]
    uploaded_zipfile.seek(0)
    return natsorted(set(processable_directories))


def can_process_file(file_name):
    _, ext = os.path.splitext(file_name)
    return str.lower(ext) in PROCESSABLE_FILE_EXTENSIONS


# Main function
def main():
    st.title("Product Categorization Application")

    # File uploader for PDF and image files
    uploaded_file = st.file_uploader("Upload your zipfile", type=["zip"])
    if uploaded_file:
        run(uploaded_file)

def write_inmemory_file_to_dir(file, output_dir):
    name, _ = os.path.basename(file)
    with open(os.path.join(output_dir, name), "wb") as output_file:
        output_file.write(file.read())

def get_processable_files_in_zip_directory(open_zipfile, directory):
    all_files_in_directory = [f for f in open_zipfile.namelist() if os.path.dirname(f) == directory]
    return [f for f in all_files_in_directory if can_process_file(f)]

def save_directory_in_zipfile_as_images(zipfile_directory, open_zipfile, output_dir, leaflet_reader: LeafletReader) -> str:
    # This is the final nested output directory to write images to
    output_dir = os.path.join(output_dir, zipfile_directory)
    os.makedirs(output_dir, exist_ok=True)
    processable_files = get_processable_files_in_zip_directory(open_zipfile, zipfile_directory)
    for filename in processable_files:
        if filename.endswith(".pdf"):
            with open_zipfile.open(filename) as pdf_file:
                leaflet_reader.convert_pdf_to_images(pdf_file, output_dir)
                st.write(f"PDF file [{filename}] successfully processed and converted to images.")
        else:
            # We have to save the images in the temporary directory
            with open(os.path.join(output_dir, os.path.basename(filename)), "wb") as output_image_file:
                with open_zipfile.open(filename) as file:
                    output_image_file.write(file.read())
    return output_dir

def run(uploaded_zipfile):
    # Load API key
    leaflet_reader = LeafletReader(download_url=URL)
    openai_client = MockLLM() if USE_TEST_LLM_CLIENT else OpenAIClient(api_key=st.secrets["openai_api_key"])
    result_saver = ResultSaver()
    categorizer = ProductCategorizer()

    # Initialize session state variables if not set
    if 'cat_df' not in st.session_state:
        st.session_state.cat_df = pd.DataFrame()
    if 'unique_categories' not in st.session_state:
        st.session_state.unique_categories = []

    #################
    # Initialize session state for selected files if not set
    if 'selected_folders' not in st.session_state:
        st.session_state.selected_folders = []

    # Checkbox for "Select All"
    select_all_checkbox = st.checkbox("Select All")
    deselect_all_checkbox = st.checkbox("Deselect All")

    folders = get_processable_directories_in_zip(uploaded_zipfile)

    file_df = pd.DataFrame({
        'Folders':folders,
        'Select': [True]*len(folders)
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
        disabled=["Folders"],
        hide_index=True,
    )


    # Update the session state with selected files
    st.session_state.selected_folders = df_edited[([not deselect_all_checkbox]*len(df_edited['Select']))*(df_edited['Select'])+[select_all_checkbox ]*len(df_edited['Select'])]["Folders"].to_list()

    # Display selected files for validation (optional)
    st.write("Selected folders:", st.session_state.selected_folders)

    #################


    # st.session_state.selected_folders = st.multiselect("Select PDF files to process", files)
    if st.button("Next - Process Selected Folders") and st.session_state.selected_folders:
        with tempfile.TemporaryDirectory() as temp_dir:
            print(f"Temporary directory created at: {temp_dir}")
            with zipfile.ZipFile(io.BytesIO(uploaded_zipfile.read())) as zf:
                for folder_name in st.session_state.selected_folders:
                    image_dir = save_directory_in_zipfile_as_images(folder_name, zf, temp_dir, leaflet_reader)
                    cat_df = process_directory(image_dir, image_dir, openai_client, categorizer, result_saver)
                    if not cat_df.empty:
                        st.session_state.cat_df = pd.concat([st.session_state.cat_df, cat_df])
                        st.session_state.unique_categories = st.session_state.cat_df['Category'].unique()
                    st.success(f"Processing completed for {folder_name}!")

            # Display unique categories for selection

            ####################
            if 'selected_categories' not in st.session_state:
                st.session_state.selected_categories = []


            select_all_checkbox_cat = st.checkbox("Select All Categories")
            deselect_all_checkbox_cat = st.checkbox("Deselect All categories")

            categories_df = pd.DataFrame({
                'Category':st.session_state.unique_categories,
                'Select': [False]*len(st.session_state.unique_categories)
                })

            # Table headers
            cat_df_edited = st.data_editor(
                categories_df,
                column_config={
                    'Select': st.column_config.CheckboxColumn(
                        "Select?",
                        help="Select your **favorite** categories",
                        default=False,
                    )
                },
                disabled=["Category"],
                hide_index=True,
            )

            # Update the session state with selected files
            st.session_state.selected_categories = cat_df_edited[([not deselect_all_checkbox_cat]*len(cat_df_edited['Select']))*(cat_df_edited['Select'])+[select_all_checkbox_cat]*len(cat_df_edited['Select'])]["Category"].to_list()
            # Display selected files for validation (optional)
            st.write("Selected files:", st.session_state.selected_categories)

            combined_results = result_saver.combine_results_from_all_subdirectories(temp_dir)
            combined_results_filename = result_saver.save(combined_results, temp_dir)
            with open(combined_results_filename, 'rb') as results_file:
                st.download_button("Download Results", results_file.read(), os.path.basename(combined_results_filename))

            ####################

            # st.session_state.selected_categories = st.multiselect("Select categories to include", st.session_state.unique_categories)

            # Step 5: Filter selected categories and save results
            if st.button("Next - Filter Categories") and st.session_state.selected_categories:
                filtered_df = st.session_state.cat_df[st.session_state.cat_df['Category'].isin(st.session_state.selected_categories)]
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
