import os
import json
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from agent.agent import SupportAgent

app = FastAPI(title="Sagepilot Support Agent Demo")

# Serve static frontend files
frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

LOG_PATH = os.path.join(os.path.dirname(__file__), "logs", "audit_log.json")

# Initialize the agent
agent = SupportAgent()

class ChatRequest(BaseModel):
    message: str

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open(os.path.join(frontend_dir, "index.html"), "r") as f:
        return f.read()

@app.post("/api/chat")
async def chat(req: ChatRequest):
    try:
        response_text = agent.process_message(req.message)
        return {"response": response_text}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/api/logs")
async def get_logs():
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r") as f:
            try:
                logs = json.load(f)
                return logs
            except json.JSONDecodeError:
                return []
    return []

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
