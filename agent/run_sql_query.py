import os
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
from generate_sql_query import generate_sql_query

# Load environment variables from .env file
load_dotenv()

# Configuration: Database Connection
db_user = os.getenv("POSTGRES_USER")
db_password = os.getenv("POSTGRES_PASSWORD")
db_name = os.getenv("POSTGRES_DB")
db_host = os.getenv("POSTGRES_HOST", "localhost")
db_port = os.getenv("POSTGRES_PORT", "5432")

DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


def is_readonly_query(query: str) -> bool:
    """
    Validate that the query is read-only (SELECT only).
    
    Args:
        query: SQL query string
    
    Returns:
        True if the query is read-only, False otherwise
    """
    # Remove comments and normalize whitespace
    query_clean = " ".join(query.split())
    query_upper = query_clean.upper().strip()
    
    # Check if query starts with SELECT
    if not query_upper.startswith("SELECT"):
        return False
    
    # List of potentially dangerous SQL keywords that modify data
    dangerous_keywords = [
        "INSERT", "UPDATE", "DELETE", "DROP", "CREATE", "ALTER",
        "TRUNCATE", "GRANT", "REVOKE", "EXEC", "EXECUTE"
    ]
    
    # Check for dangerous keywords (excluding SELECT)
    for keyword in dangerous_keywords:
        # Use word boundaries to avoid false positives
        if f" {keyword} " in query_upper or query_upper.endswith(f" {keyword}"):
            return False
    
    return True


def execute_readonly_query(
    sql_query: str,
    connection_string: str = None
) -> Optional[List[Dict[str, Any]]]:
    """
    Execute a SQL query against PostgreSQL in read-only mode.
    
    Args:
        sql_query: The SQL query to execute
        connection_string: PostgreSQL connection string. If None, uses environment variables.
    
    Returns:
        List of dictionaries representing query results, or None if an error occurred
    """
    
    # Validate that the query is read-only
    if not is_readonly_query(sql_query):
        print("Error: Only SELECT queries are allowed in read-only mode.")
        return None
    
    try:
        # Connect to database
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password
        )
        
        # Set connection to read-only mode
        conn.set_session(readonly=True, autocommit=False)
        
        try:
            # Use RealDictCursor to get results as dictionaries
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(sql_query)
                
                # Fetch all results
                results = cursor.fetchall()
                
                # Convert to list of dictionaries
                return [dict(row) for row in results]
        
        finally:
            conn.close()
    
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return None
    except Exception as e:
        print(f"Error executing query: {e}")
        return None


def generate_and_run_query(
    user_input: str,
    schema_path: str = None,
    ollama_url: str = "http://localhost:11434",
    model: str = "mannix/defog-llama3-sqlcoder-8b"
) -> Optional[List[Dict[str, Any]]]:
    """
    Generate a SQL query from user input and execute it against the database.
    
    Args:
        user_input: The natural language prompt describing the SQL query to generate
        schema_path: Path to schema.json file. If None, uses schema.json in the same directory.
        ollama_url: The base URL of the Ollama API (default: http://localhost:11434)
        model: The model name to use (default: mannix/defog-llama3-sqlcoder-8b)
    
    Returns:
        List of dictionaries representing query results, or None if an error occurred
    """
    # Generate SQL query
    sql_query = generate_sql_query(
        user_input=user_input,
        schema_path=schema_path,
        ollama_url=ollama_url,
        model=model
    )
    
    if sql_query is None:
        print("Failed to generate SQL query.")
        return None
    
    print(f"Generated SQL Query:\n{sql_query}\n")
    
    # Execute the query
    results = execute_readonly_query(sql_query)
    
    return results


if __name__ == "__main__":
    # Example usage
    test_input = "Show me all products in the Electronics category"
    results = generate_and_run_query(test_input)
    
    if results is not None:
        print(f"\nQuery Results ({len(results)} rows):")
        print("-" * 50)
        for i, row in enumerate(results, 1):
            print(f"Row {i}: {row}")
    else:
        print("Failed to execute query")

