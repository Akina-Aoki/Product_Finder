import pandas as pd
import random
import csv

print("Reading in reference data from CSV files...")

brands_df = pd.read_csv('data/raw/brands.csv', sep=';')
colours_df = pd.read_csv('data/raw/colours.csv', sep=';')
sizes_df = pd.read_csv('data/raw/sizes.csv', sep=';')
categories_df = pd.read_csv('data/raw/categories.csv', sep=';')

brand_ids = brands_df['brand_id'].tolist()
colour_ids = colours_df['colour_id'].tolist()
size_ids = sizes_df['size_id'].tolist()

# Gender definition:
GENDER_MALE = 1
GENDER_FEMALE = 2
GENDER_UNISEX = 3

# Subcategories for each main category
synonyms = {
    "underwear": ["Boxers", "Briefs", "Underwear"],
    "t-shirt": ["T-Shirt", "Tee", "Top"],
    "shirt": ["Shirt", "Polo", "Longsleeve"],
    "jacket": ["Jacket", "Windbreaker", "Coat", "Parka", "Shell"],
    "shorts": ["Shorts", "Boardshorts"],
    "pants": ["Pants", "Tights", "Sweatpants"],
    "skirt": ["Skirt", "Skort"],
    "socks": ["Socks", "Ankle Socks", "Wool Socks"],
    "shoes": ["Shoes", "Sneakers", "Boots"]
}

category_mapping = {}
for _, row in categories_df.iterrows():
    cat_id = row['category_id']
    cat_name = row['category_names'].lower()
    category_mapping[cat_id] = synonyms.get(cat_name, [cat_name.title()])

category_ids = list(category_mapping.keys())
adjectives = ["Storm", "Urban", "Alpine", "Flex", "Active", "Pulse", "Summit", "Mountain", "Sprint", "Trail", "Velocity", "Glacier", "Skyline", "Core", "Blaze"]

# How many total variants do we want to generate?
TARGET_TOTAL_VARIANTS = 10

products_data = []
product_id_counter = 1

print(f"Generating base products and exploding them into sizes and colors...")

# Memorybank for product codes
used_product_codes = set()

# Loop until we have generated our target number of variants
while product_id_counter <= TARGET_TOTAL_VARIANTS:
    
    # --- 1. CREATE BASE PRODUCT ---
    brand_id = random.choice(brand_ids)
    category_id = random.choice(category_ids)
    noun = random.choice(category_mapping[category_id])
    product_name = f"{random.choice(adjectives)} {noun}"
    base_price = round(random.uniform(19.99, 299.99), 2)
    
    # --- 2. LOGIC FOR GENDER ---
    # If it's a skirt, make it mostly for women, otherwise choose Unisex OR Men+Women
    if category_id == 7: # 7 = Skirt
        genders_for_this_product = [GENDER_FEMALE]
    else:
        # Randomly choose: Either [3] (Unisex) OR [1, 2] (Men and Women)
        genders_for_this_product = random.choice([[GENDER_UNISEX], [GENDER_MALE, GENDER_FEMALE]])
    
    # --- 3. LOGIC FOR COLORS ---
    # Randomly select how many colors this product should have (1 to 5)
    num_colors = random.randint(1, min(5, len(colour_ids)))
    # Välj ut de specifika färgerna från vår ID-lista
    colors_for_this_product = random.sample(colour_ids, k=num_colors)

    # --- 4. LOGIC FOR SIZES ---
    # We want to always have ALL sizes for each color
    sizes_for_this_product = size_ids
    
    # --- 5. EXPLODE TO VARIANTS ---
    for gender_id in genders_for_this_product:
        for colour_id in colors_for_this_product:
            for size_id in sizes_for_this_product:
                
                # Generate a unique product code per variant
                while True:
                    new_code = f"{random.randint(10000000, 99999999)}"
                    
                    if new_code not in used_product_codes:
                        used_product_codes.add(new_code)
                        product_code = new_code
                        break
                active = "true"

                products_data.append([
                    product_id_counter, product_code, product_name, brand_id, category_id, 
                    colour_id, size_id, base_price, gender_id, active
                ])
                
                product_id_counter += 1

# Saving to CSV file
products_path = 'data/raw/products.csv'
with open(products_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerow(['product_id', 'product_code', 'product_name', 'brand_id', 'category_id', 'colour_id', 'size_id', 'price', 'gender_id', 'active'])
    writer.writerows(products_data)
    
print(f"Done! Created a total of {len(products_data)} product variants.")