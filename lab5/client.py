# client.py
import requests
import uuid
import time

URL = "http://localhost:8000/orders"


def create_order():
    request_id = str(uuid.uuid4())

    attempt = 0
    while attempt >= 0:
        try:
            print(f"Attempt {attempt + 1}")

            response = requests.post(
                URL,
                params={"request_id": request_id},
                timeout=6
            )

            print("SUCCESS:", response.json())
            return

        except requests.exceptions.Timeout:
            print("Timeout, retrying...")
            time.sleep(1)
            attempt += 1

    print("Failed after retries")


if __name__ == "__main__":
    create_order()