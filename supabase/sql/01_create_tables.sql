-- ==========================================
-- 1. CREATE SCHEMAS
-- ==========================================
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS refined;

-- ==========================================
-- 2. CREATE STAGING TABLES
-- ==========================================
CREATE TABLE IF NOT EXISTS staging.categories ( "category_id" serial PRIMARY KEY, "category_name" varchar(30) NOT NULL );
CREATE TABLE IF NOT EXISTS staging.colours ( "colour_id" serial PRIMARY KEY, "colour_name" varchar(20) NOT NULL );
CREATE TABLE IF NOT EXISTS staging.sizes ( "size_id" serial PRIMARY KEY, "size_name" varchar(20) NOT NULL );
CREATE TABLE IF NOT EXISTS staging.genders ( "gender_id" serial PRIMARY KEY, "gender_name" varchar(20) NOT NULL );
CREATE TABLE IF NOT EXISTS staging.brands ( "brand_id" serial PRIMARY KEY, "brand_name" varchar(50) NOT NULL );
CREATE TABLE IF NOT EXISTS staging.products ( "product_id" serial PRIMARY KEY, "product_code" integer NOT NULL UNIQUE, "product_name" varchar(50) NOT NULL, "brand_id" integer NOT NULL, "category_id" integer NOT NULL, "colour_id" integer NOT NULL, "size_id" integer NOT NULL, "gender_id" integer NOT NULL, "price" numeric(10,2) NOT NULL CHECK ("price" >= 0), "active" boolean NOT NULL DEFAULT true );
CREATE TABLE IF NOT EXISTS staging.stores ( "store_id" serial PRIMARY KEY, "store_code" varchar(10) NOT NULL UNIQUE, "store_name" varchar(50) NOT NULL, "city" varchar(50) NOT NULL );
CREATE TABLE IF NOT EXISTS staging.inventories ( "inventory_id" serial PRIMARY KEY, "product_id" integer NOT NULL, "amount" integer NOT NULL DEFAULT 0 check ("amount" >= 0), "store_id" integer NOT NULL, "update_date" timestamptz NOT NULL DEFAULT now(), "created_at" timestamptz NOT NULL DEFAULT now(), constraint "uq_inventory_store_product" unique ("store_id", "product_id") );
CREATE TABLE IF NOT EXISTS staging.orders ( "order_id" serial PRIMARY KEY, "source_event_id" varchar (100) UNIQUE, "store_id" integer NOT NULL, "order_price" numeric(10,2) NOT NULL CHECK ("order_price" >= 0), "order_date" timestamptz NOT NULL DEFAULT now() );
CREATE TABLE IF NOT EXISTS staging.items ( "item_id" serial PRIMARY KEY, "product_id" integer NOT NULL, "item_price" numeric (10,2) NOT NULL CHECK ("item_price" >= 0), "order_id" integer NOT NULL, "quantity" integer NOT NULL DEFAULT 1 CHECK ("quantity" >= 0), "created_at" timestamptz NOT NULL DEFAULT now() );

-- ==========================================
-- 3. ADD RELATIONSHIPS (Foreign Keys)
-- ==========================================
ALTER TABLE staging.products ADD FOREIGN KEY ("brand_id") REFERENCES staging.brands ("brand_id") DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE staging.products ADD FOREIGN KEY ("category_id") REFERENCES staging.categories ("category_id") DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE staging.products ADD FOREIGN KEY ("colour_id") REFERENCES staging.colours ("colour_id") DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE staging.products ADD FOREIGN KEY ("size_id") REFERENCES staging.sizes ("size_id") DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE staging.products ADD FOREIGN KEY ("gender_id") REFERENCES staging.genders ("gender_id") DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE staging.orders ADD FOREIGN KEY ("store_id") REFERENCES staging.stores ("store_id") DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE staging.items ADD FOREIGN KEY ("product_id") REFERENCES staging.products ("product_id") DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE staging.items ADD FOREIGN KEY ("order_id") REFERENCES staging.orders ("order_id") ON DELETE CASCADE DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE staging.inventories ADD FOREIGN KEY ("product_id") REFERENCES staging.products ("product_id") DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE staging.inventories ADD FOREIGN KEY ("store_id") REFERENCES staging.stores ("store_id") DEFERRABLE INITIALLY IMMEDIATE;

