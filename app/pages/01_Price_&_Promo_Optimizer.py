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
st.markdown("Maximize margin by simulating price elasticity, retail price hikes, and identifying promotional cannibalization.")

with st.spinner("Loading Data..."):
    stores_df, products_df, customers_df, tx_prod, inventory_df, store_reviews_df = load_data()

st.sidebar.success("✅ Connected to Data Engine")
st.sidebar.markdown("---")
st.sidebar.info("Select filters and adjust pricing parameters directly on the page layout.")

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
daily_sales = prod_tx.groupby(['transaction_date', 'discount_pct'])['quantity'].sum().reset_index()
elasticity_data = daily_sales.groupby('discount_pct')['quantity'].mean().reset_index()

# Prepare pricing simulation parameters first so the chart can draw the target strategy point
st.markdown("---")
st.subheader("📊 Interactive Price & Promo ROI Simulator")
st.markdown("Raise the selling price or apply a discount to forecast demand and calculate profitability changes.")

sim_col1, sim_col2, sim_col3 = st.columns(3)
with sim_col1:
    price_adjust_pct = st.slider("Adjust Base Selling Price (%)", min_value=-20, max_value=50, value=0, step=1, help="Raise or lower the base retail selling price before promotions. Raising the price represents a negative discount in the elasticity model.")
    new_base_price = base_price * (1 + price_adjust_pct/100)
    st.markdown(f"New Base Price: **₱{new_base_price:.2f}** ({'Price Increase' if price_adjust_pct >= 0 else 'Price Markdown'} of {abs(price_adjust_pct)}%)")
with sim_col2:
    sim_discount = st.slider("Planned Promo Discount %", min_value=0, max_value=50, value=0, step=5, help="Discount applied to the new base price during the promotion.")
with sim_col3:
    sim_duration = st.number_input("Simulation Duration (Days)", min_value=1, max_value=30, value=7)

# Calculate base trendline parameters
if len(elasticity_data) > 1:
    z = np.polyfit(elasticity_data['discount_pct'], elasticity_data['quantity'], 1)
    hist_slope = z[0]
    hist_intercept = z[1]
else:
    hist_slope = 1.0
    hist_intercept = elasticity_data['quantity'].mean()

# Price Elasticity Controls placed above chart
st.markdown("---")
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(
        f"Price Elasticity Model: {selected_product}",
        help="This scatter plot maps average daily quantities sold (Y-axis) against discount percentages (X-axis). The line of best fit represents the modeled demand elasticity curve. A downward-sloping curve indicates normal price-volume behavior (higher discounts drive higher sales volume)."
    )
    
    # Interactive Elasticity Override Slider
    sim_elasticity_slope = st.slider(
        "Simulate Demand Sensitivity (Slope Coefficient)", 
        min_value=-5.0, 
        max_value=10.0, 
        value=float(hist_slope), 
        step=0.1,
        help="Adjust how responsive product demand is to discounts. A larger coefficient rotates the line, making demand change more drastically with price adjustments. This updates the chart and ROI metrics in real-time."
    )
    
    p = np.poly1d([sim_elasticity_slope, hist_intercept])

# Calculate simulation metrics using the interactive elasticity model
promo_price = new_base_price * (1 - sim_discount/100)
effective_discount = ((base_price - promo_price) / base_price) * 100

base_daily_qty = p(0)
promo_daily_qty = p(effective_discount)
promo_daily_qty = max(0.1, promo_daily_qty) # Clamp quantity

# Finish sim_col2 display with final discounted price
with sim_col2:
    effective_change_pct = ((promo_price - base_price) / base_price) * 100
    st.markdown(f"Discounted Promo Price: **₱{promo_price:.2f}** (Net Price Change: {effective_change_pct:+.1f}%)")

# Render Chart inside col1
with col1:
    if len(elasticity_data) > 1:
        x_range = np.linspace(-30, elasticity_data['discount_pct'].max() + 5, 150)
        y_fit = p(x_range)
        
        fig = px.scatter(elasticity_data, x='discount_pct', y='quantity', 
                         title="Average Daily Volume vs. Discount %",
                         labels={'discount_pct': 'Discount %', 'quantity': 'Avg Daily Quantity Sold'},
                         color_discrete_sequence=[REVINTEL_COLORS[0]])
        
        # Add trendline
        fig.add_trace(go.Scatter(x=x_range, y=y_fit, mode='lines', name='Elasticity Trend', line=dict(color=REVINTEL_COLORS[1])))
        
        # Add Live Strategy Marker (pink star)
        fig.add_trace(go.Scatter(
            x=[effective_discount],
            y=[promo_daily_qty],
            mode='markers+text',
            name='Current Strategy Target',
            text=['Selected Strategy'],
            textposition='top center',
            marker=dict(color='#FF2E93', size=15, symbol='star', line=dict(color='white', width=2))
        ))
        
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#f8f9fa')
        st.plotly_chart(fig, use_container_width=True)
        
        # AI Insight
        if sim_elasticity_slope > 0:
            insight_text = f"✨ **AI Elasticity Insight:** At the current simulated slope of **{sim_elasticity_slope:.2f}**, demand is highly responsive to pricing. Each 1% price decrease (discount) applied is projected to increase daily volume by **{sim_elasticity_slope:.2f} units**."
        else:
            insight_text = f"✨ **AI Elasticity Insight:** At the current simulated slope of **{sim_elasticity_slope:.2f}**, demand behaves inversely or is inelastic. Adjusting pricing shows minimal positive correlation with volume."
        st.info(insight_text)
    else:
        st.warning("Not enough variance in historical discounts to model elasticity for this product.")
        
with col2:
    st.markdown("### Product Baseline")
    st.metric("Base Price", f"₱{base_price:.2f}")
    st.metric("Cost Price", f"₱{cost_price:.2f}")
    st.metric("Base Margin", f"{((base_price - cost_price) / base_price * 100):.1f}%")

st.markdown("---")
st.subheader("💰 Simulation Financial Forecast")

# Scenario metrics
no_change_qty = base_daily_qty * sim_duration
no_change_rev = no_change_qty * base_price
no_change_cost = no_change_qty * cost_price
no_change_profit = no_change_rev - no_change_cost

promo_qty = promo_daily_qty * sim_duration
promo_rev = promo_qty * promo_price
promo_cost = promo_qty * cost_price
promo_profit = promo_rev - promo_cost

profit_delta = promo_profit - no_change_profit

col_r1, col_r2, col_r3 = st.columns(3)
with col_r1:
    st.metric("Est. Total Volume", f"{promo_qty:,.0f} units", f"{promo_qty - no_change_qty:+,.0f} vs original")
with col_r2:
    st.metric("Est. Revenue", f"₱{promo_rev:,.2f}", f"₱{promo_rev - no_change_rev:+,.2f} vs original")
with col_r3:
    st.metric("Est. Gross Profit", f"₱{promo_profit:,.2f}", f"₱{profit_delta:+,.2f} vs original", 
              delta_color="normal" if profit_delta >= 0 else "inverse")

if profit_delta < 0:
    st.error(f"⚠️ **Margin Erosion Alert!** This pricing strategy is projected to reduce gross profit by ₱{abs(profit_delta):.2f} compared to the original baseline due to suppressed demand volume.")
else:
    st.success(f"✅ **Profitable Strategy!** This pricing strategy is projected to increase gross profit by +₱{profit_delta:.2f} compared to the original baseline.")
