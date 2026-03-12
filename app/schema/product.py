from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

class SaleItem(BaseModel):
    """Model for a single item in a sale event, representing a product sold."""
    product_id: int
    price: float = Field(gt=0, description="Price of the product. Must be greater than 0.")
    quantity: int = Field(gt=0, description="Quantity of the product sold. Must be greater than 0.")

class SaleEvent(BaseModel):
    """Model for a sale event, representing a collection of products sold."""
    event_id: int
    event_type: str = Field(default="sale")
    timestamp: datetime
    store_id: int
    items: List[SaleItem]