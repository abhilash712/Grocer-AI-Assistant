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

from langchain_community.document_loaders import TextLoader
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

# Vectorstore setup with auto-build fallback
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
persist_dir = "./grocer_ai_db"

if not os.path.exists(persist_dir):
    print("⚡ Building vector DB from policies...")
    loader = TextLoader("grocer_ai_policies.txt")
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(docs)
    vectorstore = Chroma.from_documents(chunks, embeddings, persist_directory=persist_dir)
    vectorstore.persist()
else:
    print("✅ Loading existing vector DB...")
    vectorstore = Chroma(persist_directory=persist_dir, embedding_function=embeddings)

retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 10}  # fetch up to 10 most similar docs
)


# Prompt template (used only if LLM exists)
prompt = PromptTemplate.from_template("""
You are Grocer-AI Assistant. 
Always answer questions **only** using the provided tools and retrieved documents. 
If the answer is not in the documents, say "I could not find this in the policies."

You have access to the following tools:

{tools}

Use the following format:

Question: {input}
Thought: think about which tool to use
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}
""")


# Tools
python_repl = PythonREPLTool()
tools = [
    create_retriever_tool(
        retriever,
        "GrocerAI_data_retriever",
        "Use this to fetch company policies and rules."
    ),
    Tool(
        name="Python_REPL",
        func=python_repl.run,
        description="Run Python code for calculations. Use print() to see results."
    ),
]

# Agent setup (only if LLM is available)
agent_executor = None
if HAS_GOOGLE_GENAI and llm is not None:
    agent = create_react_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# ✅ Main function for Streamlit
def run_query(question: str):
    """
    Returns (answer_text, [retrieved_doc_snippets]).
    If Gemini/GG is unavailable or answer is unclear, shows top retrieved docs.
    """
    # Always try retrieval first
    try:
        docs = retriever.get_relevant_documents(question)
        retrieved_docs = [getattr(d, "page_content", str(d)) for d in docs[:5]]
    except Exception as e:
        return f"Error accessing retriever: {e}", []

    # If no LLM → fallback to docs
    if not HAS_GOOGLE_GENAI or agent_executor is None:
        if retrieved_docs:
            snippet = "\n\n---\n\n".join(retrieved_docs[:3])
            return f"(Fallback) LLM not available. Top retrieved documents:\n\n{snippet}", retrieved_docs
        else:
            return "(Fallback) No LLM and no docs found.", []

    # If LLM is available → use agent
    try:
        result = agent_executor.invoke({"input": question})
        answer = result.get("output") or ""
        # 🔑 Fallback if LLM answer is empty/unhelpful
        if not answer.strip() and retrieved_docs:
            snippet = "\n\n---\n\n".join(retrieved_docs[:3])
            return f"(LLM gave no clear answer, showing retrieved docs instead):\n\n{snippet}", retrieved_docs
        return answer, retrieved_docs
    except Exception as e:
        # On error, still fallback to docs
        if retrieved_docs:
            snippet = "\n\n---\n\n".join(retrieved_docs[:3])
            return f"(LLM error: {e})\n\nTop retrieved docs:\n\n{snippet}", retrieved_docs
        return f"Agent error: {e}", []
