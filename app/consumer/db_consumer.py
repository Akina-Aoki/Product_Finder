import os
import json
import psycopg
from confluent_kafka import Consumer
from pydantic import ValidationError

# Importing the schemas to clean and validate incoming "dirty" data
from app.schema.product import SaleEvent, InventoryEvent, NewProductEvent

# Configuration from environment variables
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
TOPIC = os.getenv("PRODUCTS_TOPIC", "inventory_events")
DB_URL = os.getenv("DB_URL", "postgresql://postgres:postgres@postgres:5432/SportWearDB")

def on_assign(consumer, partitions):
    """Callback triggered when Kafka assigns partitions to this consumer."""
    print(f"Kafka approved access to: {partitions}")

print(f"Starting DB Consumer against {KAFKA_BOOTSTRAP_SERVERS}...")

# Consumer configuration
conf = {
    'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
    'group.id': "sportwear_inventory_consumer",
    'auto.offset.reset': 'earliest',
    'error_cb': lambda err: print(f"Kafka network error: {err}") 
}

consumer = Consumer(conf)
consumer.subscribe([TOPIC], on_assign=on_assign)

print(f"The Consumer is listening to {TOPIC} and is ready to save to the database!")

def parse_and_validate_event(message):
    """
    Parses the raw Kafka message and validates it against Pydantic models.
    This acts as a 'data cleaning' step before the database is touched.
    Returns the validated data as a standard Python dictionary.
    """
    raw_data = message.value().decode('utf-8')
    data = json.loads(raw_data)

    # Handle double-serialized JSON strings if they occur
    if isinstance(data, str):
        data = json.loads(data)

    event_type = data.get("event_type")

    # Match event type to the correct validation schema and return as a dictionary
    if event_type == "sale":
        return SaleEvent(**data).model_dump()
    elif event_type in ["restock", "stock_update"]:
        return InventoryEvent(**data).model_dump()
    elif event_type == "new_product":
        return NewProductEvent(**data).model_dump()
    else:
        raise ValueError(f"Unknown event_type received: {event_type}")

def upsert_inventory_delta(cur, store_id, product_id, quantity_delta, timestamp):
    """
    Updates inventory by adding/subtracting a delta. 
    Uses GREATEST(..., 0) to ensure stock never drops below zero in the DB.
    """
    cur.execute(
        """
        INSERT INTO staging.inventories (product_id, store_id, amount, update_date)
        VALUES (%s, %s, GREATEST(%s, 0), %s)
        ON CONFLICT (store_id, product_id)
        DO UPDATE
            SET amount = GREATEST(staging.inventories.amount + %s, 0),
                update_date = EXCLUDED.update_date;
        """,
        (product_id, store_id, quantity_delta, timestamp, quantity_delta)
    )

def set_inventory_absolute(cur, store_id, product_id, stock_after_event, timestamp):
    """
    Sets inventory to an absolute value.
    Uses GREATEST(..., 0) as an extra safeguard against negative values.
    """
    cur.execute(
        """
        INSERT INTO staging.inventories (product_id, store_id, amount, update_date)
        VALUES (%s, %s, GREATEST(%s, 0), %s)
        ON CONFLICT (store_id, product_id)
        DO UPDATE
            SET amount = GREATEST(EXCLUDED.amount, 0),
                update_date = EXCLUDED.update_date;
        """,
        (product_id, store_id, stock_after_event, timestamp)
    )

def process_sale_event(cur, event):
    """
    Handles a sale by creating an order, adding items, and reducing inventory.
    """
    total_order_price = sum(item["price"] * item["quantity"] for item in event["items"])

    # Insert into orders table; ignore if the event_id already exists (idempotency)
    cur.execute(
        """
        INSERT INTO staging.orders (source_event_id, store_id, order_price, order_date)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (source_event_id) DO NOTHING
        RETURNING order_id;
        """,
        (str(event["event_id"]), event["store_id"], total_order_price, event["timestamp"])
    )

    inserted_order = cur.fetchone()
    if inserted_order is None:
        print(f"Duplicate sale event skipped (Event ID: {event.get('event_id')})")
        return

    new_order_id = inserted_order[0]

    for item in event["items"]:
        # Link items to the newly created order
        cur.execute(
            """
            INSERT INTO staging.items (product_id, item_price, order_id, quantity)
            VALUES (%s, %s, %s, %s);
            """,
            (item["product_id"], item["price"], new_order_id, item["quantity"])
        )
        # Decrease stock based on quantity sold
        upsert_inventory_delta(
            cur,
            event["store_id"],
            item["product_id"],
            -int(item["quantity"]),
            event["timestamp"]
        )

    print("The sale has been saved to the database and inventory has been updated!")

