import os
import json
from typing import List
from contextlib import asynccontextmanager

from fastapi import FastAPI
from kafka import KafkaProducer

from app.schema.product import InventoryEvent, NewProductEvent, SaleEvent


KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:29092")
PRODUCTS_TOPIC = os.getenv("PRODUCTS_TOPIC", "inventory_events")


# ---------------------------
# Kafka Lifecycle Management
# ---------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up FastAPI and connecting to Kafka...")

    app.state.kafka_producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        key_serializer=lambda k: k.encode("utf-8") if k else None,
    )

    yield

    print("Shutting down API and closing Kafka connection...")
    try:
        app.state.kafka_producer.flush()
        app.state.kafka_producer.close()
    except Exception as e:
        print(f"Shutdown error: {e}")


app = FastAPI(lifespan=lifespan)


# ---------------------------
# Helper: Publish Event
# ---------------------------
def publish_event(producer, topic, event):
    producer.send(
        topic,
        value=event.model_dump(mode="json")  # ✅ always send dict
    )


# ---------------------------
# Sales Endpoints
# ---------------------------
@app.post("/api/sales")
async def receive_single_sale(event: SaleEvent):
    publish_event(app.state.kafka_producer, PRODUCTS_TOPIC, event)

    return {
        "status": "success",
        "message": "One sale sent to Kafka!"
    }


@app.post("/api/sales/batch")
async def receive_sales_batch(events: List[SaleEvent]):
    for event in events:
        publish_event(app.state.kafka_producer, PRODUCTS_TOPIC, event)

    return {
        "status": "success",
        "message": f"{len(events)} sales sent to Kafka!"
    }


# ---------------------------
# New Product Endpoints
# ---------------------------
@app.post("/api/products/new")
async def receive_new_product_event(event: NewProductEvent):
    publish_event(app.state.kafka_producer, PRODUCTS_TOPIC, event)

    return {
        "status": "success",
        "message": "new_product event sent to Kafka!"
    }


@app.post("/api/products/new/batch")
async def receive_new_product_events_batch(events: List[NewProductEvent]):
    for event in events:
        publish_event(app.state.kafka_producer, PRODUCTS_TOPIC, event)

    return {
        "status": "success",
        "message": f"{len(events)} new_product events sent to Kafka!"
    }


# ---------------------------
# Inventory Events (Restock / Stock Update)
# ---------------------------
@app.post("/api/inventory-events/batch")
async def receive_inventory_events_batch(events: List[InventoryEvent]):
    for event in events:
        publish_event(app.state.kafka_producer, PRODUCTS_TOPIC, event)

    return {
        "status": "success",
        "message": f"{len(events)} inventory events sent to Kafka!"
    }