CREATE SCHEMA IF NOT EXISTS staging;

CREATE TABLE IF NOT EXISTS staging.categories (
  "category_id" serial PRIMARY KEY,
  "category_name" varchar(30) NOT NULL
);

CREATE TABLE IF NOT EXISTS staging.colours (
  "colour_id" serial PRIMARY KEY,
  "colour_name" varchar(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS staging.sizes (
  "size_id" serial PRIMARY KEY,
  "size_name" varchar(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS staging.genders (
  "gender_id" serial PRIMARY KEY,
  "gender_name" varchar(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS staging.brands (
  "brand_id" serial PRIMARY KEY,
  "brand_name" varchar(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS staging.products (
  "product_id" serial PRIMARY KEY,
  "product_code" varchar(20) NOT NULL,
  "product_name" varchar(50) NOT NULL,
  "brand_id" integer NOT NULL,
  "category_id" integer NOT NULL,
  "colour_id" integer NOT NULL,
  "size_id" integer NOT NULL,
  "gender_id" integer NOT NULL,
  "price" decimal NOT NULL,
  "active" boolean DEFAULT true
);

CREATE TABLE IF NOT EXISTS staging.stores (
  "store_id" serial PRIMARY KEY,
  "store_code" varchar(10) NOT NULL,
  "store_name" varchar(50) NOT NULL,
  "city" varchar(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS staging.orders (
  "order_id" serial PRIMARY KEY,
  "store_id" integer NOT NULL,
  "order_price" decimal NOT NULL,
  "order_date" timestamptz NOT NULL
);

CREATE TABLE IF NOT EXISTS staging.items (
  "item_id" serial PRIMARY KEY,
  "product_id" integer NOT NULL,
  "item_price" decimal NOT NULL,
  "order_id" integer NOT NULL,
  "quantity" integer DEFAULT 1
);

CREATE TABLE IF NOT EXISTS staging.inventories (
  "inventory_id" serial PRIMARY KEY,
  "product_id" integer NOT NULL,
  "amount" integer DEFAULT 0,
  "store_id" integer NOT NULL,
  "update_date" timestamptz NOT NULL
);

ALTER TABLE staging.products ADD FOREIGN KEY ("brand_id") REFERENCES staging.brands ("brand_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE staging.products ADD FOREIGN KEY ("category_id") REFERENCES staging.categories ("category_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE staging.products ADD FOREIGN KEY ("colour_id") REFERENCES staging.colours ("colour_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE staging.products ADD FOREIGN KEY ("size_id") REFERENCES staging.sizes ("size_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE staging.products ADD FOREIGN KEY ("gender_id") REFERENCES staging.genders ("gender_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE staging.orders ADD FOREIGN KEY ("store_id") REFERENCES staging.stores ("store_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE staging.items ADD FOREIGN KEY ("product_id") REFERENCES staging.products ("product_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE staging.items ADD FOREIGN KEY ("order_id") REFERENCES staging.orders ("order_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE staging.inventories ADD FOREIGN KEY ("product_id") REFERENCES staging.products ("product_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE staging.inventories ADD FOREIGN KEY ("store_id") REFERENCES staging.stores ("store_id") DEFERRABLE INITIALLY IMMEDIATE;
