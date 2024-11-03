from typing import List
import pandas as pd
import os
from datetime import datetime

class ResultSaver:
    def __init__(self, output_dir: str = "results"):
        """
        Initializes the ResultSaver with the directory to save the results.

        Parameters:
            output_dir (str): Directory to save the Excel file with results.
        """
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def save_to_excel(self, categorized_df: pd.DataFrame) -> str:
        """
        Saves a pandas df to an Excel file.

        Parameters:
            categorized_df (pd.DataFrame): The pandas df.
        Returns:
            str: File path to the saved Excel file.
        """
        # Define the file name with a timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        excel_file_path = os.path.join(self.output_dir, f"extracted_data_{timestamp}.xlsx")
        csv_file_path = os.path.join(self.output_dir, f"extracted_data_{timestamp}.csv")

        # Save DataFrame to an Excel file
        categorized_df.to_excel(excel_file_path, index=False)
        categorized_df.to_csv(csv_file_path, index=False)
        return excel_file_path
