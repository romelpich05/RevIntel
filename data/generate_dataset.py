# /// script
# dependencies = [
#   "faker",
#   "pandas",
#   "numpy",
# ]
# ///

import os
import random
import datetime
import numpy as np
import pandas as pd
from faker import Faker

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

# Initialize Faker
fake = Faker()

print("Generating synthetic datasets for RevIntel RGM Decision Support System...")

# ==========================================
# 1. GENERATE STORES (10 Stores)
# ==========================================
print("1. Generating store master data...")
store_categories = ["Supermarket", "Convenience", "Drugstore", "Hypermarket"]
store_types = ["Standalone", "Mall-based", "Kiosk"]
philippine_cities = ["Makati", "Quezon City", "Taguig", "Pasig", "Mandaluyong", "Manila", "Alabang"]

stores = []
for i in range(1, 11):
    store_id = f"S-{i:02d}"
    
    # Correlate category, type, and size
    if i == 1:
        category = "Hypermarket"
        store_type = "Standalone"
        size_sqm = random.uniform(5000, 8000)
        city = "Quezon City"
        loc_type = "Suburban"
    elif i in [2, 3, 4, 5]:
        category = "Supermarket"
        store_type = "Mall-based" if i % 2 == 0 else "Standalone"
        size_sqm = random.uniform(1500, 3000)
        city = philippine_cities[i % len(philippine_cities)]
        loc_type = "Suburban" if i % 3 != 0 else "Urban"
    elif i in [6, 7, 8]:
        category = "Convenience"
        store_type = "Kiosk" if i == 8 else "Standalone"
        size_sqm = random.uniform(50, 150)
        city = philippine_cities[(i + 1) % len(philippine_cities)]
        loc_type = "Urban"
    else:
        category = "Drugstore"
        store_type = "Mall-based" if i == 9 else "Standalone"
        size_sqm = random.uniform(100, 300)
        city = philippine_cities[(i + 2) % len(philippine_cities)]
        loc_type = "Urban"
        
    size_category = "Large" if size_sqm > 3000 else "Medium" if size_sqm > 500 else "Small"
    opening_year = random.randint(2015, 2023)
    store_name = f"RevIntel {category} - {city}"
    
    stores.append({
        "store_id": store_id,
        "store_name": store_name,
        "category": category,
        "store_type": store_type,
        "location_city": city,
        "location_type": loc_type,
        "size_sqm": round(size_sqm, 2),
        "size_category": size_category,
        "opening_year": opening_year
    })

df_stores = pd.DataFrame(stores)
df_stores.to_csv("data/stores.csv", index=False)
print(f"Generated {len(df_stores)} stores.")

