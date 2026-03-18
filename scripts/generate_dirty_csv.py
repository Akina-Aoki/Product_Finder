import pandas as pd
import random
import csv

# -----------------------------------
# CONFIG
# -----------------------------------
OUTPUT_PATH = "data/raw/products_dirty.csv"

TARGET_TOTAL_ROWS = 30        # total rows we want
TARGET_BASE_PRODUCTS = 6      # number of different products

# Corruption probabilities (tuned for ETL testing)
PROB_NEGATIVE_PRICE = 0.25
PROB_MISSING_PRICE = 0.15
PROB_DIRTY_NAME = 0.30
PROB_MISSING_NAME = 0.10
PROB_INVALID_CODE = 0.10
PROB_INVALID_FK = 0.15
PROB_INVALID_ACTIVE = 0.30

print("Reading reference data...")

brands_df = pd.read_csv("data/raw/brands.csv", sep=";")
colours_df = pd.read_csv("data/raw/colours.csv", sep=";")
sizes_df = pd.read_csv("data/raw/sizes.csv", sep=";")
categories_df = pd.read_csv("data/raw/categories.csv", sep=";")

brand_ids = brands_df["brand_id"].tolist()
colour_ids = colours_df["colour_id"].tolist()
size_ids = sizes_df["size_id"].tolist()

# Gender constants
GENDER_MALE = 1
GENDER_FEMALE = 2
GENDER_UNISEX = 3

# -----------------------------------
# CATEGORY → NAME MAPPING
# -----------------------------------
synonyms = {
    "underwear": ["Boxers", "Briefs", "Underwear"],
    "t-shirt": ["T-Shirt", "Tee", "Top"],
    "shirt": ["Shirt", "Polo", "Longsleeve"],
    "jacket": ["Jacket", "Windbreaker", "Coat", "Shell"],
    "shorts": ["Shorts", "Boardshorts"],
    "pants": ["Pants", "Tights", "Sweatpants"],
    "skirt": ["Skirt", "Skort"],
    "socks": ["Socks", "Ankle Socks", "Wool Socks"],
    "shoes": ["Shoes", "Sneakers", "Boots"]
}

category_mapping = {}
for _, row in categories_df.iterrows():
    cat_id = row["category_id"]
    cat_name = row["category_names"].lower()
    category_mapping[cat_id] = synonyms.get(cat_name, [cat_name.title()])

category_ids = list(category_mapping.keys())

adjectives = [
    "Storm", "Urban", "Alpine", "Flex", "Active",
    "Pulse", "Summit", "Mountain", "Sprint",
    "Trail", "Velocity", "Glacier", "Skyline",
    "Core", "Blaze"
]

# -----------------------------------
# HELPERS
# -----------------------------------
def generate_product_name(category_id):
    noun = random.choice(category_mapping[category_id])
    return f"{random.choice(adjectives)} {noun}"


def corrupt_name(name):
    if random.random() < PROB_MISSING_NAME:
        return None

    if random.random() < PROB_DIRTY_NAME:
        # messy spacing + random casing
        name = "   " + name.upper() + "   "

    return name


def corrupt_price(price):
    if random.random() < PROB_MISSING_PRICE:
        return None

    if random.random() < PROB_NEGATIVE_PRICE:
        return -price

    return price


def corrupt_fk(value):
    if random.random() < PROB_INVALID_FK:
        return random.choice([-1, 0, 9999])
    return value


def generate_product_code(used_codes):
    if random.random() < PROB_INVALID_CODE:
        return "INVALID_CODE"

    while True:
        code = str(random.randint(10000000, 99999999))
        if code not in used_codes:
            used_codes.add(code)
            return code


def corrupt_active():
    options = ["true", "false", "1", "0", "yes", "no", "T", "F", "kanske", ""]
    if random.random() < PROB_INVALID_ACTIVE:
        return random.choice(options)
    return "true"


# -----------------------------------
# MAIN GENERATION
# -----------------------------------
print("Generating DIRTY dataset for ETL testing...")

products_data = []
used_product_codes = set()
product_id_counter = 1

for _ in range(TARGET_BASE_PRODUCTS):

    brand_id = random.choice(brand_ids)
    category_id = random.choice(category_ids)

    base_name = generate_product_name(category_id)
    base_price = round(random.uniform(19.99, 299.99), 2)

    # Gender logic
    if category_id == 7:
        genders = [GENDER_FEMALE]
    else:
        genders = random.choice([
            [GENDER_UNISEX],
            [GENDER_MALE, GENDER_FEMALE]
        ])

    # Select subset of colors + sizes
    colors = random.sample(colour_ids, k=random.randint(1, 3))
    sizes = random.sample(size_ids, k=random.randint(1, 3))

    for gender_id in genders:
        for colour_id in colors:
            for size_id in sizes:

                if len(products_data) >= TARGET_TOTAL_ROWS:
                    break

                product_name = corrupt_name(base_name)
                price = corrupt_price(base_price)

                row = [
                    product_id_counter,
                    generate_product_code(used_product_codes),
                    product_name,
                    corrupt_fk(brand_id),
                    corrupt_fk(category_id),
                    corrupt_fk(colour_id),
                    corrupt_fk(size_id),
                    price,
                    corrupt_fk(gender_id),
                    corrupt_active()
                ]

                products_data.append(row)
                product_id_counter += 1

            if len(products_data) >= TARGET_TOTAL_ROWS:
                break
        if len(products_data) >= TARGET_TOTAL_ROWS:
            break


# -----------------------------------
# FORCE EDGE CASES (guarantee ETL hits)
# -----------------------------------
print("Injecting guaranteed edge cases...")

if len(products_data) >= 5:
    products_data[0][7] = -99.99        # negative price
    products_data[1][7] = None          # missing price
    products_data[2][2] = None          # missing name
    products_data[3][1] = "BAD_CODE"    # invalid product code
    products_data[4][3] = -1            # invalid brand_id


# -----------------------------------
# SAVE FILE
# -----------------------------------
with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, delimiter=";")
    writer.writerow([
        "product_id",
        "product_code",
        "product_name",
        "brand_id",
        "category_id",
        "colour_id",
        "size_id",
        "price",
        "gender_id",
        "active"
    ])
    writer.writerows(products_data)

print(f"Done! Created DIRTY dataset with {len(products_data)} rows.")
print(f"Saved to: {OUTPUT_PATH}")