import streamlit as st
import pandas as pd
import numpy as np
import sys
import os
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import load_data, inject_custom_css, REVINTEL_COLORS

st.set_page_config(page_title="Fit Matrix Cockpit", page_icon="🧩", layout="wide")
inject_custom_css()

st.title("🧩 Fit Matrix Cockpit")
st.markdown("Consolidated location intelligence, buyer profiling, and demographic affinity matrices.")

with st.spinner("Synchronizing alignments..."):
    stores_df, products_df, customers_df, tx_prod, inventory_df, store_reviews_df = load_data()

# Preprocess Customer Age & City
current_year = datetime.now().year
customers_df['date_of_birth'] = pd.to_datetime(customers_df['date_of_birth'], errors='coerce')
customers_df['age'] = current_year - customers_df['date_of_birth'].dt.year

def categorize_age(age):
    if pd.isna(age): return 'Unknown'
    if age < 25: return 'Gen Z (<25)'
    if age < 40: return 'Millennials (25-39)'
    if age < 55: return 'Gen X (40-54)'
    return 'Boomers (55+)'

customers_df['age_group'] = customers_df['age'].apply(categorize_age)

st.sidebar.success("✅ Connected to Data Engine")
st.sidebar.markdown("---")
st.sidebar.info("Select filters directly inside each tab below.")

tab1, tab2, tab3 = st.tabs(["🏪 Store & Product Fit", "👥 Customer & Product Fit", "🗺️ Store & Customer Fit"])

# ==================== TAB 1 ====================
with tab1:
    st.subheader(
        "Store Format Clustering & Product Fit",
        help="This tab groups store physical locations into distinct business formats (e.g. Convenience vs Supermarkets) using scikit-learn K-Means clustering, then plots category performance across formats."
    )
    
    col_param, _ = st.columns([1, 2])
    with col_param:
        k_clusters = st.slider("Configure Store K-Means Clusters", min_value=2, max_value=5, value=3, step=1, key="tab1_k_clusters")
    
    # Store K-Means size clustering
    cluster_features = stores_df[['size_sqm']].copy()
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(cluster_features)
    
    kmeans = KMeans(n_clusters=k_clusters, random_state=42, n_init=10)
    stores_df['cluster'] = kmeans.fit_predict(scaled_features)
    
    # Order formats by size average
    cluster_centers = stores_df.groupby('cluster')['size_sqm'].mean().sort_values()
    format_mapping = {}
    
    if k_clusters == 2:
        format_mapping = {cluster_centers.index[0]: 'Small Format', cluster_centers.index[1]: 'Large Format'}
    elif k_clusters == 3:
        format_mapping = {cluster_centers.index[0]: 'Convenience', cluster_centers.index[1]: 'Supermarket', cluster_centers.index[2]: 'Hypermarket'}
    elif k_clusters == 4:
        format_mapping = {cluster_centers.index[0]: 'Kiosk', cluster_centers.index[1]: 'Convenience', cluster_centers.index[2]: 'Supermarket', cluster_centers.index[3]: 'Hypermarket'}
    else:
        format_mapping = {cluster_centers.index[0]: 'Kiosk', cluster_centers.index[1]: 'Convenience', cluster_centers.index[2]: 'Medium Store', cluster_centers.index[3]: 'Supermarket', cluster_centers.index[4]: 'Hypermarket'}
        
    stores_df['Store Format'] = stores_df['cluster'].map(format_mapping)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        fig_stores = px.scatter(stores_df, x='size_sqm', y='store_id', color='Store Format', 
                                hover_data=['location_type', 'store_id'],
                                title=f"Store Clustering by Size (k={k_clusters})",
                                labels={'size_sqm': 'Store Area (sqm)', 'store_id': 'Store ID'},
                                color_discrete_sequence=REVINTEL_COLORS)
        fig_stores.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#f8f9fa')
        st.plotly_chart(fig_stores, use_container_width=True)
        
    with col2:
        st.markdown("### Store Formats Identified")
        format_counts = stores_df['Store Format'].value_counts()
        for fmt, count in format_counts.items():
            st.metric(fmt, f"{count} stores")
            
    # AI Insight for clustering
    largest_format = format_counts.index[0]
    st.info(f"✨ **AI Cluster Insight:** Store size clustering isolates **{largest_format}** as your most common layout format ({format_counts.iloc[0]} outlets). Adjusting assortments specifically for this format will yield the highest chain-wide margin impact.")
            
    st.markdown("---")
    st.subheader(
        "🔥 Product & Store Fit Heatmap",
        help="This cross-tabular heatmap maps product categories against store formats. Darker purple blocks represent product-store format combinations with higher cumulative sales volume or revenue."
    )
    
    # Merge store formats into transactions
    tx_full = pd.merge(tx_prod, stores_df[['store_id', 'Store Format']], on='store_id', how='left')
    
    metric_choice = st.radio("Select Heatmap Metric", ["Sales Volume (Units)", "Total Revenue (₱)"], horizontal=True, key="heat_metric")
    
    if metric_choice == "Sales Volume (Units)":
        pivot_matrix = pd.pivot_table(tx_full, values='quantity', index='Store Format', columns='category', aggfunc='sum').fillna(0)
    else:
        pivot_matrix = pd.pivot_table(tx_full, values='total_amount', index='Store Format', columns='category', aggfunc='sum').fillna(0)
        
    fig_heat = px.imshow(pivot_matrix, text_auto=".0f" if metric_choice == "Sales Volume (Units)" else ".0f", 
                         color_continuous_scale='Purples', aspect="auto",
                         labels=dict(x="Product Category", y="Store Format", color=metric_choice))
    fig_heat.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#f8f9fa')
    st.plotly_chart(fig_heat, use_container_width=True)
    
    # AI Insight for fit heatmap
    max_cat = pivot_matrix.max(axis=0).idxmax()
    max_fmt = pivot_matrix.max(axis=1).idxmax()
    st.info(f"✨ **AI Fit Insight:** **{max_cat}** generates the highest performance within **{max_fmt}** stores. Ensure these items have prime shelf positioning and priority allocation in these locations.")


