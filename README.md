# 🛒 Grocer-AI Data & Analytics Assistant

[![Streamlit](https://img.shields.io/badge/Built%20With-Streamlit-orange?logo=streamlit)](https://streamlit.io/)
[![LangChain](https://img.shields.io/badge/AI-LangChain-blue?logo=python)](https://langchain.com/)
[![Prophet](https://img.shields.io/badge/Forecasting-Prophet-brightgreen)](https://facebook.github.io/prophet/)
[![GitHub Actions](https://img.shields.io/github/workflow-status/abhilash712/Grocer-AI-Assistant/CI)](https://github.com/abhilash712/Grocer-AI-Assistant/actions)

---

## 🌟 Overview

**Grocer-AI Data & Analytics Assistant** is a full-stack, AI-powered assistant built for the retail and grocery industry.  
It enables natural language Q&A, data analytics, sales forecasting, and automated daily reports—streamlining decision-making for managers and analysts.

---

## 🚀 Why Use This Project?

- **End-to-end solution:** From synthetic data generation to interactive dashboards and email automation.
- **Real business value:** Focused on retail/grocery analytics, policies, and employee management.
- **Modern AI stack:** Utilizes Streamlit, LangChain (RAG), Prophet, ChromaDB, and GitHub Actions.
- **Great for demos & interviews:** Showcases data science, ML, analytics engineering, and automation skills.

---

## 🏗️ Project Structure

```
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
```

---

## ✨ Features

### 🛒 Synthetic Dataset
- 50k+ transactions with multiple branches, employees, and products
- Includes customer feedback, referrals, hiring events

### 🧑‍💼 Company Policies Q&A (RAG)
- Ask about refund, leave, performance policies
- Powered by LangChain + ChromaDB (Retrieval Augmented Generation)

### 🤖 AI Assistant
- ReAct agent with:
  - **GrocerAI_Transactions retriever**
  - **GrocerAI_Policies retriever**
  - **Python REPL analytics tool**

### 📊 Interactive Dashboards
- Sales KPIs, filters, top products & categories
- New hires and performance tracking

### 🔮 Sales Forecasting
- 7-day forecasts (overall, by category, by branch) using Prophet

### 📧 Automation & Reporting
- Daily synthetic data generation
- Automated daily email reports (GitHub Actions)

---


## 🖥️ Demo

[Watch Demo Video (Google Drive)](https://drive.google.com/file/d/165ZywUCgcoZD4babfqeTqsqn2DV64Mvq/view?usp=drive_link)

---

## 🚦 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/abhilash712/Grocer-AI-Assistant.git
cd Grocer-AI-Assistant
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Generate Synthetic Data

```bash
python generate_data.py
```

### 4. Run the App

```bash
streamlit run app.py
```

---

## 📁 Customization

- **Policies:** Edit `grocer_ai_policies.txt` to update company rules.
- **GitHub Actions:** Modify workflows in `.github/workflows` for automation customizations.
- **Email Reports:** Configure recipients and SMTP in `send_email.py`.

---

## 🛠️ Technologies Used

- **Streamlit:** Interactive UI
- **LangChain + ChromaDB:** Retrieval-Augmented Generation
- **Prophet:** Time series forecasting
- **GitHub Actions:** CI/CD and automation

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for more information.

---

## 🙌 Acknowledgements

- [Streamlit](https://streamlit.io/)
- [LangChain](https://www.langchain.com/)
- [Prophet](https://facebook.github.io/prophet/)
- [ChromaDB](https://www.trychroma.com/)

---

> **Created by [Abhilash](https://github.com/abhilash712)**
