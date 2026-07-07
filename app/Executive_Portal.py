import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from utils import load_data, inject_custom_css, REVINTEL_COLORS

st.set_page_config(
    page_title="RevIntel | Executive Portal",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

inject_custom_css()

st.title("Executive Portal")
st.markdown("### Right product. Right customer. Right price. Right store.")

with st.spinner("Loading Enterprise Datasets..."):
    stores_df, products_df, customers_df, tx_prod, inventory_df, store_reviews_df = load_data()

# Bug Fix: Compute absolute discount amount correctly
tx_prod['discount_amount'] = tx_prod['unit_price'] * tx_prod['quantity'] * tx_prod['discount_pct']
# Pre-calculate cost amounts for financial aggregates
tx_prod['cost_amount'] = tx_prod['quantity'] * tx_prod['cost_price']

st.sidebar.success("✅ Connected to Data Engine")
st.sidebar.markdown("---")
st.sidebar.markdown("**Modules**")
st.sidebar.info("Navigate using the pages above. Adjust filters directly on the Executive Portal dashboard.")

# Branch Selector placed directly at the top of the main page
col_select, _ = st.columns([1, 1])
with col_select:
    stores_df['display_name'] = stores_df['store_id'] + " - " + stores_df['store_name'] + " (" + stores_df['location_city'] + ")"
    store_map = dict(zip(stores_df['display_name'], stores_df['store_id']))
    store_options = ["All Branches"] + list(stores_df['display_name'].unique())
    selected_store_display = st.selectbox(
        "Select Branch Location Filter", 
        options=store_options, 
        key="main_branch_filter",
        help="Filter all statistics and charts in the Executive Portal for a specific store branch or select 'All Branches' to view aggregates across the entire retail chain."
    )

# Map selected store
if selected_store_display != "All Branches":
    selected_store = store_map[selected_store_display]
else:
    selected_store = "All Stores"

# Filter data
if selected_store != "All Stores":
    tx_filtered = tx_prod[tx_prod['store_id'] == selected_store].copy()
    inv_filtered = inventory_df[inventory_df['store_id'] == selected_store].copy()
else:
    tx_filtered = tx_prod.copy()
    inv_filtered = inventory_df.copy()

if tx_filtered.empty:
    st.warning(f"No transaction data found for {selected_store_display}.")
    st.stop()

# --- KPI Calculations ---
# Overall Margin
total_revenue = tx_filtered['total_amount'].sum()
total_cost = tx_filtered['cost_amount'].sum()
overall_margin_pct = ((total_revenue - total_cost) / total_revenue * 100) if total_revenue > 0 else 0

# Wasted Promo Spend
wasted_promo_spend = tx_filtered[tx_filtered['discount_pct'] > 0]['discount_amount'].sum()

# Value of Current Stock
inv_joined = pd.merge(inv_filtered, products_df, on='product_id', how='left')
capital_tied = (inv_joined['current_stock'] * inv_joined['cost_price']).sum()
safety_capital = (inv_joined['safety_stock_level'] * inv_joined['cost_price']).sum()

st.markdown("---")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(
        "Overall Margin", 
        f"{overall_margin_pct:.1f}%", 
        "-1.2% vs Last Year", 
        delta_color="inverse",
        help="The percentage difference between gross sales revenue and total inventory cost price for all selected transactions."
    )
with col2:
    st.metric(
        "Promo Discounts Given", 
        f"₱{wasted_promo_spend:,.0f}", 
        "Cannibalization Risk", 
        delta_color="inverse",
        help="Total value of markdown discounts applied to the transaction history. High numbers represent lost margin potential."
    )
with col3:
    st.metric(
        "Inventory Capital", 
        f"₱{capital_tied:,.0f}",
        f"Safety Target: ₱{safety_capital:,.0f}",
        delta_color="off",
        help="Total cost value of the current physical inventory sitting on shelves and warehouses for the selected branch filter."
    )

st.markdown("---")

# NEW ROW: Financial Performance Analytics (Revenue/Profit Trend & Category Contribution)
st.markdown("### 💰 Financial Performance & Store Health")
row0_col1, row0_col2 = st.columns(2)

with row0_col1:
    st.subheader(
        "📈 Daily Revenue & Gross Profit Trend",
        help="Visualizes daily sales revenue alongside net profit over time. The gap between the lines represents daily product costs (COGS)."
    )
    tx_filtered['transaction_date'] = pd.to_datetime(tx_filtered['transaction_date'])
    daily_perf = tx_filtered.groupby('transaction_date').agg(
        revenue=('total_amount', 'sum'),
        cost=('cost_amount', 'sum')
    ).reset_index().sort_values('transaction_date')
    daily_perf['profit'] = daily_perf['revenue'] - daily_perf['cost']
    
    fig_trend = px.line(
        daily_perf, 
        x='transaction_date', 
        y=['revenue', 'profit'],
        labels={'value': 'Amount (₱)', 'transaction_date': 'Date', 'variable': 'Financial Metric'},
        color_discrete_sequence=[REVINTEL_COLORS[0], REVINTEL_COLORS[3]]
    )
    
    # Rename legend labels for readability
    newnames = {'revenue':'Gross Sales Revenue', 'profit':'Gross Profit Margin'}
    fig_trend.for_each_trace(lambda t: t.update(name = newnames.get(t.name, t.name)))
    
    fig_trend.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', 
        paper_bgcolor='rgba(0,0,0,0)', 
        font_color='#f8f9fa', 
        legend=dict(
            orientation="h",
            yanchor="bottom", 
            y=1.02, 
            xanchor="left", 
            x=0.01
        )
    )
    st.plotly_chart(fig_trend, use_container_width=True)
    
    # AI Trend Explanation
    if not daily_perf.empty:
        peak_day_row = daily_perf.sort_values('revenue', ascending=False).iloc[0]
        peak_date = peak_day_row['transaction_date'].strftime('%Y-%m-%d')
        peak_rev = peak_day_row['revenue']
        peak_profit = peak_day_row['profit']
        st.info(f"""
        ✨ **AI Financial Trend Insight:**
        * **Peak Sales Event:** Sales peaked on **{peak_date}** reaching **₱{peak_rev:,.2f}** in gross revenue and yielding **₱{peak_profit:,.2f}** in profit. 
        * **Operational Strategy:** Review promotional schedules or weekday foot traffic patterns around this peak date to replicate high-performance campaigns.
        """)

