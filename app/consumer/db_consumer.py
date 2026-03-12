import os
import json
import psycopg
from kafka import KafkaConsumer

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:29092")
TOPIC = os.getenv("PRODUCTS_TOPIC", "inventory_events")
GROUP_ID = "SportWear_DB_Consumer"

DB_URL = "postgresql://postgres:postgres@localhost:5439/SportWearDB"

def main():
    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=GROUP_ID,
        auto_offset_reset="earliest",
        value_deserializer=lambda b: json.loads(b.decode("utf-8")),
        key_deserializer=lambda b: b.decode("utf-8") if b else None,
    )

    print(f"Consumer is listening to topic: {TOPIC}...")

    try:
        with psycopg.connect(DB_URL) as conn:
            
            for msg in consumer:
                event = msg.value
                
                if event.get("event_type") == "sale":
                    print(f"New sale received! (Event ID: {event.get('event_id')})")
                    
                    try:
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
                                
                        conn.commit()
                        print(f"Saved sale to database with Order ID: {new_order_id}")

                    except Exception as db_err:
                        conn.rollback()
                        print(f"Error saving sale to database: {db_err}")

    except Exception as e:
        print(f"Error connecting to the database: {e}")

if __name__ == "__main__":
    main()