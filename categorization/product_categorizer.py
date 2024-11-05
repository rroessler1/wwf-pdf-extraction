# categorization/product_categorizer.py

import pandas as pd
from typing import Any
from PIL import Image

from openai_integration.models import CategorizationResult
from openai_integration.openai_client import OpenAIClient


class ProductCategorizer:
    def __init__(self):

        category_keywords = {
                "Barbecue": [],
                "Non-Barbecue": []
            }
        self.category_keywords = category_keywords

    def categorize_products(self, image: Image, data: pd.DataFrame, openai_client: OpenAIClient) -> pd.DataFrame:
        """
        Categorizes products 
        Parameters:
            image (Image): Image data for potential future use (e.g., OCR or visual categorization).
            data (pd.DataFrame): DataFrame containing product information from OpenAI extraction.
            openai_client (OpenAIClient): OpenAI Client for interacting with OpenAI API.
        
        Returns:
            pd.DataFrame: DataFrame with an added 'Category' column for product categorization.
        """
        
        # Initialize the 'Category' column
        data['Barbecue'] = "YES"

        categorization_results: CategorizationResult = openai_client.categorize_products(data)

        product_categories = []
        for product in categorization_results.all_products:
            product_categories.append(product.category)

        if len(data.index) == len(product_categories):
            data['Category'] = product_categories
        else:
            raise Warning("Length of the data and the assigned categories do not match!")

        return data