# ==========================================
# 2. GENERATE PRODUCTS (50 Products)
# ==========================================
print("2. Generating product catalog...")
product_templates = {
    "Beverages": [
        ("Coke 1.5L", "Soft Drinks", 65.0, "Coca-Cola", -2.5, "A", "X"),
        ("Sprite 1.5L", "Soft Drinks", 63.0, "Coca-Cola", -2.4, "B", "X"),
        ("Royal Orange 1.5L", "Soft Drinks", 63.0, "Coca-Cola", -2.2, "B", "Y"),
        ("Mineral Water 500ml", "Water", 18.0, "Nature Spring", -0.5, "A", "X"),
        ("Red Bull 250ml", "Energy Drinks", 90.0, "Red Bull", -1.8, "B", "X"),
        ("Malee Coconut Water", "Juices", 110.0, "Malee", -1.5, "C", "Z"),
        ("Del Monte Pineapple Juice", "Juices", 85.0, "Del Monte", -1.3, "B", "X"),
        ("San Miguel Pale Pilsen 320ml", "Beer", 55.0, "San Miguel", -2.0, "A", "Y"),
        ("San Miguel Light 320ml", "Beer", 58.0, "San Miguel", -2.1, "A", "Y"),
        ("Nestea Iced Tea Pitcher Pack", "Powdered Drinks", 25.0, "Nestle", -1.1, "B", "Y")
    ],
    "Snacks": [
        ("Piattos Cheese 85g", "Chips", 38.0, "Jack 'n Jill", -2.6, "A", "X"),
        ("Nova Multigrain 78g", "Chips", 36.0, "Jack 'n Jill", -2.1, "B", "X"),
        ("Chippy Barbecue 110g", "Chips", 32.0, "Jack 'n Jill", -2.2, "B", "X"),
        ("SkyFlakes Crackers 10s", "Biscuits", 55.0, "M.Y. San", -0.7, "A", "X"),
        ("Fudgee Barr Chocolate 10s", "Cakes", 78.0, "Rebisco", -1.4, "B", "X"),
        ("Grom Gourmet Cheese Platter", "Cheese & Nuts", 350.0, "Gourmet", -1.2, "C", "Z"), # Halo for Beer
        ("Oreo Double Stuf 133g", "Cookies", 52.0, "Mondelez", -2.0, "B", "X"),
        ("Growers Salted Peanuts 80g", "Nuts", 45.0, "Growers", -1.5, "B", "X"),
        ("Lays Classic 170g", "Chips", 145.0, "Frito-Lay", -2.3, "B", "Y"),
        ("Pringles Sour Cream 107g", "Chips", 98.0, "Pringles", -2.2, "B", "X")
    ],
    "Personal Care": [
        ("Creamsilk Conditioner 180ml", "Hair Care", 145.0, "Unilever", -1.2, "A", "X"),
        ("Organic Herbal Hair Serum", "Hair Care", 450.0, "Natures", -0.9, "C", "Z"), # Halo for Shampoo
        ("Sunsilk Shampoo 180ml", "Hair Care", 138.0, "Unilever", -1.5, "A", "X"),
        ("Colgate Great Regular 150g", "Oral Care", 125.0, "Colgate", -0.8, "A", "X"),
        ("Safeguard White Soap 130g", "Bath & Body", 60.0, "P&G", -0.6, "A", "X"),
        ("Dove Beauty Bar Soap 100g", "Bath & Body", 85.0, "Unilever", -0.9, "B", "X"),
        ("Nivea Body Lotion 250ml", "Bath & Body", 230.0, "Beiersdorf", -1.4, "B", "Y"),
        ("Rexona Men Deodorant 50ml", "Deodorants", 115.0, "Unilever", -1.0, "B", "X"),
        ("Gillette Vector Razor 2s", "Shaving", 120.0, "P&G", -0.8, "B", "X"),
        ("Kleenex Facial Tissue 3-pack", "Paper & Cotton", 160.0, "Kimberly-Clark", -0.7, "B", "X")
    ],
    "Frozen Food": [
        ("Tender Juicy Hotdog 1kg", "Processed Meat", 240.0, "Purefoods", -1.6, "A", "X"),
        ("CDO Karne Norte 150g", "Canned Meat", 35.0, "CDO", -1.1, "B", "X"),
        ("Purefoods Corned Beef 150g", "Canned Meat", 88.0, "Purefoods", -0.9, "A", "X"),
        ("Swift Mighty Meaty Spaghetti Sauce 1kg", "Sauces", 110.0, "Swift", -1.3, "B", "X"),
        ("Bellagio Premium Frozen Wagyu Beef Burger 4s", "Beef Pat", 699.0, "Bellagio", -1.1, "C", "Z"),
        ("Frozen Mixed Vegetables 500g", "Vegetables", 120.0, "Golden", -1.2, "B", "X"),
        ("Century Tuna Flakes in Oil 180g", "Canned Fish", 48.0, "Century", -0.8, "A", "X"),
        ("555 Sardines Tomato Sauce 155g", "Canned Fish", 24.0, "555", -0.6, "B", "X"),
        ("Marby Frozen Siomai 30s", "Dimsum", 165.0, "Marby", -1.5, "B", "X"),
        ("Frozen French Fries 1kg", "Potato", 185.0, "Aviko", -1.9, "B", "Y")
    ],
    "Bakery": [
        ("Gardenia Classic White Bread", "Sliced Bread", 85.0, "Gardenia", -0.5, "A", "X"),
        ("Gardenia Wheat Bread", "Sliced Bread", 95.0, "Gardenia", -0.8, "B", "X"),
        ("Premium Gluten-Free Organic Granola Oats", "Cereal", 420.0, "OrganicWay", -1.0, "C", "Z"), # Halo for Sliced Bread
        ("Goldilocks Mamon 6s", "Sweet Treats", 150.0, "Goldilocks", -1.3, "B", "X"),
        ("Monde Special Muffin 6s", "Sweet Treats", 92.0, "Monde M.Y. San", -1.4, "B", "X"),
        ("Spanish Bread 6-pack", "Local Breads", 45.0, "RevIntel Bakery", -0.8, "B", "X"),
        ("Pandesal 10s bag", "Local Breads", 30.0, "RevIntel Bakery", -0.6, "A", "X"),
        ("Kraft Cheez Whiz 450g", "Spreads", 195.0, "Kraft", -1.6, "A", "X"),
        ("Lady's Choice Mayonnaise 220ml", "Spreads", 125.0, "Unilever", -1.2, "B", "X"),
        ("Lily's Peanut Butter 364g", "Spreads", 165.0, "Lily's", -1.1, "B", "X")
    ]
}

