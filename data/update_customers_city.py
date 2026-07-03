import pandas as pd
import os

base_path = "data"
customers_path = os.path.join(base_path, "customers.csv")
customers_df = pd.read_csv(customers_path)

# Mapping postal code to cities in Metro Manila
postal_city_map = {
    1000: 'Manila',
    1001: 'Manila',
    1002: 'Pasig',
    1003: 'Makati',
    1004: 'Quezon City',
    1005: 'Taguig',
    1006: 'Mandaluyong',
    1007: 'Mandaluyong',
    1008: 'Pasig',
    1009: 'Makati'
}

customers_df['home_city'] = customers_df['home_postal_code'].map(postal_city_map).fillna('Other')

customers_df.to_csv(customers_path, index=False)
print("[OK] Updated customers.csv with home_city column mapped to metropolitan cities.")
