# =========================
# app.py (Edited)
# =========================

import os
import subprocess
from datetime import datetime
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from prophet import Prophet

# Import your query handler (AI Assistant logic)
from query_app import run_query

# =========================
# 🔑 Secrets / API keys
# =========================
# Helper: get from st.secrets if available, else fallback to env vars (for local dev)
def get_secret(key):
    return st.secrets.get(key) if key in st.secrets else os.getenv(key)

# Example usage (if needed in app.py or inside query_app.py)
GOOGLE_API_KEY = get_secret("GOOGLE_API_KEY")
OPENAI_API_KEY = get_secret("OPENAI_API_KEY")

# Debug: check if key is loaded (remove in production)
# st.write("API key loaded:", bool(GOOGLE_API_KEY or OPENAI_API_KEY))

# =========================
# 📂 Data file setup
# =========================
DATA_FILE = "grocer_ai_data_sample.csv" if os.path.exists("grocer_ai_data_sample.csv") else "grocer_ai_data.csv"
print("Using data file:", DATA_FILE)

# ⚡ Auto-update dataset once per day
today_flag = "last_run.flag"
if not os.path.exists(today_flag) or open(today_flag).read().strip() != str(datetime.now().date()):
    subprocess.run(["python", "generate_data.py"])
    with open(today_flag, "w") as f:
        f.write(str(datetime.now().date()))

# =========================
# --- Streamlit Config ---
# =========================
st.set_page_config(page_title="Grocer-AI Assistant", page_icon="🛒", layout="wide")

# =========================
# --- Sidebar Navigation ---
# =========================
st.sidebar.title("📊 Navigation")
page = st.sidebar.radio("Go to", ["🤖 AI Assistant", "📊 Daily Dashboard", "🔮 Forecasts"])

# =========================
# 🤖 AI Assistant Page
# =========================
if page == "🤖 AI Assistant":
    st.markdown("## 🤖 Grocer-AI Assistant")
    st.markdown("Ask me about **sales, employees, or company policies**!")

    if "history" not in st.session_state:
        st.session_state.history = []

    user_question = st.text_input("Type your question here:", key="ai_question_input")

    col1, col2 = st.columns([1, 1])
    with col1:
        submit = st.button("Get Answer", key="ai_submit")
    with col2:
        clear = st.button("Clear", key="ai_clear")

    if clear:
        st.session_state.history = []
        st.experimental_rerun()

    if submit:
        if not user_question.strip():
            st.warning("⚠️ Please enter a question before submitting.")
        else:
            with st.spinner("Thinking... 🤔"):
                try:
                    # Pass user_question to query_app (which should use GOOGLE_API_KEY inside)
                    answer, retrieved_docs = run_query(user_question)
                    st.session_state.history.append({"q": user_question, "a": answer, "docs": retrieved_docs})
                except Exception as e:
                    st.error(f"❌ AI Assistant error: {e}")

    if st.session_state.history:
        st.markdown("---")
        st.subheader("Conversation history")
        for item in reversed(st.session_state.history[-10:]):
            st.markdown(f"**Q:** {item['q']}")
            st.markdown(f"**A:** {item['a']}")
            if item.get("docs"):
                st.markdown("**Retrieved docs (top 3):**")
                for d in item["docs"][:3]:
                    st.markdown(f"- {d}")
            st.markdown("---")

