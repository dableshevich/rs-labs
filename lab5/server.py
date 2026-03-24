from fastapi import FastAPI, HTTPException
import random
import time
import requests

app = FastAPI()

orders_db = {}
request_cache = {}

BROKER_URL = "http://localhost:8001/publish"


@app.post("/orders")
def create_order(request_id: str):
    if request_id in request_cache:
        return request_cache[request_id]

    r = random.random()
    if r < 0.3:
        time.sleep(3)

    order_id = len(orders_db) + 1
    order = {"order_id": order_id, "status": "created"}

    orders_db[order_id] = order
    request_cache[request_id] = order

    try:
        requests.post(BROKER_URL, json={
            "topic": "orders",
            "message": order
        })
    except:
        raise HTTPException(status_code=500, detail="broker don't working")

    return order