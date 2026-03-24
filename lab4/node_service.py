from flask import Flask, request, jsonify
import threading
import requests
import time
from datetime import datetime
import random
import sys

app = Flask(__name__)

NODE_ID = None
NODES = {
    1: "http://localhost:5001",
    2: "http://localhost:5002",
    3: "http://localhost:5003"
}

local_value = 0
local_timestamp = 0 
lock = threading.Lock()

@app.route('/value', methods=['GET'])
def get_value():
    with lock: # locks are used because flask is using multithreading under the hood, and every endpoint could change local_value/timestamp
        return jsonify({
            'node_id': NODE_ID,
            'value': local_value,
            'timestamp': local_timestamp
        })


@app.route('/value', methods=['POST'])
def update_value():
    global local_value, local_timestamp
    
    data = request.get_json()
    if not data or 'value' not in data:
        return jsonify({'error': 'Missing value'}), 400
    
    new_value = data['value']
    
    with lock:
        local_value = new_value
        local_timestamp = time.time_ns()
        
        # start non-blocking sync with other 2 nodes
        update_other_nodes()
        
        return jsonify({
            'node_id': NODE_ID,
            'value': local_value,
            'timestamp': local_timestamp
        })

# this endpoint is only accessed by another node
@app.route('/sync', methods=['POST'])
def sync():
    global local_value, local_timestamp
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid data'}), 400
    
    received_value = data['value']
    received_timestamp = data['timestamp']
    received_node_id = data['node_id']
    
    with lock:
        if received_timestamp > local_timestamp:
            print(f"Node {NODE_ID}: Updating from {local_value} to {received_value} (timestamp {received_timestamp} > {local_timestamp})")
            local_value = received_value
            local_timestamp = received_timestamp
        elif received_timestamp == local_timestamp and received_node_id < NODE_ID:
            # Tie-breaker: if same timestamp, lower node ID wins
            print(f"Node {NODE_ID}: Same timestamp, node {received_node_id} < {NODE_ID}, updating")
            local_value = received_value
        else:
            print(f"Node {NODE_ID}: Ignoring update (local timestamp {local_timestamp} >= {received_timestamp})")
    
    return jsonify({'status': 'synced'})

# asynchronios
def update_other_nodes():
    current_value = local_value
    current_timestamp = local_timestamp
    
    def propagate():
        for node_id, url in NODES.items():
            if node_id == NODE_ID:
                continue
            
            try:
                requests.post(f"{url}/sync", json={'value': current_value, 'timestamp': current_timestamp, 'node_id': NODE_ID}, timeout=1)
                print(f"Node {NODE_ID}: Propagated to node {node_id}")
            except:
                print(f"Node {NODE_ID}: Failed to reach node {node_id}")
    
    thread = threading.Thread(target=propagate)
    thread.daemon = True
    thread.start()


if __name__ == '__main__':
    NODE_ID = int(sys.argv[1])
    port = int(sys.argv[2])
    app.run(host='0.0.0.0', port=port, debug=False)