import os
from typing import List
from fastapi import FastAPI
from app.schema.product import InventoryEvent, SaleEvent
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI
from kafka import KafkaProducer

# Samma adress-tänk som vi pratade om tidigare!
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:29092")
PRODUCTS_TOPIC = os.getenv("PRODUCTS_TOPIC", "inventory_events")

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
        app.state.kafka_producer.close()
    except Exception as e:
        print(f"An error occurred while shutting down: {e}")

app = FastAPI(lifespan=lifespan)

@app.post("/api/sales")
async def receive_single_sale(event: SaleEvent):
    # Använder model_dump_json() istället för dict() - Helt rätt för Pydantic v2!
    app.state.kafka_producer.send(PRODUCTS_TOPIC, value=event.model_dump_json())
    app.state.kafka_producer.flush()
    
    return {"status": "success", "message": "One sale sent to Kafka!"}

@app.post("/api/sales/batch")
async def receive_sales_batch(events: List[SaleEvent]):
    for event in events:
        app.state.kafka_producer.send(PRODUCTS_TOPIC, value=event.model_dump_json())

    app.state.kafka_producer.flush()
        
    return {"status": "success", "message": f"{len(events)} sales sent to Kafka!"}

@app.post("/api/inventory-events")
async def receive_inventory_event(event: InventoryEvent):
    app.state.kafka_producer.send(PRODUCTS_TOPIC, value=event.model_dump_json())
    app.state.kafka_producer.flush()

    return {"status": "success", "message": f"{event.event_type} event sent to Kafka!"}


@app.post("/api/inventory-events/batch")
async def receive_inventory_events_batch(events: List[InventoryEvent]):
    for event in events:
        app.state.kafka_producer.send(PRODUCTS_TOPIC, value=event.model_dump_json())

    app.state.kafka_producer.flush()

    return {"status": "success", "message": f"{len(events)} inventory events sent to Kafka!"}