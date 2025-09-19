DATA_FILE = "grocer_ai_data_sample.csv"


from datetime import datetime, timedelta
import subprocess
import os
import sys
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from datetime import datetime, timedelta 


# Patch sqlite3 for Chroma on Streamlit Cloud
try:
    import pysqlite3
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
except Exception as e:
    print("SQLite patching failed:", e)

from langchain_community.document_loaders import TextLoader, CSVLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools.retriever import create_retriever_tool
from langchain_experimental.tools.python.tool import PythonREPLTool
from langchain.tools import Tool

# ✅ Optional import of GoogleGenerativeAI
try:
    from langchain_google_genai import GoogleGenerativeAI
    HAS_GOOGLE_GENAI = True
except Exception:
    GoogleGenerativeAI = None
    HAS_GOOGLE_GENAI = False
    print("⚠️ Warning: langchain_google_genai not available; running in retrieval-only mode.")

# --- Secrets handler ---
load_dotenv()  # for local .env

def get_secret(key: str):
    """Check Streamlit secrets first (Cloud), else fallback to .env/env vars (local)."""
    try:
        if hasattr(st, "secrets") and key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.getenv(key)

GOOGLE_API_KEY = get_secret("GOOGLE_API_KEY")

# =========================
# 📂 Data file setup
# =========================
DATA_FILE = "grocer_ai_data_sample.csv" if os.path.exists("grocer_ai_data_sample.csv") else "grocer_ai_data.csv"
print("Using data file:", DATA_FILE)

today = datetime.now().date()

# Load dataset if exists
df = None
if os.path.exists(DATA_FILE):
    try:
        df = pd.read_csv(DATA_FILE, parse_dates=["date_time"])
        df["date"] = df["date_time"].dt.date
    except Exception as e:
        print("⚠️ Error loading dataset:", e)

# ✅ Always ensure today's data exists
need_generate = False
if df is None:
    need_generate = True
elif today not in df["date"].unique():
    need_generate = True

if need_generate:
    print("⚡ Generating fresh data for today...")
    subprocess.run(["python", "generate_data.py"])
    # Reload after generation
    df = pd.read_csv(DATA_FILE, parse_dates=["date_time"])
    df["date"] = df["date_time"].dt.date


# --- Initialize LLM ---
llm = None
if HAS_GOOGLE_GENAI and GOOGLE_API_KEY:
    llm = GoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=GOOGLE_API_KEY
    )
    print("✅ Google Generative AI initialized")
else:
    print("❌ No valid Google API key found — running in fallback mode")

# --- Vectorstore setup ---
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Transactions DB
csv_dir = "./grocer_ai_db_csv"
if not os.path.exists(csv_dir):
    print("⚡ Building CSV vector DB...")
    csv_loader = CSVLoader(file_path=DATA_FILE)
    csv_docs = csv_loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    csv_chunks = splitter.split_documents(csv_docs)
    csv_store = Chroma.from_documents(csv_chunks, embeddings, persist_directory=csv_dir)
    csv_store.persist()
else:
    print("✅ Loading existing CSV DB...")
    csv_store = Chroma(persist_directory=csv_dir, embedding_function=embeddings)

csv_retriever = csv_store.as_retriever(search_type="similarity", search_kwargs={"k": 5})

# Policies DB
policy_dir = "./grocer_ai_db_policies"
if not os.path.exists(policy_dir):
    print("⚡ Building Policies vector DB...")
    policy_loader = TextLoader("grocer_ai_policies.txt")
    policy_docs = policy_loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    policy_chunks = splitter.split_documents(policy_docs)
    policy_store = Chroma.from_documents(policy_chunks, embeddings, persist_directory=policy_dir)
    policy_store.persist()
else:
    print("✅ Loading existing Policies DB...")
    policy_store = Chroma(persist_directory=policy_dir, embedding_function=embeddings)

policy_retriever = policy_store.as_retriever(search_type="similarity", search_kwargs={"k": 5})

