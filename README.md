# 🚀 RevIntel: Revenue Growth Management (RGM) & Inventory Velocity Cockpit

RevIntel is an enterprise-grade analytics dashboard and machine learning platform optimized for retail store operations in the Philippines. It combines mathematical demand modeling, K-Means customer segmentation, Logistic Regression classification, and Apriori market basket analysis to solve critical profit erosion and stock velocity issues.

---

## 📌 Problem Statement

Traditional retail managers face three highly correlated inventory and profit-draining problems:
1. **Stagnant Capital Tied Up in Stock**: Slow-moving products sit on store shelves for weeks, draining liquidity and increasing warehouse overhead, with no active mechanism to clear them.
2. **Margin Erosion from Flat Discounts**: Standard "one-size-fits-all" promotional markdowns are frequently applied to price-inelastic staples. This erodes the store's gross profit margin (₱) without triggering any corresponding lift in transactional volume.
3. **Distribution & Assortment Mismatch**: Store locations receive uniform catalog allocations regardless of their local neighborhood demographics, physical layout constraints (sqm size), or customer travel flows (neighborhood vs. commuter hubs).
4. **Intuition-Based Cross-Selling**: Product bundles are created using gut feelings rather than empirical transaction co-purchase probabilities, resulting in low campaign take-rates.

---

## 🛠️ Technical Approach & Analytics Engine

RevIntel solves these challenges by combining transactional data pipelines with classic statistical learning baselines:

### 1. Pricing Elasticity of Demand (Polynomial Regression)
* Fits historical price/discount values against daily sales volumes using a polynomial trendline.
* Models interactive **Demand Sensitivity (Slope overrides)** to let managers simulate how customer price resistance changes during economic shifts.
* Includes a **Buy One Take One (BOGO) Simulator** mapping psychological attraction factors (1.0x-2.5x volume lift multipliers) against compound unit COGS.

### 2. Inventory Stagnancy Classification (Logistic Regression)
* Establishes a predictive baseline classifying whether an SKU is at risk of becoming a "Slow Mover" (sales velocity falling below the median).
* Normalizes features (cost, price, discount, store size, and location formats) using `StandardScaler`.
* Renders scikit-learn coefficients on horizontal charts, giving business users full model interpretability (identifying *Stagnancy Accelerators* vs. *Velocity Accelerators*).

### 3. Basket Co-Purchase Mining (Apriori Algorithm)
* Runs transactional Market Basket Analysis dynamically based on user-configured **Min Support** and **Min Lift** parameters.
* Identifies **Strategic Anchor Packages** where high-velocity items (Anchors) are paired with slow-moving targets to boost basket values and liquidate slow inventory.

### 4. Location & Demographic Alignment (K-Means Clustering)
* Clusters stores physically by square-meter footprints into formats (e.g. *Convenience*, *Supermarket*, *Hypermarket*).
* Segments customer bases using K-Means over Recency, Frequency, and Monetary (RFM) metrics to group shoppers into cohorts (*Champions*, *Loyal*, *Recent*, *At Risk*, *Hibernating*).

---

## 🖥️ App Solutions & Module Walkthrough

RevIntel's Streamlit-powered presentation layer is styled with a premium dark HSL design system and structured into 6 main modules:

### 1. 🚀 Executive Portal (`app/Executive_Portal.py`)
* The core management dashboard providing a chain-wide or branch-level financial health check.
* **KPI Metrics**: Real-time tracking of **Overall Margin (%)**, **Promo Discounts Given (₱)**, and **Inventory Capital (₱)**.
* **Financial Trends**: Area charts displaying daily gross sales vs. profit margins to visualize performance peaks.
* **Stock Cover Alerts**: Tracks "Stock Cover" in days, and recommends the **exact reorder quantity** needed to reach safety stock plus a 10-day buffer.
* **K-Means Segment Allocation**: Pie charts mapping active segments alongside CRM Viber/coupon campaign recommendations.

### 2. 📉 Price & Promo Optimizer (`app/pages/01_Price_&_Promo_Optimizer.py`)
* Lets managers run simulated pricing campaigns before executing markdowns.
* **Elasticity Scatter Plot**: Displays price-volume points with a live **pink star marker** showing the selected strategy coordinate on the curve.
* **BOGO Sandbox**: Simulates buy-one-get-one deals, triggering **Negative Margin Safety Alerts** if the unit cost exceeds 50% of the simulated price.

### 3. ⚡ Product Velocity (`app/pages/02_Product_Velocity.py`)
* Focuses on SKU operations and inter-branch stock logistics.
* **Mapbox Bubble Map**: Projects store inventory levels (bubble size) and daily velocity (bubble color) geographically over Metro Manila.
* **Logistics Transfer Engine**: Automatically calculates **inter-branch stock transfer quantities** to move excess inventory from slow outlets directly to sales hotspot locations.

### 4. 🧩 Fit Matrix Cockpit (`app/pages/03_Fit_Matrix_Cockpit.py`)
* Consolidated demographics, buyer profiling, and traffic tracking.
* **Store Format Fit Heatmap**: Cross-tabulates category sales revenue against K-Means store formats.
* **Demographic Indexing Deviation**: Grouped bar charts showing how buyer profiles of individual products deviate from the store average.
* **Shopping Commuter Heatmap**: Maps customer home cities to store locations to classify branches as *Neighborhood neighborhood stores* or *Transit commuter hubs*.

### 5. 🎁 Product Bundler (`app/pages/05_Product_Bundler.py`)
* An interactive multi-item bundle sandbox.
* **Strategic Bundle Cards**: Presents top fast-slow pairs automatically.
* **Bundle ROI Simulator**: Users can configure 2-item, 3-item, or 4-item bundles. Selectboxes are sorted from fastest to slowest selling products and color-coded with status badges:
  * 🟢 `[Fast]` for fast-moving anchors.
  * 🔴 `[Slow]` for stagnant targets.

### 6. 💬 Revie Chatbot (`app/pages/07_Revie.py`)
* A virtual RGM conversational assistant.
* Operates in **Local Mode** using a local Pandas query parser or **AI Mode** leveraging Gemini 1.5 Flash (via RAG context payloads containing store size, best-selling SKUs, and ratings data).

---

## 📈 Projected Business Results

RevIntel is engineered to drive immediate operational improvements:
* **Tied Capital Recovery**: Releasing stagnant inventory via target BOGO or strategic fast-slow bundles transforms dead stock back into active cash flow.
* **Margin Preservation**: Outlawing discounts on inelastic categories (identified by the optimizer) prevents margin leaks.
* **Replenishment Accuracy**: Transitioning from static buffers to dynamic stock-cover replenishment reduces stockouts on top movers by up to 35%.

---

## 🚀 Setup & Execution

Ensure you have Python 3.10+ installed. Follow these steps to run the application locally:

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```
*(Or use the fast `uv` environment runner: `uv pip install -r requirements.txt`)*

### 2. Initialize Synthetic Dataset (Optional)
Generate the database logs:
```bash
python data/generate_dataset.py
```

### 3. Launch Streamlit Application
```bash
streamlit run app/Executive_Portal.py
```
Open **http://localhost:8501** in your web browser.

---

### 🔑 AI Mode Setup
To unlock conversational capabilities inside the **Revie Chatbot**:
1. Get a free Gemini API Key from Google AI Studio.
2. Enter your key inside the chatbot page sidebar, or export it as an environment variable before launching Streamlit:
```powershell
$env:GEMINI_API_KEY="your-api-key-here"
```
