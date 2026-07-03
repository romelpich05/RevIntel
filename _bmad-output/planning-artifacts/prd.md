---
title: "RevIntel: A Multi-Module Decision Support System for Revenue Growth Management"
status: draft
created: 2026-07-03
updated: 2026-07-03
---

# RevIntel — Product Requirements Document
**Version 1.1 | Data Science Bootcamp Capstone**

---

## 1. Product Overview

**Product Name:** RevIntel
**Formal Title:** RevIntel: A Multi-Module Decision Support System for Revenue Growth Management — Product Velocity, Customer Segmentation, Discount Optimization, Bundle Recommendation, and Store-Level Location Intelligence
**Tagline:** Right product. Right customer. Right price. Right store.
**Sector:** Fast-Moving Consumer Goods (FMCG) — Retail
**Team:** [Group Name]

RevIntel is a data-driven sales optimization platform built for FMCG retailers. It applies the Revenue Growth Management (RGM) framework — the same approach used by Unilever, Nestlé, and P&G — to help mid-sized retailers make smarter, faster decisions about what to promote, who to target, how deep to discount, and how to bundle products to move slow-moving stock.

---

## 2. Problem Statement

### The FMCG Challenge
FMCG retailers operate on thin net margins of 2–5%. Despite high sales volume, profitability is easily eroded by two recurring problems:

1. **Wasted promotional spend.** An estimated 20–30% of promotional budgets in FMCG produce little to no incremental sales because discounts are applied to products that would have sold anyway, at depths that are either too shallow to drive traffic or too deep to protect margin.

2. **Dead stock.** Slow-moving items tie up valuable shelf space and capital until they are marked down or written off — a direct margin drain.

### Root Cause
The deeper problem is that inventory decisions, customer targeting, and pricing promotions are made by separate teams using separate spreadsheets at separate times. There is no unified system that connects *what is selling*, *who is buying it*, *when to run a promotion*, and *how to package slow stock* into one coherent workflow.

### The Opportunity
RevIntel fills this gap for mid-sized FMCG retailers who cannot afford enterprise RGM software. By turning every promotion into a data-driven decision, RevIntel targets measurable improvements in promotional effectiveness and stock velocity.

---

## 3. Target Users

| User | Role | Primary Need |
|---|---|---|
| Merchandising Manager | Decides what goes on promotion | Know which products need a push and what discount is appropriate |
| Marketing Analyst | Plans customer-facing promotions | Know which customer segments to target with which offer |
| Store Operations Manager | Manages inventory and shelf space | Clear slow-moving stock without excessive markdowns |

---

## 4. Platform Modules

RevIntel is organized into five interconnected modules. The output of each module feeds into the next, forming a complete RGM workflow.

---

### Module 1: Product Velocity Analyzer

**Purpose:** Identify which products are selling fast, which are stalling, and which are effectively dead on the shelf. This is the foundation that drives all other modules.

**Input Data:**
- Transaction records (product ID, quantity sold, date, store)
- Product master data (product name, category, unit price)

**Methodology:**
- **ABC Analysis** classifies products by total revenue contribution: A = top 70%, B = next 20%, C = bottom 10%.
- **XYZ Analysis** classifies products by sales consistency over time: X = stable demand, Y = variable demand, Z = highly irregular demand.
- Combining ABC and XYZ creates a 3×3 grid (e.g., AX = high-revenue, predictable star products; CZ = low-revenue, erratic dead weight).
- **Time series trending** using Facebook Prophet identifies whether a product's velocity is accelerating, stable, or declining.

**Output / Dashboard Feature:**
- Product velocity grid (ABC/XYZ matrix visualization)
- Trending chart per product or category
- Flagged list of slow-moving items (C-class) that need intervention

---

### Module 2: Customer Segmentation

**Purpose:** Identify distinct groups of customers based on their purchasing behavior and preferences, so promotions can be targeted rather than generic.

**Input Data:**
- Transaction records linked to loyalty program members (customer ID, purchase date, amount, store, category)
- Customer profile data (age, gender, marital status, income bracket, membership tier)

**Methodology:**
- **RFM Feature Engineering:** For each customer, compute three behavioral scores:
  - **Recency** — how recently they last made a purchase
  - **Frequency** — how often they purchase
  - **Monetary** — how much they spend on average
