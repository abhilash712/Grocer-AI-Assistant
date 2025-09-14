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
POLICY_UPDATE_PROB = 0.2   # 20% chance policies get updated
EMPLOYEE_JOIN_PROB = 0.3   # 30% chance new employee joins
EMPLOYEE_LEAVE_PROB = 0.1  # 10% chance someone leaves
DATA_FILE = "grocer_ai_data.csv"
POLICY_FILE = "grocer_ai_policies.txt"

# Feedback pool
feedback_pool = {
    "positive": [
        "Great service, very satisfied!",
        "Excellent product quality.",
        "Friendly staff and quick checkout."
    ],
    "neutral": [
        "Average experience.",
        "Nothing special, just okay.",
        "Service was fine, nothing to complain."
    ],
    "negative": [
        "Poor service, not happy.",
        "Had to wait too long.",
        "Product was not fresh, disappointed."
    ]
}

# Employees list (load if exists, else start new)
employees = []
if os.path.exists(DATA_FILE):
    try:
        existing_df = pd.read_csv(DATA_FILE)
        employees = existing_df[["employee_id", "employee_name", "branch_id", "role", "date_of_joining"]].drop_duplicates().to_dict("records")
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

# --- Simulate employee join/leave ---
if random.random() < EMPLOYEE_JOIN_PROB:
    new_emp = {
        'employee_id': f"EMP-{random.randint(100,999)}-{random.randint(10,99)}",
        'employee_name': fake.name(),
        'branch_id': random.choice(branches),
        'role': random.choice(['Cashier', 'Store Manager', 'Inventory Specialist', 'Merchandiser']),
        'date_of_joining': datetime.now().strftime('%Y-%m-%d')
    }
    employees.append(new_emp)
    print(f"New employee joined: {new_emp['employee_name']} ({new_emp['employee_id']})")

if employees and random.random() < EMPLOYEE_LEAVE_PROB:
    leaving_emp = random.choice(employees)
    employees.remove(leaving_emp)
    print(f"Employee left: {leaving_emp['employee_name']} ({leaving_emp['employee_id']})")

# --- Generate new transactions ---
transactions = []
today = datetime.now().strftime('%Y-%m-%d')

for i in range(DAILY_NEW_TRANSACTIONS):
    branch_id = random.choice(branches)
    employee = random.choice([e for e in employees if e['branch_id'] == branch_id])
    product = products_df.sample(1).iloc[0]
    quantity = random.randint(1, 3)
    item_total = round(product['unit_price'] * quantity, 2)

    # Weighted feedback: 60% pos, 30% neutral, 10% neg
    feedback_type = random.choices(["positive", "neutral", "negative"], [0.6, 0.3, 0.1])[0]
    feedback = random.choice(feedback_pool[feedback_type])

    transactions.append({
        'transaction_id': f"TRN-{int(datetime.now().timestamp())}-{i}",
        'date_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'customer_id': f"CUST-{random.randint(1, 20000)}",
        'branch_id': branch_id,
        'employee_id': employee['employee_id'],
        'product_sku': product['product_sku'],
        'product_name': product['product_name'],
        'product_category': product['product_category'],
        'unit_price': product['unit_price'],
        'quantity': quantity,
        'total_amount': item_total,
        'customer_feedback': feedback,
        'referral_source': random.choice(['Social Media', 'Newspaper', 'Word-of-Mouth', 'Online Ad'])
    })

new_df = pd.DataFrame(transactions)

# Merge with employees info
employees_df = pd.DataFrame(employees)
final_df = new_df.merge(employees_df, on=['employee_id', 'branch_id'], how='left')

# Append to existing
if not existing_df.empty:
    final_df = pd.concat([existing_df, final_df], ignore_index=True)

# Keep only last 365 days
final_df['date_time'] = pd.to_datetime(final_df['date_time'])
cutoff = datetime.now() - timedelta(days=365)
final_df = final_df[final_df['date_time'] >= cutoff]

# Save back
final_df.to_csv(DATA_FILE, index=False)
print(f"Updated {DATA_FILE} with {len(new_df)} new rows. Total rows now: {len(final_df)}")

# --- Update policy file occasionally ---
if random.random() < POLICY_UPDATE_PROB:
    with open(POLICY_FILE, "a") as f:
        f.write(f"\n[Update {datetime.now().strftime('%Y-%m-%d')}] Refund policy adjusted.\n")
    print("Policy file updated.")

