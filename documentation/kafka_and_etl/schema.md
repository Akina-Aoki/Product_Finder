# Data Schema: Inventory Events

This document defines the rules and structure for the event log within the inventory management system.

## Implemented Event Types

The current codebase supports these event types:

### `sale`
- accepted by `/api/sales` and `/api/sales/batch`,
- creates rows in `staging.orders` and `staging.items`,
- decreases inventory in `staging.inventories`.

### `restock`
- accepted through `/api/inventory-events/batch`,
- increases inventory using `quantity_change`.

### `stock_update`
- accepted through `/api/inventory-events/batch`,
- either applies a delta or sets an absolute inventory value.

### `new_product`
- accepted by `/api/products/new` and `/api/products/new/batch`,
- inserts or upserts a product,
- seeds starting inventory for stores `1` and `2`.

---

## Database Design

### `staging` schema
The staging layer stores operational tables such as:

- `categories`
- `colours`
- `sizes`
- `genders`
- `brands`
- `products`
- `stores`
- `inventories`
- `orders`
- `items`

This schema acts as the integration layer where both seed data and streaming outputs land.

### `refined` schema
The refined layer exposes materialized views for analytics:

- `refined.products`
- `refined.stores`
- `refined.inventories`
- `refined.items`
- `refined.orders`