# ==================== TAB 2 ====================
with tab2:
    st.subheader("Buyer Profile & Demographic Indexing")
    st.markdown("Identify target audiences by comparing the buyer demographics of the selected product against the company average.")
    
    col_t2_1, col_t2_2 = st.columns(2)
    with col_t2_1:
        category_options = ["All"] + list(products_df['category'].unique())
        selected_category = st.selectbox("Filter by Category", options=category_options, key="tab2_cat")
    with col_t2_2:
        if selected_category != "All":
            product_options = products_df[products_df['category'] == selected_category]['product_name'].tolist()
        else:
            product_options = products_df['product_name'].tolist()
        selected_product = st.selectbox("Select Product to Profile", options=product_options, key="tab2_prod")
        
    prod_id = products_df[products_df['product_name'] == selected_product]['product_id'].values[0]
    
    tx_full_cust = pd.merge(tx_prod, customers_df, on='customer_id', how='left')
    tx_target = tx_full_cust[tx_full_cust['product_id'] == prod_id]
    
    if tx_target.empty:
        st.warning("No transactions found for the selected product.")
    else:
        def get_indexing_data(df_target, df_all, col_name):
            target_counts = df_target.groupby(col_name)['quantity'].sum()
            target_dist = (target_counts / target_counts.sum()).to_dict()
            
            baseline_counts = df_all.groupby(col_name)['quantity'].sum()
            baseline_dist = (baseline_counts / baseline_counts.sum()).to_dict()
            
            records = []
            for val in baseline_dist.keys():
                t_val = target_dist.get(val, 0.0)
                b_val = baseline_dist.get(val, 0.0)
                diff = t_val - b_val
                records.append({
                    'Attribute': val,
                    'Target Share': t_val,
                    'Baseline Share': b_val,
                    'Deviation (pp)': diff * 100
                })
            return pd.DataFrame(records).sort_values('Deviation (pp)', ascending=False)
            
        st.subheader(
            "📊 Target Indexing Deviations (Product vs Company Avg)",
            help="Displays how much the buyer share for this product deviates from the average customer baseline. A bar pointing to the right means this group is over-represented (e.g. +10% indicates they purchase this product 10 percentage points more than they purchase other products). Bars to the left indicate under-representation."
        )
        
        idx_age = get_indexing_data(tx_target, tx_full_cust, 'age_group')
        idx_gender = get_indexing_data(tx_target, tx_full_cust, 'gender')
        idx_income = get_indexing_data(tx_target, tx_full_cust, 'income_bracket')
        idx_tier = get_indexing_data(tx_target, tx_full_cust, 'membership_tier')
        
        idx_age['Demographic Type'] = 'Age Group'
        idx_gender['Demographic Type'] = 'Gender'
        idx_income['Demographic Type'] = 'Income Bracket'
        idx_tier['Demographic Type'] = 'Membership Tier'
        
        combined_idx = pd.concat([idx_age, idx_gender, idx_income, idx_tier])
        
        fig_idx = px.bar(combined_idx, x='Deviation (pp)', y='Attribute', color='Demographic Type',
                         orientation='h', barmode='group',
                         title=f"Demographic Indexing Deviation for {selected_product} (Percentage Points)",
                         labels={'Deviation (pp)': 'Deviation from baseline (pp)', 'Attribute': 'Demographic Attribute'},
                         color_discrete_sequence=REVINTEL_COLORS[3:7])
        fig_idx.update_layout(yaxis={'categoryorder':'total ascending'}, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#f8f9fa')
        st.plotly_chart(fig_idx, use_container_width=True)
        
        # AI Persona Summary Card
        top_over_index = combined_idx.sort_values('Deviation (pp)', ascending=False).head(3)['Attribute'].tolist()
        
        st.success(f"""
        🎯 **Target Persona Blueprint**: 
        The core buyers of **{selected_product}** over-index most strongly in: **{', '.join(top_over_index)}**. 
        Tailoring local marketing assets and store placement around these specific groups will maximize velocity.
        """)


# ==================== TAB 3 ====================
with tab3:
    col_t3, _ = st.columns([1, 1])
    with col_t3:
        stores_df['display_name'] = stores_df['store_id'] + " - " + stores_df['store_name'] + " (" + stores_df['location_city'] + ")"
        store_map = dict(zip(stores_df['display_name'], stores_df['store_id']))
        selected_store_display = st.selectbox("Select Store to Analyze Location Fit", options=list(stores_df['display_name'].unique()), key="tab3_store")
    
    selected_store_id = store_map[selected_store_display]
    selected_store_info = stores_df[stores_df['store_id'] == selected_store_id].iloc[0]

    st.subheader(f"Store & Customer Fits for {selected_store_info['store_name']}")
    
    # Merge store formats and details
    tx_cust = pd.merge(tx_prod, customers_df, on='customer_id', how='left')
    tx_cust_store = pd.merge(tx_cust, stores_df, on='store_id', how='left', suffixes=('_cust', '_store'))
    
    # 1. Traffic Heatmap
    st.subheader(
        "🗺️ Shopping Traffic Heatmap (Customer City vs. Store City)",
        help="Maps the customer home city (Y-axis) against the store location city (X-axis). Concentrated blocks tell us if customers are local to the store or if they travel across cities (commuter shoppers) to visit."
    )
    traffic_pivot = pd.crosstab(tx_cust_store['home_city'], tx_cust_store['location_city'])
    fig_traffic = px.imshow(traffic_pivot, text_auto=True, color_continuous_scale='GnBu',
                            labels=dict(x="Store Location City", y="Customer Home City", color="Transactions"))
    fig_traffic.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#f8f9fa')
    st.plotly_chart(fig_traffic, use_container_width=True)
    
    # AI Traffic Insight
    local_city = selected_store_info['location_city']
    local_shoppers_count = traffic_pivot.loc[local_city, local_city] if local_city in traffic_pivot.index and local_city in traffic_pivot.columns else 0
    total_store_shoppers = traffic_pivot[local_city].sum() if local_city in traffic_pivot.columns else 1
    local_ratio = local_shoppers_count / total_store_shoppers
    
    st.info(f"✨ **AI Traffic Insight:** **{local_ratio:.1%}** of shoppers visiting stores in **{local_city}** are local residents (living in the same city). The remaining **{1-local_ratio:.1%}** represents commuter traffic from surrounding municipalities.")
    
    # 2. Demographic Affinity Model
    visitors = tx_cust[tx_cust['store_id'] == selected_store_id]['customer_id'].unique()
    customers_df['visited_target'] = customers_df['customer_id'].isin(visitors).astype(int)
    
    ml_cust = pd.get_dummies(customers_df, columns=['gender', 'income_bracket', 'home_city', 'membership_tier', 'age_group'], drop_first=True)
    feature_cols = [c for c in ml_cust.columns if any(p in c for p in ['gender_', 'income_bracket_', 'home_city_', 'membership_tier_', 'age_group_'])]
    
    if len(visitors) >= 5 and len(customers_df['visited_target'].unique()) > 1:
        X = ml_cust[feature_cols].copy().fillna(0)
        y = ml_cust['visited_target']
        
        log_reg = LogisticRegression(max_iter=1000)
        log_reg.fit(X, y)
        
        st.subheader(
            "🧠 Store Demographic Affinity Coefficients",
            help="Displays the weights of customer attributes predicting their likelihood of visiting this specific store. Positive weights represent demographic groups with high affinity (more likely to visit)."
        )
        
        coeff_df = pd.DataFrame({
            'Demographic Feature': [c.replace('_', ' ').replace('Gender ', '').replace('Income Bracket ', '').replace('Home City ', '').replace('Membership Tier ', '').replace('Age Group ', '').title() for c in feature_cols],
            'Affinity Score': log_reg.coef_[0]
        }).sort_values('Affinity Score', ascending=True)
        
        fig_aff = px.bar(coeff_df, x='Affinity Score', y='Demographic Feature', orientation='h',
                         color_discrete_sequence=[REVINTEL_COLORS[2]])
        fig_aff.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#f8f9fa')
        st.plotly_chart(fig_aff, use_container_width=True)
        
        # AI Affinity Insight
        highest_aff_group = coeff_df.iloc[-1]['Demographic Feature']
        st.info(f"✨ **AI Affinity Insight:** Customers belonging to the **{highest_aff_group}** group have the highest probability coefficient of shopping at this branch.")
    else:
        st.info("Insufficient visitor data to build an affinity model for this store.")
        
    st.markdown("---")
    
    # 3. Store Sentiment Tab & Feedback Keyword Search
    st.subheader("⭐ Customer Feedback & Sentiment Explorer")
    
    store_reviews = store_reviews_df[store_reviews_df['store_id'] == selected_store_id]
    
    if store_reviews.empty:
        st.warning("No customer reviews found for this store.")
    else:
        avg_rating = store_reviews['rating'].mean()
        
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric("Average Rating", f"{avg_rating:.2f} / 5.0 ⭐")
        with col_m2:
            pos_pct = (store_reviews['sentiment'] == 'Positive').mean()
            st.metric("Positive Sentiment", f"{pos_pct:.1%}")
        with col_m3:
            neg_pct = (store_reviews['sentiment'] == 'Negative').mean()
            st.metric("Negative Sentiment", f"{neg_pct:.1%}", delta_color="inverse")
            
        st.markdown("---")
        
        col_s1, col_s2 = st.columns([1, 1.5])
        
        with col_s1:
            st.subheader(
                "Sentiment Breakdown",
                help="A pie chart representing customer review sentiment. Green represents positive reviews, purple represents neutral comments, and red represents negative feedback."
            )
            sentiment_counts = store_reviews['sentiment'].value_counts().reset_index()
            sentiment_counts.columns = ['Sentiment', 'Reviews Count']
            
            fig_sent = px.pie(sentiment_counts, names='Sentiment', values='Reviews Count', hole=0.4,
                              color_discrete_sequence=['#00CC96', '#AB63FA', '#EF553B'])
            fig_sent.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#f8f9fa')
            st.plotly_chart(fig_sent, use_container_width=True)
            
        with col_s2:
            st.markdown("#### Customer Comments & Live Keyword Filter")
            
            sel_sent = st.radio("Sentiment filter", ["All", "Positive", "Neutral", "Negative"], horizontal=True, key="sent_radio")
            keyword_search = st.text_input("🔍 Search comments for keyword (e.g. checkout, AC, staff, rude):", value="", key="search_review_keyword")
            
            filtered_reviews = store_reviews.copy()
            if sel_sent != "All":
                filtered_reviews = filtered_reviews[filtered_reviews['sentiment'] == sel_sent]
                
            if keyword_search.strip() != "":
                filtered_reviews = filtered_reviews[filtered_reviews['review_text'].str.contains(keyword_search, case=False, na=False)]
                
            filtered_reviews = pd.merge(filtered_reviews, customers_df[['customer_id', 'full_name']], on='customer_id', how='left')
            
            review_display = filtered_reviews[['full_name', 'rating', 'review_text', 'sentiment']].copy()
            review_display.columns = ['Customer Name', 'Rating (Stars)', 'Comment', 'Sentiment']
            
            st.dataframe(review_display, use_container_width=True, hide_index=True)
