# 📄 Product Requirements Document (PRD) — RevIntel

## 🚀 RevIntel: Revenue Growth Management (RGM) & Inventory Velocity Platform
*Designed for Philippine Retail Enterprise Optimization*

---

## Slide 1: Executive Summary & Project Mission

### Mission Statement
To maximize gross margin (₱), eliminate stockouts on key volume drivers, and recover tied-up capital from stagnant inventory by ensuring the **right product** is at the **right price** in the **right store** for the **right customer**.

### Target Audience
*   **Executive Board (C-Suite)**: For high-level revenue, cost, and margin analytics.
*   **Category Managers & Merchandisers**: For pricing optimization, BOGO campaigns, and basket bundle configuration.
*   **Store Operations & Logistics Managers**: For store-level restock cover alerts and inter-branch stock transfer rebalancing.

---

## Slide 2: Core Problem Statements

1.  **Stagnant Capital (The Cash Flow Stall)**
    *   *Problem*: Stagnant, slow-moving items sit on shelves for weeks, locking up precious store capital and increasing warehouse carrying costs.
    *   *Impact*: Suppressed cash flows and increased inventory write-off risks.
2.  **Margin Erosion from Inefficient Promotions (The Margin Leak)**
    *   *Problem*: Running flat discounts on price-inelastic staples erodes unit margins without driving a significant volume lift (cannibalization).
    *   *Impact*: Reduced gross profit margins across top departments.
3.  **Assortment Allocation Mismatch (The Distribution Blindspot)**
    *   *Problem*: Allocating a uniform product assortment across all branches regardless of the store's physical square-meter size, city location, or local buyer demographics.
    *   *Impact*: Stockouts on fast-movers in large stores; overstocking of slow-movers in small stores.
4.  **Intuitive Bundling (The Unscientific Cross-Sell)**
    *   *Problem*: Creating product bundles based on intuition rather than co-purchase transaction patterns.
    *   *Impact*: Low promotional take-rates and failed liquidation campaigns.

---

## Slide 3: The Strategic Analytics Approach

RevIntel implements a robust data-science-first architecture:

*   **Price Elasticity Model (Polynomial Regression)**
    *   *Approach*: Fits historical transaction discounts against average daily volume sold to plot the demand curve. Includes an override for demand sensitivity (slope coefficient) to model shifts in inflation or buyer resistance.
*   **Inventory Classifier (Logistic Regression)**
    *   *Approach*: Establishes a predictive baseline classifying SKUs as stagnant (velocity below the median). Normalizes cost, price, and store size variables to present model weights (interpretability) on bar charts.
*   **Market Basket Analysis (Apriori Algorithm)**
    *   *Approach*: Mines transaction logs dynamically based on Support and Lift thresholds. Formulates fast-slow pairs where a high-velocity "Anchor" is bundled to accelerate a slow-moving "Target".
*   **Customer Segmentation (K-Means Clustering)**
    *   *Approach*: Partitions store physical size footprints into distinct formats, and clusters customer transaction history into RFM cohorts (*Champions, Loyal, Recent, At Risk, Hibernating*).

---

## Slide 4: App Solutions & Feature Sets

The RevIntel Streamlit application is organized into 6 presentation-ready modules:

### 1. Executive Portal (`Executive_Portal.py`)
*   **Overall Margin, Promo Spend, & Inventory metrics** at All-Store or single-branch resolutions.
*   **Daily Revenue & Gross Profit Area Trends** to map financial performance peaks.
*   **Grouped Category Revenue vs. Cost Bar Charts** to visual category margin gaps.
*   **Re-stock Cover alerts** mapping days of stock left and calculating the **exact units needed to reorder** to hit safety limits + a 10-day buffer.

### 2. Price & Promo Optimizer (`01_Price_&_Promo_Optimizer.py`)
*   **Interactive Price Elasticity graphs** with a live pink star marker representing the selected strategy.
*   **Buy One Take One (BOGO) Simulator** implementing BOGO psychological attraction multipliers (1.0x-2.5x) and double-COGS metrics.
*   **Capital Deficit alerts** warning the user if cost price exceeds 50% of the simulated BOGO price.

### 3. Product Velocity (`02_Product_Velocity.py`)
*   **Geographical Mapbox Inventory Bubble Maps** displaying stock levels (size) and sales velocity (color) across Metro Manila.
*   **Logistics Stock Transfer Engine** calculating the exact transfer quantity to move stagnant inventory from overstocked slow outlets to high-velocity hubs.

### 4. Fit Matrix Cockpit (`03_Fit_Matrix_Cockpit.py`)
*   **Store Size Format Heatmaps** cross-tabulating sales category performance by K-Means store size formats.
*   **Demographic Indexing Deviations** comparing buyer demographics (Age, Gender, Income, Tier) against baseline company averages.
*   **Shopping Commuter Heatmaps** mapping customer home cities against store cities to classify branches as *Neighborhood Outlets* or *Transit/Commuter Hubs*.

### 5. Product Bundler (`05_Product_Bundler.py`)
*   **Brick-Style Configurator columns** aligned symmetrically.
*   **Fast/Slow status indicators** (`🟢 [Fast]` and `🔴 [Slow]`) embedded directly in selectbox choices.
*   **Multi-item BOGO/Bundle Simulator** (simulates 2, 3, or 4-item bundles) computing packs sold, profit delta, and tied capital recovery.
*   **5 Glaring Co-Purchase Insights** providing actionable cross-selling plays (adjacent layouts, checkout displays, staple bundles).

### 6. Revie Advisor (`07_Revie.py`)
*   **Conversational Virtual Assistant** powered by Gemini 1.5 Flash.
*   Pipes local database summaries (store sizes, best-sellers, feedback) as RAG payloads to answer business questions accurately.

---

## Slide 5: Projected Business Results (Financial & Operational KPIs)

*   **💰 Margin Maximization**: Toggling the optimizer ensures no discounts are wasted on inelastic categories, recovering up to **5%-8% in gross margin leakage**.
*   **🔄 Capital Release (Stock Clearance)**: BOGO and Bundling simulators accelerate the turnover of slow-moving inventory, unlocking up to **₱150,000+ in tied-up capital** per promotional run.
*   **📦 Logistical Cost Reductions**: Rebalancing inventory via the Stock Transfer Engine reduces unnecessary fresh purchasing orders, saving **10%-15% in logistics carrying costs**.
*   **⚡ Replenishment Defense**: Stock-cover alerts and safety buffer reordering prevent out-of-stock events on top movers, ensuring a **98% shelf availability rate**.
