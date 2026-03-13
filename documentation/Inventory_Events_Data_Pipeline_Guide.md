# Inventory Events Data Pipeline Guide

## Project Overview

This system captures real-time inventory events — such as **sales** and **restocks** — and stores them durably in a PostgreSQL database. Events are produced by a FastAPI application, transmitted through an Apache Kafka topic (`inventory_events`), and consumed by a dedicated database consumer that persists each event. A base dataset of products, stores, categories, and other reference data is pre-loaded from CSV files into the database at startup.

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

### Components

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Docker Compose** | `docker-compose.yml` | Launches PostgreSQL and Kafka as local services |
| **PostgreSQL** | `postgres:16-alpine` | Stores all reference data and inventory events |
| **Apache Kafka** | `apache/kafka:latest` | Message broker for the `inventory_events` topic |
| **init.sql** | SQL DDL script | Creates the `staging` schema and all tables on first startup |
| **CSV files** | `data/raw/*.csv` | Seed data loaded into the database (products, stores, brands, etc.) |
| **FastAPI app** | `app/main.py` | REST API that receives sale events and publishes them to Kafka |
| **DB Consumer** | `app/consumer/db_consumer.py` | Reads events from Kafka and inserts them into PostgreSQL |

---

## Data Flow Diagram

```
CSV files ──────────────────────────────► PostgreSQL (staging schema)
(data/raw/*.csv)                          (reference tables: products,
                                           stores, brands, categories…)

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

## Setup and Run Instructions

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (or Docker Engine + Compose)
- Python 3.12+ with [uv](https://github.com/astral-sh/uv) (or pip)

### 1. Start Infrastructure with Docker Compose

```bash
docker compose up -d
```

This starts:
- **PostgreSQL** on port `5439` (mapped from container port `5432`)
- **Kafka** on port `9092`

On the first run, `init.sql` is executed automatically to create the `staging` schema and all tables.

### 2. Load Seed Data (CSV → Database)

Load the reference CSV files into PostgreSQL. Use your preferred tool (e.g., `psql`, DBeaver, or a custom script) to import from `data/raw/`:

```
data/raw/brands.csv
data/raw/categories.csv
data/raw/colours.csv
data/raw/genders.csv
data/raw/sizes.csv
data/raw/stores.csv
data/raw/products.csv
data/raw/inventories.csv
```

### 3. Install Python Dependencies

```bash
uv sync
# or: pip install -r requirements.txt
```

### 4. Start the FastAPI Application

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

### 5. Start the Kafka Consumer

Open a second terminal and run:

```bash
python -m app.consumer.db_consumer
```

The consumer will print:
```
Consumer is listening to topic: inventory_events...
```

### 6. Send Events via Thunder Client (or curl)

**Single sale** — `POST http://localhost:8000/api/sales`

```json
{
  "event_id": 1,
  "event_type": "sale",
  "timestamp": "2026-03-12T10:30:00Z",
  "store_id": 1,
  "items": [
    { "product_id": 1, "price": 89.99, "quantity": 2 }
  ]
}
```

**Batch of sales** — `POST http://localhost:8000/api/sales/batch`

```json
[
  {
    "event_id": 2,
    "event_type": "sale",
    "timestamp": "2026-03-12T11:00:00Z",
    "store_id": 2,
    "items": [
      { "product_id": 3, "price": 149.00, "quantity": 1 }
    ]
  }
]
```

### 7. Verify Data in the Database

Connect to PostgreSQL and query the results:

```bash
psql -h localhost -p 5439 -U postgres -d SportWearDB
```

```sql
-- Check recent orders
SELECT * FROM staging.orders ORDER BY order_id DESC LIMIT 10;

-- Check order items
SELECT * FROM staging.items ORDER BY item_id DESC LIMIT 20;
```

---

## Troubleshooting

| Problem | Likely Cause | Solution |
|---------|-------------|----------|
| `Connection refused` on port `9092` | Kafka container not running | Run `docker compose up -d` and wait ~10 seconds for Kafka to fully start |
| `Connection refused` on port `5439` | PostgreSQL container not running | Run `docker compose up -d` and check `docker compose logs postgres` |
| Consumer prints `Error connecting to the database` | Wrong DB URL or PostgreSQL not ready | Confirm `DB_URL` in `db_consumer.py` matches `docker-compose.yml` credentials |
| FastAPI returns `500` when sending events | Kafka not reachable from the API | Ensure `KAFKA_BOOTSTRAP_SERVERS` is set correctly (default: `localhost:29092`) |
| Tables do not exist after startup | `init.sql` was not executed | Remove the named volume and restart: `docker compose down -v && docker compose up -d` |
| Events not appearing in the database | Consumer not running | Ensure `db_consumer.py` is running in a separate terminal |

---

## Key Files

| File | Description |
|------|-------------|
| `docker-compose.yml` | Defines and configures the PostgreSQL and Kafka services |
| `sql/init.sql` | SQL DDL that creates the `staging` schema and all database tables |
| `app/main.py` | FastAPI application — exposes `/api/sales` endpoints and publishes events to Kafka |
| `app/consumer/db_consumer.py` | Kafka consumer — reads `inventory_events` messages and writes them to PostgreSQL |
| `app/schema/product.py` | Pydantic models for `SaleEvent` and `SaleItem` used by the API |
| `data/raw/*.csv` | Seed CSV files for reference tables (products, stores, brands, etc.) |
| `scripts/replay_sales_events.py` | Helper script to replay historical sale events |
