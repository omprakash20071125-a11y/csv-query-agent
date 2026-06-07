import pandas as pd
import sqlite3
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from langgraph.types import interrupt
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command
from dotenv import load_dotenv
load_dotenv()

# checkpointer 
checkpoint = InMemorySaver()

conn = sqlite3.connect("chatbot.db", check_same_thread=False)

# for loading csv
def load_csv(file) -> pd.DataFrame:
    df = pd.read_csv(file)
    df.to_sql("data", conn, index=False, if_exists="replace")
    return df

# fetching the schema of csv
def fetch_schema(df) -> str:
    schema = []
    schema.append("table name: data")
    schema.append(f"Total rows: {len(df)}")
    schema.append(f"Total columns: {len(df.columns)}")
    schema.append("\nColumn names and types:")
    for col in df.columns:
        dtype  = str(df[col].dtype)
        nulls  = df[col].isnull().sum()
        sample = df[col].dropna().head(3).tolist()
        schema.append(f"  - {col} ({dtype}) | nulls: {nulls} | sample: {sample}")
    schema.append(f"\nTop 5 rows:\n{df.head().to_string()}")
    schema.append(f"\nBottom 5 rows:\n{df.tail().to_string()}")
    return "\n".join(schema)

# answer schema required from model
class answer_type(BaseModel):
    sql_q: str = Field(description="Only the raw SQL query, no markdown, no backticks")
    feedb: str = Field(description="Plain English explanation of what this query does")


model = ChatGroq(model="llama-3.3-70b-versatile")
structured_model = model.with_structured_output(answer_type)

# state of the graph
class SQL_state(TypedDict):
    query:      str
    schema:     str
    feedback:   str
    sql_query:  str
    result:     str
    result_llm: str

# sql query generation
def SQL_generation(state: SQL_state) -> SQL_state:
    prompt = PromptTemplate(
        template=(
            "You are a SQL expert for SQLite.\n"
            "Generate a SQL query for this request: {query}\n\n"
            "DATABASE SCHEMA:\n{schema}\n\n"
            "STRICT RULES:\n"
            "- Table name is always: data\n"
            "- Output ONLY the raw SQL. No markdown, no backticks, no explanation.\n"
            "- Use only column names that exist in the schema above.\n"
            "- End the query with a semicolon.\n"
        ),
        input_variables=["query", "schema"]
    )
    chain  = prompt | structured_model
    result = chain.invoke({"query": state["query"], "schema": state["schema"]})

    sql = result.sql_q.strip()
    sql = sql.replace("```sql", "").replace("```", "").strip()

    return {"sql_query": sql, "feedback": result.feedb}

# implementing the query to csv
def sql_implementation(state: SQL_state) -> SQL_state:
    sql = state["sql_query"].strip()

    if sql.lower().startswith("select"):
        try:
            result_df = pd.read_sql(sql, conn)
            return {"result": result_df.to_string(index=False)}
        except Exception as e:
            return {"result": f"SQL Error: {str(e)}"}
    else:
        decision = interrupt({"message": f"approve SQL: {sql}"})
        if isinstance(decision, str) and decision.lower() == "yes":
            try:
                cursor = conn.cursor()
                cursor.execute(sql)
                conn.commit()
                return {"result": f"{cursor.rowcount} row(s) affected."}
            except Exception as e:
                return {"result": f"SQL Error: {str(e)}"}
        else:
            return {"result": "Execution cancelled by user."}


def fetching_result_llm(state: SQL_state) -> SQL_state:
    prompt = PromptTemplate(
        template=(
            "The user asked: {query}\n"
            "The SQL query run was: {sql_query}\n"
            "The raw result is:\n{result}\n\n"
            "Give a short, friendly, human-readable answer. Do not repeat the SQL."
        ),
        input_variables=["query", "sql_query", "result"]
    )
    chain  = prompt | model
    result = chain.invoke({
        "query":     state["query"],
        "sql_query": state["sql_query"],
        "result":    state["result"],
    })
    return {"result_llm":result.content}

# building the graph
graph = StateGraph(SQL_state)

# adding nodes
graph.add_node("SQL_generation",SQL_generation)
graph.add_node("sql_implementation",sql_implementation)
graph.add_node("fetching_result",fetching_result_llm)

# adding edges
graph.add_edge(START,"SQL_generation")
graph.add_edge("SQL_generation","sql_implementation")
graph.add_edge("sql_implementation","fetching_result")
graph.add_edge("fetching_result",END)

# complie the graph
sql_chatbot = graph.compile(checkpointer=checkpoint)