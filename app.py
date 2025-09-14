# app.py
import subprocess, os
from datetime import datetime

# ⚡ Auto-update dataset once per day
today_flag = "last_run.flag"
if not os.path.exists(today_flag) or open(today_flag).read().strip() != str(datetime.now().date()):
    subprocess.run(["python", "generate_data.py"])
    with open(today_flag, "w") as f:
        f.write(str(datetime.now().date()))



import streamlit as st
from query_app import run_query

st.set_page_config(page_title="Grocer-AI Assistant", page_icon="🛒", layout="centered")


st.markdown(
    """
    # 🛒 Grocer-AI Data & Analytics Assistant  

    👋 Welcome! This AI assistant helps you explore **sales data, employees, and company policies**.  

    👉 Type your question below and press **Get Answer**.  
    👉 Use **Clear** to reset the chat.  

    ---
    """
)
# Input box & history
if "history" not in st.session_state:
    st.session_state.history = []

user_question = st.text_input("Type your question here:", key="question_input")

col1, col2 = st.columns([1, 1])
with col1:
    submit = st.button("Get Answer")
with col2:
    clear = st.button("Clear")

if clear:
    st.session_state.history = []
    st.experimental_rerun()

if submit:
    if not user_question.strip():
        st.warning("⚠️ Please enter a question before submitting.")
    else:
        with st.spinner("Thinking... 🤔"):
            answer, retrieved_docs = run_query(user_question)

        # Save to history
        st.session_state.history.append({"q": user_question, "a": answer, "docs": retrieved_docs})

# Show history (latest first)
if st.session_state.history:
    st.markdown("---")
    st.subheader("Conversation history")
    for item in reversed(st.session_state.history[-10:]):  # show last 10
        st.markdown(f"**Q:** {item['q']}")
        st.markdown(f"**A:** {item['a']}")
        if item.get("docs"):
            st.markdown("**Retrieved docs (top 3):**")
            for d in item["docs"][:3]:
                st.markdown(f"- {d}")
        st.markdown("---")

import pandas as pd
from datetime import datetime

st.markdown("## 📊 Daily Sales Dashboard")

try:
    df = pd.read_csv("grocer_ai_data.csv", parse_dates=["date_time"])

    today = datetime.now().date()
    today_df = df[df["date_time"].dt.date == today]

    if not today_df.empty:
        total_txns = len(today_df)
        total_sales = today_df["total_amount"].sum()

        st.metric("🛒 Total Transactions Today", total_txns)
        st.metric("💰 Total Sales Today", f"${total_sales:,.2f}")

        st.markdown("### 🏆 Top 5 Products Today")
        top_products = today_df.groupby("product_name")["quantity"].sum().nlargest(5)
        for prod, qty in top_products.items():
            st.write(f"- {prod}: {qty} sold")

        st.markdown("### 👥 New Employees This Month")
        this_month = datetime.now().month
        new_emps = df[pd.to_datetime(df["date_of_joining"]).dt.month == this_month]["employee_name"].unique()
        if len(new_emps) > 0:
            st.write(", ".join(new_emps))
        else:
            st.write("No new employees this month.")

    else:
        st.info("No transactions recorded for today yet.")

except Exception as e:
    st.error(f"Dashboard error: {e}")
