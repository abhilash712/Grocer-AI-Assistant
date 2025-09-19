🛒 Grocer-AI Data & Analytics Assistant








An AI-powered data analytics assistant for the retail/grocery sector.
This project simulates real-world sales + policy data and enables:

Natural language Q&A about transactions, employees, and policies.

Interactive dashboards for sales analysis.

Forecasting future sales trends with Prophet.

Automated daily reports via email + GitHub Actions.

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

Multiple branches, employees, products, categories.

Includes customer feedback, referrals, hiring events.

🧑‍💼 Company Policies Assistant

Answers questions on refund rules, leave policies, employee performance.

Uses RAG (Retrieval Augmented Generation) for contextual answers.

🤖 AI Assistant (LangChain)

Supports natural language queries.

ReAct Agent with:

GrocerAI_Transactions retriever

GrocerAI_Policies retriever

Python REPL tool (for calculations).

📊 Analytics Dashboard (Streamlit)

Daily metrics (transactions, sales).

Filters by date, branch, category, product.

Top products & categories, new hires.

🔮 Forecasting (Prophet)

Overall sales forecast (7 days).

Category-wise & branch-wise forecasts.

📧 Automation (GitHub Actions + SMTP)

Auto-generates daily transactions.

Sends email reports to stakeholders.

⚙️ Setup Instructions

Clone the repository:

git clone https://github.com/abhilash712/Grocer-AI-Assistant.git
cd Grocer-AI-Assistant


Install dependencies:

pip install -r requirements.txt


Run locally:

streamlit run app.py


Secrets (create .env or add in .streamlit/secrets.toml):

GOOGLE_API_KEY = "your_api_key_here"

# Gmail SMTP (for email automation)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "your_email@gmail.com"
SMTP_PASS = "your_app_password"
EMAIL_FROM = "your_email@gmail.com"
EMAIL_TO = "recipient1@gmail.com,recipient2@gmail.com"

📸 Screenshots
🔹 AI Assistant

Ask about policies, employees, or sales:
(screenshot here)

🔹 Daily Dashboard

Track sales, products, and categories:
(screenshot here)

🔹 Forecasts

See 7-day predictions by category/branch:
(screenshot here)

🛠 Tech Stack

Python 3.10+

Streamlit → Interactive web UI

LangChain → RAG + LLM agent

ChromaDB → Vector database

Prophet → Time-series forecasting

GitHub Actions → Automation (daily updates + reports)

👨‍💻 Author

Abhilash V
📍 Aspiring Data Scientist | Passionate about AI & Analytics

🔗 LinkedIn
 • GitHub

⭐ Contribute

If you like this project, please ⭐ the repo!
Contributions (issues, PRs) are always welcome.
