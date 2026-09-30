import csv
import datetime
import random
import os
import math

def generate_sample_data(output_path, num_rows=5000):
    # Set seed for reproducibility
    random.seed(42)
    
    # Categories and products
    categories_products = {
        "Electronics": [
            ("E101", "Laptop Pro 15", 1200.0),
            ("E102", "Smartphone X", 800.0),
            ("E103", "Wireless Noise-Cancelling Headphones", 250.0),
            ("E104", "Smartwatch Series 5", 300.0),
            ("E105", "4K Ultra HD Monitor", 450.0),
            ("E106", "Mechanical Keyboard", 120.0)
        ],
        "Furniture": [
            ("F201", "Ergonomic Office Chair", 280.0),
            ("F202", "Adjustable Standing Desk", 600.0),
            ("F203", "Wooden Bookshelf", 180.0),
            ("F204", "3-Seater Fabric Sofa", 850.0),
            ("F205", "Minimalist Coffee Table", 150.0)
        ],
        "Office Supplies": [
            ("O301", "Premium Ring Binder", 15.0),
            ("O302", "Recycled Printer Paper (Case)", 45.0),
            ("O303", "Gel Pens Multi-pack", 12.0),
            ("O304", "Heavy Duty Stapler", 25.0),
            ("O305", "A5 Leather Notebook", 20.0)
        ],
        "Clothing": [
            ("C401", "Organic Cotton T-Shirt", 28.0),
            ("C402", "Slim Fit Denim Jeans", 65.0),
            ("C403", "All-Weather Windbreaker", 95.0),
            ("C404", "Running Sneakers", 110.0),
            ("C405", "Merino Wool Socks (Pack of 3)", 35.0)
        ]
    }
    
    regions = ["North", "South", "East", "West"]
    
    # Create customer profiles
    # We want ~300 unique customers with distinct buying habits
    customer_profiles = []
    first_names = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", "Elizabeth",
                   "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen",
                   "Christopher", "Lisa", "Daniel", "Nancy", "Matthew", "Betty", "Anthony", "Sandra", "Mark", "Margaret"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
                  "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]
    
    # Generate 300 customers and assign them to a behavioral profile
    # Profiles: 
    # 0: Champions (high freq, high spend, recent)
    # 1: Loyal Customers (medium-high freq, medium spend, recent)
    # 2: At Risk (previously high/med freq, but stopped buying)
    # 3: New/Promising (low freq, recent, low-med spend)
    # 4: Churned/Lost (1 or 2 purchases long ago, low spend)
    for i in range(1, 301):
        cust_id = f"CUST-{1000 + i}"
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        profile_type = random.choices([0, 1, 2, 3, 4], weights=[0.10, 0.25, 0.20, 0.25, 0.20])[0]
        region = random.choice(regions)
        customer_profiles.append({
            "id": cust_id,
            "name": name,
            "profile_type": profile_type,
            "region": region
        })
        
    start_date = datetime.date(2024, 8, 1)
    end_date = datetime.date(2026, 8, 1)
    date_range = (end_date - start_date).days
    
    # We will generate rows with timestamps
    orders = []
    
    # Base transaction generator
    for row_idx in range(num_rows):
        # Choose a customer
        cust = random.choice(customer_profiles)
        p_type = cust["profile_type"]
        
        # Determine order date based on customer profile to simulate Recency
        # Champions purchase throughout the range, including recent days
        # Churned purchase mostly in the first half
        # At Risk purchase in the first 75% of the range
        # New customers purchase in the last 25% of the range
        if p_type == 0:  # Champions
            day_offset = random.randint(0, date_range)
        elif p_type == 1:  # Loyal
            day_offset = random.randint(int(date_range * 0.1), date_range)
        elif p_type == 2:  # At Risk
            day_offset = random.randint(0, int(date_range * 0.75))
        elif p_type == 3:  # New
            day_offset = random.randint(int(date_range * 0.8), date_range)
        else:  # Churned
            day_offset = random.randint(0, int(date_range * 0.4))
            
        order_date = start_date + datetime.timedelta(days=day_offset)
        
        # Apply overall seasonal trend (Q4 boosts sales, weekends drop sales)
        # Weekday: Monday is 0, Sunday is 6
        weekday = order_date.weekday()
        is_weekend = weekday >= 5
        
        # Q4 multiplier (Oct, Nov, Dec)
        is_q4 = order_date.month in [10, 11, 12]
        
        # Probability adjustments based on seasonality
        # If it's a weekend, maybe skip it with 40% probability to reduce weekend volume
        if is_weekend and random.random() < 0.4:
            # Shift date to a weekday
            order_date = order_date - datetime.timedelta(days=(weekday - 2))
            
        # Choose category and product
        # Profile spending tendencies
        if p_type == 0 or p_type == 1: # High/Loyal value buyers buy more Electronics and Furniture
            category = random.choices(["Electronics", "Furniture", "Office Supplies", "Clothing"], weights=[0.4, 0.3, 0.15, 0.15])[0]
        else:
            category = random.choices(["Electronics", "Furniture", "Office Supplies", "Clothing"], weights=[0.15, 0.15, 0.35, 0.35])[0]
            
        prod_info = random.choice(categories_products[category])
        prod_id, prod_name, unit_price = prod_info
        
        # Quantity based on product type
        if category == "Office Supplies":
            quantity = random.randint(2, 15)
        elif category == "Clothing":
            quantity = random.randint(1, 5)
        elif category == "Furniture":
            quantity = random.randint(1, 2)
        else: # Electronics
            quantity = random.choices([1, 2, 3], weights=[0.8, 0.15, 0.05])[0]
            
        # Pricing, discounts, cost
        # Discount: Champions get small loyalty discount occasionally (e.g. 5%), Churned get none, etc.
        discount = 0.0
        if random.random() < 0.3:
            discount = random.choices([0.05, 0.10, 0.15, 0.20], weights=[0.5, 0.3, 0.15, 0.05])[0]
            
        # Unit price variation (±5% noise)
        actual_unit_price = round(unit_price * random.uniform(0.95, 1.05), 2)
        
        # Sales calculation
        raw_sales = actual_unit_price * quantity
        discount_amount = round(raw_sales * discount, 2)
        sales = round(raw_sales - discount_amount, 2)
        
        # Cost is typically 50-70% of product unit price
        cost_ratio = random.uniform(0.5, 0.7)
        # Office supplies have lower cost ratios (higher margin), Electronics have higher cost ratio
        if category == "Office Supplies":
            cost_ratio = random.uniform(0.3, 0.5)
        elif category == "Electronics":
            cost_ratio = random.uniform(0.65, 0.8)
            
        cost = round(actual_unit_price * quantity * cost_ratio, 2)
        profit = round(sales - cost, 2)
        
        # Create unique order ID (with padding)
        order_id = f"ORD-{100000 + row_idx}"
        
        orders.append({
            "order_id": order_id,
            "order_date": order_date.strftime("%Y-%m-%d"),
            "customer_id": cust["id"],
            "customer_name": cust["name"],
            "product_id": prod_id,
            "product_name": prod_name,
            "category": category,
            "region": cust["region"],
            "quantity": quantity,
            "unit_price": actual_unit_price,
            "discount": discount,
            "sales": sales,
            "cost": cost,
            "profit": profit
        })
        
    # Inject anomalies
    # Anomaly 1: A huge single day sale (B2B purchase) in Furniture
    # Let's pick a random order in the middle and inflate it massively
    large_order_idx = int(num_rows * 0.45)
    orders[large_order_idx]["quantity"] = 50
    orders[large_order_idx]["sales"] = 35000.00
    orders[large_order_idx]["cost"] = 18000.00
    orders[large_order_idx]["profit"] = 17000.00
    orders[large_order_idx]["product_name"] = "Standing Desk B2B Bulk Order"
    
    # Anomaly 2: Extreme discount (input error / promotion anomaly)
    promo_order_idx = int(num_rows * 0.72)
    orders[promo_order_idx]["discount"] = 0.90
    orders[promo_order_idx]["sales"] = 120.00
    orders[promo_order_idx]["cost"] = 800.00
    orders[promo_order_idx]["profit"] = -680.00 # Severe negative profit anomaly
    orders[promo_order_idx]["product_name"] = "Laptop Pro 15 (Promo Error)"

    # Anomaly 3: Day with almost zero sales due to server crash
    # Pick a date (e.g., 2025-06-15) and delete/shift sales to resemble crash
    crash_date = "2025-06-15"
    orders = [o for o in orders if o["order_date"] != crash_date]
    # Add just one very small transaction on that date
    orders.append({
        "order_id": f"ORD-CRASH-01",
        "order_date": crash_date,
        "customer_id": "CUST-1099",
        "customer_name": "Emergency Backup Customer",
        "product_id": "O303",
        "product_name": "Gel Pens Multi-pack",
        "category": "Office Supplies",
        "region": "West",
        "quantity": 1,
        "unit_price": 12.00,
        "discount": 0.0,
        "sales": 12.00,
        "cost": 5.00,
        "profit": 7.00
    })

    # Sort orders by date
    orders.sort(key=lambda x: x["order_date"])
    
    # Re-index order IDs to keep them sequential
    for i, o in enumerate(orders):
        if not o["order_id"].startswith("ORD-CRASH"):
            o["order_id"] = f"ORD-{100000 + i}"
            
    # Write to CSV
    dir_name = os.path.dirname(output_path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=orders[0].keys())
        writer.writeheader()
        writer.writerows(orders)
        
    print(f"Sample data generated successfully at {output_path}. Total rows: {len(orders)}")

if __name__ == "__main__":
    generate_sample_data("sample_sales.csv")
