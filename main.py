from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, List
import uuid

app = FastAPI()

# TypedDict class to represent the agent's state
class AgentState(BaseModel):
    chat_history: List[str]
    user_query: str
    sql_query: str
    final_response: str

# Dictionary to maintain the state for each user, indexed by a session_id
user_states: Dict[str, AgentState] = {}

@app.post("/chat/{session_id}")
async def chat(session_id: str, message: str):
    # Initialize state if not exists
    if session_id not in user_states:
        user_states[session_id] = AgentState(
            chat_history=[],
            user_query="",
            sql_query="",
            final_response=""
        )
    
    # Update user state with the new message
    user_states[session_id].chat_history.append(message)
    user_states[session_id].user_query = message

    # Simulate processing the message (to be replaced with actual logic)
    user_states[session_id].sql_query = f"SELECT * FROM example_table WHERE message LIKE '%{message}%'"
    user_states[session_id].final_response = f"Processed message: {message}"

    # Return the updated state
    return JSONResponse(content=user_states[session_id].dict())
