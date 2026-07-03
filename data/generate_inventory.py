import pandas as pd
import numpy as np
import os

# Set random seed for reproducibility
np.random.seed(42)

# Load existing data
base_path = "data"
stores_df = pd.read_csv(os.path.join(base_path, "stores.csv"))
products_df = pd.read_csv(os.path.join(base_path, "products.csv"))
transactions_df = pd.read_csv(os.path.join(base_path, "transactions.csv"))

# Calculate average daily sales per store per product to simulate realistic stock
transactions_df['transaction_date'] = pd.to_datetime(transactions_df['transaction_date'])
days_in_data = (transactions_df['transaction_date'].max() - transactions_df['transaction_date'].min()).days
if days_in_data == 0: days_in_data = 1

sales_velocity = transactions_df.groupby(['store_id', 'product_id'])['quantity'].sum().reset_index()
sales_velocity['avg_daily_sales'] = sales_velocity['quantity'] / days_in_data

inventory_records = []

# Generate inventory for every store-product combination
for _, store in stores_df.iterrows():
    for _, product in products_df.iterrows():
        # Get velocity, default to a small number if no sales
        vel_match = sales_velocity[(sales_velocity['store_id'] == store['store_id']) & 
                                   (sales_velocity['product_id'] == product['product_id'])]
        if not vel_match.empty:
            avg_daily = vel_match['avg_daily_sales'].values[0]
        else:
            avg_daily = 0.5
            
        # Simulate realistic inventory data
        # Lead time: random between 2 and 14 days
        lead_time = np.random.randint(2, 15)
        
        # Safety stock: enough for lead time + 3 days buffer
        safety_stock = int(np.ceil(avg_daily * (lead_time + 3)))
        if safety_stock < 5: safety_stock = 5
        
        # Current stock: random between 0.5x safety stock (reorder needed) and 4x safety stock
        current_stock = int(np.random.uniform(0.5, 4.0) * safety_stock)
        
        # Add some random out of stocks to trigger alerts in our Command Center
        if np.random.random() < 0.05:
            current_stock = int(np.random.uniform(0, 0.4) * safety_stock) # Very low stock
            
        inventory_records.append({
            'store_id': store['store_id'],
            'product_id': product['product_id'],
            'current_stock': current_stock,
            'safety_stock_level': safety_stock,
            'lead_time_days': lead_time
        })

inventory_df = pd.DataFrame(inventory_records)
inventory_df.to_csv(os.path.join(base_path, "inventory.csv"), index=False)
print(f"[OK] Generated {len(inventory_df)} inventory records and saved to data/inventory.csv")
