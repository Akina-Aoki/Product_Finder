import json
import random
from datetime import datetime, timedelta

products = [1556, 722, 580, 10061, 7447, 2443, 6109, 11447]
prices = {
    1556: 34.97,
    722: 281.22,
    580: 67.60,
    10061: 138.33,
    7447: 102.23,
    2443: 135.84,
    6109: 163.16,
    11447: 281.15
}

events = []
base_time = datetime.utcnow()

for i in range(100):
    event = {
        "event_id": 91000 + i,
        "event_type": "sale",
        "timestamp": (base_time + timedelta(minutes=i)).isoformat() + "Z",
        "store_id": random.choice([1, 2]),
        "items": []
    }

    for _ in range(random.randint(1, 3)):
        pid = random.choice(products)
        event["items"].append({
            "product_id": pid,
            "price": prices[pid],
            "quantity": random.randint(1, 3)
        })

    events.append(event)

print(json.dumps(events, indent=2))