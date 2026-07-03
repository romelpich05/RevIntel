import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

# Ensure utils can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import load_data, inject_custom_css, REVINTEL_COLORS

st.set_page_config(page_title="Price & Promo Optimizer", page_icon="📉", layout="wide")
inject_custom_css()

st.title("📉 Price & Promo Optimizer")
st.markdown("Maximize margin by simulating price elasticity and identifying promotional cannibalization.")

with st.spinner("Loading Data..."):
    stores_df, products_df, customers_df, tx_prod, inventory_df, store_reviews_df = load_data()

st.sidebar.success("✅ Connected to Data Engine")
st.sidebar.markdown("---")
st.sidebar.info("Select filters directly on the page layout above.")

# Move selectors to the top of the main page
col_sel1, col_sel2 = st.columns(2)
with col_sel1:
    selected_category = st.selectbox("Select Category", options=["All"] + list(products_df['category'].unique()), key="opt_cat")
with col_sel2:
    if selected_category != "All":
        filtered_products = products_df[products_df['category'] == selected_category]
    else:
        filtered_products = products_df
    selected_product = st.selectbox("Select Product to Analyze", options=filtered_products['product_name'].unique(), key="opt_prod")

product_info = products_df[products_df['product_name'] == selected_product].iloc[0]
product_id = product_info['product_id']
base_price = product_info['unit_price']
cost_price = product_info['cost_price']

# Filter transactions for this product
prod_tx = tx_prod[tx_prod['product_id'] == product_id].copy()

# Calculate elasticity
# Aggregate daily sales by discount level
daily_sales = prod_tx.groupby(['transaction_date', 'discount_pct'])['quantity'].sum().reset_index()
# Group by discount_pct to find average daily sales volume
elasticity_data = daily_sales.groupby('discount_pct')['quantity'].mean().reset_index()

st.markdown("---")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(
        f"Price Elasticity Model: {selected_product}",
        help="This scatter plot maps average daily quantities sold (Y-axis) against discount percentages (X-axis). The line of best fit represents the modeled demand elasticity curve. A downward-sloping curve indicates normal price-volume behavior (higher discounts drive higher sales volume)."
    )
    if len(elasticity_data) > 1:
        # Fit linear regression
        z = np.polyfit(elasticity_data['discount_pct'], elasticity_data['quantity'], 1)
        p = np.poly1d(z)
        
        # Create a line of best fit
        x_range = np.linspace(0, elasticity_data['discount_pct'].max() + 5, 100)
        y_fit = p(x_range)
        
        fig = px.scatter(elasticity_data, x='discount_pct', y='quantity', 
                         title="Average Daily Volume vs. Discount %",
                         labels={'discount_pct': 'Discount %', 'quantity': 'Avg Daily Quantity Sold'},
                         color_discrete_sequence=[REVINTEL_COLORS[0]])
        fig.add_trace(go.Scatter(x=x_range, y=y_fit, mode='lines', name='Elasticity Trend', line=dict(color=REVINTEL_COLORS[1])))
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#f8f9fa')
        st.plotly_chart(fig, use_container_width=True)
        
        # AI Insight
        elasticity_slope = z[0]
        if elasticity_slope > 0:
            insight_text = f"✨ **AI Insight:** Demand is **highly responsive** to pricing. Each 1% discount applied is projected to increase daily volume by approximately **{elasticity_slope:.2f} units**."
        else:
            insight_text = "✨ **AI Insight:** Demand is **inelastic** or has sparse promotional history. Adjusting pricing shows minimal correlation with volume shifts."
        st.info(insight_text)
    else:
        st.warning("Not enough variance in historical discounts to model elasticity for this product.")
        
with col2:
    st.markdown("### Product Baseline")
    st.metric("Base Price", f"₱{base_price:.2f}")
    st.metric("Cost Price", f"₱{cost_price:.2f}")
    st.metric("Base Margin", f"{((base_price - cost_price) / base_price * 100):.1f}%")

st.markdown("---")
st.subheader("📊 Promo ROI Simulator")
st.markdown("Test a hypothetical promotion to see if the volume lift offsets the margin drop.")

sim_col1, sim_col2, sim_col3 = st.columns(3)
with sim_col1:
    sim_discount = st.slider("Planned Discount %", min_value=0, max_value=50, value=15, step=5)
with sim_col2:
    sim_duration = st.number_input("Promotion Duration (Days)", min_value=1, max_value=30, value=7)
    
# Calculate projected metrics
base_daily_qty = p(0) if len(elasticity_data) > 1 else elasticity_data['quantity'].mean()
promo_daily_qty = p(sim_discount) if len(elasticity_data) > 1 else base_daily_qty

# No Promo Scenario
no_promo_qty = base_daily_qty * sim_duration
no_promo_rev = no_promo_qty * base_price
no_promo_cost = no_promo_qty * cost_price
no_promo_profit = no_promo_rev - no_promo_cost

# Promo Scenario
promo_price = base_price * (1 - sim_discount/100)
promo_qty = promo_daily_qty * sim_duration
promo_rev = promo_qty * promo_price
promo_cost = promo_qty * cost_price
promo_profit = promo_rev - promo_cost

profit_delta = promo_profit - no_promo_profit

col_r1, col_r2, col_r3 = st.columns(3)
with col_r1:
    st.metric("Est. Total Volume", f"{promo_qty:,.0f} units", f"{promo_qty - no_promo_qty:,.0f} vs no promo")
with col_r2:
    st.metric("Est. Revenue", f"₱{promo_rev:,.2f}", f"₱{promo_rev - no_promo_rev:,.2f} vs no promo")
with col_r3:
    st.metric("Est. Gross Profit", f"₱{promo_profit:,.2f}", f"₱{profit_delta:,.2f} vs no promo", 
              delta_color="normal" if profit_delta >= 0 else "inverse")

if profit_delta < 0:
    st.error(f"⚠️ **Cannibalization Alert!** At {sim_discount}% discount, the volume lift is insufficient. You will lose ₱{abs(profit_delta):.2f} in gross profit compared to not running the promotion.")
else:
    st.success(f"✅ **Profitable Promotion!** At {sim_discount}% discount, the volume lift outpaces the margin hit, netting +₱{profit_delta:.2f} in gross profit.")
