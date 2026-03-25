# Sprint 4 — Evidence Dashboard, Supabase Integration, and MVP Query Layer

## Sprint goal
Sprint 4 focused on completing the **serving/analytics layer** so the platform can be used by business stakeholders, not only developers.

We prioritized three outcomes:
1. Build a usable **Evidence dashboard** for inventory and sales.
2. Connect the platform to **Supabase PostgreSQL** for hosted access.
3. Create/iterate **advanced SQL queries** that directly answer MVP business questions.

---

## What was delivered

### 1) Evidence dashboard (customer-facing analytics layer)
We built the dashboard structure and pages in `evidence_app/` and connected them to SQL-backed data sources.

Delivered pages:
- `index.md` as dashboard entry point
- `sales.md` for sales KPIs, trend analysis, and product performance
- `inventory.md` for stock status monitoring and inventory health
- store-level pages for city/store views

The dashboard now supports practical business analysis through filters (store, product, category, color, stock status, etc.) and KPI cards/tables/charts.

---

### 2) Supabase integration (cloud database connectivity)
We introduced a Supabase setup so analytics and dashboard queries can run against hosted PostgreSQL infrastructure:

- Added Supabase SQL bootstrap scripts:
  - `supabase/sql/01_create_tables.sql`
  - `supabase/sql/02_reset_sequences.sql`
  - `supabase/sql/03_supabase_cron_setup.sql`
  - `supabase/sql/refresh.sql`
- Updated Evidence data source connection in:
  - `evidence_app/sources/sportwear/connection.yaml`

This gives the team a consistent hosted backend for demo, collaboration, and dashboard consumption.

---

### 3) Advanced query layer for MVP questions
We iterated heavily on business queries used in dashboard pages and archived SQL working files.

Key query outcomes:
- **Inventory movement / stock health** query family (including low-stock and out-of-stock logic fixes).
- **Sales performance** query family (revenue, units sold, orders, product-level performance, and trend analysis).
- Better alignment between dashboard visualizations and underlying query logic after debugging and refactoring.

This directly supports MVP user stories such as:
- track product movement,
- detect restocking patterns and stock risks,
- monitor sales activity,
- identify top/low performers,
- analyze revenue performance over time.

---

## Sprint 4 impact
- We moved from pipeline-only capability to a **decision-support product prototype**.
- Business users can now answer core MVP questions from a visual dashboard instead of raw SQL only.
- Supabase connectivity improves operational accessibility and team collaboration.

---
