from pydantic import AliasChoices, BaseModel, Field, model_validator
from typing import List, Literal, Optional
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


class InventoryEvent(BaseModel):
    """Model for restock and stock update events that change inventory levels."""

    event_id: int
    event_type: Literal["restock", "stock_update"]
    timestamp: datetime
    store_id: int = Field(validation_alias=AliasChoices("store_id", "warehouse_id"))
    product_id: int
    quantity_change: int
    stock_after_event: Optional[int] = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_business_rules(self):
        if self.event_type == "restock" and self.quantity_change <= 0:
            raise ValueError("restock events must have a positive quantity_change")
        if self.event_type == "stock_update" and self.quantity_change == 0 and self.stock_after_event is None:
            raise ValueError("stock_update must include a non-zero quantity_change or stock_after_event")
        return self
