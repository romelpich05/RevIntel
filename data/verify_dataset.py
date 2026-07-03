# /// script
# dependencies = [
#   "pandas",
#   "numpy",
# ]
# ///

import os
import pandas as pd
import numpy as np

print("Running validation checks on generated RevIntel datasets...")

# Load datasets
try:
    df_stores = pd.read_csv("data/stores.csv")
    df_products = pd.read_csv("data/products.csv")
    df_customers = pd.read_csv("data/customers.csv")
    df_transactions = pd.read_csv("data/transactions.csv")
    print("[OK] Successfully loaded all CSV files.")
except Exception as e:
    print(f"[FAIL] Failed to load CSV files: {e}")
    exit(1)

# Helper function to print results
def assert_check(condition, message):
    if condition:
        print(f"  [OK] {message}")
        return True
    else:
        print(f"  [FAIL] {message}")
        return False

all_passed = True

# 1. Row Count Checks
print("\n--- 1. Row Count Verification ---")
all_passed &= assert_check(len(df_stores) == 10, f"Stores table has exactly 10 records (Found: {len(df_stores)})")
all_passed &= assert_check(len(df_products) == 50, f"Products table has exactly 50 records (Found: {len(df_products)})")
all_passed &= assert_check(len(df_customers) == 1000, f"Customers table has exactly 1000 records (Found: {len(df_customers)})")
all_passed &= assert_check(len(df_transactions) > 10000, f"Transactions table has sufficient records (Found: {len(df_transactions)})")

# 2. Schema Verification (Checking required columns from PRD)
print("\n--- 2. Column Schema Verification ---")
store_cols = ["store_id", "store_name", "category", "store_type", "location_city", "location_type", "size_sqm", "size_category", "opening_year"]
all_passed &= assert_check(all(c in df_stores.columns for c in store_cols), "Stores table matches PRD schema")

product_cols = ["product_id", "product_name", "category", "subcategory", "unit_price", "cost_price", "brand", "elasticity", "abc_class", "xyz_class"]
all_passed &= assert_check(all(c in df_products.columns for c in product_cols), "Products table matches PRD schema")

customer_cols = ["customer_id", "full_name", "date_of_birth", "gender", "marital_status", "num_children", "home_postal_code", "income_bracket", "occupation_type", "membership_tier", "member_since", "preferred_payment"]
all_passed &= assert_check(all(c in df_customers.columns for c in customer_cols), "Customers table matches PRD schema")

tx_cols = ["transaction_id", "customer_id", "transaction_date", "store_id", "product_id", "product_category", "quantity", "unit_price", "discount_pct", "total_amount", "payment_method"]
all_passed &= assert_check(all(c in df_transactions.columns for c in tx_cols), "Transactions table matches PRD schema")

# 3. Referential Integrity (Foreign key checks)
print("\n--- 3. Referential Integrity Verification ---")
invalid_customers = df_transactions[~df_transactions["customer_id"].isin(df_customers["customer_id"])]
all_passed &= assert_check(len(invalid_customers) == 0, f"All transactions point to valid customers (Invalid rows: {len(invalid_customers)})")

invalid_products = df_transactions[~df_transactions["product_id"].isin(df_products["product_id"])]
all_passed &= assert_check(len(invalid_products) == 0, f"All transactions point to valid products (Invalid rows: {len(invalid_products)})")

invalid_stores = df_transactions[~df_transactions["store_id"].isin(df_stores["store_id"])]
all_passed &= assert_check(len(invalid_stores) == 0, f"All transactions point to valid stores (Invalid rows: {len(invalid_stores)})")

# 4. Null & Data Quality Checks
print("\n--- 4. Data Quality & Value Check ---")
all_passed &= assert_check(df_transactions["total_amount"].min() > 0, "No zero or negative total amounts in transactions")
all_passed &= assert_check(df_transactions["quantity"].min() >= 1, "Minimum purchase quantity is at least 1")
all_passed &= assert_check(df_transactions["discount_pct"].max() <= 0.30, "Promotional discounts are within maximum 30% bound")
all_passed &= assert_check(df_transactions.isnull().sum().sum() == 0, "No missing (NaN) values in any of the datasets")

# 5. Injected Pattern Verification (Crucial for ML modeling)
print("\n--- 5. Injected Modeling Patterns Verification ---")

# A. Price Elasticity pattern check
# Calculate average quantity sold for elastic items (elasticity < -2.0) with vs without discount
elastic_p_ids = df_products[df_products["elasticity"] < -2.0]["product_id"].tolist()
tx_elastic = df_transactions[df_transactions["product_id"].isin(elastic_p_ids)]
avg_qty_no_promo = tx_elastic[tx_elastic["discount_pct"] == 0]["quantity"].mean()
avg_qty_with_promo = tx_elastic[tx_elastic["discount_pct"] > 0]["quantity"].mean()
lift = avg_qty_with_promo / avg_qty_no_promo if avg_qty_no_promo > 0 else 0

all_passed &= assert_check(lift > 1.1, f"Price Elasticity: Promo lift active for elastic products (Promo Qty/Non-Promo Qty: {avg_qty_with_promo:.2f} / {avg_qty_no_promo:.2f} = {lift:.2f}x lift)")

# B. Market Basket Association pattern check
# Check correlation/rules: San Miguel Beer (P-08 or P-09) and Gourmet Cheese Platter (P-16)
# Check Whole Milk (P-03) and Oatmeal (P-22)
baskets = df_transactions.groupby("transaction_id")["product_id"].apply(list)
beer_basket_count = 0
both_count = 0
for basket in baskets:
    if "P-08" in basket or "P-09" in basket:
        beer_basket_count += 1
        if "P-16" in basket:
            both_count += 1

co_occurrence_rate = both_count / beer_basket_count if beer_basket_count > 0 else 0
all_passed &= assert_check(co_occurrence_rate > 0.40, f"Association Rules: High co-occurrence of Beer and Gourmet Cheese Platter in baskets (Found: {co_occurrence_rate*100:.1f}%)")

# C. Seasonality Check
df_transactions["transaction_date"] = pd.to_datetime(df_transactions["transaction_date"])
december_tx = df_transactions[df_transactions["transaction_date"].dt.month == 12]
january_tx = df_transactions[df_transactions["transaction_date"].dt.month == 1]

dec_daily = len(december_tx) / 31
jan_daily = len(january_tx) / 31
seasonality_ratio = dec_daily / jan_daily if jan_daily > 0 else 0

all_passed &= assert_check(seasonality_ratio > 1.5, f"Prophet Seasonality: December holiday sales volume exceeds January slump (December/January ratio: {dec_daily:.1f} / {jan_daily:.1f} = {seasonality_ratio:.2f}x)")

print("\n-------------------------------------------")
if all_passed:
    print("[SUCCESS] All validation checks passed successfully! The datasets are ready for ML modeling.")
    exit(0)
else:
    print("[FAIL] Some validation checks failed. Please review the output above.")
    exit(1)
