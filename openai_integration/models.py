# openai_integration/models.py

from pydantic import BaseModel
from typing import List, Optional

class GroceryProduct(BaseModel):
    """
    Model for a grocery product extracted from the leaflet.
    
    Attributes:
        product_name (str): The name of the product.
        original_price (Optional[str]): The original price of the product.
        discount_price (Optional[str]): The discounted price of the product.
        percentage_discount (Optional[float]): The discount percentage.
        discount_details (Optional[str]): Additional discount details, if any.
    """
    product_name: str
    original_price: Optional[str] = None
    discount_price: Optional[str] = None
    percentage_discount: Optional[float] = None
    discount_details: Optional[str] = None

class Results(BaseModel):
    """
    Model for storing all extracted grocery products from the leaflet.
    
    Attributes:
        all_products (List[GroceryProduct]): List of extracted products.
    """
    all_products: List[GroceryProduct]
