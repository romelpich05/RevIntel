import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from mlxtend.frequent_patterns import apriori, association_rules
from utils import load_data, inject_custom_css, REVINTEL_COLORS

st.set_page_config(page_title="Product Bundler", page_icon="🎁", layout="wide")
inject_custom_css()

st.title("🎁 Product Bundler & Association Cockpit")
st.markdown("Run Market Basket Analysis dynamically, discover co-purchase rules, and simulate bundle profitability.")

with st.spinner("Loading Enterprise Datasets..."):
    stores_df, products_df, customers_df, tx_prod, inventory_df, store_reviews_df = load_data()

# Calculate Velocity to classify Slow vs Fast Movers
days = (tx_prod['transaction_date'].max() - tx_prod['transaction_date'].min()).days or 1
sales_vel = tx_prod.groupby('product_name')['quantity'].sum().reset_index()
sales_vel['avg_daily'] = sales_vel['quantity'] / days
median_vel = sales_vel['avg_daily'].median()

# A product is a "Slow Mover" if its daily velocity is below the median
sales_vel['velocity_class'] = sales_vel['avg_daily'].apply(lambda x: 'Fast' if x >= median_vel else 'Slow')
velocity_map = dict(zip(sales_vel['product_name'], sales_vel['velocity_class']))

st.sidebar.success("✅ Connected to Data Engine")
st.sidebar.markdown("---")
st.sidebar.info("Adjust the parameters directly on the page layout above.")

# Move sliders to the main page top
col_sl1, col_sl2 = st.columns(2)
with col_sl1:
    min_support = st.slider("Min Support (Transaction Frequency)", min_value=0.001, max_value=0.05, value=0.005, step=0.001, format="%.3f", key="bundler_support")
with col_sl2:
    min_lift = st.slider("Min Lift (Association Strength)", min_value=1.0, max_value=5.0, value=1.1, step=0.1, key="bundler_lift")

# Prepare data for Market Basket Analysis
# Group by transaction_id to create baskets
basket = tx_prod.groupby(['transaction_id', 'product_name'])['quantity'].sum().unstack().reset_index().fillna(0)
basket.set_index('transaction_id', inplace=True)

# Convert quantities to boolean (1 if bought, 0 if not)
def encode_units(x):
    return x >= 1

basket_sets = basket.map(encode_units)

# Run Apriori
frequent_itemsets = apriori(basket_sets, min_support=min_support, use_colnames=True)

if frequent_itemsets.empty:
    st.error("Could not find any frequent itemsets. Try lowering the minimum support slider.")
    st.stop()

rules = association_rules(frequent_itemsets, metric="lift", min_threshold=min_lift)

if rules.empty:
    st.warning("No association rules found matching your criteria. Try lowering the minimum lift or support.")
    st.stop()

# Formatting Rules Dataframe
# Convert frozensets to strings
rules['antecedents_str'] = rules['antecedents'].apply(lambda x: ', '.join(list(x)))
rules['consequents_str'] = rules['consequents'].apply(lambda x: ', '.join(list(x)))

# Filter rules: We want to recommend Bundles where Antecedent is a Fast Mover, and Consequent is a Slow Mover
def is_anchor_bundle(row):
    if ',' in row['antecedents_str'] or ',' in row['consequents_str']: return False
    ant_class = velocity_map.get(row['antecedents_str'], 'Slow')
    con_class = velocity_map.get(row['consequents_str'], 'Fast')
    return ant_class == 'Fast' and con_class == 'Slow'

rules['is_strategic_bundle'] = rules.apply(is_anchor_bundle, axis=1)
strategic_bundles = rules[rules['is_strategic_bundle'] == True].sort_values('lift', ascending=False)

tab1, tab2, tab3 = st.tabs(["💡 Strategic Bundles", "🎛️ Bundle ROI Simulator", "🌐 Association Scatter Plot"])

with tab1:
    st.subheader(
        "💡 Strategic Anchor Packages",
        help="Pairs popular Anchor products (high sales velocity) with slow-moving target products that buyers frequently add to the same basket anyway. Selling these as a bundle helps clear slow inventory capital."
    )
    
    if not strategic_bundles.empty:
        # Show Top 3 Showcase Cards
        top_3 = strategic_bundles.head(3)
        cols = st.columns(3)
        for i, (_, row) in enumerate(top_3.iterrows()):
            with cols[i]:
                st.info(f"""
                **Pack {i+1}: The co-purchase booster**
                * **Anchor (Fast):** {row['antecedents_str']}
                * **Target (Slow):** {row['consequents_str']}
                * **Co-purchase rate:** {row['confidence']:.1%}
                * **Association Strength:** {row['lift']:.2f}x lift
                """)
                
        st.markdown("---")
        st.subheader("📋 Complete Recommendations Table")
        
        display_cols = ['antecedents_str', 'consequents_str', 'support', 'confidence', 'lift']
        display_df = strategic_bundles[display_cols].rename(columns={
            'antecedents_str': 'Anchor Product (Fast)',
            'consequents_str': 'Target Product (Slow)',
            'support': 'Support',
            'confidence': 'Confidence',
            'lift': 'Lift'
        })
        display_df['Support'] = display_df['Support'].apply(lambda x: f"{x:.2%}")
        display_df['Confidence'] = display_df['Confidence'].apply(lambda x: f"{x:.2%}")
        display_df['Lift'] = display_df['Lift'].apply(lambda x: f"{x:.2f}x")
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.info("No strategic 'Fast -> Slow' bundles found in the current dataset. Try reducing your Support or Lift thresholds.")

