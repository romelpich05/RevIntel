import pandas as pd
import numpy as np
import os

np.random.seed(42)

base_path = "data"
customers_path = os.path.join(base_path, "customers.csv")
customers_df = pd.read_csv(customers_path)

n_customers = len(customers_df)
half = n_customers // 2

# Create a balanced gender list
genders = ['Female'] * half + ['Male'] * (n_customers - half)
np.random.shuffle(genders)

customers_df['gender'] = genders

# Save
customers_df.to_csv(customers_path, index=False)
print(f"[OK] Re-assigned genders in customers.csv to exactly {half} Females and {n_customers - half} Males.")
