# app.py
import subprocess, os
from datetime import datetime
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from query_app import run_query

# ⚡ Auto-update dataset once per day
today_flag = "last_run.flag"
if not os.path.exists(today_flag) or open(today_flag).read().strip() != str(datetime.now().date()):
    subprocess.run(["python", "generate_data.py"])
    with open(today_flag, "w") as f:
        f.write(str(datetime.now().date()))

# --------------------
# Streamlit Setup
# --------------------
st.set_page_config(page_title="Grocer-AI Assistant", page_icon="🛒", layout="wide")

st.markdown(
    """
    # 🛒 Grocer-AI Data & Analytics Assistant  

    👋 Welcome! This AI assistant helps you explore **sales data, employees, and company policies**.  

    👉 Type your question below and press **Get Answer**.  
    👉 Use **Clear** to reset the chat.  

    ---
    """
)

# --------------------
# Q&A Section
# --------------------
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

# --------------------
# Load Data
# --------------------
st.markdown("## 📊 Daily Sales Dashboard")

try:
    df = pd.read_csv("grocer_ai_data.csv", parse_dates=["date_time"])
    df["date"] = pd.to_datetime(df["date_time"]).dt.date  # ensure clean date column

    # --------------------
    # Sidebar Filters
    # --------------------
    st.sidebar.header("🔎 Filters")

    start_date = st.sidebar.date_input("Start Date", df["date"].min())
    end_date = st.sidebar.date_input("End Date", df["date"].max())
    branch_options = ["All"] + sorted(df["branch_id"].unique().tolist())
    selected_branch = st.sidebar.selectbox("Select Branch", branch_options)
    search_product = st.sidebar.text_input("Search Product")

    # Apply filters
    filtered_df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]

    if selected_branch != "All":
        filtered_df = filtered_df[filtered_df["branch_id"] == selected_branch]

    if search_product:
        filtered_df = filtered_df[filtered_df["product_name"].str.contains(search_product, case=False, na=False)]

    # --------------------
    # Daily Metrics
    # --------------------
    today = datetime.now().date()
    today_df = filtered_df[filtered_df["date"] == today]

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

    # --------------------
    # Sales Trend (7 Days)
    # --------------------
    st.subheader("📈 Sales Trend (Last 7 Days)")

    last_7_days = filtered_df[filtered_df["date"] >= (filtered_df["date"].max() - pd.Timedelta(days=7))]
    sales_trend = last_7_days.groupby("date")["total_amount"].sum()

    fig, ax = plt.subplots()
    sales_trend.plot(kind="line", marker="o", ax=ax)
    ax.set_ylabel("Sales ($)")
    ax.set_xlabel("Date")
    ax.set_title("Total Sales in Last 7 Days")
    st.pyplot(fig)

    # --------------------
    # Top 5 Categories Today
    # --------------------
    st.subheader("📊 Top 5 Categories Today")

    today_data = filtered_df[filtered_df["date"] == today]
    if not today_data.empty:
        top_categories = today_data.groupby("product_category")["total_amount"].sum().sort_values(ascending=False).head(5)

        fig, ax = plt.subplots()
        top_categories.plot(kind="bar", ax=ax, color="skyblue")
        ax.set_ylabel("Sales ($)")
        ax.set_xlabel("Category")
        ax.set_title("Top 5 Product Categories Today")
        st.pyplot(fig)

except Exception as e:
    st.error(f"Dashboard error: {e}")