with tab2:
    st.subheader("🎛️ Bundle ROI Simulator")
    st.markdown("Pick a slow-moving product to simulate a bundle campaign and forecast its revenue impact.")
    
    # Isolate slow movers that actually have transaction records
    slow_movers = [k for k, v in velocity_map.items() if v == 'Slow']
    selected_slow = st.selectbox("Select a Slow Moving Product to Liquidate", options=slow_movers)
    
    # Try to find associated anchor
    match_rule = strategic_bundles[strategic_bundles['consequents_str'] == selected_slow]
    
    if not match_rule.empty:
        best_rule = match_rule.sort_values('lift', ascending=False).iloc[0]
        anchor_item = best_rule['antecedents_str']
        association_found = True
        confidence = best_rule['confidence']
        lift = best_rule['lift']
    else:
        # Fallback: Suggest a fast mover in the same category
        slow_category = products_df[products_df['product_name'] == selected_slow]['category'].values[0]
        cat_fast_movers = [k for k, v in velocity_map.items() if v == 'Fast' and products_df[products_df['product_name'] == k]['category'].values[0] == slow_category]
        if cat_fast_movers:
            anchor_item = cat_fast_movers[0]
        else:
            anchor_item = products_df[products_df['product_name'] != selected_slow]['product_name'].values[0]
        association_found = False
        confidence = 0.15 # Assumed baseline
        lift = 1.0

    st.success(f"🎯 **Recommended Pairing**: Pair **{selected_slow}** (Target) with **{anchor_item}** (Anchor).")
    if not association_found:
        st.info("ℹ️ *Note: No direct association rule was found for this slow mover. This recommendation is based on category-based alignment.*")
    else:
        st.success(f"⚡ *Strong Association Found: Buyers of **{anchor_item}** have a **{confidence:.1%}** likelihood of adding **{selected_slow}** to their basket (Lift: {lift:.2f}x).*")

    st.markdown("---")
    
    # Input simulation variables
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        bundle_discount = st.slider("Bundle Discount %", min_value=0, max_value=30, value=10, step=5)
    with col_s2:
        projected_weekly_sales = st.number_input("Anchor Baseline Weekly Sales (Units)", min_value=10, max_value=1000, value=150)
        
    # Get Prices
    p_info_target = products_df[products_df['product_name'] == selected_slow].iloc[0]
    p_info_anchor = products_df[products_df['product_name'] == anchor_item].iloc[0]
    
    target_price = p_info_target['unit_price']
    anchor_price = p_info_anchor['unit_price']
    target_cost = p_info_target['cost_price']
    anchor_cost = p_info_anchor['cost_price']
    
    # Calculations
    normal_combined = target_price + anchor_price
    discounted_combined = normal_combined * (1 - bundle_discount / 100)
    
    # Simulate
    sim_conversion_rate = confidence * (1 + (bundle_discount / 100))
    sim_bundles_sold = int(projected_weekly_sales * sim_conversion_rate)
    
    # ROI Metrics
    bundle_revenue = sim_bundles_sold * discounted_combined
    bundle_cost = sim_bundles_sold * (target_cost + anchor_cost)
    bundle_profit = bundle_revenue - bundle_cost
    
    # Compare to no bundle scenario
    no_bundle_target_sold = int(projected_weekly_sales * 0.05)
    no_bundle_rev = (projected_weekly_sales * anchor_price) + (no_bundle_target_sold * target_price)
    no_bundle_cost = (projected_weekly_sales * anchor_cost) + (no_bundle_target_sold * target_cost)
    no_bundle_profit = no_bundle_rev - no_bundle_cost
    
    profit_delta = bundle_profit - no_bundle_profit
    capital_recovered = sim_bundles_sold * target_price
    
    col_r1, col_r2, col_r3 = st.columns(3)
    with col_r1:
        st.metric("Simulated Weekly Bundles Sold", f"{sim_bundles_sold:,} packs")
    with col_r2:
        st.metric("Net Profit Change", f"₱{profit_delta:,.2f}", 
                  delta="Profitable" if profit_delta >= 0 else "Unprofitable",
                  delta_color="normal" if profit_delta >= 0 else "inverse")
    with col_r3:
        st.metric("Tied Capital Recovered", f"₱{capital_recovered:,.2f}")
        
    st.markdown("""
    * **Simulated Weekly Bundles Sold**: Estimated quantity of customer transactions containing both items under the campaign.
    * **Net Profit Change**: The weekly earnings difference compared to running separate items without a bundle promotion.
    * **Tied Capital Recovered**: Total value of slow-moving inventory liquidated and turned back into cash.
    """)

with tab3:
    st.subheader(
        "🌐 Association Rules Support vs. Confidence Grid",
        help="Maps all generated co-purchase rules. The X-axis represents 'Support' (overall transaction frequency of the pairing). The Y-axis represents 'Confidence' (the conditional probability that buying item A leads to item B). The bubble size and color represent 'Lift' (how many times more likely the pairing is compared to random chance)."
    )
    
    fig = px.scatter(rules, x='support', y='confidence', size='lift', color='lift',
                     hover_data=['antecedents_str', 'consequents_str'],
                     labels={'support': 'Support (Frequency)', 'confidence': 'Confidence (Likelihood)', 'lift': 'Lift'},
                     color_continuous_scale='Viridis', title="Association Rules Distribution")
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#f8f9fa')
    st.plotly_chart(fig, use_container_width=True)
    
    # AI Rule Insight
    strongest_rule = rules.sort_values('lift', ascending=False).iloc[0]
    st.info(f"✨ **AI Association Insight:** The strongest correlation identified is between **{strongest_rule['antecedents_str']}** and **{strongest_rule['consequents_str']}** (Lift: {strongest_rule['lift']:.2f}x, Confidence: {strongest_rule['confidence']:.1%}). Pair these items to drive maximum co-purchase conversions.")
