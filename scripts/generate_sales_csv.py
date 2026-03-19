import pandas as pd
import random
from datetime import datetime, timedelta, timezone
import uuid
import csv

# ==========================================
# 1. LOAD DATA & BUILD VIRTUAL INITIAL INVENTORY
# ==========================================
print("Loading stores and clean product data...")
try:
    products_df = pd.read_csv('data/processed/products_clean.csv', sep=';')
    stores_df = pd.read_csv('data/raw/stores.csv', sep=';')
except FileNotFoundError as e:
    print(f"Files not found! Make sure you have run the Airas washing script first. Error: {e}")
    exit()

product_prices = dict(zip(products_df['product_id'], products_df['price']))
stores = stores_df['store_id'].tolist()

print("Building virtual initial inventory (CROSS JOIN in Python)...")
inventory_stock = {}

START_AMOUNT = 50

for store_id in stores:
    for product_id in products_df['product_id']:
        inventory_stock[(store_id, product_id)] = START_AMOUNT


# ==========================================
# 2. GENERATE HISTORICAL RECEIPTS
# ==========================================
orders_data = []
items_data = []

order_id_counter = 1
item_id_counter = 1

days_to_simulate = 2 * 365
start_date = datetime.now(timezone.utc) - timedelta(days=days_to_simulate)

print(f"Simulating sales day by day for the last {days_to_simulate} days...")

for day_offset in range(days_to_simulate):
    current_date = start_date + timedelta(days=day_offset)
    
    num_sales_today = random.randint(1, 3)

    for _ in range(num_sales_today):
        store_id = random.choice(stores)

        available_products = [pid for (sid, pid), amount in inventory_stock.items() 
                              if sid == store_id and amount > 0 and pid in product_prices]

        if not available_products:
            continue

        num_items_in_sale = random.randint(1, min(3, len(available_products)))
        chosen_products = random.sample(available_products, k=num_items_in_sale)

        order_price = 0
        sale_items = []

        for prod_id in chosen_products:
            stock_available = inventory_stock[(store_id, prod_id)]
            
            quantity = random.randint(1, min(2, stock_available))

            # REMOVE FROM INVENTORY
            inventory_stock[(store_id, prod_id)] -= quantity

            item_price = product_prices[prod_id]
            order_price += item_price * quantity

            sale_items.append({
                'product_id': prod_id,
                'item_price': item_price,
                'quantity': quantity
            })

        order_time = current_date.replace(
            hour=random.randint(9, 17), 
            minute=random.randint(0, 59), 
            second=random.randint(0, 59)
        )
        order_date_str = order_time.strftime("%Y-%m-%d %H:%M:%S+00")
        source_event_id = str(uuid.uuid4())

        orders_data.append([
            order_id_counter, source_event_id, store_id, round(order_price, 2), order_date_str
        ])

        for item in sale_items:
            items_data.append([
                item_id_counter, item['product_id'], round(item['item_price'], 2), 
                order_id_counter, item['quantity'], order_date_str
            ])
            item_id_counter += 1

        order_id_counter += 1

# ==========================================
# 3. SAVE TO CSV FILES
# ==========================================
orders_path = 'data/raw/orders.csv'
with open(orders_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerow(['order_id', 'source_event_id', 'store_id', 'order_price', 'order_date'])
    writer.writerows(orders_data)
print(f"Created {orders_path} with {len(orders_data)} historical receipts.")

items_path = 'data/raw/items.csv'
with open(items_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerow(['item_id', 'product_id', 'item_price', 'order_id', 'quantity', 'created_at'])
    writer.writerows(items_data)
print(f"Created {items_path} with {len(items_data)} historical purchased items.")

# --- SKAPA DEN NYA INVENTORIES.CSV ---
inventories_data = []
inv_id_counter = 1
current_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S+00")

for (store_id, product_id), amount in inventory_stock.items():
    inventories_data.append([
        inv_id_counter, product_id, amount, store_id, current_time, current_time
    ])
    inv_id_counter += 1

inventories_path = 'data/raw/inventories.csv'
with open(inventories_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerow(['inventory_id', 'product_id', 'amount', 'store_id', 'update_date', 'created_at'])
    writer.writerows(inventories_data)
    
print(f"Created {inventories_path} with correct ending balance after 2 years of sales!")