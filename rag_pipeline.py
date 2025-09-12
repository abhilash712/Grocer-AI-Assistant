from langchain_community.document_loaders import CSVLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# --- Phase 2: Data Ingestion and Chunking ---
# Step 1: Load the CSV and text files.
print("Loading data...")
csv_loader = CSVLoader(file_path="grocer_ai_data.csv")
csv_docs = csv_loader.load()

text_loader = TextLoader(file_path="grocer_ai_policies.txt")
policy_docs = text_loader.load()

# Step 2: Combine all documents into a single list.
all_docs = csv_docs + policy_docs

# Step 3: Split the combined documents into smaller chunks.
print("Splitting documents into chunks...")
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)
chunks = text_splitter.split_documents(all_docs)

# --- Phase 2: Embedding and Vector Store ---
# Step 4: Create a local embedding model.
# This model converts text into numerical vectors.
# The first time you run this, it will download the model.
print("Creating embedding model...")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Step 5: Create a vector store from our chunks.
# This will save your vectors to a new folder called "grocer_ai_db".
print("Creating vector store...")
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./grocer_ai_db"
)

print("Vector store creation complete!")