products = []
p_counter = 1
for category, items in product_templates.items():
    for item in items:
        product_id = f"P-{p_counter:02d}"
        p_name, subcat, price, brand, elasticity, abc_class, xyz_class = item
        
        # Calculate cost price to ensure a margin between 20% and 40%
        margin = random.uniform(0.20, 0.40)
        cost_price = price * (1.0 - margin)
        
        products.append({
            "product_id": product_id,
            "product_name": p_name,
            "category": category,
            "subcategory": subcat,
            "unit_price": price,
            "cost_price": round(cost_price, 2),
            "brand": brand,
            "elasticity": elasticity,
            "abc_class": abc_class,
            "xyz_class": xyz_class
        })
        p_counter += 1

df_products = pd.DataFrame(products)
df_products.to_csv("data/products.csv", index=False)
print(f"Generated {len(df_products)} products.")

# ==========================================
# 3. GENERATE CUSTOMERS (1,000 Customers)
# ==========================================
print("3. Generating customer profiles...")
income_brackets = ["Under ₱15k", "₱15k-₱30k", "₱30k-₱60k", "₱60k-₱100k", "Over ₱100k"]
occupations = ["Student", "Private Employee", "Government Employee", "Self-employed", "Retired", "Unemployed"]
membership_tiers = ["Basic", "Silver", "Gold", "Platinum"]
payments = ["Cash", "Credit Card", "Debit Card", "E-wallet"]

customers = []
for i in range(1, 1001):
    customer_id = f"C-{i:05d}"
    full_name = fake.name()
    
    # Generate age between 18 and 75
    age = random.randint(18, 75)
    dob = datetime.date.today() - datetime.timedelta(days=int(age * 365.25))
    
    gender = random.choices(["Male", "Female"], weights=[48, 52])[0]
    
    # Correlate marital status and number of children with age
    if age < 25:
        marital_status = "Single"
        num_children = 0
    elif age < 45:
        marital_status = random.choices(["Single", "Married", "Separated"], weights=[30, 60, 10])[0]
        num_children = random.choices([0, 1, 2, 3], weights=[30, 40, 20, 10])[0] if marital_status == "Married" else 0
    else:
        marital_status = random.choices(["Married", "Separated", "Widowed", "Single"], weights=[65, 15, 10, 10])[0]
        num_children = random.choices([0, 1, 2, 3, 4], weights=[20, 30, 30, 15, 5])[0] if marital_status == "Married" else 0
        
    home_postal_code = f"1{random.randint(0, 9):03d}"
    
    # Occupation correlated with age
    if age < 22:
        occupation = random.choices(["Student", "Unemployed", "Private Employee"], weights=[75, 15, 10])[0]
    elif age > 60:
        occupation = random.choices(["Retired", "Self-employed"], weights=[85, 15])[0]
    else:
        occupation = random.choices(["Private Employee", "Government Employee", "Self-employed", "Unemployed"], weights=[60, 15, 20, 5])[0]
        
    # Income correlated with occupation
    if occupation == "Student" or occupation == "Unemployed":
        income = random.choices(["Under ₱15k", "₱15k-₱30k"], weights=[85, 15])[0]
    elif occupation == "Retired":
        income = random.choices(["Under ₱15k", "₱15k-₱30k", "₱30k-₱60k"], weights=[40, 50, 10])[0]
    elif occupation == "Self-employed":
        income = random.choices(["₱15k-₱30k", "₱30k-₱60k", "₱60k-₱100k", "Over ₱100k"], weights=[20, 40, 30, 10])[0]
    else: # Employee
        income = random.choices(["₱15k-₱30k", "₱30k-₱60k", "₱60k-₱100k", "Over ₱100k"], weights=[30, 45, 20, 5])[0]
        
    # Membership tier correlated with income
    income_idx = income_brackets.index(income)
    if income_idx <= 1:
        tier = random.choices(["Basic", "Silver"], weights=[90, 10])[0]
    elif income_idx == 2:
        tier = random.choices(["Basic", "Silver", "Gold"], weights=[50, 40, 10])[0]
    else:
        tier = random.choices(["Silver", "Gold", "Platinum"], weights=[30, 50, 20])[0]
        
    member_since = datetime.date(2021, 1, 1) + datetime.timedelta(days=random.randint(0, 1800))
    preferred_payment = random.choices(payments, weights=[35, 25, 15, 25])[0]
    
    # Assign hidden customer segment type to guide transaction generation
    if tier in ["Gold", "Platinum"] and income_idx >= 3:
        behavior_class = "VIP Loyalist"
    elif tier == "Basic" and income_idx <= 1 and random.random() < 0.6:
        behavior_class = "Bargain Hunter"
    elif random.random() < 0.15:
        behavior_class = "Sleeper"
    else:
        behavior_class = "Average Shopper"
        
    customers.append({
        "customer_id": customer_id,
        "full_name": full_name,
        "date_of_birth": dob,
        "gender": gender,
        "marital_status": marital_status,
        "num_children": num_children,
        "home_postal_code": home_postal_code,
        "income_bracket": income,
        "occupation_type": occupation,
        "membership_tier": tier,
        "member_since": member_since,
        "preferred_payment": preferred_payment,
        "behavior_class": behavior_class # Used for generation only, dropped later or kept for validation
    })

