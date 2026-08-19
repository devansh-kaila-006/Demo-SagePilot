import json
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "mock_products_orders.json")

def _load_data():
    with open(DATA_PATH, 'r') as f:
        return json.load(f)

def _save_data(data):
    with open(DATA_PATH, 'w') as f:
        json.dump(data, f, indent=2)

def check_order_status(order_id: str) -> str:
    """Checks the status of an order given its ID."""
    data = _load_data()
    for order in data.get("orders", []):
        if order["id"] == str(order_id):
            return f"Order #{order_id} for {order['customer']} is currently {order['status']}. Expected delivery: {order['expected_delivery']}."
    return f"Could not find order #{order_id}."

def issue_refund(order_id: str, amount: float) -> str:
    """Issues a refund for a given order ID and amount."""
    data = _load_data()
    for order in data.get("orders", []):
        if order["id"] == str(order_id):
            # MOCK ACTION: Update the status to refunded (in reality, would call payment gateway)
            order["payment_status"] = f"Refunded ₹{amount}"
            _save_data(data)
            return f"Successfully issued refund of ₹{amount} for order #{order_id}."
    return f"Failed to issue refund: Order #{order_id} not found."
