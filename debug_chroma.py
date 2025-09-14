from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
db = Chroma(persist_directory="./grocer_ai_db", embedding_function=embeddings)

query = "refund policy"
docs = db.similarity_search(query, k=3)

print("🔍 Retrieved documents:")
for i, d in enumerate(docs, 1):
    print(f"\n--- Doc {i} ---\n")
    print(d.page_content[:400])  # print first 400 characters
