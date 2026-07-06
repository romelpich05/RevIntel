import streamlit as st
import pandas as pd
import numpy as np
import sys
import os
import plotly.express as px
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import load_data, inject_custom_css, REVINTEL_COLORS

st.set_page_config(page_title="Product Velocity", page_icon="⚡", layout="wide")
inject_custom_css()

st.title("⚡ Product Velocity & ML Baseline")
st.markdown("Analyze sales velocity, track inventory levels, and interpret the Logistic Regression classification model.")

with st.spinner("Analyzing Product Velocity & Training Classification Model..."):
    stores_df, products_df, customers_df, tx_prod, inventory_df, store_reviews_df = load_data()

# Calculate days in data
days = (tx_prod['transaction_date'].max() - tx_prod['transaction_date'].min()).days or 1

# Merge transactions with stores to get size and location type
tx_stores = pd.merge(tx_prod, stores_df, on='store_id', how='left')

# Prepare dataset for training ML models
# Aggregate sales velocity at the store-product level
ml_base = tx_stores.groupby(['store_id', 'product_id']).agg(
    total_qty=('quantity', 'sum'),
    avg_discount=('discount_pct', 'mean'),
    unit_price=('unit_price', 'first'),
    cost_price=('cost_price', 'first'),
    size_sqm=('size_sqm', 'first'),
    location_type=('location_type', 'first')
).reset_index()

ml_base['velocity'] = ml_base['total_qty'] / days

# Define label for Logistic Regression: 1 if Slow Mover (below median velocity), 0 otherwise
median_velocity = ml_base['velocity'].median()
ml_base['is_slow'] = (ml_base['velocity'] < median_velocity).astype(int)

# One-hot encode location_type
ml_data = pd.get_dummies(ml_base, columns=['location_type'], drop_first=True)

# Select features
feature_cols = ['avg_discount', 'unit_price', 'cost_price', 'size_sqm'] + [c for c in ml_data.columns if 'location_type_' in c]
X = ml_data[feature_cols].copy()

# Fill missing columns/NAs
X = X.fillna(0)

# Target variables
y_logistic = ml_data['is_slow']

# Scale features for fair coefficient comparison (interpretability)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Fit model
log_reg = LogisticRegression(max_iter=1000)
log_reg.fit(X_scaled, y_logistic)

st.sidebar.success("✅ Connected to Data Engine")
st.sidebar.markdown("---")
st.sidebar.info("Select filters directly on the page layout above.")

# Move selectors to the top of the main page with tooltips
col_sel1, col_sel2 = st.columns(2)
with col_sel1:
    category_options = ["All"] + list(products_df['category'].unique())
    selected_category = st.selectbox(
        "Select Category", 
        options=category_options, 
        key="vel_cat",
        help="Select a product category to filter the item selection dropdown."
    )
with col_sel2:
    if selected_category != "All":
        product_options = products_df[products_df['category'] == selected_category]['product_name'].tolist()
    else:
        product_options = products_df['product_name'].tolist()
    selected_product = st.selectbox(
        "Select Product", 
        options=product_options, 
        key="vel_prod",
        help="Choose a specific product SKU to display its current inventory stats, geographical heatmap, and velocity classifications."
    )

prod_id = products_df[products_df['product_name'] == selected_product]['product_id'].values[0]

# --- Operations Metrics ---
prod_tx = tx_prod[tx_prod['product_id'] == prod_id]
prod_inv = inventory_df[inventory_df['product_id'] == prod_id]

actual_velocity = prod_tx['quantity'].sum() / days
remaining_stock = prod_inv['current_stock'].sum()
restock_baseline = prod_inv['safety_stock_level'].sum()

# Compute predictions for the selected product
prod_ml = ml_data[ml_data['product_id'] == prod_id]
if not prod_ml.empty:
    prod_features = prod_ml[feature_cols].mean().to_frame()
    prod_features = prod_features.T.fillna(0)
    prod_features_scaled = scaler.transform(prod_features)
    pred_slow_prob = log_reg.predict_proba(prod_features_scaled)[0][1]
else:
    pred_slow_prob = 0.5

st.markdown("---")

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Actual Velocity", f"{actual_velocity:.2f} units/day", help="Average daily units sold for this product across all stores over the total operational period.")
with col2:
    st.metric("Remaining Stock (Units)", f"{remaining_stock:,} units", help="Total physical units currently in stock across all stores.")
