-- ==========================================
-- RESET SEQUENCES
-- ==========================================
select setval(pg_get_serial_sequence('staging.brands', 'brand_id'), coalesce(max("brand_id"), 1), max("brand_id") is not null) from "staging"."brands";
select setval(pg_get_serial_sequence('staging.categories', 'category_id'), coalesce(max("category_id"), 1), max("category_id") is not null) from "staging"."categories";
select setval(pg_get_serial_sequence('staging.colours', 'colour_id'), coalesce(max("colour_id"), 1), max("colour_id") is not null) from "staging"."colours";
select setval(pg_get_serial_sequence('staging.genders', 'gender_id'), coalesce(max("gender_id"), 1), max("gender_id") is not null) from "staging"."genders";
select setval(pg_get_serial_sequence('staging.sizes', 'size_id'), coalesce(max("size_id"), 1), max("size_id") is not null) from "staging"."sizes";
select setval(pg_get_serial_sequence('staging.stores', 'store_id'), coalesce(max("store_id"), 1), max("store_id") is not null) from "staging"."stores";
select setval(pg_get_serial_sequence('staging.products', 'product_id'), coalesce(max("product_id"), 1), max("product_id") is not null) from "staging"."products";
select setval(pg_get_serial_sequence('staging.inventories', 'inventory_id'), coalesce(max("inventory_id"), 1), max("inventory_id") is not null) from "staging"."inventories";
select setval(pg_get_serial_sequence('staging.orders', 'order_id'), coalesce(max("order_id"), 1), max("order_id") is not null) from "staging"."orders";
select setval(pg_get_serial_sequence('staging.items', 'item_id'), coalesce(max("item_id"), 1), max("item_id") is not null) from "staging"."items";