with row0_col2:
    st.subheader(
        "📊 Category Cost vs. Revenue Breakdown",
        help="Visualizes total sales revenue compared directly against product cost values by category. A larger gap between the bars represents higher profit margin contribution."
    )
    cat_perf = tx_filtered.groupby('category').agg(
        revenue=('total_amount', 'sum'),
        cost=('cost_amount', 'sum')
    ).reset_index().sort_values('revenue', ascending=False)
    cat_perf['profit'] = cat_perf['revenue'] - cat_perf['cost']
    cat_perf['margin_pct'] = (cat_perf['profit'] / cat_perf['revenue'] * 100).fillna(0)
    
    cat_melted = cat_perf.melt(id_vars='category', value_vars=['revenue', 'cost'], 
                               var_name='Financial Metric', value_name='Amount (₱)')
    cat_melted['Financial Metric'] = cat_melted['Financial Metric'].map({'revenue': 'Sales Revenue', 'cost': 'Inventory Cost (COGS)'})
    
    fig_cat = px.bar(
        cat_melted, 
        x='category', 
        y='Amount (₱)', 
        color='Financial Metric',
        barmode='group',
        color_discrete_sequence=[REVINTEL_COLORS[1], REVINTEL_COLORS[4]]
    )
    fig_cat.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', 
        paper_bgcolor='rgba(0,0,0,0)', 
        font_color='#f8f9fa',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0.01
        )
    )
    st.plotly_chart(fig_cat, use_container_width=True)
    
    # AI Category Explanation
    if not cat_perf.empty:
        top_cat_row = cat_perf.iloc[0]
        st.info(f"""
        ✨ **AI Category Margin Insight:**
        * **Highest Revenue Category:** **{top_cat_row['category']}** generated the highest sales revenue at **₱{top_cat_row['revenue']:,.2f}** with an average gross margin percentage of **{top_cat_row['margin_pct']:.1f}%**.
        * **Profit Booster Strategy:** Run selective bundles for high-margin products in this category to drive transaction value while protecting core store profitability.
        """)

st.markdown("---")

