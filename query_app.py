# Patch sqlite3 for Chroma on Streamlit Cloud
try:
    import pysqlite3
    import sys
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
except Exception as e:
    print("SQLite patching failed:", e)

import os
import pandas as pd
from dotenv import load_dotenv

from langchain_community.document_loaders import TextLoader, CSVLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools.retriever import create_retriever_tool
from langchain_experimental.tools.python.tool import PythonREPLTool
from langchain.tools import Tool

# ✅ optional import of GoogleGenerativeAI
try:
    from langchain_google_genai import GoogleGenerativeAI
    HAS_GOOGLE_GENAI = True
except Exception:
    GoogleGenerativeAI = None
    HAS_GOOGLE_GENAI = False
    print("⚠️ Warning: langchain_google_genai not available; running in retrieval-only mode.")

# Load API key
load_dotenv()

# Optional: load dataset (for local analytics, not mandatory in Streamlit)
try:
    df = pd.read_csv("grocer_ai_data.csv")
except FileNotFoundError:
    df = None

# Initialize LLM if available
llm = None
if HAS_GOOGLE_GENAI:
    llm = GoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )

# --- Vectorstore setup ---
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Transactions DB
csv_dir = "./grocer_ai_db_csv"
if not os.path.exists(csv_dir):
    print("⚡ Building CSV vector DB...")
    csv_loader = CSVLoader(file_path="grocer_ai_data.csv")
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
You are Grocer-AI, an intelligent assistant for a grocery retail company.

Available tools:
{tools}

IMPORTANT:
- If the question is about **refunds, leave days, employee rules, or policies** → use **GrocerAI_Policies**.
- If the question is about **sales, employees, numbers, transactions** → use **GrocerAI_Transactions**.
- If calculations are required, use **Python_REPL**.

Answer format:
Question: {input}
Thought: Reason about which tool is needed
Action: Choose one tool from [{tool_names}]
Action Input: The exact input
Observation: The tool output
... (repeat if needed)
Thought: I now know the final answer
Final Answer: 📝 **Answer:** (clear, friendly explanation)

{agent_scratchpad}
""")


# --- Tools ---
# Tools setup
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

def run_query(question: str):
    """
    Routes questions to the right retriever (Policies vs Transactions).
    Returns (answer_text, [retrieved_doc_snippets]).
    """

    # --- Routing logic ---
    policy_keywords = ["policy", "refund", "leave", "rules", "guidelines", "conduct"]
    use_policy = any(kw in question.lower() for kw in policy_keywords)

    retriever_to_use = policy_retriever if use_policy else csv_retriever

    # --- Get documents ---
    try:
        docs = retriever_to_use.get_relevant_documents(question)
        retrieved_docs = [getattr(d, "page_content", str(d)) for d in docs[:5]]
    except Exception as e:
        return f"Error accessing retriever: {e}", []

    # --- Fallback mode ---
    if not HAS_GOOGLE_GENAI or agent_executor is None:
        if docs:
            snippet = "\n\n---\n\n".join(retrieved_docs[:3])
            return f"(Fallback: LLM not available)\n\n{snippet}", retrieved_docs
        return "(Fallback: No docs found)", []

    # --- Agent mode ---
    try:
        result = agent_executor.invoke({"input": question})
        answer = result.get("output") or ""
        if not answer.strip() and docs:
            snippet = "\n\n---\n\n".join(retrieved_docs[:3])
            return f"(LLM gave no clear answer, showing docs instead):\n\n{snippet}", retrieved_docs
        return answer, retrieved_docs
    except Exception as e:
        if docs:
            snippet = "\n\n---\n\n".join(retrieved_docs[:3])
            return f"(LLM error: {e})\n\nDocs:\n\n{snippet}", retrieved_docs
        return f"Agent error: {e}", []

 