with col3:
    st.metric("Restock Baseline (Safety Stock)", f"{restock_baseline:,} units", help="Total configured safety stock floor. When stock drops below this baseline, it triggers reorder recommendations.")
with col4:
    product_info = products_df[products_df['product_id'] == prod_id].iloc[0]
    st.metric("Cost Per Unit", f"₱{product_info['cost_per_unit']:.2f}", help="The cost to purchase/manufacture one unit of this product.")
with col5:
    st.metric("Unit Selling Price", f"₱{product_info['unit_price']:.2f}", help="The retail selling price of one unit of this product.")

st.markdown("---")

col_left, col_right = st.columns([1.5, 1.0])

with col_left:
    st.subheader(
        "📈 Logistic Regression Coefficients",
        help="This horizontal bar chart displays the mathematical weights (coefficients) of features in the Logistic Regression model. Bars pointing to the right increase the likelihood of the product being classified as a slow-moving item. Bars pointing to the left decrease it, meaning they drive faster sales velocity."
    )
    
    coeff_df_log = pd.DataFrame({
        'Feature': feature_cols,
        'Coefficient': log_reg.coef_[0]
    }).sort_values('Coefficient', ascending=True)
    
    coeff_df_log['Feature'] = coeff_df_log['Feature'].apply(lambda x: x.replace('_', ' ').title())
    
    fig_log = px.bar(coeff_df_log, x='Coefficient', y='Feature', orientation='h',
                     color_discrete_sequence=[REVINTEL_COLORS[1]])
    fig_log.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#f8f9fa')
    st.plotly_chart(fig_log, use_container_width=True)

with col_right:
    st.subheader(
        "💡 Interpretability & Prediction Report",
        help="Shows the model's prediction report and calculated probability that this product is a slow mover based on its price, average discount, store size, and location."
    )
    st.markdown(f"Evaluating the probability that **{selected_product}** is slow-moving.")
    
    st.metric("Slow Mover Probability", f"{pred_slow_prob:.1%}")
    
    if pred_slow_prob > 0.6:
        st.error("⚠️ **High Risk Mover:** This product has a high probability of operating as a slow mover. Consider bundling or promotional markdown.")
    elif pred_slow_prob > 0.4:
        st.warning("⚠️ **Moderate Risk Mover:** Monitor velocity and stock cover closely.")
    else:
        st.success("✅ **Healthy Velocity Mover:** This product is operating at healthy velocity levels.")

    # Find strongest positive and negative drivers
    top_pos_driver = coeff_df_log.iloc[-1]['Feature']
    top_neg_driver = coeff_df_log.iloc[0]['Feature']
    
    # Render detailed drivers explanation
    st.info(f"""
    ✨ **AI Interpretability & Driver Analysis:**
    * **Stagnancy Accelerator:** **{top_pos_driver}** exhibits the highest positive coefficient (**{coeff_df_log.iloc[-1]['Coefficient']:.2f}**). This indicates that increases or presence in this feature strongly push this product toward slow-moving status. 
    * **Velocity Accelerator:** **{top_neg_driver}** exhibits the strongest negative weight (**{coeff_df_log.iloc[0]['Coefficient']:.2f}**). This is your primary lever to trigger fast-mover dynamics. If this feature is 'Avg Discount', it confirms the effectiveness of price elasticity promotions for this item.
    * **Action Plan:** To optimize inventory velocity, align pricing adjustments directly with the high-impact negative drivers while reducing exposure to stores or layouts correlated with positive weights.
    """)

st.markdown("---")
st.subheader(
    "🏬 Store-Level Inventory & Velocity Heatmap",
    help="This map projects your stores geographically. The size of each bubble represents the current stock level (larger bubbles = more items in storage). The color of the bubble represents daily sales velocity (brighter/greener = fast moving, darker/blue = slow moving)."
)

# Join store inventory, store descriptions, and average sales velocity
store_details = pd.merge(prod_inv, stores_df, on='store_id', how='left')
# Calculate velocity per store
store_sales = prod_tx.groupby('store_id')['quantity'].sum().reset_index()
store_sales['avg_daily_sales'] = store_sales['quantity'] / days

store_details = pd.merge(store_details, store_sales[['store_id', 'avg_daily_sales']], on='store_id', how='left').fillna({'avg_daily_sales': 0.0})

