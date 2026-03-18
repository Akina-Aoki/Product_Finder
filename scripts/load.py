import pandas as pd
import psycopg
import os

DB_URL = os.getenv(
    "DB_URL",
    "postgresql://postgres:postgres@localhost:5439/SportWearDB"
)

FILE_PATH = "data/processed/products_clean.csv"

def load_products():
    df = pd.read_csv(FILE_PATH, sep=";")

    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            for _, row in df.iterrows():
                cur.execute("""
                    INSERT INTO staging.products (
                        product_code,
                        product_name,
                        brand_id,
                        category_id,
                        colour_id,
                        size_id,
                        gender_id,
                        price,
                        active
                    )
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT (product_code) DO NOTHING;
                """, tuple(row))

    print("Loaded clean products into staging.products")

if __name__ == "__main__":
    load_products()