- **K-Means Clustering** groups customers into segments based on their RFM scores. The optimal number of clusters (K) is determined using the Elbow Method.
- **Segment profiling:** Each cluster is described by its average demographics and RFM scores, and given a human-readable label (e.g., "High-value loyalists," "Occasional bargain hunters," "Lapsed members").

**Output / Dashboard Feature:**
- Cluster scatter plot (RFM visualization)
- Segment profile cards with key characteristics
- Customer count and revenue contribution per segment

---

### Module 3: Discount Optimizer

**Purpose:** Predict the optimal time to run a promotion and the optimal discount depth for a given product-segment combination — deep enough to drive sales, but not so deep it destroys margin.

**Input Data:**
- Historical transaction data with past promotion records (product, discount %, sales volume during and outside promo)
- Customer segment labels from Module 2
- Product velocity classifications from Module 1

**Methodology:**
- **Price Elasticity Modeling:** For each product, estimate how sensitive sales volume is to a change in price using regression. A product with high elasticity responds strongly to discounts; a low-elasticity product sells roughly the same regardless of price.
- **XGBoost Regression** predicts expected sales lift at different discount levels (e.g., at 10%, 15%, 20% off) for each product-segment pair.
- **Margin Guard:** A rule-based constraint layer ensures the recommended discount does not push gross margin below a configurable threshold.
- **Timing signal:** Combines transaction time patterns (weekday vs weekend, seasonal peaks) with product velocity trend from Module 1 to suggest optimal promotion windows.

**Output / Dashboard Feature:**
- Recommended discount range per product per segment (e.g., "15–20% for Segment B on weekends")
- Projected sales lift and projected margin impact
- Promotion calendar view

---

### Module 4: Bundle Recommender

**Purpose:** Suggest which slow-moving products should be bundled with fast-moving products, and at what combined price. This clears slow stock without training customers to wait for deep standalone discounts.

**Input Data:**
- Transaction records (used to find products frequently bought together)
- Slow-mover list from Module 1 (C-class products)
- Discount output from Module 3 (to price the bundle correctly)

