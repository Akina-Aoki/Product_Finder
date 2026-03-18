import pandas as pd
import subprocess
import sys

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
    text = str(value).strip().lower()
    if text in {'true', '1', 'yes', 'y', 't'}:
        return True
    if text in {'false', '0', 'no', 'n', 'f'}:
        return False
    return True


def clean_name(value):
    if pd.isna(value):
        return value
    return " ".join(str(value).split()).title()


def add_rejection_reason(df, condition, reason):
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
    """Load valid IDs from reference CSVs"""
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
    Validate that foreign keys:
    1. Are > 0
    2. Exist in reference tables
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
def run_etl():
    try:
        print("Starting ETL process...")

        # -------------------------
        # EXTRACT
        # -------------------------
        df = pd.read_csv(INPUT_PATH, sep=';')

        missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing:
            raise ValueError(f'Missing required columns: {missing}')

        df = df[REQUIRED_COLUMNS].copy()

        # -------------------------
        # TRANSFORM
        # -------------------------
        df['product_name'] = df['product_name'].apply(clean_name)

        # Convert to numeric
        numeric_values = {
            col: pd.to_numeric(df[col], errors='coerce')
            for col in ID_COLUMNS
        }

        price_numeric = pd.to_numeric(df['price'], errors='coerce')

        # Load reference data
        valid_ids = load_reference_ids()

        # Create rejection column
        df['rejection_reason'] = pd.NA

        # Basic validation rules
        add_rejection_reason(df, numeric_values['product_code'].isna(), 'invalid_product_code')
        add_rejection_reason(df, price_numeric.isna() | (price_numeric < 0), 'invalid_price')
        add_rejection_reason(df, df[REQUIRED_COLUMNS].isna().any(axis=1), 'missing_required_field')

        # Foreign key validation
        invalid_fk = validate_foreign_keys(numeric_values, valid_ids, df)
        add_rejection_reason(df, invalid_fk, 'invalid_foreign_key')

        # -------------------------
        # SPLIT DATA
        # -------------------------
        rejected_df = df[df['rejection_reason'].notna()].copy()
        valid_df = df[df['rejection_reason'].isna()].copy()

        # -------------------------
        # CLEAN VALID DATA
        # -------------------------
        valid_df['active'] = valid_df['active'].apply(normalize_active)
        valid_df['price'] = price_numeric[valid_df.index]

        for col in ['product_code', 'brand_id', 'category_id', 'colour_id', 'size_id', 'gender_id']:
            valid_df[col] = numeric_values[col][valid_df.index].astype(int)

        # Remove duplicates
        valid_df = valid_df.sort_values(['product_code']).drop_duplicates(
            subset=['product_code'], keep='last'
        )

        # Recreate product_id
        valid_df = valid_df.reset_index(drop=True)

        # Sort rejected
        rejected_df = rejected_df.sort_values(
            ['rejection_reason', 'product_code'],
            na_position='last'
        )

        valid_df = valid_df.drop(columns=['rejection_reason'])

        # -------------------------
        # SAVE
        # -------------------------
        valid_df.to_csv(CLEAN_OUTPUT_PATH, sep=';', index=False)
        rejected_df.to_csv(REJECTED_OUTPUT_PATH, sep=';', index=False)

        print(f'ETL complete: {len(df)} input → {len(valid_df)} valid → {len(rejected_df)} rejected')

        # -------------------------
        # LOAD
        # -------------------------
        print("Starting LOAD step...")
        subprocess.run([sys.executable, "scripts/load_products.py"], check=True)

        print("ETL pipeline finished successfully.")

    except Exception as e:
        print(f"ETL pipeline failed: {e}")


if __name__ == '__main__':
    run_etl()