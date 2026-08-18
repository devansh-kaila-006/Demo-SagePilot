import json
import os
import time
from datetime import datetime
import google.generativeai as genai
from .rag import get_rag
from .tools import check_order_status, issue_refund
from .permissions import check_refund_permission

api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# Use a model that supports tool calling
model = genai.GenerativeModel(
    model_name="gemini-3.5-flash", 
    tools=[check_order_status, issue_refund],
    system_instruction=(
        "You are a helpful customer support agent for a D2C brand. "
        "You ONLY answer questions using the provided context. If the context does not contain the answer, "
        "say 'I cannot answer this with confidence based on the available information.' and escalate. "
        "You can check order statuses and issue refunds. For refunds, only issue them if the user explicitly asks for it, "
        "and you must extract the order ID and amount."
    )
)

LOG_PATH = os.path.join(os.path.dirname(__file__), "..", "logs", "audit_log.json")

def _log_action(action, permission_used, confidence, status):
    if not os.path.exists(LOG_PATH):
        with open(LOG_PATH, 'w') as f:
            json.dump([], f)
            
    with open(LOG_PATH, 'r') as f:
        try:
            logs = json.load(f)
        except json.JSONDecodeError:
            logs = []
            
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "permission_used": permission_used,
        "confidence": confidence,
        "status": status
    }
    logs.append(log_entry)
    
    with open(LOG_PATH, 'w') as f:
        json.dump(logs, f, indent=2)

class SupportAgent:
    def __init__(self):
        self.rag = get_rag()
        self.chat = model.start_chat()
        
    def process_message(self, user_message: str):
        # 1. RAG Grounding
        context = self.rag.retrieve(user_message, top_k=2)
        
        # 2. Add context to the prompt
        prompt = f"User Query: {user_message}\n\nRelevant Context from Knowledge Base:\n{context}\n\nRespond to the user. If they want an action, call the appropriate tool."
        
        # 3. Generate response and handle tools
        response = self.chat.send_message(prompt)
        
        # Check if model wants to call a tool
        function_calls = []
        try:
            for part in response.parts:
                if hasattr(part, 'function_call') and part.function_call:
                    function_calls.append(part.function_call)
        except Exception:
            pass
            
        if function_calls:
            for function_call in function_calls:
                name = function_call.name
                # convert args to dict safely
                args = {}
                if hasattr(function_call.args, 'items'):
                    for k, v in function_call.args.items():
                        args[k] = v
                elif isinstance(function_call.args, dict):
                    args = function_call.args
                
                if name == "check_order_status":
                    _log_action("check_order_status", "None", "High", "Auto-Approved")
                    tool_result = check_order_status(**args)
                    
                    # Send tool result back to the model
                    response = self.chat.send_message(
                        genai.protos.Part(
                            function_response=genai.protos.FunctionResponse(
                                name=name,
                                response={"result": tool_result}
                            )
                        )
                    )
                    return response.text
                
                elif name == "issue_refund":
                    amount = args.get("amount")
                    order_id = args.get("order_id")
                    
                    # 4. Permission Gate
                    if check_refund_permission(amount):
                        tool_result = issue_refund(order_id=order_id, amount=amount)
                        _log_action(f"issue_refund (Amount: {amount})", "check_refund_permission", "High", "Auto-Approved")
                        response = self.chat.send_message(
                            genai.protos.Part(
                                function_response=genai.protos.FunctionResponse(
                                    name=name,
                                    response={"result": tool_result}
                                )
                            )
                        )
                        return response.text
                    else:
                        # 5. Escalation for high refund amount
                        _log_action(f"issue_refund (Amount: {amount})", "check_refund_permission", "High", "Escalated - Exceeds Threshold")
                        msg = f"Your refund request for ₹{amount} exceeds my auto-approval limit of ₹2000. I have escalated this to a human agent for approval."
                        # Send this back so the agent knows it couldn't be done
                        response = self.chat.send_message(
                            genai.protos.Part(
                                function_response=genai.protos.FunctionResponse(
                                    name=name,
                                    response={"error": "Escalated for human approval"}
                                )
                            )
                        )
                        return msg
                        
        else:
            # Check for out-of-scope based on system instruction response
            if "I cannot answer this with confidence" in response.text or "I do not have" in response.text:
                 _log_action("answer_query", "None", "Low", "Escalated - Out of Scope")
                 return response.text
                 
            # Normal grounded answer
            _log_action("answer_query", "None", "High", "Auto-Approved")
            return response.text
