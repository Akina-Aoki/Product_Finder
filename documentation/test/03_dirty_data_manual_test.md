Run this messy data in terminal to test the etl cleaner `scripts_run_products_etl.py`

```
cat > data/raw/products_dirty.csv <<'CSV'
product_id;product_code;product_name;brand_id;category_id;colour_id;size_id;price;gender_id;active
1;10010001;  storm   tee  ;1;2;1;1;49.90;3;YES
2;10010001;storm tee v2;1;2;1;1;59.90;3;true
3;BADCODE;bad sku row;1;2;1;1;79.90;3;true
4;10010002;bad negative price;1;2;1;1;-5.00;3;true
CSV
```

Then test the Transformation script in terminal:
`uv run python scripts_run_products_etl.py`