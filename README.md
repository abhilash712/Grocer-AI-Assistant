# 🛒 Grocer-AI Data & Analytics Assistant

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/streamlit-cloud-red.svg)](https://streamlit.io/)
[![LangChain](https://img.shields.io/badge/LangChain-RAG-green.svg)](https://www.langchain.com/)

This project simulates a **grocery retail environment** and builds an **AI-powered data analytics and policy assistant**.  
It includes **synthetic data generation**, a **retrieval-augmented generation (RAG) pipeline**, and an **interactive web app** built with **Streamlit**.

---

## 📂 Project Structure
├── generate_data.py # Generates synthetic grocery data
├── grocer_ai_policies.txt # Company policies handbook
├── rag_pipeline.py # RAG pipeline: ingestion, embeddings, ChromaDB
├── data_analytics_tool.py # LangChain Python REPL analytics tool
├── query_app.py # Agent + tools (backend logic)
├── app.py # Streamlit app (frontend UI)
├── requirements.txt # Python dependencies
├── .gitignore # Ignore local files (CSV, venv, etc.)
└── README.md # Project documentation


## 🚀 Features
- **Synthetic Dataset (50k+ transactions)**  
  - Branches, employees, products, sales, customer feedback.
- **Company Policies**  
  - Employee performance, leave rules, customer service guidelines.
- **RAG Pipeline**  
  - Combines structured (CSV) + unstructured (text).  
  - Embeddings with `sentence-transformers` + storage in **ChromaDB**.
- **Interactive Assistant**  
  - LangChain-powered agent to query data and policies.  
  - Streamlit UI for natural language Q&A.

---
## ⚙️ Setup Instructions
```bash
git clone https://github.com/abhilash712/Grocer-AI-Assistant.git
cd grocer-ai-assistant
pip install -r requirements.txt
streamlit run app.py
```

## 🚀 Live Demo
👉 [Try the Grocer-AI Assistant](https://grocer-ai-assistant-qzcyuuprgu9pplownbsnsm.streamlit.app)


