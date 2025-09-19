import pandas as pd
from faker import Faker
import random
from datetime import datetime, timedelta
import os

# Initialize Faker
Faker.seed(0)
fake = Faker()

# --- Configuration ---
DAILY_NEW_TRANSACTIONS = 200
NUM_PRODUCTS = 100
DATA_FILE = "grocer_ai_data.csv"
POLICY_FILE = "grocer_ai_policies.txt"

# Employees list
employees = []
if os.path.exists(DATA_FILE):
    try:
        existing_df = pd.read_csv(DATA_FILE)
        employees = existing_df[["employee_id", "employee_name", "branch_id", "role", "date_of_joining"]] \
            .drop_duplicates().to_dict("records")
    except Exception:
        existing_df = pd.DataFrame()
else:
    existing_df = pd.DataFrame()

branches = [f"BCH-{i:03d}" for i in range(1, 11)]

# Ensure employees exist
if not employees:
    for branch_id in branches:
        for i in range(5):
            employee_id = f"EMP-{branch_id.split('-')[-1]}-{i:03d}"
            employees.append({
                'employee_id': employee_id,
                'employee_name': fake.name(),
                'branch_id': branch_id,
                'role': random.choice(['Cashier', 'Store Manager', 'Inventory Specialist', 'Merchandiser']),
                'date_of_joining': datetime.now().strftime('%Y-%m-%d')
            })

employees_df = pd.DataFrame(employees)

# Products
products = []
for i in range(NUM_PRODUCTS):
    products.append({
        'product_sku': f"SKU-{i:04d}",
        'product_name': fake.unique.word().capitalize() + " " + random.choice(["Chips", "Cereal", "Juice", "Milk", "Soap", "Pasta"]),
        'product_category': random.choice(['Snacks', 'Beverages', 'Dairy', 'Personal Care', 'Pantry']),
        'unit_price': round(random.uniform(0.5, 25.0), 2)
    })
products_df = pd.DataFrame(products)

# --- Generate today's transactions ---
today = datetime.now()

transactions = []
for i in range(DAILY_NEW_TRANSACTIONS):
    branch_id = random.choice(branches)
    employee = random.choice([e for e in employees if e['branch_id'] == branch_id])
    product = products_df.sample(1).iloc[0]
    quantity = random.randint(1, 3)
    item_total = round(product['unit_price'] * quantity, 2)

    transactions.append({
        'transaction_id': f"TRN-{today.strftime('%Y%m%d')}-{i}",
        'date_time': today.strftime("%Y-%m-%d %H:%M:%S"),
        'customer_id': f"CUST-{random.randint(1, 20000)}",
        'branch_id': branch_id,
        'employee_id': employee['employee_id'],
        'product_sku': product['product_sku'],
        'product_name': product['product_name'],
        'product_category': product['product_category'],
        'unit_price': product['unit_price'],
        'quantity': quantity,
        'total_amount': item_total,
        'customer_feedback': random.choice(["Great service!", "Okay", "Not satisfied"]),
        'referral_source': random.choice(['Social Media', 'Newspaper', 'Word-of-Mouth', 'Online Ad'])
    })

new_df = pd.DataFrame(transactions)
new_df = new_df.merge(employees_df, on=['employee_id', 'branch_id'], how='left')

# Append to existing
if not existing_df.empty:
    final_df = pd.concat([existing_df, new_df], ignore_index=True)
else:
    final_df = new_df

# Keep only last 365 days
final_df['date_time'] = pd.to_datetime(final_df['date_time'])
cutoff = datetime.now() - timedelta(days=365)
final_df = final_df[final_df['date_time'] >= cutoff]

# Save
final_df.to_csv(DATA_FILE, index=False)
print(f"✅ Added {DAILY_NEW_TRANSACTIONS} rows for {today.date()} — total rows: {len(final_df)}")

# --- Occasionally update policies ---
if random.random() < 0.2:  # 20%
    with open(POLICY_FILE, "a") as f:
        f.write(f"\n[Update {today.strftime('%Y-%m-%d')}] Refund policy adjusted.\n")
    print("📄 Policy file updated.")