**Methodology:**
- **Association Rule Mining using FP-Growth** identifies products that are frequently purchased together (measured by support, confidence, and lift metrics).
- **Filtering logic:** Bundle candidates are filtered so that at least one item in the pair is a slow-mover (from Module 1's C-class list) and at least one is a fast-mover (A-class). This is the "hero-halo" bundling strategy.
- **Bundle pricing:** The combined bundle price is set using the margin constraint from Module 3, ensuring the fast-moving "hero" product protects overall margin while the slow "halo" product is moved.

**Output / Dashboard Feature:**
- Ranked list of recommended bundles with projected lift
- Bundle price suggestion
- Visual pairing cards (product A + product B → suggested bundle)

---

### Module 5: Store Clustering & Location Intelligence

**Purpose:** Group stores into clusters based on shared physical and commercial characteristics, then use those clusters to predict where a given product sells fastest and where a given customer demographic shops most frequently. This adds a *location* dimension that the other four modules don't cover on their own.

**Input Data:**
- Store master data (category, type, location, size — see Section 5.4)
- Transaction records (to link product performance and customer visits back to stores)
- Product velocity classifications from Module 1
- Customer segment labels from Module 2

**Methodology:**
- **Feature preparation:** Store attributes are encoded into numbers the clustering algorithm can use — categorical fields like category and type are one-hot encoded (turned into 0/1 columns), and size is scaled so it's on a comparable range to the other features.
- **K-Means Clustering** groups stores into clusters based on these encoded features. As with Module 2, the optimal number of clusters is chosen using the Elbow Method.
- **Cross-referencing for product prediction:** For each store cluster, aggregate the Module 1 velocity classifications of products sold there. This produces a "best-selling product profile" per cluster — e.g., "Cluster 2 (small urban convenience stores) sells beverages and snacks fastest."
- **Cross-referencing for customer prediction:** For each store cluster, count how often each customer segment from Module 2 shops there. This produces a "customer segment affinity" per cluster — e.g., "Cluster 1 (large suburban supermarkets) is frequented most by the 'family bulk buyers' segment."

**Output / Dashboard Feature:**
- Store cluster map or grid showing which stores belong to which cluster
- "Best product fit" panel per cluster (which product categories move fastest there)
- "Customer affinity" panel per cluster (which customer segments shop there most)
- Cross-module recommendation: e.g., "Recommend Bundle X in Cluster 2 stores, targeted at Segment B"

---

## 5. Data Requirements

RevIntel will use a **realistic synthetic dataset** generated in Python, modeled after data that mall-based FMCG retailers collect through loyalty programs and point-of-sale systems.

### 5.1 Customer Profile Table

| Field | Data Type | Description | Generation Method |
|---|---|---|---|
| customer_id | String | Unique customer identifier (e.g., C-00142) | Sequential |
| full_name | String | Customer full name | Faker (`name()`) |
| date_of_birth | Date | Used to compute age; also triggers birthday promos | Faker with age distribution |
| gender | Categorical | Male / Female | Weighted random (50/50 or local demographic split) |
| marital_status | Categorical | Single / Married / Separated / Widowed | Weighted random |
| num_children | Integer | Number of children (0–4) | Random, correlated with marital status |
| home_postal_code | String | Determines distance from mall | Faker or sampled from real postal codes |
| income_bracket | Categorical | Monthly income range (e.g., ₱15k–₱30k) | Weighted distribution |
| occupation_type | Categorical | Student / Employed / Self-employed / Retired | Weighted, correlated with income bracket |
| membership_tier | Categorical | Basic / Silver / Gold / Platinum | Correlated with spending history |
| member_since | Date | Date of loyalty program enrollment | Random within last 5 years |
| preferred_payment | Categorical | Cash / Credit Card / Debit Card / E-wallet | Weighted random |

### 5.2 Transaction Table

| Field | Data Type | Description | Generation Method |
|---|---|---|---|
| transaction_id | String | Unique transaction identifier | Sequential |
| customer_id | String | Foreign key linking to customer profile | Sampled from customer table |
| transaction_date | DateTime | Date and time of purchase | Weighted (weekends busier, lunch/evening peaks) |
| store_id | String | Which store the transaction occurred at | Sampled from store list |
| product_id | String | Product purchased | Sampled from product catalog |
| product_category | Categorical | E.g., Beverages, Snacks, Personal Care | Derived from product_id |
| quantity | Integer | Number of units bought | Random (1–5, right-skewed) |
| unit_price | Float | Price per unit | From product catalog |
| discount_pct | Float | Discount applied (0 if no promo) | Occasionally applied based on promo schedule |
| total_amount | Float | Final amount paid | `quantity × unit_price × (1 - discount_pct)` |
| payment_method | Categorical | Cash / Card / E-wallet | Sampled from customer's preferred payment |

### 5.3 Product Catalog Table

| Field | Data Type | Description |
|---|---|---|
| product_id | String | Unique product identifier |
| product_name | String | Product name (e.g., "Yakult 5-pack") |
| category | Categorical | Product category |
| subcategory | Categorical | Product subcategory |
| unit_price | Float | Standard retail price |
| cost_price | Float | Cost to the retailer (used for margin calculations) |
| brand | String | Product brand |

### 5.4 Store Master Table

| Field | Data Type | Description | Generation Method |
|---|---|---|---|
| store_id | String | Unique store identifier | Sequential |
| store_name | String | Store display name | Faker (`company()`) or templated |
| category | Categorical | Supermarket / Convenience / Drugstore / Hypermarket | Weighted random |
| store_type | Categorical | Standalone / Mall-based / Kiosk | Weighted random |
| location_city | String | City or district where the store is located | Sampled from a fixed list of areas |
| location_type | Categorical | Urban / Suburban / Rural | Correlated with location_city |
| size_sqm | Float | Store floor area in square meters | Random, correlated with category (e.g., hypermarkets are larger) |
| size_category | Categorical | Small / Medium / Large | Derived from size_sqm using fixed thresholds |
| opening_year | Integer | Year the store opened | Random within a realistic range |

This table links to the Transaction Table via `store_id`, which is already part of your schema — no changes needed there.

---

## 6. Technical Stack

| Component | Tool / Library | Purpose |
|---|---|---|
| Language | Python 3.10+ | All data processing and ML |
| Data Generation | Faker, NumPy, Pandas | Synthetic dataset creation |
| Data Analysis | Pandas, NumPy | Cleaning, aggregation, feature engineering |
| Machine Learning | Scikit-learn, XGBoost, mlxtend, Prophet | All five module ML components |
| Visualization | Plotly, Matplotlib, Seaborn | Charts and dashboards |
| Application Framework | Streamlit | Interactive web dashboard |
| AI Chatbot | Anthropic Claude API (`claude-sonnet-4-6`) | Dataset-aware Q&A assistant |
| Version Control | Git + GitHub | Source code repository |

---

## 7. Application Features

### 7.1 Home / Overview Dashboard
- Key performance indicators: total revenue, total transactions, active customers, number of slow-moving products
- Summary of current promotions and active bundles
- Quick-access links to each module

### 7.2 Module Pages
Each of the five modules has its own dedicated page in the Streamlit app with its charts, outputs, and actionable recommendations (as described in Section 4).

### 7.3 AI Assistant (RevIntel Chat)
- Powered by the Claude API
- Constrained to answer questions about the loaded dataset only (no general advice)
- Can answer questions like: "Which product category had the most growth last month?" or "What is the best segment to target for a weekend promotion?"
- System prompt includes dataset summaries and computed metrics so the AI has full context

### 7.4 CSV Data Upload
- Users can upload their own transaction CSV (formatted to the RevIntel schema) to run the platform on real or alternative data

---

## 8. Deliverables

Aligned with the capstone rubric:

| Deliverable | Description |
|---|---|
| Working prototype | Streamlit app with all five modules functional and runnable locally |
| Source code | GitHub repository with clean folder structure and a README |
| Synthetic dataset | Generated Python script + output CSV files |
| Written summary | 1–2 page document covering problem, approach, and results |
| Demo + pitch | 8–10 minute live or recorded presentation |

### Recommended Repository Structure
```
shelfiq/
│
├── app/
│   ├── main.py               # Streamlit entry point
│   ├── pages/
│   │   ├── 01_product_velocity.py
│   │   ├── 02_customer_segments.py
│   │   ├── 03_discount_optimizer.py
│   │   ├── 04_bundle_recommender.py
│   │   └── 05_store_clustering.py
│
├── data/
│   ├── generate_dataset.py   # Synthetic data generation script
│   ├── customers.csv
│   ├── transactions.csv
│   ├── products.csv
│   └── stores.csv
│
├── models/
│   ├── segmentation.py       # K-Means clustering logic (customers)
│   ├── velocity.py           # ABC/XYZ + Prophet logic
│   ├── discount.py           # XGBoost price elasticity logic
│   ├── bundles.py            # FP-Growth association rules logic
│   └── store_clustering.py   # K-Means clustering logic (stores)
│
├── utils/
│   └── helpers.py            # Shared functions (formatting, charting)
│
├── requirements.txt
└── README.md
```

---

## 9. Rubric Alignment

| Criterion | Weight | How RevIntel Addresses It |
|---|---|---|
| Problem Significance and Impact | 25% | Addresses real, measurable FMCG pain point (wasted promo spend, dead stock) with clear monetary impact. RGM is a recognized industry framework, lending credibility. |
| Technical Complexity and Innovation | 25% | Five distinct ML techniques (ABC/XYZ + Prophet, K-Means for customers, XGBoost elasticity, FP-Growth, K-Means for stores) working as a connected system — not isolated models. Store Clustering adds a location dimension most competing projects lack. AI chatbot adds a further AI component. |
| Solution Functionality and Completeness | 20% | End-to-end Streamlit app with five working module pages, an AI assistant, and a data upload feature. All modules produce visible, actionable outputs. |
| Data and Methodology | 15% | Realistic synthetic dataset modeled on actual mall loyalty program data. Each module uses appropriate evaluation (silhouette score for clustering, RMSE for regression, lift/confidence for association rules). |
| Presentation and Business Case | 15% | Clear pitch narrative: retailers are leaving money on the table. RevIntel turns every promotion into a data-driven decision. Tagline and module names make the pitch easy to follow for a non-technical audience. |

---

## 10. Suggested Two-Week Timeline

| Day(s) | Task |
|---|---|
| 1–2 | Finalize PRD, divide module ownership among group members, set up GitHub repo |
| 3–4 | Write and run `generate_dataset.py`, explore the synthetic data together |
| 5–6 | Build Module 1 (Product Velocity) and Module 2 (Customer Segments) |
| 7 | Build Module 3 (Discount Optimizer) |
| 8 | Build Module 4 (Bundle Recommender) and Module 5 (Store Clustering) |
| 9 | Integrate all five modules into the Streamlit app |
| 10 | Add AI chatbot (Claude API), home dashboard KPI cards |
| 11 | Test the full app end-to-end, fix bugs |
| 12 | Write the short summary, polish the UI |
| 13 | Rehearse the pitch, record demo if needed |
| 14 | Final presentation |

---

*RevIntel PRD v1.1 — prepared for Data Science Bootcamp Capstone*
