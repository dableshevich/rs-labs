from fastapi import FastAPI
import requests

app = FastAPI()

subscribers = {
    "orders": ["http://localhost:8002/"]
}


@app.post("/publish")
def publish(data: dict):
    topic = data["topic"]
    message = data["message"]

    for sub in subscribers.get(topic, []):
        try:
            requests.post(sub, json=message)
        except:
            pass

    return {"status": "sent"}