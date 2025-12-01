from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, List

from graph.workflow import SQLAgentState, workflow

app = FastAPI()


class AgentState(BaseModel):
    chat_history: List[str] = Field(default_factory=list)
    workflow_history: List[str] = Field(default_factory=list)
    user_query: str = ""
    sql_query: str = ""
    final_response: str = ""
    query_results: List[Dict[str, Any]] = Field(default_factory=list)


user_states: Dict[str, AgentState] = {}


@app.post("/chat/{session_id}")
async def chat(session_id: str, message: str):
    if session_id not in user_states:
        user_states[session_id] = AgentState()

    state = user_states[session_id]

    state.chat_history.append(message)
    state.user_query = message

    workflow_history = list(state.workflow_history)
    workflow_history.append(message)
    graph_input: SQLAgentState = {
        "user_input": message,
        "history": workflow_history,
    }
    graph_result = workflow.invoke(graph_input)

    state.workflow_history = graph_result.get("history", workflow_history)
    state.sql_query = graph_result.get("sql_query", "")
    state.query_results = graph_result.get("query_results", [])
    state.final_response = graph_result.get("final_response", "")

    return JSONResponse(content=state.dict())
