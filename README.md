# Sagepilot Grounded Support Agent — Demo

This repository contains a miniature proof-of-concept demonstrating an AI-powered support agent designed to mimic the core capabilities of Sagepilot's enterprise offerings. 

Unlike a generic "chat with your data" RAG bot, this demo proves three specific technical capabilities crucial for modern D2C customer support:

1. **Agents act inside real business systems:** The agent doesn't just read data; it calls mock API tools to interact with a fake order management system and issue refunds.
2. **Permission Gates & Safety Escapes:** The agent is given explicit guardrails. It can autonomously approve refunds under ₹2000, but is explicitly blocked and forced to escalate to a human for anything exceeding that threshold or for out-of-scope policies it isn't trained on.
3. **100% Traceable & Grounded:** Every single action the agent takes, or refuses to take, is recorded in a real-time audit log specifying the permission used, the confidence level, and the specific data source it relied on.

---

## Architecture & Technology Stack

- **Backend Framework:** FastAPI (Python) for rapid, asynchronous API endpoints.
- **LLM Engine:** Google Gemini (`gemini-3.5-flash`) for fast reasoning, decision-making, and native function calling.
- **Embeddings:** `gemini-embedding-2` to embed local mock data into a lightweight vector store.
- **Frontend UI:** Pure HTML/CSS/JS replicating a WhatsApp-style chat interface alongside a live-updating audit log pane.

### Core Modules
* `app.py`: The FastAPI server serving the static UI and routing chat messages to the agent.
* `agent/agent.py`: The orchestrator. Takes user input, decides whether to fetch RAG context, decides whether to call a tool, evaluates permission gates, formats the final response, and appends to the audit log.
* `agent/rag.py`: A lightweight Retrieval-Augmented Generation implementation. Loads dummy JSON datasets, chunks them, generates embeddings, and retrieves top-k relevant snippets using cosine similarity.
* `agent/tools.py` & `agent/permissions.py`: Defines the mock tools (e.g. `check_order_status`, `issue_refund`) and the logic to gate their execution.

---

## Prerequisites & Installation

1. **Clone the repository and install dependencies:**
   This project uses the modern (and deprecated for older syntax) Google Generative AI Python SDK.
   ```bash
   pip install -r requirements.txt
   ```

2. **Acquire a Google Gemini API Key:**
   You will need a valid Google Gemini API key to run the models. You can get one for free at Google AI Studio.

3. **Set the API Key in your environment:**
   The API key is completely isolated and never hardcoded into the source. 
   ```bash
   # Windows (PowerShell)
   $env:GEMINI_API_KEY="your_api_key_here"
   
   # Mac/Linux (Bash/Zsh)
   export GEMINI_API_KEY="your_api_key_here"
   ```
   *(Optional: If you use a `.env` file via `python-dotenv`, ensure it is added to your `.gitignore`!)*

---

## Running the Application

1. **Start the FastAPI backend:**
   From the project root directory, run:
   ```bash
   python app.py
   ```
   *(Note: The first time you boot the server, it will take ~2-3 seconds to generate embeddings for the mock dataset into memory).*

2. **Open the Web Interface:**
   Navigate to [http://localhost:8000](http://localhost:8000) in your web browser. You will see the chat interface on the left and the real-time audit log pane on the right.

3. **Running the Automated Test Suite:**
   If you want to run an automated simulation of several edge cases from the terminal without using the UI, open a new terminal window and run:
   ```bash
   python test_flows.py
   ```

---

## Demo Walkthrough & Test Scenarios

To see the system working exactly as designed, try sending these exact prompts one-by-one. Watch how the Audit Log pane updates with each response!

### 1. Simple Grounded Query (Data Lookup)
> **User:** *"What's the status of order #1042?"*

**What happens:** The agent triggers the `check_order_status` tool, successfully retrieves the tracking data, and relays it back.
**Audit Log Result:** `Status: Auto-Approved | Confidence: High | Action: check_order_status`

### 2. In-Scope Action (Auto-Approved)
> **User:** *"I received a broken mug. Refund order #1043, it's ₹950."*

**What happens:** The agent evaluates the request against its internal policy. Because the refund amount (₹950) is below the ₹2000 auto-approval threshold, the agent executes the `issue_refund` tool successfully.
**Audit Log Result:** `Status: Auto-Approved | Confidence: High | Action: issue_refund (Amount: 950.0) | Permission: check_refund_permission`

### 3. In-Scope Action (Permission Escalation)
> **User:** *"My vacuum cleaner never arrived! Refund order #1042, it's ₹3400."*

**What happens:** The agent extracts the refund intent and amount, but realizes ₹3400 exceeds its strict hardcoded boundary. It halts the tool execution, refuses the request politely, and marks it for human review.
**Audit Log Result:** `Status: Escalated - Exceeds Threshold | Confidence: High`

### 4. Out-of-Scope Query (Safety Fallback)
> **User:** *"What is your return policy for international wholesale orders to Germany?"*

**What happens:** The agent checks its RAG context, finds no information on international wholesale policies, and triggers the `answer_query` safety fallback. Rather than hallucinating a guess, it escalates to a human.
**Audit Log Result:** `Status: Escalated - Out of Scope | Confidence: Low`

### 5. Product Recommendation (Grounded Semantic Search)
> **User:** *"I need a sunscreen that isn't greasy. What do you recommend?"*

**What happens:** The agent uses semantic vector search against the mock product database to find products matching "not greasy" and successfully recommends the Matte Sunscreen product.
**Audit Log Result:** `Status: Auto-Approved | Action: answer_query`

---

## Troubleshooting

- **500 Internal Server Error / 429 Quota Exceeded:** If you are testing the application rapidly using a free-tier Google API key, you may hit rate limits (Free tier is limited to 15 requests/minute and 20 requests/day for `gemini-3.5-flash`). Wait a few minutes before trying again, or use a paid-tier key.
- **Port 8000 in use:** If the server fails to start, make sure you don't have a background python process holding onto `localhost:8000`. You can kill it by restarting your terminal or hunting down the process ID.
- **Unicode Errors on Windows Terminal:** Running `test_flows.py` in older Windows PowerShell versions may occasionally throw a `cp1252` encoding error when trying to print the Indian Rupee symbol (₹). The web UI at localhost:8000 uses UTF-8 and will always display correctly.
