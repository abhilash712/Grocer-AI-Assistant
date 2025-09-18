from langchain_community.document_loaders import CSVLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

print("📂 Loading data...")

# Load CSV
csv_loader = CSVLoader(file_path="grocer_ai_data_sample.csv")
csv_docs = csv_loader.load()
print(f"✅ Loaded {len(csv_docs)} CSV docs")

# Load policies
policy_loader = TextLoader(file_path="grocer_ai_policies.txt")
policy_docs = policy_loader.load()
print(f"✅ Loaded {len(policy_docs)} policy docs")

# Debug: show sample policy text
if policy_docs:
    print("📑 Sample policy doc:\n", policy_docs[0].page_content[:300])
else:
    raise FileNotFoundError("❌ No policy docs found! Check grocer_ai_policies.txt")

# Combine CSV + Policies
all_docs = csv_docs + policy_docs
print(f"📊 Total docs combined: {len(all_docs)}")

# Split into chunks
print("✂️ Splitting documents into chunks...")
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)
chunks = text_splitter.split_documents(all_docs)
print(f"✅ Total chunks created: {len(chunks)}")

# Create embeddings
print("🔎 Creating embedding model...")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Save into Chroma DB
print("💾 Creating vector store...")
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,   # ✅ works with your version
    persist_directory="./grocer_ai_db"
)


print("🎉 Vector store creation complete!")

# Test query
print("\n🔍 Test search for 'refund policy':")
docs = vectorstore.similarity_search("refund policy", k=2)
for i, d in enumerate(docs, 1):
    print(f"\n--- Doc {i} ---\n{d.page_content[:400]}")
