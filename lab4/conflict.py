import threading
import time
import requests

NODES = {
    1: "http://localhost:5001/value",
    2: "http://localhost:5002/value"
}

def send_value(node_id, value, sleep):
    time.sleep(sleep)
    try:
        r = requests.post(
            NODES[node_id],
            json={"value": value},
            timeout=2
        )
        print(f"Node {node_id} set value {value} -> {r.json()}")
    except Exception as e:
        print(f"Node {node_id} error: {e}")

if __name__ == "__main__":
    t1 = threading.Thread(target=send_value, args=(1, 10, 0.00))
    t2 = threading.Thread(target=send_value, args=(2, 20, 0.02))

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    print("Done sending concurrent updates")