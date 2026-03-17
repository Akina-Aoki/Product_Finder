# Product_Finder

## Project Overview

This system captures real-time inventory events — such as **sales** and **restocks** — and stores them durably in a PostgreSQL database. Events are produced by a FastAPI application, transmitted through an Apache Kafka topic (`inventory_events`), and consumed by a dedicated database consumer that persists each event. A base dataset of products, stores, categories, and other reference data is pre-loaded from CSV files into the database at startup.

## User Story
 ![User Story](assets/User_Story_Version2.jpeg)


[Repository Setup](documentation/kafka/setup.md)
---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Docker Compose                      │
│                                                      │
│   ┌──────────────────┐    ┌──────────────────────┐   │
│   │   PostgreSQL 16  │    │   Apache Kafka        │   │
│   │  (SportWearDB)   │    │  (inventory_events)   │   │
│   └──────────────────┘    └──────────────────────┘   │
└─────────────────────────────────────────────────────┘
         ▲  ▲                          ▲
         │  │                          │
         │  └─── init.sql (schema)     │
         │        CSV seed data        │
         │                             │
   db_consumer.py            app/main.py (FastAPI)
   (reads Kafka,              (receives HTTP requests,
    writes to DB)              publishes to Kafka)
```

### Other Documentations
[Minimum Viable Product and User Stories](documentation/kafka/MVP.md)
[Connect Host Services](documentation/kafka/connect_docker_psql_kafka.md)


### Components

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Docker Compose** | `docker-compose.yml` | Launches PostgreSQL and Kafka as local services |
| **PostgreSQL** | `postgres:16-alpine` | Stores all reference data and inventory events |
| **Apache Kafka** | `apache/kafka:latest` | Message broker for the `inventory_events` topic |
| **init.sql** | SQL DDL script | Creates both `staging` and `refined` schemas with batch-load logic on first startup |
| **CSV files** | `data/raw/*.csv` | Seed data loaded into the database (products, stores, brands, etc.) |
| **FastAPI app** | `app/main.py` | REST API that receives sale events and publishes them to Kafka |
| **DB Consumer** | `app/consumer/db_consumer.py` | Reads events from Kafka and inserts them into PostgreSQL |

---

## Data Flow Diagram

```
CSV files ──────────────────────────────► PostgreSQL (staging schema)
(data/raw/*.csv)                          (reference tables: products,
                                           stores, brands, categories…)

 │
                                                     ▼
                                        refined.refresh_refined() batch load
                                                     │
                                                     ▼
                                    PostgreSQL (refined schema for analytics)                                           

HTTP Client          FastAPI              Kafka               PostgreSQL
(Thunder Client) ──► app/main.py ──────► inventory_events ──► db_consumer.py ──► staging.orders
POST /api/sales       (producer)          (topic)             (consumer)          staging.items
```

**Step-by-step:**

1. **CSV → Database**: Reference data (products, stores, brands, colours, sizes, genders, categories) is loaded from `data/raw/*.csv` into the `staging` schema.
2. **API → Kafka**: A client sends a `POST /api/sales` (or `POST /api/sales/batch`) request to the FastAPI app. The app serialises the event as JSON and publishes it to the `inventory_events` Kafka topic.
3. **Kafka → Consumer → Database**: `db_consumer.py` reads messages from `inventory_events`. For each `sale` event, it inserts a new row into `staging.orders` and one row per item into `staging.items`, then commits the transaction.

---

## Event Schema
[Events Schema](documentation/kafka/schema.md)


A sale event published to Kafka follows this structure:

```json
{
  "event_id": 1,
  "event_type": "sale",
  "timestamp": "2026-03-12T10:30:00Z",
  "store_id": 1,
  "items": [
    {
      "product_id": 101,
      "price": 89.99,
      "quantity": 2
    }
  ]
}
```

- `event_type`: Currently `"sale"`. Future support planned for `"restock"`.
- `items`: One or more products included in the sale.
- `price`: Price per unit (must be > 0).
- `quantity`: Units sold (must be > 0).

---

### 📊 Data Model
 ![SportWear Data Model](documentation/data_model/SportWear_Inc_Logical_final.png)
 [Data Model Relationship Description](documentation/kafka/relationship_desc.md)
