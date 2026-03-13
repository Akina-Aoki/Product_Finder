# Product_Finder

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

---

# 🧱 Tech Stack & Dependencies

| Package        | Purpose                                     |
| -------------- | ------------------------------------------- |
| kafka-python   | Kafka producer/consumer client              |
| psycopg        | PostgreSQL driver                           |
| psycopg-binary | Binary build of psycopg for easier installs |
| pydantic       | Schema validation for event data            |
| orjson         | Fast JSON parsing (Kafka events)            |
| tenacity       | retrying for kafka connection & DB inserts  |
| structlog      | Structured logging: pipeline observability  |


---

# 📦 Prerequisites

Install uv if needed:

```bash
pip install uv
```

----
## First Time Set-up
1️⃣ Clone the Repository
```
git clone https://github.com/YOUR_USERNAME/Product_Finder.git
```

2️⃣ Install & Pin Python 3.12
In your VSCode/IDE
```
uv python install 3.12
uv python pin 3.12
```

Verify:
```
cat .python-version
```

Expected output:
```
3.12
```

3️⃣ Create Virtual Environment
```
uv venv
```

Activate it: Windows (Git Bash)
```
source .venv/Scripts/activate
```

Mac/Linux
```
source .venv/bin/activate
```

You should now see:
```
(Product_Finder)
```

4️⃣ Install Project Dependencies
- This installs all dependencies from uv.lock.
```
uv sync
```

- ⚠️ Do NOT use pip install.
- Always use for new dependencies.:
```
uv add <package>
```

5️⃣ Verify Environment Isolation

Check Python version:
```
python -V
```

Expected:
```
Python 3.12.x
```

Check interpreter path:
```
python -c "import sys; print(sys.executable)"
```

It must point to:
```
Product_Finder/.venv/...
```