# categorization/product_categorizer.py

import pandas as pd
from typing import Any
from PIL import Image

class ProductCategorizer:
    def __init__(self):

        category_keywords = {
                "Barbecue": [],
                "Non-Barbecue": []
            }
        self.category_keywords = category_keywords

    def categorize_products(self, image: Image, data: pd.DataFrame) -> pd.DataFrame:
        """
        Categorizes products 
        Parameters:
            image (Image): Image data for potential future use (e.g., OCR or visual categorization).
            data (pd.DataFrame): DataFrame containing product information from OpenAI extraction.
        
        Returns:
            pd.DataFrame: DataFrame with an added 'Category' column for product categorization.
        """
        
        # Initialize the 'Category' column
        data['Barbecue'] = "YES"

        return data