df_customers = pd.DataFrame(customers)
# Save version with behavior class for verification, but we will write a clean version without it
df_customers_clean = df_customers.drop(columns=["behavior_class"])
df_customers_clean.to_csv("data/customers.csv", index=False)
print(f"Generated {len(df_customers)} customers.")

# ==========================================
# 4. GENERATE TRANSACTIONS (35,000 Transactions)
# ==========================================
print("4. Generating transaction records...")
start_date = datetime.datetime(2025, 7, 1)
end_date = datetime.datetime(2026, 6, 30)
days_to_generate = (end_date - start_date).days + 1

# Pre-define weekly promotions for Module 3 (Discount Optimizer)
# Each week (52 weeks), 3 random products will be on promotion at a specific store or all stores
promo_calendar = {}
all_product_ids = df_products["product_id"].tolist()
for week in range(53):
    promo_products = random.sample(all_product_ids, 5)
    promo_discounts = [random.choice([0.10, 0.15, 0.20, 0.25, 0.30]) for _ in range(5)]
    promo_calendar[week] = dict(zip(promo_products, promo_discounts))

transactions = []
t_counter = 1

# Define purchase rules for associations (Module 4: Bundle Recommender)
# (Hero product A -> Halo product B)
association_pairs = [
    ("P-08", "P-16", 0.65),  # San Miguel Pale Pilsen (Fast A) -> Gourmet Cheese Platter (Slow C)
    ("P-09", "P-16", 0.60),  # San Miguel Light (Fast A) -> Gourmet Cheese Platter (Slow C)
    ("P-41", "P-43", 0.70),  # Gardenia Sliced Bread (Fast A) -> Organic Granola Oats (Slow C)
    ("P-23", "P-22", 0.55),  # Sunsilk Shampoo (Fast A) -> Organic Hair Serum (Slow C)
    ("P-31", "P-34", 0.50)   # TJ Hotdog (Fast A) -> Swift Spaghetti Sauce (Medium B)
]

