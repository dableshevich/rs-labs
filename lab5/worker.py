from fastapi import FastAPI
import time

app = FastAPI()


@app.post("/")
def process_order(order: dict):
    print(f"Processing order {order['order_id']}...")

    time.sleep(5)

    print(f"Order {order['order_id']} done")
    return {"status": "ok"}