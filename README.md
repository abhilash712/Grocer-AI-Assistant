# 🛒 Grocer-AI Data & Analytics Assistant

This project simulates a **grocery retail environment** and builds an **AI-powered data analytics and policy assistant**.  
It includes **synthetic data generation**, a **retrieval-augmented generation (RAG) pipeline**, and an **interactive data analysis tool**.

---

## 📂 Project Structure
├── generate_data.py # Generates synthetic grocery data
├── grocer_ai_policies.txt # Company policies handbook
├── rag_pipeline.py # RAG pipeline: ingestion, embeddings, ChromaDB
├── data_analytics_tool.py # LangChain Python REPL analytics tool
├── requirements.txt # Python dependencies
├── .gitignore # Ignore local files (CSV, venv, etc.)
└── README.md # Project documentation


---

## 🚀 Features
- **Synthetic Dataset (50k+ transactions)**  
  - Branches, employees, products, sales, customer feedback.
- **Company Policies**  
  - Employee performance, leave rules, customer service guidelines.
- **RAG Pipeline**  
  - Combines structured (CSV) + unstructured (text).  
  - Embeddings with `sentence-transformers` + storage in **ChromaDB**.
- **Analytics Tool**  
  - LangChain-powered Python REPL agent to query the dataset.

---

## ⚙️ Setup Instructions

### 1. Clone Repository
```bash
git clone https://github.com/your-username/grocer-ai-assistant.git
cd grocer-ai-assistant