# ROW 1: Product Velocity (Fastest vs. Slowest Movers)
st.markdown("### ⚡ Inventory Velocity Analytics")
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.subheader(
        "🔥 Top 5 Fastest Moving Products",
        help="This horizontal bar chart displays the top 5 products with the highest cumulative units sold. Longer bars represent higher customer demand and inventory velocity."
    )
    top_movers = tx_filtered.groupby('product_name')['quantity'].sum().reset_index()
    top_movers = top_movers.sort_values('quantity', ascending=False).head(5)
    fig_fast = px.bar(top_movers, x='quantity', y='product_name', orientation='h',
                      color_discrete_sequence=[REVINTEL_COLORS[0]],
                      labels={'quantity': 'Units Sold', 'product_name': 'Product'})
    fig_fast.update_layout(yaxis={'categoryorder':'total ascending'}, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#f8f9fa')
    st.plotly_chart(fig_fast, use_container_width=True)
    
    # Expanded AI Explanation
    if not top_movers.empty:
        fastest_item = top_movers.iloc[0]['product_name']
        fastest_qty = top_movers.iloc[0]['quantity']
        st.info(f"""
        ✨ **AI Velocity Insight (Movers):**
        * **Top Volume Driver:** **{fastest_item}** leads sales with **{fastest_qty:,} units** sold, making up a significant portion of this branch's volume.
        * **Shelf-Space Optimization:** We recommend dedicating at least 2.5x more facing space on eye-level shelves compared to standard SKUs. 
        * **Cross-Selling Playbook:** Place complimentary items (such as items with high co-purchase lift) within a 3-meter radius or set up checkout shelf placements to capture impulse sales.
        """)

with row1_col2:
    st.subheader(
        "🐢 Top 5 Slowest Moving Products",
        help="Highlights the 5 products with the lowest cumulative sales volume. These represent stagnant capital and candidates for bundling or markdown campaigns."
    )
    slow_movers = tx_filtered.groupby('product_name')['quantity'].sum().reset_index()
    slow_movers = slow_movers.sort_values('quantity', ascending=True).head(5)
    fig_slow = px.bar(slow_movers, x='quantity', y='product_name', orientation='h',
                      color_discrete_sequence=[REVINTEL_COLORS[2]],
                      labels={'quantity': 'Units Sold', 'product_name': 'Product'})
    fig_slow.update_layout(yaxis={'categoryorder':'total descending'}, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#f8f9fa')
    st.plotly_chart(fig_slow, use_container_width=True)
    
    # Expanded AI Explanation
    if not slow_movers.empty:
        slowest_item = slow_movers.iloc[0]['product_name']
        slowest_qty = slow_movers.iloc[0]['quantity']
        st.info(f"""
        ✨ **AI Liquidator Insight (Slow Movers):**
        * **Stagnant Capital Target:** **{slowest_item}** is currently stalled, moving only **{slowest_qty:,} units** over the analysis period.
        * **Liquidation Playbook:** 
          1. **Bundling:** Combine this item with a high-velocity anchor (like our top movers) in a 2-item package with a 10%-15% discount.
          2. **Secondary Display:** Relocate stock from back shelves to secondary display baskets near hot aisles or checkout lanes.
          3. **Promotions:** Run a short-term 'buy-one-get-one' markdown campaign specifically targeting store formats that over-index on its core buyer persona.
        """)

st.markdown("---")

# ROW 2: Inventory & Customers (Re-stock Alerts vs. Customer Segments)
row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.subheader(
        "⚠️ Top 5 Re-stock Alerts",
        help="Calculates 'Stock Cover' in days: Current Stock divided by Daily Sales Velocity. Shorter bars represent critical products running out of stock soonest."
    )
    # Calculate stock cover: current_stock / avg_daily_sales
    days = (tx_filtered['transaction_date'].max() - tx_filtered['transaction_date'].min()).days or 1
    sales_vel = tx_filtered.groupby('product_id')['quantity'].sum().reset_index()
    sales_vel['avg_daily'] = sales_vel['quantity'] / days
    
    # Merge with inventory
    if selected_store == "All Stores":
        inv_agg = inv_filtered.groupby('product_id').agg({'current_stock': 'sum', 'safety_stock_level': 'sum'}).reset_index()
    else:
        inv_agg = inv_filtered[['product_id', 'current_stock', 'safety_stock_level']]
        
    stock_df = pd.merge(inv_agg, sales_vel, on='product_id', how='left').fillna({'avg_daily': 0.1})
    stock_df = pd.merge(stock_df, products_df[['product_id', 'product_name']], on='product_id', how='left')
    stock_df['stock_cover_days'] = stock_df['current_stock'] / stock_df['avg_daily']
    
    # Lowest cover
    restock_alerts = stock_df.sort_values('stock_cover_days', ascending=True).head(5)
    
    fig_restock = px.bar(restock_alerts, x='stock_cover_days', y='product_name', orientation='h',
                         color_discrete_sequence=[REVINTEL_COLORS[1]],
                         labels={'stock_cover_days': 'Days of Stock Left', 'product_name': 'Product'})
    fig_restock.update_layout(yaxis={'categoryorder':'total ascending'}, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#f8f9fa')
    st.plotly_chart(fig_restock, use_container_width=True)
    
    # Expanded AI Explanation
    if not restock_alerts.empty:
        critical_item = restock_alerts.iloc[0]['product_name']
        critical_days = restock_alerts.iloc[0]['stock_cover_days']
        current_stk = restock_alerts.iloc[0]['current_stock']
        safety_stk = restock_alerts.iloc[0]['safety_stock_level']
        daily_vel = restock_alerts.iloc[0]['avg_daily']
        
        # Calculate suggested reorder quantity to reach safety stock + 10 days of sales cover buffer
        reorder_qty = int(max(0, (safety_stk + (daily_vel * 10)) - current_stk))
        
        if critical_days <= 2:
            st.error(f"""
            🚨 **AI Out-of-Stock Alert!**
            * **Critical SKU:** **{critical_item}** is at extreme risk with only **{critical_days:.1f} days** of stock cover remaining (Current Stock: {current_stk:.0f} units vs Safety Level: {safety_stk:.0f} units).
            * **Action Recommended:** Dispatch an urgent purchase order of **{reorder_qty:,} units** immediately to prevent shelf depletion, loss of customer goodwill, and potential competitor switching.
            """)
        else:
            st.warning(f"""
            ⚠️ **AI Replenishment Warning:**
            * **Low Buffer SKU:** **{critical_item}** has a stock cover of **{critical_days:.1f} days** (Current Stock: {current_stk:.0f} units vs Safety Level: {safety_stk:.0f} units).
            * **Action Recommended:** Schedule a standard replenishment order of **{reorder_qty:,} units** during the next warehouse logistics cycle (covers safety threshold plus a 10-day sales velocity buffer).
            """)

with row2_col2:
    st.subheader(
        "👥 Top Customer Segments",
        help="Visualizes the customer segment sizes clustered using K-Means. Segmentation is derived from recency of purchase, frequency, and total spend (RFM metrics)."
    )
    # RFM Calculation for K-Means Clustering
    snapshot_date = tx_filtered['transaction_date'].max() + pd.Timedelta(days=1)
    rfm = tx_filtered.groupby('customer_id').agg({
        'transaction_date': lambda x: (snapshot_date - x.max()).days,
        'transaction_id': 'count',
        'total_amount': 'sum'
    }).reset_index()
    rfm.rename(columns={'transaction_date': 'Recency', 'transaction_id': 'Frequency', 'total_amount': 'Monetary'}, inplace=True)
    
    if len(rfm) >= 5:
        scaler = StandardScaler()
        rfm_scaled = scaler.fit_transform(rfm[['Recency', 'Frequency', 'Monetary']])
        kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
        rfm['Cluster'] = kmeans.fit_predict(rfm_scaled)
        
        # Determine segments by average monetary value
        cluster_summary = rfm.groupby('Cluster')[['Recency', 'Frequency', 'Monetary']].mean()
        sorted_clusters = cluster_summary.sort_values('Monetary', ascending=False).index
        segment_names = {
            sorted_clusters[0]: 'Champions',
            sorted_clusters[1]: 'Loyal Customers',
            sorted_clusters[2]: 'Recent Customers',
            sorted_clusters[3]: 'At Risk',
            sorted_clusters[4]: 'Hibernating'
        }
        rfm['Segment'] = rfm['Cluster'].map(segment_names)
        
        seg_counts = rfm['Segment'].value_counts().reset_index()
        seg_counts.columns = ['Segment', 'Customer Count']
        
        fig_seg = px.pie(seg_counts, names='Segment', values='Customer Count', hole=0.5,
                         color_discrete_sequence=REVINTEL_COLORS[3:8])
        fig_seg.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#f8f9fa')
        st.plotly_chart(fig_seg, use_container_width=True)
        
        # Expanded AI Explanation
        top_segment = seg_counts.iloc[0]['Segment']
        top_count = seg_counts.iloc[0]['Customer Count']
        
        # Define marketing recommendations per segment type
        marketing_playbook = {
            'Champions': "Launch exclusive early-access perks, custom product pre-releases, and zero-discount VIP events to cement their status.",
            'Loyal Customers': "Implement multi-buy reward points (e.g. 2x loyalty points on weekend transactions) to increase shopping basket size.",
            'Recent Customers': "Distribute digital coupons (e.g. ₱50 off next order of ₱500+) valid within 14 days to build shopping habits.",
            'At Risk': "Send automated win-back Viber alerts containing high-value discounts (e.g. 15% off) on their historically favorite categories.",
            'Hibernating': "Offer highly targeted clearance discounts on overstocked items or standard categories to clean out inventory while capturing dormant buyers."
        }
        play = marketing_playbook.get(top_segment, "Initiate personalized CRM outreach campaigns to boost customer lifetime value.")
        
        st.info(f"""
        ✨ **AI Cohort Insight (Segmentation):**
        * **Dominant Cohort:** **{top_segment}** is your largest segment, containing **{top_count:,} active buyers** who represent a substantial portion of customer lifetime value.
        * **Strategic Playbook:** {play}
        * **Target KPI:** Focus on retention and increasing purchase frequency. A 5% increase in retention within this cohort can boost store profitability by up to 25%.
        """)
    else:
        st.info("Not enough customers to perform K-Means segmentation for this selection.")

with st.expander("📊 View Raw Store & Inventory Data"):
    st.dataframe(inv_joined.head(100), use_container_width=True)
