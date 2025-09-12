import pandas as pd
from langchain.tools.retriever import create_retriever_tool
from langchain.agents import create_tool_calling_agent
from langchain_core.prompts import PromptTemplate
from langchain_community.llms import OpenAI
from langchain_community.utilities import PythonREPL

# Load the dataframe we created earlier
df = pd.read_csv("grocer_ai_data.csv")

# Initialize the Python REPL tool
python_repl = PythonREPL()

# Create a tool that the agent can use to run Python code
data_analytics_tool = python_repl