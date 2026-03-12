# 🐳 PostgreSQL Setup Guide (Docker)

This guide documents the workflow for starting the PostgreSQL database using Docker, connecting to it via `psql`, and verifying that the project schemas and tables are correctly initialized.

The goal of this runbook is to ensure the database environment is **reproducible**, **easy to restart**, and **consistent across development environments**.

---

# 1️⃣ Start the Docker Environment

Before starting development, ensure that the database container is initialized cleanly.

Stop and remove existing containers and volumes:

```
docker compose down -v
```

Start the services again:

```
docker compose up -d
```

Verify that the containers are running:

```
docker ps
```

Expected running containers:

- `SportWear_Postgres`
- `SportWear_Kafka`
- `SportWear_Kafka_UI`

---

# 2️⃣ Connect to PostgreSQL

Connect to the PostgreSQL container using `psql`.

```
docker exec -it SportWear_Postgres psql -U postgres -d SportWearDB
```

You should now see the PostgreSQL interactive shell:

```
psql (16.x)
Type "help" for help.
```

---

# 3️⃣ Verify PostgreSQL Installation

Run the following command to confirm PostgreSQL is running correctly.

```
SELECT version();
```

Example output:

```
PostgreSQL 16.x on x86_64-pc-linux-musl
```

---

# 4️⃣ Verify Database Schemas

Check that the database schemas were created successfully.

```
SELECT schema_name
FROM information_schema.schemata;
```

Expected result:

```
public
staging
information_schema
pg_catalog
pg_toast
```

### Schema Usage

| Schema | Purpose |
|------|------|
| `staging` | Raw ingested data and reference tables |
| `refined` | Future cleaned and transformed data layer |
| `public` | Default PostgreSQL schema |

For this project, development initially focuses on the **`staging` schema**.

---

# 5️⃣ List Tables in the `staging` Schema

To confirm the tables were created successfully, run:

```
\dt staging.*
```

Expected tables:

```
brands
categories
colours
sizes
genders
products
stores
inventory
```

These tables represent **reference and operational data** used by the data platform.

---

# 6️⃣ Validate Table Structure

Run a simple query to inspect one of the tables.

Example using the `products` table:

```
SELECT * FROM staging.products LIMIT 5;
```

Expected result:

- Table columns are visible
- Rows may be empty if CSV data has not yet been loaded

Example output:

```
 product_id | product_code | product_name | brand_id | category_id | colour_id | size_id | gender_id | price | active
------------+--------------+--------------+----------+-------------+-----------+---------+-----------+-------+--------
(0 rows)
```

This confirms the **schema and table structure are working correctly**.

---

# 🔄 Restarting the Environment

Whenever changes are made to `init.sql`, the PostgreSQL volume must be reset so the initialization scripts run again.

Run:

```
docker compose down -v
docker compose up -d
```

This ensures:

- Database is recreated
- Initialization SQL scripts execute again
- Schema changes are applied

---

# ✅ Environment Validation Checklist

Before continuing development, confirm:

- [ ] Docker containers are running
- [ ] PostgreSQL container is healthy
- [ ] Database connection works
- [ ] `staging` schema exists
- [ ] Tables are visible
- [ ] Queries execute successfully

Once these checks pass, the environment is ready for:

- Loading CSV reference data
- Kafka event ingestion
- Building the analytics layer