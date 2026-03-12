# inventory_events MVP Event Contract

## 1) Canonical event schema (one line = one event)

Each message in Kafka topic `inventory_events` and each line in `data/inventory_events.jsonl` should follow this JSON shape:

```json
{
  "event_id": "evt_20260312_000001",
  "event_type": "sale",
  "event_timestamp": "2026-03-12T10:30:00Z",
  "product_id": 1001,
  "store_id": 1,
  "quantity": 2,
  "unit_price": 89.99,
  "currency": "SEK",
  "stock_after_event": 48
}
```

Notes:
- `event_type` must be either `sale` or `restock`.
- `quantity` is always a **positive integer**. Direction is represented by `event_type`.
- `unit_price` means:
  - sale price per unit when `event_type = sale`
  - purchase cost per unit when `event_type = restock`

## 2) Field-by-field explanation

- **event_id**: Unique id for one inventory movement event.
- **event_type**: Type of stock movement (`sale` reduces stock, `restock` increases stock).
- **event_timestamp**: When the event happened (UTC recommended).
- **product_id**: Product identifier from product catalog.
- **warehouse_id**: Warehouse/store/inventory location where movement occurred.
- **quantity**: Number of units moved.
- **unit_price**: Monetary amount per unit for the movement.
- **currency**: ISO-like currency code for `unit_price` (MVP can enforce one currency).
- **stock_after_event**: Inventory level immediately after this event is applied.

## 3) Validation rules per field

- **event_id**
  - Required
  - String
  - Must be unique across all events
  - Suggested pattern: `^evt_[A-Za-z0-9_-]+$`

- **event_type**
  - Required
  - String enum: `sale` or `restock`

- **event_timestamp**
  - Required
  - String in ISO 8601 format (for example `2026-03-12T10:30:00Z`)
  - Should not be null

- **product_id**
  - Required
  - Integer
  - Must be > 0

- **store_id**
  - Required
  - Integer
  - Must be > 0

- **quantity**
  - Required
  - Integer
  - Must be >= 1

- **unit_price**
  - Required
  - Number
  - Must be >= 0

- **currency**
  - Required
  - String
  - Recommended MVP rule: exactly `SEK`

- **stock_after_event**
  - Required
  - Integer
  - Must be >= 0

## 4) Example events

### Sale event

```json
{
  "event_id": "evt_20260312_000101",
  "event_type": "sale",
  "event_timestamp": "2026-03-12T10:30:00Z",
  "product_id": 1001,
  "store_id": 1,
  "quantity": 2,
  "unit_price": 89.99,
  "currency": "USD",
  "stock_after_event": 48
}
```

### Restock event

```json
{
  "event_id": "evt_20260312_000102",
  "event_type": "restock",
  "event_timestamp": "2026-03-12T11:00:00Z",
  "product_id": 1001,
  "store_id": 1,
  "quantity": 20,
  "unit_price": 55.00,
  "currency": "USD",
  "stock_after_event": 68
}
```

## 5) Topic strategy recommendation for MVP

Use **one topic**: `inventory_events`.

Why this is best for MVP:
- Easier for a beginner team to manage and monitor.
- One producer contract and one consumer parsing flow.
- `event_type` cleanly separates behavior in code.
- Simplifies replay, debugging, and local testing.

When to split later:
- Very high event volume with different scaling needs per event type.
- Different retention/security requirements by event type.
- Many downstream consumers that only need a single subtype.
