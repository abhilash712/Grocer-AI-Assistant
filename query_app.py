import pandas as pd
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools.retriever import create_retriever_tool
from langchain_experimental.tools.python.tool import PythonREPLTool
from langchain.tools import Tool
from langchain_experimental.utilities import PythonREPL
from langchain.chains import LLMMathChain

# Load the dataframe we created earlier
df = pd.read_csv("grocer_ai_data.csv")

# Initialize a Python REPL tool
python_repl = PythonREPLTool()

# Set up the LLM and the prompt.
print("Setting up the Language Model...")
llm = GoogleGenerativeAI(model="gemini-1.5-flash", google_api_key="AIzaSyBtOUH0n7G4Ax5lrlZkWVkJxjHZPukExhk")

# This is the corrected prompt template that includes all required variables for the agent
prompt = PromptTemplate.from_template("""
Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}""")
    

# Load the vector database.
print("Loading vector database...")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore = Chroma(persist_directory="./grocer_ai_db", embedding_function=embeddings)
retriever = vectorstore.as_retriever()

# Create the tools for the agent.
tools = [
    create_retriever_tool(
        retriever,
        "GrocerAI_data_retriever",
        "A tool for retrieving information from the Grocer-AI policy documents. Use this when a question is about company policy or rules.",
    ),
    Tool(
        name="Python_REPL",
        func=python_repl.run,
        description="A Python shell. Use this to execute Python commands. Input should be a valid Python command. If you want to see the output of a value, you should print it out with `print( )`."
    ),
]

# Create the agent.
agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Run the query.
print("Running a query...")
# Ask a more specific question that is in the policy document
query = "What is the average sales performance score for our employees?"

result = agent_executor.invoke({"input": query})

print("\n--- Answer ---")
print(result['output'])



# Import all the necessary libraries for our RAG and agent system.
from langchain_community.vectorstores import Chroma

# --- Phase 3: The Query System ---
# Load the vector database we created earlier.
print("Loading vector database...")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore = Chroma(persist_directory="./grocer_ai_db", embedding_function=embeddings)

# Create a Python tool that the agent can use to perform data analysis.
python_repl = PythonREPLTool()