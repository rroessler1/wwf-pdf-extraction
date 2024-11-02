from typing import List
import pandas as pd
from openai_integration.models import GroceryProduct
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

    def save_to_excel(self, products: List[GroceryProduct]) -> str:
        """
        Saves a list of GroceryProduct instances to an Excel file.
        
        Parameters:
            products (List[GroceryProduct]): List of GroceryProduct instances to save.
        
        Returns:
            str: File path to the saved Excel file.
        """
        # Convert GroceryProduct instances to a list of dictionaries
        data = [product.dict() for product in products]
        
        # Create a DataFrame from the list of dictionaries
        df = pd.DataFrame(data)
        
        # Define the file name with a timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(self.output_dir, f"extracted_data_{timestamp}.xlsx")
        
        # Save DataFrame to an Excel file
        df.to_excel(file_path, index=False)
        print(f"Data saved to {file_path}")
        
        return file_path