for day_idx in range(days_to_generate):
    current_day = start_date + datetime.timedelta(days=day_idx)
    day_of_week = current_day.weekday() # 0 = Monday, 6 = Sunday
    week_number = day_idx // 7
    
    # 1. Determine base transactions for the day
    base_tx_count = 60 # average daily transactions
    
    # Weekend multiplier (Friday, Saturday, Sunday)
    if day_of_week in [4, 5, 6]:
        base_tx_count = int(base_tx_count * random.uniform(1.5, 2.0))
        
    # Seasonality multipliers
    # Summer peak (March = 2, April = 3, May = 4)
    if current_day.month in [3, 4, 5]:
        base_tx_count = int(base_tx_count * random.uniform(1.1, 1.3))
    # December Holiday peak (December = 11)
    elif current_day.month == 12:
        base_tx_count = int(base_tx_count * random.uniform(1.6, 2.2))
    # Holiday slump (January = 0)
    elif current_day.month == 1:
        base_tx_count = int(base_tx_count * random.uniform(0.7, 0.9))
        
    # Random daily fluctuation
    daily_tx_count = int(base_tx_count * random.uniform(0.85, 1.15))
    
    # 2. Select customer list for this day
    # VIPs shop often, Sleepers rarely, Bargain Hunters on promo weekends
    weights = []
    for c in customers:
        b_class = c["behavior_class"]
        if b_class == "VIP Loyalist":
            weights.append(0.65)
        elif b_class == "Bargain Hunter":
            # high weight on promo weekends
            weights.append(0.50 if day_of_week in [4, 5, 6] else 0.10)
        elif b_class == "Sleeper":
            weights.append(0.04)
        else: # Average
            weights.append(0.25)
            
    # Normalize weights
    weights = np.array(weights)
    weights /= weights.sum()
    
    shopping_customers = np.random.choice(customers, size=min(daily_tx_count, 400), replace=False, p=weights)
    
    # 3. Generate transactions for selected customers
    for customer in shopping_customers:
        b_class = customer["behavior_class"]
        
        # Decide which store the customer visits (affinity logic)
        # Convenience stores are visited more by single/young people, Hypermarkets by large families
        store_weights = [1.0] * 10
        
        # Store 1 is Hypermarket (large size, standalone, Quezon City)
        # Store 6,7,8 are Convenience (small size, urban)
        # Store 9,10 are Drugstores (medium size)
        
        if customer["num_children"] >= 2:
            store_weights[0] = 3.0  # Hypermarket
            store_weights[1] = 2.0  # Supermarket 2
            store_weights[5] = 0.2  # Convenience 1 (fewer convenience visits)
            store_weights[6] = 0.2
        elif customer["date_of_birth"].year > 2000: # younger
            store_weights[5] = 4.0  # Convenience
            store_weights[6] = 4.0
            store_weights[7] = 4.0
            store_weights[0] = 0.5  # Hypermarket
            
        store_weights = np.array(store_weights)
        store_weights /= store_weights.sum()
        
        store = np.random.choice(stores, p=store_weights)
        store_id = store["store_id"]
        
        # Generate random time of purchase
        hour = random.choices(
            [8,9,10, 11,12,13, 14,15,16, 17,18,19, 20,21], 
            weights=[5,8,10, 18,20,15, 10,12,15, 25,30,22, 10,5]
        )[0]
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        tx_datetime = datetime.datetime(
            current_day.year, current_day.month, current_day.day,
            hour, minute, second
        )
        
        # Generate basket size based on customer class
        if b_class == "VIP Loyalist":
            basket_size = random.randint(3, 8)
        elif b_class == "Bargain Hunter":
            basket_size = random.randint(1, 4)
        elif b_class == "Sleeper":
            basket_size = random.randint(1, 3)
        else:
            basket_size = random.randint(1, 5)
            
        # Select items for the basket
        basket_items = []
        
        # Core product selection weights based on category preferences
        # Convenience stores sell mostly Beverages and Snacks
        cat_weights = {
            "Beverages": 1.0,
            "Snacks": 1.0,
            "Personal Care": 0.8,
            "Frozen Food": 0.7,
            "Bakery": 0.9
        }
        if store["category"] == "Convenience":
            cat_weights["Beverages"] = 4.0
            cat_weights["Snacks"] = 3.5
            cat_weights["Frozen Food"] = 0.2
            cat_weights["Personal Care"] = 0.4
        elif store["category"] == "Drugstore":
            cat_weights["Personal Care"] = 5.0
            cat_weights["Beverages"] = 1.0
            cat_weights["Snacks"] = 1.0
            cat_weights["Frozen Food"] = 0.0
            cat_weights["Bakery"] = 0.0
            
        # Add demographic preferences
        if customer["num_children"] >= 2:
            cat_weights["Frozen Food"] *= 2.0 # PJ Hotdogs, etc.
            cat_weights["Bakery"] *= 1.5
        if customer["gender"] == "Female":
            cat_weights["Personal Care"] *= 1.4
            
        # Map category weights to products
        product_probs = []
        for p in products:
            p_cat = p["category"]
            p_abc = p["abc_class"]
            
            # Base probability from category weight
            prob = cat_weights.get(p_cat, 1.0)
            
            # ABC classification weight modifier (A items bought much more often)
            if p_abc == "A":
                prob *= 4.0
            elif p_abc == "B":
                prob *= 1.5
            else: # C
                prob *= 0.3
                
            # If the product is on promotion today, increase probability (especially for Bargain Hunters)
            is_promo = p["product_id"] in promo_calendar[week_number]
            if is_promo:
                promo_discount = promo_calendar[week_number][p["product_id"]]
                if b_class == "Bargain Hunter":
                    prob *= (1.0 + abs(p["elasticity"]) * promo_discount * 5.0) # very sensitive
                else:
                    prob *= (1.0 + abs(p["elasticity"]) * promo_discount * 1.5)
                    
            product_probs.append(prob)
            
        product_probs = np.array(product_probs)
        product_probs /= product_probs.sum()
        
        # Sample unique products for the basket
        chosen_products_indices = np.random.choice(
            len(products), size=min(basket_size, len(products)), 
            replace=False, p=product_probs
        )
        chosen_products = [products[idx] for idx in chosen_products_indices]
        
        # Inject association pairs manually
        # E.g., if product A was selected, add product B with high probability
        chosen_ids = {p["product_id"] for p in chosen_products}
        for hero_id, halo_id, trigger_prob in association_pairs:
            if hero_id in chosen_ids and halo_id not in chosen_ids:
                if random.random() < trigger_prob:
                    # Find and append the halo product
                    halo_p = next(p for p in products if p["product_id"] == halo_id)
                    chosen_products.append(halo_p)
                    chosen_ids.add(halo_id)
                    
        # Now construct transaction rows for each item in the basket
        for p in chosen_products:
            prod_id = p["product_id"]
            unit_price = p["unit_price"]
            elasticity = p["elasticity"]
            
            # Determine discount
            discount = 0.0
            if prod_id in promo_calendar[week_number]:
                discount = promo_calendar[week_number][prod_id]
                
            # Determine quantity base
            qty_choices = [1, 2, 3, 4]
            qty_weights = [0.70, 0.20, 0.07, 0.03]
            
            if p["category"] == "Beverages" and p["unit_price"] < 30: # water packs, etc
                qty_weights = [0.40, 0.30, 0.20, 0.10]
            elif p["abc_class"] == "C": # slow moving premium things
                qty_weights = [0.95, 0.04, 0.01, 0.00]
                
            qty = random.choices(qty_choices, weights=qty_weights)[0]
            
            # Apply elasticity to quantity if discount is active
            if discount > 0:
                # quantity lift factor = 1 + |elasticity| * discount
                lift_factor = 1.0 + abs(elasticity) * discount
                # Apply random variation around lift
                qty = int(np.round(qty * random.uniform(lift_factor * 0.9, lift_factor * 1.1)))
                qty = max(1, min(qty, 10)) # clamp between 1 and 10
                
            total_amount = qty * unit_price * (1.0 - discount)
            
            transactions.append({
                "transaction_id": f"T-{t_counter:07d}",
                "customer_id": customer["customer_id"],
                "transaction_date": tx_datetime,
                "store_id": store_id,
                "product_id": prod_id,
                "product_category": p["category"],
                "quantity": qty,
                "unit_price": unit_price,
                "discount_pct": round(discount, 2),
                "total_amount": round(total_amount, 2),
                "payment_method": customer["preferred_payment"]
            })
            
        t_counter += 1

df_transactions = pd.DataFrame(transactions)
# Sort transactions by date
df_transactions = df_transactions.sort_values(by="transaction_date")
df_transactions.to_csv("data/transactions.csv", index=False)
print(f"Generated {len(df_transactions)} transactions across {df_transactions['transaction_id'].nunique()} unique baskets.")

print("\nAll datasets generated successfully!")
print("Outputs written to:")
print(" - data/stores.csv")
print(" - data/products.csv")
print(" - data/customers.csv")
print(" - data/transactions.csv")
