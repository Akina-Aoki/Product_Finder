---
title: Sales
---

This page is made to see how sales goes.

```sql filter_stores
  SELECT
      store_id,
      store_name
  FROM sportwear.meta_stores
```
<div style="display: flex; gap: 20px;">
  <Dropdown
    data={filter_stores}
    name="stores"
    value=store_name
    label=store_name
    selectAll="true"
  />
</div>

```sql product_revenue_by_product
    SELECT
        item_id AS product,
        sum(item_price) AS Sale
    FROM sportwear.data_sales
    WHERE 
        ('${inputs.stores.value}' = 'true' OR '${inputs.stores.value}' = '') 
        OR store_name = '${inputs.stores.value}'
    GROUP BY product
    ORDER BY Sale DESC
    LIMIT 5;
```

<BarChart 
    data={product_revenue_by_product}
    x=product
    y=Sale
    title="Revenue per product"
/>