# Coordinates mapping for Metro Manila cities
manila_coords = {
    'Quezon City': (14.6760, 121.0437),
    'Taguig': (14.5176, 121.0509),
    'Pasig': (14.5733, 121.0615),
    'Mandaluyong': (14.5794, 121.0359),
    'Manila': (14.5995, 120.9842),
    'Makati': (14.5547, 121.0244)
}

store_details['latitude'] = store_details['location_city'].map(lambda x: manila_coords.get(x, (14.5995, 120.9842))[0])
store_details['longitude'] = store_details['location_city'].map(lambda x: manila_coords.get(x, (14.5995, 120.9842))[1])

# Adding a small jitter so overlapping bubbles in the same city are slightly visible
store_details['latitude'] += np.random.uniform(-0.008, 0.008, size=len(store_details))
store_details['longitude'] += np.random.uniform(-0.008, 0.008, size=len(store_details))

# Mapbox bubble plot
fig_map = px.scatter_mapbox(
    store_details, 
    lat='latitude', 
    lon='longitude', 
    size='current_stock', 
    color='avg_daily_sales',
    color_continuous_scale='Viridis', 
    size_max=20, 
    zoom=11,
    hover_name='store_name',
    hover_data=['current_stock', 'safety_stock_level', 'avg_daily_sales'],
    title=f"Geographical Inventory Heatmap: {selected_product}",
    labels={'current_stock': 'Current Stock', 'avg_daily_sales': 'Velocity (units/day)'},
    mapbox_style="open-street-map"
)
fig_map.update_layout(
    margin=dict(l=0, r=0, t=40, b=0),
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font_color='#f8f9fa'
)

# Render Map
st.plotly_chart(fig_map, use_container_width=True)

# Generate detailed map insights
highest_stock_store = store_details.sort_values('current_stock', ascending=False).iloc[0]
highest_vel_store = store_details.sort_values('avg_daily_sales', ascending=False).iloc[0]

# Calculate specific stock transfer recommendations
stock_transfer_qty = int(highest_stock_store['current_stock'] * 0.40)

st.info(f"""
✨ **AI Map Logistics & Transfer Insight:**
* **Inventory Concentration:** **{highest_stock_store['store_name']}** holds the highest current stock level with **{highest_stock_store['current_stock']:,} units** (largest bubble).
* **Sales Hotspot:** **{highest_vel_store['store_name']}** exhibits the fastest product velocity at **{highest_vel_store['avg_daily_sales']:.2f} units/day** (brightest bubble).
* **Inter-branch Transfer Play:** We recommend executing a stock transfer request of **{stock_transfer_qty:,} units** from the overstocked store (**{highest_stock_store['store_name']}**) directly to the high-velocity hotspot (**{highest_vel_store['store_name']}**). This immediately rebalances safety stock coverage without committing additional cash to purchasing fresh supplier inventory.
""")

# Restock Recommendation Status
def check_restock(row):
    if row['current_stock'] == 0:
        return "🚨 Out of Stock - Reorder Now!"
    elif row['current_stock'] <= row['safety_stock_level']:
        return "⚠️ Below Safety Stock - Reorder"
    return "✅ Stock Level Adequate"

store_details['Restock Recommendation'] = store_details.apply(check_restock, axis=1)

# Calculate cost per unit and capital tied up
store_details['cost_per_unit'] = product_info['cost_per_unit']
store_details['capital_tied_up'] = store_details['current_stock'] * store_details['cost_per_unit']

# Format table for display
table_df = store_details[['store_id', 'store_name', 'location_city', 'location_type', 'size_sqm', 'cost_per_unit', 'current_stock', 'capital_tied_up', 'safety_stock_level', 'avg_daily_sales', 'Restock Recommendation']].copy()
table_df.columns = ['Store ID', 'Store Name', 'Location/City', 'Location Type', 'Store Size (sqm)', 'Cost Per Unit (₱)', 'Current Stock (Units)', 'Capital Tied Up (₱)', 'Safety Stock (Units)', 'Daily Velocity (Units/Day)', 'Status']

# Format currency columns in display
table_df['Cost Per Unit (₱)'] = table_df['Cost Per Unit (₱)'].apply(lambda x: f"₱{x:,.2f}")
table_df['Capital Tied Up (₱)'] = table_df['Capital Tied Up (₱)'].apply(lambda x: f"₱{x:,.2f}")

st.dataframe(table_df, use_container_width=True, hide_index=True)
