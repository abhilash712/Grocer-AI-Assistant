🛒 Grocer-AI Data & Analytics Assistant

An AI-powered data analytics assistant for the retail/grocery sector.

🤖 Natural language Q&A about sales, employees, policies

📊 Interactive dashboards for analytics

🔮 Sales forecasting with Prophet

📧 Automated daily reports via email + GitHub Actions

📂 Project Structure
├── app.py                 # Streamlit app (frontend UI)
├── query_app.py           # Backend: AI agent, retrievers, tools
├── generate_data.py       # Synthetic grocery dataset generator
├── grocer_ai_policies.txt # Company policies handbook
├── rag_pipeline.py        # RAG pipeline (embeddings + ChromaDB)
├── data_analytics_tool.py # LangChain Python REPL analytics
├── send_email.py          # Email automation (daily sales report)
├── requirements.txt       # Python dependencies
├── .github/workflows      # GitHub Actions CI/CD
├── .gitignore             # Ignore local files/venv
└── README.md              # Project documentation

🚀 Features
🛒 Synthetic Dataset (50k+ transactions)

Multiple branches, employees, products, categories

Includes customer feedback, referrals, hiring events

🧑‍💼 Company Policies Assistant

Refund rules, leave policies, employee performance

Powered by RAG (LangChain + ChromaDB)

🤖 AI Assistant

ReAct agent with:

GrocerAI_Transactions retriever

GrocerAI_Policies retriever

Python REPL tool

📊 Daily Dashboard

Sales KPIs, filters, top products & categories

New hires and performance tracking

🔮 Forecasting (Prophet)

7-day forecasts overall, by category, by branch

📧 Automation

Daily synthetic data generation

Automated email reports with GitHub Actions
