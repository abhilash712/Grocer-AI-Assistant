# send_email.py
import os
import smtplib
from dotenv import load_dotenv
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import pandas as pd

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_TO = [addr.strip() for addr in os.getenv("EMAIL_TO").split(",")]
CSV_PATH = os.getenv("CSV_PATH", "grocer_ai_data.csv")

def build_summary():
    try:
        df = pd.read_csv(CSV_PATH, parse_dates=["date_time"])
    except Exception as e:
        return f"❌ Failed to read CSV: {e}"

    today = pd.Timestamp.today().date()
    today_df = df[df["date_time"].dt.date == today]

    total_txns = len(today_df)
    total_sales = today_df["total_amount"].sum() if total_txns > 0 else 0

    body = [
        f"📊 Grocer-AI Daily Report — {today}",
        "",
        f"🛒 Transactions today: {total_txns}",
        f"💰 Total sales: ₹{total_sales:,.2f}",
        "",
        "🏆 Top Products:"
    ]

    if not today_df.empty:
        top_products = (
            today_df.groupby("product_name")["quantity"]
            .sum()
            .sort_values(ascending=False)
            .head(5)
        )
        for prod, qty in top_products.items():
            body.append(f"- {prod}: {qty} sold")
    else:
        body.append("No transactions yet today.")

    return "\n".join(body)

def send_email():
    subject = f"Grocer-AI Daily Update — {date.today()}"
    body = build_summary()

    msg = MIMEMultipart()
    msg["From"] = EMAIL_FROM
    msg["To"] = ", ".join(EMAIL_TO)
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    # Attach CSV if under 5MB
    if os.path.exists(CSV_PATH) and os.path.getsize(CSV_PATH) < 5*1024*1024:
        with open(CSV_PATH, "rb") as f:
            part = MIMEApplication(f.read(), Name=os.path.basename(CSV_PATH))
        part["Content-Disposition"] = f'attachment; filename="{os.path.basename(CSV_PATH)}"'
        msg.attach(part)

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
        print("✅ Email sent to:", EMAIL_TO)

if __name__ == "__main__":
    send_email()
