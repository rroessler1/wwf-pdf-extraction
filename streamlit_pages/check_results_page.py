import streamlit as st
import pandas as pd
from PIL import Image

def show_check_results_page():
    # Load the data from csv file
    result_csv_path = 'pdf-files/results.csv'
    data = pd.read_csv(result_csv_path)

    # Ensure 'extracted_folder', 'extracted_page_number', and 'categorization_all_same' columns are present
    required_columns = ['extracted_folder', 'extracted_page_number', 'categorization_all_same']
    if not all(col in data.columns for col in required_columns):
        st.error(f"The dataframe must have {required_columns} columns.")
        st.stop()

    # Get the unique combinations of folder and page number
    unique_images = data[['extracted_folder', 'extracted_page_number']].drop_duplicates()

    # Initialize session state for current page index if not already set
    if 'current_page_index' not in st.session_state:
        st.session_state.current_page_index = 0

    # Navigation buttons for switching between images (top)
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Previous Image (Top)") and st.session_state.current_page_index > 0:
            st.session_state.current_page_index -= 1
    with col2:
        if st.button("Next Image (Top)") and st.session_state.current_page_index < len(unique_images) - 1:
            st.session_state.current_page_index += 1

    # Get the current folder and page number based on session state index
    current_image = unique_images.iloc[st.session_state.current_page_index]
    current_folder = current_image['extracted_folder']
    current_page_number = current_image['extracted_page_number']

    # Filter the dataframe based on the current folder, page number, and categorization_all_same == True
    filtered_data = data[
        (data['extracted_folder'] == current_folder) &
        (data['extracted_page_number'] == current_page_number) &
        (data['categorization_all_same'] == True)
    ]

    # Load the image corresponding to the current folder and page number
    try:
        image_path = f'pdf-files/{current_folder}/{current_page_number}'
        image = Image.open(image_path)
        st.sidebar.image(image, caption=f"Image for {current_folder}, Page {current_page_number}", use_column_width=True)
    except FileNotFoundError:
        st.sidebar.warning(f"Image not found for {current_folder}, Page {current_page_number}")

    # Set up the Streamlit page
    st.title("Supermarket Data Editing Tool")

    # Function to edit the dataframe row by row
    def edit_row(index, df, csv_path):
        with st.form(key=f"form_{index}"):
            st.write(f"Editing Row {index + 1}")

            # Create editable input fields for each relevant column in the row
            product_name = st.text_input("Product Name", value=str(df.loc[index, "final_product_name"]))
            original_price = st.text_input("Original Price", value=str(df.loc[index, "final_original_price"]))
            discount_price = st.text_input("Discount Price", value=str(df.loc[index, "final_discount_price"]))
            percentage_discount = st.text_input("Percentage Discount", value=str(df.loc[index, "final_percentage_discount"]))
            discount_details = st.text_input("Discount Details", value=str(df.loc[index, "extracted_discount_details"]))
            final_category = st.text_input("Final Category", value=str(df.loc[index, "final_category"]))

            # Button to save the changes for this row
            submitted = st.form_submit_button("Save Changes")

            if submitted:
                # Update the dataframe with the new values
                df.loc[index, "final_product_name"] = product_name
                df.loc[index, "final_original_price"] = original_price
                df.loc[index, "final_discount_price"] = discount_price
                df.loc[index, "final_percentage_discount"] = percentage_discount
                df.loc[index, "extracted_discount_details"] = discount_details
                df.loc[index, "final_category"] = final_category

                data.to_csv(csv_path, index=False)
                st.success(f"Row {index + 1} updated successfully!")

    # Display filtered rows and provide options for editing them
    if not filtered_data.empty:
        for idx in filtered_data.index:
            edit_row(idx, data, result_csv_path)

        # Display navigation buttons below the edit section
        st.write("### Navigation")
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Previous Image (Bottom)") and st.session_state.current_page_index > 0:
                st.session_state.current_page_index -= 1
        with col2:
            if st.button("Next Image (Bottom)") and st.session_state.current_page_index < len(unique_images) - 1:
                st.session_state.current_page_index += 1

        # Display the updated dataframe after editing
        st.write("### Updated Dataframe")
        st.dataframe(filtered_data)
    else:
        st.write("No rows available for the current image with categorization_all_same == True.")
