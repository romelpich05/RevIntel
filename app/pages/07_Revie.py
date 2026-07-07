import streamlit as st
import pandas as pd
import numpy as np
import sys
import os
import requests
import json
from utils import load_data, inject_custom_css

st.set_page_config(page_title="RevIntel | Revie", page_icon="💬", layout="wide")
inject_custom_css()

st.title("💬 Revie")
st.markdown("Query the RevIntel platform context directly with Revie, using the local Pandas analyzer or live Gemini AI.")

with st.spinner("Connecting to Data Engine..."):
    stores_df, products_df, customers_df, tx_prod, inventory_df, store_reviews_df = load_data()

# Sidebar Configuration
st.sidebar.header("AI Status")

# Handle API Key from Environment
api_key = os.environ.get("GEMINI_API_KEY", "")

if api_key:
    st.sidebar.success("🤖 AI Mode Active (Key Loaded)")
else:
    st.sidebar.info("💾 Local Data Mode Active")

# Pre-calculate RAG context summary for Gemini
# Store footprint
store_summary = []
for _, row in stores_df.iterrows():
    store_summary.append(f"- {row['store_name']} ({row['location_city']}): Size {row['size_sqm']} sqm, Type: {row['store_type']}")

# Products velocity
days = (tx_prod['transaction_date'].max() - tx_prod['transaction_date'].min()).days or 1
tx_grouped = tx_prod.groupby('product_name')['quantity'].sum().reset_index().sort_values('quantity', ascending=False)
top_5_products = list(tx_grouped.head(5)['product_name'])
bottom_5_products = list(tx_grouped.tail(5)['product_name'])

# Store feedback
review_summary = []
if not store_reviews_df.empty:
    avg_ratings = store_reviews_df.groupby('store_id')['rating'].mean().reset_index()
    avg_ratings = pd.merge(avg_ratings, stores_df[['store_id', 'store_name']], on='store_id')
    for _, row in avg_ratings.iterrows():
        review_summary.append(f"- {row['store_name']}: {row['rating']:.2f} Stars")

ai_context = f"""
You are Revie, RevIntel's AI Retail Advisor, an expert revenue growth manager and data scientist based in the Philippines.
Below is the summary of the retail store datasets:

Store Footprint:
{os.linesep.join(store_summary)}

Top 5 Best Selling Products (by Volume):
{", ".join(top_5_products)}

Bottom 5 Slowest Moving Products:
{", ".join(bottom_5_products)}

Store Customer Feedback Ratings:
{os.linesep.join(review_summary)}

Answer user questions accurately, professionally, and strategically based on this retail context. Keep recommendations action-oriented. Identify yourself as Revie.
"""

def get_gemini_response(prompt, api_key, context):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [
            {
                "parts": [
                    {"text": f"{context}\n\nUser Question: {prompt}"}
                ]
            }
        ]
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            res_json = response.json()
            return res_json['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Error from Gemini API: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Request failed: {str(e)}"

def get_local_response(prompt):
    prompt_lower = prompt.lower()
    
    if "store" in prompt_lower or "branch" in prompt_lower:
        summary = "Here are the stores currently managed in the platform:\n\n"
        for _, row in stores_df.iterrows():
            summary += f"- **{row['store_name']}** in {row['location_city']} ({row['location_type']} location, size: {row['size_sqm']:,} sqm)\n"
        return summary
        
    elif "restock" in prompt_lower or "inventory" in prompt_lower or "safety" in prompt_lower:
        alerts = inventory_df[inventory_df['current_stock'] <= inventory_df['safety_stock_level']]
        alerts_joined = pd.merge(alerts, products_df[['product_id', 'product_name']], on='product_id')
        alerts_joined = pd.merge(alerts_joined, stores_df[['store_id', 'store_name']], on='store_id')
        
        if not alerts_joined.empty:
            summary = "🚨 **Critical Restock Alerts (Stock <= Safety Level):**\n\n"
            for _, row in alerts_joined.head(10).iterrows():
                summary += f"- **{row['product_name']}** at *{row['store_name']}* (Current: {row['current_stock']} | Safety: {row['safety_stock_level']})\n"
            return summary
        else:
            return "✅ All inventory levels are currently above their safety stock baselines."
            
    elif "velocity" in prompt_lower or "fast" in prompt_lower or "slow" in prompt_lower:
        summary = "🔥 **Top 5 Fastest Moving Products:**\n"
        for p in top_5_products:
            summary += f"- {p}\n"
        
        summary += "\n🐢 **Top 5 Slowest Moving Products:**\n"
        for p in bottom_5_products:
            summary += f"- {p}\n"
        return summary
        
    elif "rating" in prompt_lower or "review" in prompt_lower or "sentiment" in prompt_lower:
        if not store_reviews_df.empty:
            summary = "⭐ **Store Average Ratings:**\n"
            for r in review_summary:
                summary += f"{r}\n"
            return summary
        else:
            return "No review data found."
            
    return """
Hello! I am **Revie**, your virtual RGM assistant. 
    
Currently, I am running in **Local Mode** because no Gemini API Key was supplied. You can ask me questions about:
- **Stores**: Type "show stores"
- **Inventory/Restock**: Type "reorder status" or "restock alerts"
- **Velocity/Movers**: Type "fastest moving products" or "slowest movers"
- **Feedback/Ratings**: Type "customer ratings"
    
*Tip: Set the GEMINI_API_KEY environment variable to unlock open-ended conversational intelligence!*
"""

# Initialize Chat History
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "Hello! I am **Revie**, your virtual RGM assistant. Ask me anything about your stores, sales velocities, restock recommendations, or customer sentiments."}
    ]

# Display Chat History
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if user_query := st.chat_input("Type your question here..."):
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_query)
    st.session_state.chat_history.append({"role": "user", "content": user_query})
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing data..."):
            if api_key:
                response = get_gemini_response(user_query, api_key, ai_context)
            else:
                response = get_local_response(user_query)
            st.markdown(response)
    st.session_state.chat_history.append({"role": "assistant", "content": response})
