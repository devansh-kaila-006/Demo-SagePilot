# Grounded Support Agent Demo

A miniature proof-of-concept demonstrating a support agent that grounds answers in enterprise data, enforces permission gates before taking action, and produces a complete audit log of its decisions.

## What this demonstrates
1. **Grounded Responses:** Answers questions using a mock product/order dataset via a simple RAG pipeline.
2. **Permission-Gated Actions:** Calls mock tools (e.g., "issue refund") but pauses to request human approval if the action exceeds a predefined threshold (₹2000).
3. **Escalation & Logging:** Escalates out-of-scope queries gracefully and logs every decision (timestamp, confidence, permission used, approval status).

## Setup & Running

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Set your Gemini API Key:**
   ```bash
   # Windows (PowerShell)
   $env:GEMINI_API_KEY="your_api_key_here"
   ```
3. **Run the server:**
   ```bash
   python app.py
   ```
4. **Open the UI:**
   Navigate to [http://localhost:8000](http://localhost:8000)

## Test Conversations to Try

1. **Simple grounded query:** "What's the status of order #1042?"
2. **In-scope action (Auto-Approved):** "Refund order #1043, it's ₹950"
3. **In-scope action (Escalated):** "Refund order #1042, it's ₹3400"
4. **Out-of-scope query (Escalated):** "What is your return policy for international orders?"
