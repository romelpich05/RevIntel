import pandas as pd
import numpy as np
import os

np.random.seed(42)

base_path = "data"
stores_df = pd.read_csv(os.path.join(base_path, "stores.csv"))
customers_df = pd.read_csv(os.path.join(base_path, "customers.csv"))

comments_pool = {
    'Positive': [
        "Clean store, very fast checkouts. Will shop here again!",
        "Excellent staff and very helpful cashiers. Wide range of products.",
        "Convenient location, plenty of parking space.",
        "Always fully stocked with fresh vegetables and drinks.",
        "Aircon is very cold, makes shopping pleasant. Great service!",
        "Best place to get grocery items quickly. Love the layout.",
        "The membership promos are very worth it. Staff are polite.",
        "Quick service, staff assisted me immediately in finding items.",
        "Clean aisles, safe environment, and fast checkout counters."
    ],
    'Neutral': [
        "Standard shopping experience. Nothing special but gets the job done.",
        "Clean enough but sometimes long lines at checkout.",
        "Decent product variety, prices are okay.",
        "Store is alright, though parking can be difficult during peak hours.",
        "A bit crowded on weekends, but weekdays are fine.",
        "Staff are ok, selection is average.",
        "Clean store but some items are out of stock.",
        "Standard drugstore selection. Service is average.",
        "Prices are slightly high compared to others but it's nearby."
    ],
    'Negative': [
        "Super long queue times! Only two cashiers working on a busy day.",
        "Staff were rude when I asked where to find milk. Terrible service.",
        "Very dirty floors and messy shelves. Needs better management.",
        "Many items are out of stock. Very disappointed with availability.",
        "Extremely narrow aisles, hard to navigate with a shopping cart.",
        "Prices are too high! Promos are misleading.",
        "No parking slots left, and guards were not helpful at all.",
        "AC was broken, super hot inside. Checkout was very slow.",
        "Had to wait 20 minutes just to get medicine. Understaffed."
    ]
}

reviews = []
review_id_counter = 1

# Generate around 350 reviews
for _ in range(350):
    store = stores_df.sample(1).iloc[0]
    customer = customers_df.sample(1).iloc[0]
    
    # Determine sentiment and rating
    rand_val = np.random.random()
    if rand_val < 0.50:
        sentiment = 'Positive'
        rating = np.random.choice([4, 5])
    elif rand_val < 0.80:
        sentiment = 'Neutral'
        rating = np.random.choice([3, 4])
    else:
        sentiment = 'Negative'
        rating = np.random.choice([1, 2])
        
    text = np.random.choice(comments_pool[sentiment])
    
    reviews.append({
        'review_id': f"R-{review_id_counter:05d}",
        'customer_id': customer['customer_id'],
        'store_id': store['store_id'],
        'rating': int(rating),
        'review_text': text,
        'sentiment': sentiment
    })
    review_id_counter += 1

reviews_df = pd.DataFrame(reviews)
reviews_df.to_csv(os.path.join(base_path, "store_reviews.csv"), index=False)
print("[OK] Generated store_reviews.csv feedback dataset.")
