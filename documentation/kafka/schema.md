# Data Schema: Inventory Events

This document defines the rules and structure for the event log within the inventory management system.

---

## 1. Root Object (API Response)

| Field | Type | Description |
| --- | --- | --- |
| `success` | Boolean | `true` if data was retrieved successfully. |
| `total_events` | Integer | Number of event objects in the list. |
| `message` | String | Status message for the system log. |
| `events` | Array | A list of event objects according to the specification below. |

---

## 2. Event Object

Each event represents a physical or administrative change to the stock levels.

| Field | Type | Validation Rules (Constraints) | Description |
| --- | --- | --- | --- |
| `event_id` | Integer | Unique, no duplicates allowed. | Unique ID for traceability. |
| `timestamp` | ISO8601 | YYYY-MM-DDTHH:MM:SSZ | Point in time when the event occurred. |
| **`event_type`** | String | `sale`, `restock`, or `stock_update` | Type of inventory event. |
| `product_id` | Integer | Positive integer. | Reference to the product's SKU/ID. |
| `product_name` | String | Cannot be empty. | Name of the product. |
| `price` | Number | Always $\ge 0$ | Unit price at the time of the event. |
| **`quantity_change`** | Integer | **See logic table below** | Number of units added or removed. |
| `stock_after` | Integer | Must never be $< 0$ | Stock level after the change is applied. |
| `store_id` | Integer | Positive integer. | ID of the physical warehouse location. |

---

## 3. `quantity_change` Logic by Type

To ensure data integrity, the following rules must be applied when an event is created:

| Event Type | Value Requirement | Purpose |
| --- | --- | --- |
| **`sale`** | **Negative ($< 0$)** | Items leaving the stock (e.g., `-1`). |
| **`restock`** | **Positive ($> 0$)** | Items arriving from a supplier (e.g., `+50`). |
| **`stock_update`** | **Flexible ($+/-$)** | Used for audits, shrinkage, or corrections. |

> **Note:** If a `sale` is registered with a positive value, the system should throw an error and abort the transaction.