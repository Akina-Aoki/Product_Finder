# Validations in our Repository at Sprint # 3

## 1) API-level validation (Pydantic models)
These validations are enforced when requests hit the FastAPI endpoints that accept `SaleEvent` / `InventoryEvent` models. `app/main.py` uses those models directly in endpoint signatures, so invalid payloads should be rejected before being sent to Kafka.

Sale item price must be > 0
```
SaleItem.price: Field(gt=0)
```

Sale item quantity must be > 0
```
SaleItem.quantity: Field(gt=0)
```

Inventory `stock_after_event` must be >= 0 (if provided)
```
stock_after_event: Optional[int] = Field(..., ge=0)
```

Restock event must have positive quantity_change
```
if event_type == "restock" and quantity_change <= 0: raise ValueError(...)
```

Stock update must include either `OR stock_after_event` OR `non-zero quantity_change`
OR stock_after_event
```
if event_type == "stock_update" and quantity_change == 0 and stock_after_event is None: raise ValueError(...)
```



----  



## 2) Database-level validation (PostgreSQL CHECK constraints)
These are hard constraints in `sql/init.sql`, so DB writes violating them fail even if app logic misses something.

Product price cannot be below zero
```
staging.products.price CHECK (price >= 0)
```

Inventory amount cannot be below zero
```
staging.inventories.amount CHECK (amount >= 0)
```

Order total price cannot be below zero
```
staging.orders.order_price CHECK (order_price >= 0)
```

Item price cannot be below zero
```
staging.items.item_price CHECK (item_price >= 0)
```

Item quantity cannot be below zero
```
staging.items.quantity CHECK (quantity >= 0)
```


-----



## 3) Consumer logic that actively clamps inventory to non-negative
When processing events, inventory updates use GREATEST(..., 0) so values are forcibly prevented from going below zero.

- Insert inventory amount as `GREATEST(value, 0)`

- Update existing inventory as `GREATEST(current + delta, 0)`

- Absolute stock updates also use `GREATEST(EXCLUDED.amount, 0)`

## 3 layers protecting non-negative inventory:
```

Pydantic (stock_after_event >= 0),

SQL CHECK (amount >= 0),

Consumer clamping with GREATEST(..., 0).
```