def process_restock_event(cur, event):
    """
    Handles a restock event by increasing the inventory level.
    """
    upsert_inventory_delta(
        cur,
        event["store_id"],
        event["product_id"],
        int(event["quantity_change"]),
        event["timestamp"]
    )
    print(f"Restock event saved (Event ID: {event.get('event_id')})")

def process_stock_update_event(cur, event):
    """
    Handles manual stock updates, either by setting an absolute value or applying a delta.
    """
    if event.get("stock_after_event") is not None:
        set_inventory_absolute(
            cur,
            event["store_id"],
            event["product_id"],
            int(event["stock_after_event"]),
            event["timestamp"]
        )
    else:
        upsert_inventory_delta(
            cur,
            event["store_id"],
            event["product_id"],
            int(event["quantity_change"]),
            event["timestamp"]
        )

    print(f"Stock update event saved (Event ID: {event.get('event_id')})")

def process_new_product_event(cur, event):
    """
    Handles the introduction of a new product by inserting it into the products table
    and initializing its inventory to 10 for both stores.
    """
    product = event["product"]

    cur.execute(
        """
        INSERT INTO staging.products (
            product_code,
            product_name,
            brand_id,
            category_id,
            colour_id,
            size_id,
            gender_id,
            price,
            active
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, TRUE)
        ON CONFLICT (product_code) DO UPDATE
            SET product_name = EXCLUDED.product_name,
                brand_id = EXCLUDED.brand_id,
                category_id = EXCLUDED.category_id,
                colour_id = EXCLUDED.colour_id,
                size_id = EXCLUDED.size_id,
                gender_id = EXCLUDED.gender_id,
                price = EXCLUDED.price,
                active = TRUE
        RETURNING product_id;
        """,
        (
            product["product_code"],
            product["product_name"],
            product["brand_id"],
            product["category_id"],
            product["colour_id"],
            product["size_id"],
            product["gender_id"],
            product["price"],
        )
    )

    new_product_id = cur.fetchone()[0]

    for store_id in (1, 2):
        cur.execute(
            """
            INSERT INTO staging.inventories (product_id, store_id, amount, update_date)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (store_id, product_id)
            DO UPDATE SET
                amount = EXCLUDED.amount,
                update_date = EXCLUDED.update_date;
            """,
            (new_product_id, store_id, 10, event["timestamp"])
        )

    print(f"New product event saved (Event ID: {event.get('event_id')}, Product ID: {new_product_id})")

# Main processing loop
while True:
    msg = consumer.poll(1.0)
    
    if msg is None:
        continue
    if msg.error():
        print(f"An Error occurred in Kafka: {msg.error()}")
        continue

    try:
        # 1. Parse, clean and validate data. 
        # Returns a dictionary if valid, raises ValidationError if it's "dirty data".
        event = parse_and_validate_event(msg)
        event_type = event.get("event_type")

        # 2. Process based on event type
        with psycopg.connect(DB_URL) as conn:
            with conn.cursor() as cur:
                if event_type == "sale":
                    print(f"Caught sale event from Kafka! (Event ID: {event.get('event_id')})")
                    process_sale_event(cur, event)
                elif event_type == "restock":
                    print(f"Caught restock event from Kafka! (Event ID: {event.get('event_id')})")
                    process_restock_event(cur, event)
                elif event_type == "stock_update":
                    print(f"Caught stock_update event from Kafka! (Event ID: {event.get('event_id')})")
                    process_stock_update_event(cur, event)
                elif event_type == "new_product":
                    print(f"Caught new product event from Kafka! (Event ID: {event.get('event_id')}) ")
                    process_new_product_event(cur, event)
                
                # Commit the transaction if everything succeeded
                conn.commit()

    except ValidationError as v_err:
        print(f"Dirty Data Detected! Validation failed for event: {v_err}")
    except ValueError as val_err:
        print(f"Value Error: {val_err}")
    except json.JSONDecodeError as json_err:
        print(f"An error occurred while decoding JSON: {json_err}")
    except psycopg.Error as db_err:
        print(f"The database is having issues! Error in SQL or connection: {db_err}")
    except Exception as e:
        print(f"Something went wrong when we tried to save: {e}")