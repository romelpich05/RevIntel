import streamlit as st
import pandas as pd
import os

# Load local .env variables into environment if present
if os.path.exists(".env"):
    with open(".env", "r") as f:
        for line in f:
            stripped = line.strip()
            if stripped and "=" in stripped and not stripped.startswith("#"):
                key, val = stripped.split("=", 1)
                os.environ[key.strip()] = val.strip()

@st.cache_data
def load_data():
    """Loads all synthetic datasets for the RevIntel platform."""
    # Assume the app is run from the project root
    base_path = "data"
    
    stores_df = pd.read_csv(os.path.join(base_path, "stores.csv"))
    products_df = pd.read_csv(os.path.join(base_path, "products.csv"))
    customers_df = pd.read_csv(os.path.join(base_path, "customers.csv"))
    transactions_df = pd.read_csv(os.path.join(base_path, "transactions.csv"))
    inventory_df = pd.read_csv(os.path.join(base_path, "inventory.csv"))
    store_reviews_df = pd.read_csv(os.path.join(base_path, "store_reviews.csv"))
    
    # Convert date to datetime
    transactions_df['transaction_date'] = pd.to_datetime(transactions_df['transaction_date'])
    
    # Merge transactions with products to get cost_price, selling_price, category
    tx_prod = pd.merge(transactions_df, products_df, on='product_id', how='left', suffixes=('', '_prod'))
    
    return stores_df, products_df, customers_df, tx_prod, inventory_df, store_reviews_df

def inject_custom_css():
    """Injects premium dark mode and glassmorphism CSS theme."""
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Outfit', sans-serif !important;
        }

        /* Metric cards */
        [data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            transition: transform 0.2s ease, border-color 0.2s ease;
        }
        [data-testid="stMetric"]:hover {
            transform: translateY(-2px);
            border-color: rgba(255, 255, 255, 0.2);
        }
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: #0f111a;
        }
        
        /* Headers */
        h1, h2, h3 {
            color: #f8f9fa;
        }
        </style>
    """, unsafe_allow_html=True)

# Custom color palette for Plotly charts
REVINTEL_COLORS = ["#636EFA", "#EF553B", "#00CC96", "#AB63FA", "#FFA15A", "#19D3F3", "#FF6692", "#B6E880", "#FF97FF", "#FECB52"]
