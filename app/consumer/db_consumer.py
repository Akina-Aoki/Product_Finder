import os
import json
import psycopg
from confluent_kafka import Consumer

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
TOPIC = os.getenv("PRODUCTS_TOPIC", "inventory_events")
DB_URL = os.getenv("DB_URL", "postgresql://postgres:postgres@postgres:5432/SportWearDB")

def on_assign(consumer, partitions):
    print(f"Kafka approved access to: {partitions}")

print(f"Starting DB Consumer against {KAFKA_BOOTSTRAP_SERVERS}...")

conf = {
    'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
    'group.id': "sportwear_inventory_consumer",
    'auto.offset.reset': 'earliest',
    'error_cb': lambda err: print(f"Kafka network error: {err}") 
}

consumer = Consumer(conf)
consumer.subscribe([TOPIC], on_assign=on_assign)

print(f"The Consumer is listening to {TOPIC} and is ready to save to the database!")

while True:
    msg = consumer.poll(1.0)
    
    if msg is None:
        continue
    if msg.error():
        print(f"An Error occurred in Kafka: {msg.error()}")
        continue

    try:
        raw_data = msg.value().decode('utf-8')
        event = json.loads(raw_data)

        if isinstance(event, str):
            event = json.loads(event)

        if event.get("event_type") == "sale":
            print(f"Caught sale event from Kafka! (Event ID: {event.get('event_id')})")
            
            with psycopg.connect(DB_URL) as conn:
                with conn.cursor() as cur:
                    
                    total_order_price = sum(item["price"] * item["quantity"] for item in event["items"])
                    
                    cur.execute(
                        """
                        INSERT INTO staging.orders (store_id, order_price, order_date)
                        VALUES (%s, %s, %s)
                        RETURNING order_id;
                        """,
                        (event["store_id"], total_order_price, event["timestamp"])
                    )
                    
                    new_order_id = cur.fetchone()[0]
                    
                    for item in event["items"]:
                        cur.execute(
                            """
                            INSERT INTO staging.items (product_id, item_price, order_id, quantity)
                            VALUES (%s, %s, %s, %s);
                            """,
                            (item["product_id"], item["price"], new_order_id, item["quantity"])
                        )
                        
            print("The sale has been saved to the database!")

    except json.JSONDecodeError as json_err:
        print(f"An error occurred while decoding JSON: {json_err}")
        
    except psycopg.Error as db_err:
        print(f"The database is having issues! Error in SQL or connection: {db_err}")
        
    except Exception as e:
        print(f"Something went wrong when we tried to save: {e}")