-- ==========================================
-- 4. CREATE REFINED MATERIALIZED VIEWS
-- ==========================================
DROP MATERIALIZED VIEW IF EXISTS refined.items CASCADE;
DROP MATERIALIZED VIEW IF EXISTS refined.inventories CASCADE;
DROP MATERIALIZED VIEW IF EXISTS refined.stores CASCADE;
DROP MATERIALIZED VIEW IF EXISTS refined.products CASCADE;
DROP MATERIALIZED VIEW IF EXISTS refined.orders CASCADE;

CREATE MATERIALIZED VIEW refined.products AS
SELECT 
    p.product_id, 
    p.product_name, 
    b.brand_name, 
    c.category_name, 
    co.colour_name, 
    si.size_name, 
    g.gender_name, 
    p.price
FROM staging.products p
JOIN staging.brands b ON b.brand_id = p.brand_id
JOIN staging.categories c ON c.category_id = p.category_id
JOIN staging.colours co ON co.colour_id = p.colour_id
JOIN staging.sizes si ON si.size_id = p.size_id
JOIN staging.genders g ON g.gender_id = p.gender_id;

-- Unika index KRÄVS för att kunna använda REFRESH MATERIALIZED VIEW CONCURRENTLY
CREATE UNIQUE INDEX idx_refined_products_id ON refined.products(product_id);

CREATE MATERIALIZED VIEW refined.stores AS
SELECT 
    s.store_id, 
    s.store_code, 
    s.store_name, 
    s.city
FROM staging.stores s;

CREATE UNIQUE INDEX idx_refined_stores_id ON refined.stores(store_id);

CREATE MATERIALIZED VIEW refined.inventories AS
SELECT 
    i.inventory_id, 
    p.product_id, 
    p.product_name, 
    i.amount, 
    s.store_name, 
    s.city, 
    i.update_date
FROM staging.inventories i
JOIN staging.products p ON p.product_id = i.product_id
JOIN staging.stores s ON s.store_id = i.store_id;

CREATE UNIQUE INDEX idx_refined_inventories_id ON refined.inventories(inventory_id);

CREATE MATERIALIZED VIEW refined.items AS
SELECT 
    it.item_id, 
    o.order_id, 
    o.order_date, 
    p.product_id, 
    p.product_name, 
    it.item_price, 
    it.quantity, 
    s.store_name, 
    s.city
FROM staging.items it
JOIN staging.orders o ON o.order_id = it.order_id
JOIN staging.products p ON p.product_id = it.product_id
JOIN staging.stores s ON s.store_id = o.store_id;

CREATE UNIQUE INDEX idx_refined_items_id ON refined.items(item_id);


CREATE MATERIALIZED VIEW refined.orders AS
SELECT 
    o.order_id,
    o.order_date,
    s.store_name,
    s.city,
    o.order_price
FROM staging.orders o
JOIN staging.stores s ON s.store_id = o.store_id;

CREATE UNIQUE INDEX idx_refined_orders_id ON refined.orders(order_id);


-- ==========================================
-- 5. UPDATE FUNCTION
-- ==========================================
CREATE OR REPLACE FUNCTION refined.refresh_refined() RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
  REFRESH MATERIALIZED VIEW CONCURRENTLY refined.products;
  REFRESH MATERIALIZED VIEW CONCURRENTLY refined.stores;
  REFRESH MATERIALIZED VIEW CONCURRENTLY refined.inventories;
  REFRESH MATERIALIZED VIEW CONCURRENTLY refined.items;
  REFRESH MATERIALIZED VIEW CONCURRENTLY refined.orders;
END;
$$;