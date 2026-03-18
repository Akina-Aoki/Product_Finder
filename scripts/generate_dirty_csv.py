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

# Gender definition
GENDER_MALE = 1
GENDER_FEMALE = 2
GENDER_UNISEX = 3

# Subcategories
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

adjectives = [
    "Storm", "Urban", "Alpine", "Flex", "Active",
    "Pulse", "Summit", "Mountain", "Sprint",
    "Trail", "Velocity", "Glacier", "Skyline",
    "Core", "Blaze"
]

TARGET_TOTAL_VARIANTS = 10

products_data = []
product_id_counter = 1

print("Generating DIRTY product dataset for ETL testing...")

used_product_codes = set()

while product_id_counter <= TARGET_TOTAL_VARIANTS:

    # -------------------------------
    # BASE PRODUCT (CLEAN START)
    # -------------------------------
    brand_id = random.choice(brand_ids)
    category_id = random.choice(category_ids)

    noun = random.choice(category_mapping[category_id])
    product_name = f"{random.choice(adjectives)} {noun}"

    base_price = round(random.uniform(19.99, 299.99), 2)

    # -------------------------------
    # 🔴 DATA CORRUPTION (ETL PURPOSE)
    # -------------------------------

    # Invalid price
    if random.random() < 0.1:
        base_price = -base_price

    # Missing price
    if random.random() < 0.05:
        base_price = None

    # Dirty spacing
    if random.random() < 0.1:
        product_name = "   " + product_name + "   "

    # Missing product name
    if random.random() < 0.03:
        product_name = None

    # Invalid product_code flag
    force_invalid_code = False
    if random.random() < 0.05:
        force_invalid_code = True

    # Invalid foreign key
    if random.random() < 0.05:
        brand_id = -1

    # -------------------------------
    # GENDER LOGIC
    # -------------------------------
    if category_id == 7:
        genders_for_this_product = [GENDER_FEMALE]
    else:
        genders_for_this_product = random.choice([
            [GENDER_UNISEX],
            [GENDER_MALE, GENDER_FEMALE]
        ])

    # -------------------------------
    # COLOR LOGIC
    # -------------------------------
    num_colors = random.randint(1, min(5, len(colour_ids)))
    colors_for_this_product = random.sample(colour_ids, k=num_colors)

    # -------------------------------
    # SIZE LOGIC
    # -------------------------------
    sizes_for_this_product = size_ids

    # -------------------------------
    # EXPLODE TO VARIANTS
    # -------------------------------
    for gender_id in genders_for_this_product:
        for colour_id in colors_for_this_product:
            for size_id in sizes_for_this_product:

                # Product code generation
                while True:
                    if force_invalid_code:
                        new_code = "INVALID_CODE"
                    else:
                        new_code = str(random.randint(10000000, 99999999))

                    if new_code not in used_product_codes:
                        used_product_codes.add(new_code)
                        product_code = new_code
                        break

                active = "true"

                products_data.append([
                    product_id_counter,
                    product_code,
                    product_name,
                    brand_id,
                    category_id,
                    colour_id,
                    size_id,
                    base_price,
                    gender_id,
                    active
                ])

                product_id_counter += 1

                if product_id_counter > TARGET_TOTAL_VARIANTS:
                    break

            if product_id_counter > TARGET_TOTAL_VARIANTS:
                break

        if product_id_counter > TARGET_TOTAL_VARIANTS:
            break


# -------------------------------
# SAVE DIRTY DATA
# -------------------------------
products_path = 'data/raw/products_dirty.csv'

with open(products_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerow([
        'product_id',
        'product_code',
        'product_name',
        'brand_id',
        'category_id',
        'colour_id',
        'size_id',
        'price',
        'gender_id',
        'active'
    ])
    writer.writerows(products_data)

print(f"Done! Created DIRTY dataset with {len(products_data)} rows → ready for ETL.")