prompt = PromptTemplate.from_template("""
You are **Grocer-AI Assistant**, a helpful, friendly, and professional company AI.

You have access to the following tools:
{tools}

Tool names you can use: {tool_names}

Rules:
- If question is about **policies** → use GrocerAI_Policies.
- If about **sales, employees, transactions** → use GrocerAI_Transactions.
- If calculations needed → use Python_REPL.

Always answer like this:

📝 **Answer:** (clear explanation in plain English)  
📊 **Supporting Info:** (facts, numbers, or doc snippets if available)  

If you cannot find the answer, say:  
📝 **Answer:** I'm sorry, I could not find that policy in the available documents.  
📊 **Supporting Info:** Try asking about refunds, leave days, or employee performance.  

Format:
Question: {input}
Thought: reasoning
Action: the action to take (from [{tool_names}])
Action Input: the input
Observation: result
... (repeat as needed)
Thought: I now know the final answer
Final Answer: 📝 **Answer:** ...
📊 **Supporting Info:** ...
{agent_scratchpad}
""")


# --- Tools ---
python_repl = PythonREPLTool()
tools = [
    create_retriever_tool(
        csv_retriever,
        "GrocerAI_Transactions",
        "Use this tool for answering questions about sales, employees, transactions, or numbers."
    ),
    create_retriever_tool(
        policy_retriever,
        "GrocerAI_Policies",
        "Use this tool for answering questions about company policies, refunds, rules, and employee guidelines."
    ),
    Tool(
        name="Python_REPL",
        func=python_repl.run,
        description="Run Python code for calculations. Use print() to see results."
    ),
]

# --- Agent setup ---
agent_executor = None
if HAS_GOOGLE_GENAI and llm is not None:
    agent = create_react_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# ✅ Main function for Streamlit
from datetime import datetime, timedelta

def run_query(question: str):
    """
    Handle queries:
    - Policies → grocer_ai_policies.txt
    - Transactions → grocer_ai_data.csv
    - Direct sales questions (today, yesterday, last 7 days)
    """
    q_lower = question.lower()

    # --- Direct sales calculations ---
    if df is not None:
        df["date_time"] = pd.to_datetime(df["date_time"])
        df["date"] = df["date_time"].dt.date

        if "sales today" in q_lower or "today's sales" in q_lower:
            today = datetime.now().date()
            sales_today = df[df["date"] == today]["total_amount"].sum()
            return f"📝 **Answer:** Total sales today = ${sales_today:,.2f}", []

        if "sales yesterday" in q_lower or "yesterday's sales" in q_lower:
            yesterday = (datetime.now() - timedelta(days=1)).date()
            sales_yest = df[df["date"] == yesterday]["total_amount"].sum()
            return f"📝 **Answer:** Total sales yesterday = ${sales_yest:,.2f}", []

        if "last 7 days" in q_lower or "past week" in q_lower:
            start = datetime.now().date() - timedelta(days=7)
            sales_7d = df[df["date"] >= start]["total_amount"].sum()
            return f"📝 **Answer:** Total sales in last 7 days = ${sales_7d:,.2f}", []

    # --- Retriever route ---
    if any(word in q_lower for word in ["policy", "refund", "exchange", "leave", "guideline", "rule", "discount"]):
        docs = policy_retriever.get_relevant_documents(question)
        retriever_used = "GrocerAI_Policies"
    else:
        docs = csv_retriever.get_relevant_documents(question)
        retriever_used = "GrocerAI_Transactions"

    retrieved_docs = [getattr(d, "page_content", str(d)) for d in docs[:5]]

    # --- No LLM fallback ---
    if not HAS_GOOGLE_GENAI or agent_executor is None:
        if retrieved_docs:
            snippet = "\n\n---\n\n".join(retrieved_docs[:3])
            return f"(Fallback - {retriever_used})\n\n{snippet}", retrieved_docs
        return f"(Fallback) No documents found in {retriever_used}", []

    # --- Use LLM ---
    try:
        context = "\n\n".join(retrieved_docs)
        custom_prompt = f"""
You are Grocer-AI, an assistant for a retail company.

User Question: {question}

Relevant Context:
{context}

📝 Answer the user question using the context above. 
If the answer is not in the context, clearly say: "This information is not available in company data."
"""
        result = llm.invoke(custom_prompt)
        return result, retrieved_docs
    except Exception as e:
        if retrieved_docs:
            snippet = "\n\n---\n\n".join(retrieved_docs[:3])
            return f"(LLM error: {e})\n\nTop {retriever_used} docs:\n\n{snippet}", retrieved_docs
        return f"Agent error: {e}", []
