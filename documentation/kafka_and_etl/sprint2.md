# Sprint #2 Backlog Plan

## Sprint Goal

By the end of **Sprint #2**, the team will have a working backend pipeline that:

- Generates **synthetic container product inventory data**
- Processes the dataset from a **JSONL file**
- Loads the data into **PostgreSQL running in Docker**
- Executes **SQL queries that answer business questions**

This demonstrates the **core MVP capability**:  
helping users identify which stores have container products available and at what price.

---

1. Infrastructure setup  
2. Data schema definition  
3. Synthetic dataset creation  
4. Data ingestion pipeline  
5. SQL queries that produce business insights  


---

# Priority

## P0 (Must Finish This Sprint)

- Docker Compose environment with PostgreSQL
- JSONL dataset representing container inventory
- Data schema for products, stores, and inventory
- Python processing script to load data into PostgreSQL
- SQL queries showing inventory availability

---

## P1 (Nice to Have)

- Data validation checks
- Database indexes for performance
- README runbook explaining setup and demo steps

---

# Backlog Breakdown

---

# Part 1 — Infrastructure Setup (Docker + PostgreSQL)

## User Story

As a developer,  
I want PostgreSQL running inside Docker  
so that the team can run the database consistently across machines.

---

## Tasks

1. Create `docker-compose.yml`
2. Add PostgreSQL service
3. Configure environment variables

```
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_DB
```

4. Expose PostgreSQL port

```
5432:5432
```

5. Create persistent volume for database data
6. Add `.env` configuration file
7. Verify database connection using Python or `psql`

---

## Acceptance Criteria

- `docker compose up -d` starts PostgreSQL successfully
- Team members can connect to the database locally
- Database persists after container restart

---

## Definition of Done

- `docker-compose.yml` committed
- `.env.example` documented
- Setup instructions added to README

---

# Part 2 — JSONL Dataset (Synthetic Inventory Data)

## User Story

As a data engineer,  
I want a JSONL dataset that simulates inventory across our 2 stores  
so that we can test our data platform pipeline.

---

## Example JSONL Schema

Each line represents **one product in one store**.

```json
{
  "product_id": "...",
  "product_name": "...",
  "category": "jacket",
  "color": "black",
  "price": 100,
  "store_id": "STO02",
  "store_name": "Liljeholmen Centrum",
  "city": "Stockholm",
  "stock_quantity": 34,
  "last_updated": "2026-03-07T10:30:00Z"
}
```

---

## Tasks

1. Define the JSON schema contract
2. Create a synthetic JSONL dataset
3. Generate **300–1000 rows of data**
4. Include variation in:
   - sizes
   - colors
   - store locations
5. Save dataset in repository

```
data/raw/container_inventory.jsonl
```

6. Validate JSON structure

---

## Acceptance Criteria

- JSONL file loads correctly
- Each row represents product availability in a store
- Data matches schema contract

---

## Definition of Done

- JSON schema documented
- JSONL dataset committed
- Sample rows validated

---

# Part 3 — Database Data Model

## User Story

As an analyst or operations manager,  
I want a structured database model so I can query product availability across stores.

---

# MVP Data Model

### Table: stores

```
store_id (PK)
store_name
city
```

---

### Table: products

```
product_id (PK)
product_brand
product_name
category
color
size
gender
price_sek
```

---

### Table: inventory

```
inventory_id (PK)
product_id (FK)
store_id (FK)
price
stock_quantity
created_at
```

---

## Tasks

1. Draw ERD diagram (logical/physical)
2. Write SQL DDL scripts
3. Define primary keys
4. Define foreign keys
5. Add constraints
6. Add indexes

Example index:

```sql
CREATE INDEX idx_inventory_product
ON inventory(product_id);
```

---

## Acceptance Criteria

- Tables match JSON schema
- Data can be inserted successfully
- Foreign key relationships work correctly

---

## Definition of Done

- ERD committed to repository
- SQL schema script committed
- Database tables successfully created

---

# Part 4 — Processing JSONL and Loading into PostgreSQL

## User Story

As a product owner,  
I want the inventory dataset loaded into the database  
so stakeholders can analyze store availability.

---

## Tasks

1. Create Python loader script

```
src/load_inventory.py
```

2. Read JSONL file
3. Validate data structure
4. Insert records into database
5. Handle duplicate entries
6. Log loading results

---

## Acceptance Criteria

- Script loads JSONL data into database tables
- No schema errors occur
- Data appears correctly in all tables

---

## Definition of Done

- Loader script committed
- Successful execution documented

---

# Part 5 — SQL Queries (Business Value)

## User Story

As a business user,  
I want to query the database  
so I can find container products available in stores.

---

# MVP Query Examples

### Which containers are available in stores?

```sql
SELECT product_name, store_name, stock_quantity
FROM inventory
JOIN products USING(product_id)
JOIN stores USING(store_id);
```

---

### Which store sells the cheapest container?

```sql
SELECT product_name, store_name, price
FROM inventory
ORDER BY price ASC;
```

---

### Which containers are out of stock?

```sql
SELECT product_name, store_name
FROM inventory
WHERE stock_quantity = 0;
```

---

### Which products have the highest stock?

```sql
SELECT product_name, SUM(stock_quantity)
FROM inventory
GROUP BY product_name
ORDER BY SUM(stock_quantity) DESC;
```

---

## Definition of Done

- At least **4 SQL queries implemented**
- Queries return meaningful results
- SQL file committed to repository

---

## Infrastructure and Schema

Tasks:

- Start PostgreSQL container
- Finalize JSON schema

Deliverable:

- Running database
- Approved schema contract

---

## Dataset Creation

Tasks:

- Generate synthetic JSONL dataset
- Validate dataset structure

Deliverable:

- Inventory dataset committed

---

## Database Modeling

Tasks:

- Implement SQL schema
- Create database tables

Deliverable:

- Database ready for ingestion

---

## Data Loading and Queries

Tasks:

- Load JSONL data into PostgreSQL
- Implement SQL queries
- Prepare demo output

Deliverable:

- End-to-end pipeline working for KAFKA


