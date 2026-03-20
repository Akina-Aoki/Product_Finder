import pandas as pd
import subprocess
import sys
import argparse

"""Simple ETL script for cleaning product data.

This script reads a raw products CSV, validates and cleans the rows,
splits valid and rejected records, and saves both outputs.
"""

# -------------------------
# FILE PATH CONFIGURATION
# -------------------------
INPUT_PATH = 'data/raw/products_dirty.csv'
CLEAN_OUTPUT_PATH = 'data/processed/products_clean.csv'
REJECTED_OUTPUT_PATH = 'data/processed/products_rejected.csv'


# -------------------------
# REQUIRED STRUCTURE
# -------------------------
REQUIRED_COLUMNS = [
    'product_id',
    'product_code',
    'product_name',
    'brand_id',
    'category_id',
    'colour_id',
    'size_id',
    'price',
    'gender_id',
    'active',
]

ID_COLUMNS = [
    'product_id',
    'product_code',
    'brand_id',
    'category_id',
    'colour_id',
    'size_id',
    'gender_id'
]


# -------------------------
# HELPERS
# -------------------------
def normalize_active(value):
    """Convert many true/false text values to a real boolean.

    If the value is unknown, this defaults to True.
    """
    text = str(value).strip().lower()
    if text in {'true', '1', 'yes', 'y', 't'}:
        return True
    if text in {'false', '0', 'no', 'n', 'f'}:
        return False
    return True


def clean_name(value):
    """Clean product names by trimming spaces and applying title case."""
    if pd.isna(value):
        return value
    return " ".join(str(value).split()).title()


def add_rejection_reason(df, condition, reason):
    """Add a rejection reason for rows that match a condition.

    If a row already has a reason, this appends the new reason using '|'.
    """
    needs_separator = df['rejection_reason'].notna() & condition

    df.loc[needs_separator, 'rejection_reason'] = (
        df.loc[needs_separator, 'rejection_reason'] + '|'
    )

    df.loc[condition, 'rejection_reason'] = (
        df.loc[condition, 'rejection_reason'].fillna('') + reason
    )


# -------------------------
# REFERENCE DATA
# -------------------------
def load_reference_ids():
    """Load valid foreign key IDs from reference CSV files.

    Returns a dictionary where each key is a column name and each value
    is a set of allowed IDs for that column.
    """
    return {
        "category_id": set(pd.read_csv('data/raw/categories.csv', sep=';')['category_id']),
        "brand_id": set(pd.read_csv('data/raw/brands.csv', sep=';')['brand_id']),
        "colour_id": set(pd.read_csv('data/raw/colours.csv', sep=';')['colour_id']),
        "size_id": set(pd.read_csv('data/raw/sizes.csv', sep=';')['size_id']),
        "gender_id": set(pd.read_csv('data/raw/genders.csv', sep=';')['gender_id']),
    }


# -------------------------
# VALIDATION
# -------------------------
def validate_foreign_keys(numeric_values, valid_ids, df):
    """
    Check foreign key columns and mark rows with invalid values.

    A foreign key is invalid when it is present but:
    1. It is less than or equal to 0, or
    2. It does not exist in the matching reference table.

    Returns a boolean mask where True means the row has an invalid key.
    """
    invalid_fk = pd.Series(False, index=df.index)

    for col, valid_set in valid_ids.items():
        values = numeric_values[col]

        # Rule 1: must be > 0
        invalid_fk |= (values.notna() & (values <= 0))

        # Rule 2: must exist in reference table
        invalid_fk |= (values.notna() & ~values.isin(valid_set))

    return invalid_fk


# -------------------------
# MAIN ETL
# -------------------------
def run_etl(load_to_db=False):
    """Run the full ETL pipeline.

    Steps:
    1. Extract raw product data.
    2. Transform and validate fields.
    3. Split valid and rejected rows.
    4. Save both outputs.
    5. Optionally load clean data into the database.
    """
    try:
        print("Starting ETL process...")

        # EXTRACT: read raw input data from CSV.
        df = pd.read_csv(INPUT_PATH, sep=';')

        missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing:
            raise ValueError(f'Missing required columns: {missing}')

        df = df[REQUIRED_COLUMNS].copy()

        # TRANSFORM: clean text and convert columns to numeric values.
        df['product_name'] = df['product_name'].apply(clean_name)

        # Convert to numeric
        numeric_values = {
            col: pd.to_numeric(df[col], errors='coerce')
            for col in ID_COLUMNS
        }

        price_numeric = pd.to_numeric(df['price'], errors='coerce')

        # Load reference IDs used to validate foreign key values.
        valid_ids = load_reference_ids()

        # Keep all validation failures in one column for easy auditing.
        df['rejection_reason'] = pd.NA

        # Basic validation rules for required product fields.
        add_rejection_reason(df, numeric_values['product_code'].isna(), 'invalid_product_code')
        add_rejection_reason(df, price_numeric.isna() | (price_numeric < 0), 'invalid_price')
        add_rejection_reason(df, df[REQUIRED_COLUMNS].isna().any(axis=1), 'missing_required_field')

        # Foreign key validation against reference tables.
        invalid_fk = validate_foreign_keys(numeric_values, valid_ids, df)
        add_rejection_reason(df, invalid_fk, 'invalid_foreign_key')

        # SPLIT DATA: separate valid rows from rejected rows.
        rejected_df = df[df['rejection_reason'].notna()].copy()
        valid_df = df[df['rejection_reason'].isna()].copy()

        # CLEAN VALID DATA: finalize data types and normalize values.
        valid_df['active'] = valid_df['active'].apply(normalize_active)
        valid_df['price'] = price_numeric[valid_df.index]

        for col in ['product_code', 'brand_id', 'category_id', 'colour_id', 'size_id', 'gender_id']:
            valid_df[col] = numeric_values[col][valid_df.index].astype(int)

        # Remove duplicates by product code, keeping the latest row.
        valid_df = valid_df.sort_values(['product_code']).drop_duplicates(
            subset=['product_code'], keep='last'
        )

        # Sort rejected rows to make review easier.
        rejected_df = rejected_df.sort_values(
            ['rejection_reason', 'product_code'],
            na_position='last'
        )

        valid_df = valid_df.drop(columns=['rejection_reason'])

        # SAVE: write clean and rejected datasets to output CSV files.
        valid_df.to_csv(CLEAN_OUTPUT_PATH, sep=';', index=False)
        rejected_df.to_csv(REJECTED_OUTPUT_PATH, sep=';', index=False)

        print(f'ETL complete: {len(df)} input → {len(valid_df)} valid → {len(rejected_df)} rejected')

        # LOAD: optionally run the database loading script.
        if load_to_db:
            print("Starting LOAD step...")
            subprocess.run([sys.executable, "scripts/load_products.py"], check=True)
        else:
            print("ETL complete. Data saved to CSV. (Skipping database load)")

    except Exception as e:
        # Show a clear error message if anything in the pipeline fails.
        print(f"ETL pipeline failed: {e}")


if __name__ == '__main__':
    # Parse command-line options, then run the pipeline.
    parser = argparse.ArgumentParser(description='Run the ETL process to clean product data.')
    parser.add_argument('--load', action='store_true', help='Automatically load data into the database after cleaning')
    
    args = parser.parse_args()
    
    run_etl(load_to_db=args.load)