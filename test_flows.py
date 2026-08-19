import requests
import json
import time
import sys

# Fix Windows console encoding for ₹ symbol
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

URL = "http://localhost:8000/api/chat"

print("--- Testing Conversational Flows ---")

def test_flow(name, message):
    print(f"\n{name}")
    print(f"User: {message}")
    try:
        res = requests.post(URL, json={"message": message})
        print(f"Agent: {res.json().get('response', res.text)}")
    except Exception as e:
        print(f"Error: {e}")

# Core scenarios
test_flow("Flow 1: Simple Grounded Query (Order Status)", "What's the status of order #1042?")
test_flow("Flow 2: In-scope Action (Auto-Approved Refund)", "Refund order #1043, it's ₹950")
test_flow("Flow 3: In-scope Action (Escalated Refund)", "Refund order #1042, it's ₹3400")
test_flow("Flow 4: Out-of-scope query (Escalated)", "What is your return policy for international orders?")

# Additional Scenarios
test_flow("Flow 5: Policy Lookup (Grounded)", "Do you offer free shipping?")
test_flow("Flow 6: Product Recommendation (Grounded)", "I need a sunscreen that isn't greasy. What do you recommend?")
test_flow("Flow 7: Invalid Order Status", "Check the status of order #9999")
test_flow("Flow 8: General Greeting", "Hello! Are you a robot?")
test_flow("Flow 9: Edge Case Refund (Exactly Threshold)", "I want to refund order #1044 for ₹2000.")

print("\n--- Audit Logs ---")
time.sleep(2) # wait for logs to flush
try:
    logs = requests.get("http://localhost:8000/api/logs").json()
    print(json.dumps(logs, indent=2))
except Exception as e:
    print(f"Failed to fetch logs: {e}")

