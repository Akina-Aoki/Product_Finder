# SportWear Logical Data Model

This document describes the entities, cardinality relationships, and relationship descriptions for the **SportWear** project data model.

The model supports product catalog management, store inventory tracking, and sales/order analysis.

---

## Data Model Entities

| Entity | Description |
|--------|-------------|
| **Brands** | Stores the list of product brands, such as the brand identity associated with each product. |
| **Categories** | Stores product categories, such as jackets, socks, shoes, or other sportswear groupings. |
| **Colours** | Stores available product colours. |
| **Sizes** | Stores available product sizes. |
| **Genders** | Stores gender groupings used for product classification. |
| **Products** | Central product catalog table containing product details such as code, name, price, active flag, and links to brand, category, colour, size, and gender. |
| **Stores** | Stores physical store information, including store code, store name, and city. |
| **Inventories** | Stores the stock level of each product in each store, including quantity and update timestamps. |
| **Orders** | Stores customer order headers, including which store placed/recorded the order, the order total price, and order date. |
| **Items** | Stores the line items of each order, linking products to orders with item price and quantity. |

---

## Cardinality Relationships

| # | Entity A | Entity B | Cardinality |
|---|----------|----------|-------------|
| 1 | Brands | Products | 1 : N |
| 2 | Categories | Products | 1 : N |
| 3 | Colours | Products | 1 : N |
| 4 | Sizes | Products | 1 : N |
| 5 | Genders | Products | 1 : N |
| 6 | Products | Inventories | 1 : N |
| 7 | Stores | Inventories | 1 : N |
| 8 | Stores | Orders | 1 : N |
| 9 | Orders | Items | 1 : N |
| 10 | Products | Items | 1 : N |

---

## Relationship Descriptions

| # | Entity A | Entity B | Cardinality | Description |
|---|----------|----------|-------------|-------------|
| 1 | Brands | Products | 1 : N | One brand may be associated with many products. Each product belongs to exactly one brand. |
| 2 | Categories | Products | 1 : N | One category may contain many products. Each product belongs to exactly one category. |
| 3 | Colours | Products | 1 : N | One colour may be used by many products. Each product is assigned exactly one colour in the current model. |
| 4 | Sizes | Products | 1 : N | One size may apply to many products. Each product is assigned exactly one size in the current model. |
| 5 | Genders | Products | 1 : N | One gender grouping may classify many products. Each product belongs to exactly one gender grouping. |
| 6 | Products | Inventories | 1 : N | One product may appear in many inventory records across different stores. Each inventory record refers to exactly one product. |
| 7 | Stores | Inventories | 1 : N | One store may have many inventory records. Each inventory record belongs to exactly one store. |
| 8 | Stores | Orders | 1 : N | One store may record many orders. Each order is associated with exactly one store. |
| 9 | Orders | Items | 1 : N | One order may contain many items. Each item belongs to exactly one order. |
| 10 | Products | Items | 1 : N | One product may appear in many order items across many orders. Each item refers to exactly one product. |

---

## Model Summary

The **Products** entity is the central master data table in the model. It connects to descriptive lookup entities:

- Brands
- Categories
- Colours
- Sizes
- Genders

This allows each product to be classified consistently across multiple business dimensions.

The **Inventories** entity captures stock levels for products in stores. It creates a bridge between:

- **Products**
- **Stores**

This makes it possible to answer business questions such as:

- What is the current stock of a product?
- Which store has the most inventory?
- Which products are low in stock?

The sales side of the model is built around:

- **Orders**
- **Items**

An **Order** acts as the transaction header, while **Items** store the product-level details for each order. This supports business questions such as:

- Which products sell the most?
- How much revenue does each product generate?
- How much revenue does each store generate?

---

## Business Purpose of the Model

This logical model supports three major business areas:

1. **Product catalog management**  
   Products can be organized by brand, category, colour, size, and gender.

2. **Inventory tracking**  
   Stores can track how much stock of each product is currently available.

3. **Sales and analytics**  
   Orders and items make it possible to analyze product sales, store performance, and revenue.

---

## Notes

- All entities use a primary key for unique identification.
- Foreign keys define the main business relationships in the model.
- The model is normalized so that product attributes such as brand, category, colour, size, and gender are stored separately from the product table.
- The model is designed to support both operational reporting and future analytics use cases.