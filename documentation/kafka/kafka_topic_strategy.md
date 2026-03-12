# Kafka Topic Strategy for MVP (Sportswear Inventory)## 1) One topic or multiple topics?

### Recommendation for MVP: **One topic**
Use a single topic for both event types:

- `sale`
- `restock`


## 2) Topic name

- `inventory_events`

Optional future split (not needed now):
- `inventory_sale_events`
- `inventory_restock_events`

For now, keep only `inventory_events` to reduce complexity.


## 3) Message key strategy for ordering/grouping

### Recommendation for MVP key: `"{store_id}:{product_id}"`

Example keys:
- `"1:1001"`
- `"2:2044"`

Why this key works:
- Groups events for the same product at the same location.
- Preserves order for that product-location stream (important for stock math).
- Keeps key generation simple in producer code.

Keep 1 partition initially, keys still prepare you for easy future scaling to more partitions.


## MVP baseline

- Topics: `inventory_events` only
- Partitions: `1`
- Key: `"{store_id}:{product_id}"`
- Event types in payload: `sale`, `restock`

