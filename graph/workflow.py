"""
LangGraph workflow that orchestrates the database agent pipeline.

The workflow has four nodes:
1. Retrieve table context
2. Generate SQL query
3. Execute SQL query
4. Generate final response
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, TypedDict

from langgraph.graph import END, StateGraph

from agent.generate_sql_query import generate_sql_query, load_schema
from agent.run_sql_query import execute_readonly_query


class SQLAgentState(TypedDict, total=False):
    """
    State container passed between LangGraph nodes.

    The history field stores past reasoning steps so the agent can answer
    multi-step client questions.
    """

    user_input: str
    table_context: str
    sql_query: str
    query_results: List[Dict[str, Any]]
    final_response: str
    history: List[str]


def _append_history(state: SQLAgentState, message: str) -> List[str]:
    """Return an updated history list with the new message appended."""
    history = list(state.get("history", []))
    history.append(message)
    return history


def retrieve_table_context(state: SQLAgentState) -> SQLAgentState:
    """Load the schema and attach it to the state."""
    schema_dict = load_schema()
    table_context = json.dumps(schema_dict, indent=2)
    history = _append_history(
        state,
        "Retrieved database schema context for downstream use.",
    )
    return {"table_context": table_context, "history": history}


def generate_sql_query_node(state: SQLAgentState) -> SQLAgentState:
    """Generate a SQL query using the user input and schema context."""
    user_query = state.get("user_input", "")
    if not user_query:
        raise ValueError("user_input must be provided before running the graph.")

    sql_query = generate_sql_query(user_input=user_query)
    history = _append_history(
        state,
        "Generated SQL query from the latest user request.",
    )
    return {"sql_query": sql_query, "history": history}


def execute_sql_query_node(state: SQLAgentState) -> SQLAgentState:
    """Execute the generated SQL query against the warehouse."""
    sql_query = state.get("sql_query")
    if not sql_query:
        raise ValueError("sql_query must be populated before executing it.")

    results: Optional[List[Dict[str, Any]]] = execute_readonly_query(sql_query)
    history = _append_history(
        state,
        "Executed SQL query and stored the raw results.",
    )
    return {"query_results": results or [], "history": history}


def generate_final_response_node(state: SQLAgentState) -> SQLAgentState:
    """Summarize the execution results for the end user."""
    user_query = state.get("user_input", "")
    query_results = state.get("query_results", [])

    if not query_results:
        final_response = (
            f"I ran the requested analysis: '{user_query}'. "
            "No rows were returned for the given filters."
        )
    else:
        preview = query_results[:3]
        final_response = (
            f"Answer to '{user_query}':\n"
            f"- Returned {len(query_results)} rows.\n"
            f"- Sample rows: {preview}"
        )

    history = _append_history(
        state,
        "Summarized SQL results and produced the final response.",
    )
    return {"final_response": final_response, "history": history}


builder = StateGraph(SQLAgentState)
builder.add_node("retrieve_table_context", retrieve_table_context)
builder.add_node("generate_sql_query", generate_sql_query_node)
builder.add_node("execute_sql_query", execute_sql_query_node)
builder.add_node("generate_final_response", generate_final_response_node)

# Entry point: user query feeds directly into the context retrieval node.
builder.set_entry_point("retrieve_table_context")
builder.add_edge("retrieve_table_context", "generate_sql_query")
builder.add_edge("generate_sql_query", "execute_sql_query")
builder.add_edge("execute_sql_query", "generate_final_response")
builder.add_edge("generate_final_response", END)

# Compiled workflow that can be imported elsewhere.
workflow = builder.compile()


__all__ = [
    "SQLAgentState",
    "workflow",
    "retrieve_table_context",
    "generate_sql_query_node",
    "execute_sql_query_node",
    "generate_final_response_node",
]

