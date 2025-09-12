import pandas as pd
from faker import Faker
import random
from datetime import datetime, timedelta

# Initialize Faker with a consistent seed to ensure reproducibility
Faker.seed(0)
fake = Faker()

# --- Configuration ---
NUM_RECORDS = 50000
NUM_BRANCHES = 10
NUM_EMPLOYEES_PER_BRANCH = 5
NUM_PRODUCTS = 100
START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2025, 1, 1)

# --- Generate Core Data ---
# Branches
branches = [f"BCH-{i:03d}" for i in range(1, NUM_BRANCHES + 1)]
branch_locations = [fake.city() for _ in range(NUM_BRANCHES)]

# Employees
employees = []
for branch_id in branches:
    for i in range(NUM_EMPLOYEES_PER_BRANCH):
        employee_id = f"EMP-{branch_id.split('-')[-1]}-{i:03d}"
        employees.append({
            'employee_id': employee_id,
            'employee_name': fake.name(),
            'branch_id': branch_id,
            'role': random.choice(['Cashier', 'Store Manager', 'Inventory Specialist', 'Merchandiser']),
            'date_of_joining': fake.date_between(start_date=START_DATE, end_date=END_DATE).strftime('%Y-%m-%d'),
            'leave_days_taken': random.randint(0, 15),
            'sales_performance_score': random.randint(60, 100)
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

# Transactions
transactions = []
for i in range(NUM_RECORDS):
    branch_id = random.choice(branches)
    # choose an employee from that branch
    employee_id = random.choice([e['employee_id'] for e in employees if e['branch_id'] == branch_id])
    num_items = random.randint(1, 5)

    selected_products = products_df.sample(n=num_items, replace=True)
    for _, item in selected_products.iterrows():
        quantity = random.randint(1, 3)
        item_total = round(item['unit_price'] * quantity, 2)
        transactions.append({
            'transaction_id': f"TRN-{i:06d}",
            'date_time': (START_DATE + timedelta(days=random.randint(0, 364), seconds=random.randint(0, 86399))).strftime('%Y-%m-%d %H:%M:%S'),
            'customer_id': f"CUST-{random.randint(1, 10000)}",
            'branch_id': branch_id,
            'employee_id': employee_id,
            'product_sku': item['product_sku'],
            'product_name': item['product_name'],
            'product_category': item['product_category'],
            'unit_price': item['unit_price'],
            'quantity': quantity,
            'total_amount': item_total,
            'customer_feedback': fake.text(max_nb_chars=100) if random.random() < 0.1 else "",
            'referral_source': random.choice(['Social Media', 'Newspaper', 'Word-of-Mouth', 'Online Ad'])
        })

transactions_df = pd.DataFrame(transactions)

# Join and save
final_df = transactions_df.merge(employees_df, on=['employee_id', 'branch_id'], how='left')
final_df.to_csv("grocer_ai_data.csv", index=False)

print("grocer_ai_data.csv has been successfully generated.")
print(f"Total rows created: {len(final_df)}")
print("\nSample Data:")
print(final_df.head())
