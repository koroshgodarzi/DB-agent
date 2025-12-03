import json
from pathlib import Path
from typing import Optional
from langchain_ollama.llms import OllamaLLM
from dotenv import load_dotenv
import os

load_dotenv()
OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

def load_schema(schema_path: str = None) -> dict:
    """
    Load the database schema from schema.json file.
    
    Args:
        schema_path: Path to schema.json file. If None, uses schema.json in the same directory.
    
    Returns:
        Dictionary containing the schema data
    """
    if schema_path is None:
        # Get the directory where this file is located
        current_dir = Path(__file__).parent
        schema_path = current_dir / "schema.json"
    
    with open(schema_path, 'r') as f:
        return json.load(f)


def generate_sql_query(
    user_input: str,
    schema_path: str = None,
    ollama_url: str = OLLAMA_URL,
    model: str = "mannix/defog-llama3-sqlcoder-8b"
) -> Optional[str]:
    """
    Generate a SQL query from natural language using the database schema.
    
    Args:
        user_input: The natural language prompt describing the SQL query to generate
        schema_path: Path to schema.json file. If None, uses schema.json in the same directory.
        ollama_url: The base URL of the Ollama API (default: http://localhost:11434)
        model: The model name to use (default: mannix/defog-llama3-sqlcoder-8b)
    
    Returns:
        The generated SQL query as a string, or None if an error occurred
    """
    try:
        # Load and format schema
        schema = load_schema(schema_path)
        prompt = f"""
        You are an expert Database Engineer and Data Analyst.
        
        Your goal is to generate valid PostgreSQL queries based on the user's question.
        
        Here is the Database Schema in JSON format:
        -------------------------------------------
        {schema}
        -------------------------------------------
        
        Instructions:
        1. Return ONLY the SQL code. No markdown (```sql), no explanations.
        2. Use the table names and column names exactly as defined in the schema.
        3. Pay close attention to the 'relationships' and 'business_logic' in the schema.
        4. For profit calculations, use the formula: (Sales Revenue - Purchase Cost).

        Here's user's question: 
        {user_input}
        """
        
          
        llm = OllamaLLM(
            base_url=ollama_url,
            model=model,
            timeout=300,
            num_ctx=2048 
        )
        
        sql_query = llm.invoke(prompt)
        print(sql_query)
        # sql_query = sql_query.choices[0].message.content.strip()
        
        # Clean up markdown if the LLM adds it by mistake (common issue)
        sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
        
        return sql_query
        
    except FileNotFoundError as e:
        print(f"Error: Schema file not found: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in schema file: {e}")
        return None
    except Exception as e:
        print(f"Error calling Ollama API through LangChain: {e}")
        return None


if __name__ == "__main__":
    # Example usage
    test_input = "Show me all products in the Electronics category"
    sql_query = generate_sql_query(test_input)
    
    if sql_query:
        print("Generated SQL Query:")
        print(sql_query)
    else:
        print("Failed to generate SQL query")