# =========================
# 📊 Daily Dashboard Page
# =========================
elif page == "📊 Daily Dashboard":
    st.title("📊 Daily Sales Dashboard")

    try:
        df = pd.read_csv(DATA_FILE, parse_dates=["date_time"])
        df["date"] = pd.to_datetime(df["date_time"]).dt.date

        # --- Sidebar filters (PowerBI-like) ---
        st.sidebar.header("🔎 Filters")

        start_date = st.sidebar.date_input("Start Date", df["date"].min(), key="sid_start")
        end_date = st.sidebar.date_input("End Date", df["date"].max(), key="sid_end")

        branches_all = sorted(df["branch_id"].unique().tolist())
        selected_branches = st.sidebar.multiselect(
            "Branches (multi)", branches_all, default=branches_all, key="sid_branches"
        )

        categories_all = sorted(df["product_category"].unique().tolist())
        selected_categories = st.sidebar.multiselect(
            "Categories (multi)", categories_all, default=categories_all, key="sid_categories"
        )

        search_product = st.sidebar.text_input("Search Product", key="sid_product_search")

        # Apply filters
        filtered_df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]

        if selected_branches:
            filtered_df = filtered_df[filtered_df["branch_id"].isin(selected_branches)]

        if selected_categories:
            filtered_df = filtered_df[filtered_df["product_category"].isin(selected_categories)]

        if search_product:
            filtered_df = filtered_df[
                filtered_df["product_name"].str.contains(search_product, case=False, na=False)
            ]

        # --- Daily metrics ---
        today = datetime.now().date()
        today_df = filtered_df[filtered_df["date"] == today]

        if not today_df.empty:
            st.metric("🛒 Total Transactions Today", len(today_df))
            st.metric("💰 Total Sales Today", f"${today_df['total_amount'].sum():,.2f}")

            st.markdown("### 🏆 Top 5 Products Today")
            top_products = today_df.groupby("product_name")["quantity"].sum().nlargest(5)
            for prod, qty in top_products.items():
                st.write(f"- {prod}: {qty} sold")

            st.markdown("### 👥 New Employees This Month")
            this_month = datetime.now().month
            new_emps = df[pd.to_datetime(df["date_of_joining"]).dt.month == this_month]["employee_name"].unique()
            st.write(", ".join(new_emps) if len(new_emps) > 0 else "No new employees this month.")
        else:
            st.info("No transactions recorded for today yet.")

        # --- Sales trend (7 days) ---
        st.subheader("📈 Sales Trend (Last 7 Days)")
        last_7_days = filtered_df[filtered_df["date"] >= (filtered_df["date"].max() - pd.Timedelta(days=7))]
        sales_trend = last_7_days.groupby("date")["total_amount"].sum()
        fig, ax = plt.subplots()
        sales_trend.plot(kind="line", marker="o", ax=ax)
        ax.set_ylabel("Sales ($)")
        ax.set_title("Total Sales in Last 7 Days")
        st.pyplot(fig)

        # --- Top categories today ---
        st.subheader("📊 Top 5 Categories Today")
        today_data = filtered_df[filtered_df["date"] == today]
        if not today_data.empty:
            top_categories = today_data.groupby("product_category")["total_amount"].sum().nlargest(5)
            fig, ax = plt.subplots()
            top_categories.plot(kind="bar", ax=ax, color="skyblue")
            ax.set_ylabel("Sales ($)")
            ax.set_title("Top 5 Product Categories Today")
            st.pyplot(fig)

    except Exception as e:
        st.error(f"Dashboard error: {e}")

# =========================
# 🔮 Forecasts Page
# =========================
elif page == "🔮 Forecasts":
    st.title("🔮 Sales Forecasts")

    try:
        df = pd.read_csv(DATA_FILE, parse_dates=["date_time"])
        df["date"] = pd.to_datetime(df["date_time"]).dt.date

        # --- Overall Forecast ---
        st.subheader("📈 Overall Sales Forecast (Next 7 Days)")
        daily_sales = df.groupby("date")["total_amount"].sum().reset_index()
        daily_sales.columns = ["ds", "y"]

        if len(daily_sales) > 10:
            model = Prophet(daily_seasonality=True)
            model.fit(daily_sales)
            future = model.make_future_dataframe(periods=7)
            forecast = model.predict(future)
            st.pyplot(model.plot(forecast))
            st.pyplot(model.plot_components(forecast))

        # --- Category-wise Forecast ---
        st.subheader("📊 Category-wise Sales Forecast")
        categories = df["product_category"].unique().tolist()
        selected_category = st.selectbox("Select a category:", categories, key="forecast_cat")

        cat_sales = df[df["product_category"] == selected_category]
        daily_cat_sales = cat_sales.groupby("date")["total_amount"].sum().reset_index()
        daily_cat_sales.columns = ["ds", "y"]

        if len(daily_cat_sales) > 10:
            model_cat = Prophet(daily_seasonality=True)
            model_cat.fit(daily_cat_sales)
            forecast_cat = model_cat.predict(model_cat.make_future_dataframe(periods=7))
            st.pyplot(model_cat.plot(forecast_cat))
            st.success(f"✅ Forecast for **{selected_category}** (next 7 days).")
        else:
            st.warning("⚠️ Not enough data to forecast.")

        # --- Branch-wise Forecast ---
        st.subheader("🏬 Branch-wise Sales Forecast")
        branches = df["branch_id"].unique().tolist()
        selected_branch = st.selectbox("Select a branch:", branches, key="forecast_branch")

        branch_sales = df[df["branch_id"] == selected_branch]
        daily_branch_sales = branch_sales.groupby("date")["total_amount"].sum().reset_index()
        daily_branch_sales.columns = ["ds", "y"]

        if len(daily_branch_sales) > 10:
            model_branch = Prophet(daily_seasonality=True)
            model_branch.fit(daily_branch_sales)
            forecast_branch = model_branch.predict(model_branch.make_future_dataframe(periods=7))
            st.pyplot(model_branch.plot(forecast_branch))
            st.success(f"✅ Forecast for **{selected_branch}** (next 7 days).")
        else:
            st.warning("⚠️ Not enough data to forecast.")

    except Exception as e:
        st.error(f"Forecasting error: {e}")
