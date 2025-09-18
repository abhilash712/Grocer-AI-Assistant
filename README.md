# 🛒 Grocer-AI Data & Analytics Assistant  

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red?logo=streamlit)
![LangChain](https://img.shields.io/badge/LangChain-AI-orange?logo=ai)
![Prophet](https://img.shields.io/badge/Forecasting-Prophet-green)

This project simulates a **grocery retail environment** and builds an **AI-powered data analytics and policy assistant**.  
It integrates **synthetic data generation**, **retrieval-augmented generation (RAG)**, **predictive forecasting**, and an **interactive web app** built with Streamlit.  

👉 **Live App:** [Grocer-AI Assistant](https://grocer-ai-assistant-qzcyuuprgu9pplownbsnsm.streamlit.app)  

---

## 📂 Project Structure
├── generate_data.py # Generates synthetic grocery data
├── grocer_ai_policies.txt # Company policies handbook
├── rag_pipeline.py # RAG pipeline: ingestion, embeddings, ChromaDB
├── data_analytics_tool.py # LangChain Python REPL analytics tool
├── query_app.py # Agent + tools (backend logic)
├── app.py # Streamlit app (frontend UI)
├── requirements.txt # Python dependencies
├── send_email.py # Automated daily email reports
├── .github/workflows # GitHub Actions for automation
├── .gitignore # Ignore local files (CSV, venv, etc.)
└── README.md # Project documentation

---

## 🚀 Features
- **Synthetic Dataset (50k+ transactions)**  
  Branches, employees, products, sales, customer feedback.  

- **Company Policies Assistant**  
  Employee performance, leave rules, refund policies, customer service guidelines.  

- **RAG Pipeline (LangChain)**  
  Combines structured CSV data + unstructured text policies.  
  Embeddings with `sentence-transformers` stored in **ChromaDB**.  

- **Interactive AI Assistant**  
  Natural language queries about sales, employees, or policies.  
  Powered by LangChain ReAct + Python REPL.  

- **📊 Analytics Dashboard**  
  Sales KPIs, product trends, top categories, new hires.  

- **🔮 Predictive Analysis (Prophet)**  
  Sales forecasting (overall, category-wise, branch-wise).  

- **📧 Automation**  
  GitHub Actions workflow sends **daily sales summary via email**.  

---

## ⚙️ Setup Instructions
Clone the repository:
```bash
git clone https://github.com/abhilash712/Grocer-AI-Assistant.git
cd Grocer-AI-Assistant

pip install -r requirements.txt

streamlit run app.py

🛠 Tech Stack

Python

Streamlit – UI

LangChain – RAG + LLM agent

ChromaDB – Vector storage

Prophet – Forecasting

GitHub Actions – Automation (daily reports)

🚀 Live Demo

👉 Try it here: Grocer-AI Assistant (Streamlit)

👨‍💻 Author

Abhilash V
📍 Aspiring Data Scientist | Passionate about AI & Analytics


⭐ Contribute

If you like this project, please ⭐ star the repo and share it!
Pull requests and suggestions are welcome.
