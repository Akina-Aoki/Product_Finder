import pandas as pd
import subprocess

# -------------------------
# FILE PATH CONFIGURATION
# -------------------------
# INPUT_PATH: Raw (dirty) data coming from source
# CLEAN_OUTPUT_PATH: Cleaned + validated data
# REJECTED_OUTPUT_PATH: Rows that failed validation
INPUT_PATH = 'data/raw/products_dirty.csv'
CLEAN_OUTPUT_PATH = 'data/processed/products_clean.csv'
REJECTED_OUTPUT_PATH = 'data/processed/products_rejected.csv'


# -------------------------
# REQUIRED STRUCTURE
# -------------------------
# These are the columns we expect from the raw dataset.
# If any are missing → we stop the pipeline.
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

# Columns that must be numeric IDs (foreign keys / identifiers)
ID_COLUMNS = [
    'product_id',
    'product_code',
    'brand_id',
    'category_id',
    'colour_id',
    'size_id',
    'gender_id'
]


def normalize_active(value):
    """
    Normalize the 'active' column to boolean values.

    The raw dataset may contain different representations:
    - 'true', '1', 'yes', etc. → True
    - 'false', '0', 'no', etc. → False

    Any unknown value defaults to True to avoid accidental deactivation.

    Args:
        value: Raw value from dataset

    Returns:
        bool: Normalized boolean value
    """
    text = str(value).strip().lower()
    if text in {'true', '1', 'yes', 'y', 't'}:
        return True
    if text in {'false', '0', 'no', 'n', 'f'}:
        return False
    return True


def add_rejection_reason(df, condition, reason):
    """
    Add a rejection reason to rows that fail validation.

    If multiple validation rules fail for the same row,
    reasons are concatenated using '|'.

    Example:
        "invalid_price|missing_required_field"

    Args:
        df (DataFrame): Dataset being validated
        condition (Series): Boolean mask of rows to mark
        reason (str): Reason for rejection
    """
    needs_separator = df['rejection_reason'].notna() & condition

    df.loc[needs_separator, 'rejection_reason'] = (
        df.loc[needs_separator, 'rejection_reason'] + '|'
    )

    df.loc[condition, 'rejection_reason'] = (
        df.loc[condition, 'rejection_reason'].fillna('') + reason
    )


def clean_name(value):
    """
    Clean and normalize product names.

    Fixes:
    - Extra spaces
    - Inconsistent casing

    Example:
        "  storm   jacket  " → "Storm Jacket"

    Args:
        value: Raw product name

    Returns:
        str: Cleaned product name
    """
    if pd.isna(value):
        return value
    return " ".join(str(value).split()).title()


def run_etl():
    """
    Main ETL pipeline.

    This function performs the full data pipeline:

    1. EXTRACT
       - Read raw CSV file

    2. TRANSFORM
       - Clean text fields
       - Validate data types
       - Identify invalid records
       - Split into valid vs rejected datasets

    3. LOAD
       - Save clean + rejected CSV files
       - Load clean data into PostgreSQL staging schema

    This function is the orchestration layer of the ETL process.
    """
    try:
        print("Starting ETL process...")

        # -------------------------
        # EXTRACT
        # -------------------------
        # Load raw dataset into memory
        df = pd.read_csv(INPUT_PATH, sep=';')

        # Validate structure
        missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing:
            raise ValueError(f'Missing required columns: {missing}')

        # Keep only relevant columns
        df = df[REQUIRED_COLUMNS].copy()

        # -------------------------
        # TRANSFORM
        # -------------------------

        # Clean product names
        df['product_name'] = df['product_name'].apply(clean_name)

        # Convert columns to numeric (invalid values become NaN)
        numeric_values = {}
        for col in ID_COLUMNS:
            numeric_values[col] = pd.to_numeric(df[col], errors='coerce')

        price_numeric = pd.to_numeric(df['price'], errors='coerce')

        # Create column to track validation errors
        df['rejection_reason'] = pd.NA

        # Apply validation rules
        add_rejection_reason(df, numeric_values['product_code'].isna(), 'invalid_product_code')
        add_rejection_reason(df, price_numeric.isna() | (price_numeric < 0), 'invalid_price')
        add_rejection_reason(df, df[REQUIRED_COLUMNS].isna().any(axis=1), 'missing_required_field')

        # Validate foreign keys (IDs must be > 0)
        invalid_fk = pd.Series(False, index=df.index)
        for col in ID_COLUMNS:
            invalid_fk |= (numeric_values[col].notna() & (numeric_values[col] <= 0))

        add_rejection_reason(df, invalid_fk, 'invalid_foreign_key')

        # Split dataset
        rejected_df = df[df['rejection_reason'].notna()].copy()
        valid_df = df[df['rejection_reason'].isna()].copy()

        # Normalize and cast types
        valid_df['active'] = valid_df['active'].apply(normalize_active)
        valid_df['price'] = price_numeric[valid_df.index]

        for col in ['product_code', 'brand_id', 'category_id', 'colour_id', 'size_id', 'gender_id']:
            valid_df[col] = numeric_values[col][valid_df.index].astype(int)

        # Remove duplicates based on product_code
        valid_df = valid_df.sort_values(['product_code']).drop_duplicates(
            subset=['product_code'], keep='last'
        )

        # Recreate product_id sequence
        valid_df = valid_df.reset_index(drop=True)
        valid_df['product_id'] = valid_df.index + 1

        # Sort rejected rows for readability
        rejected_df = rejected_df.sort_values(
            ['rejection_reason', 'product_code'],
            na_position='last'
        )

        # Remove helper column from clean dataset
        valid_df = valid_df.drop(columns=['rejection_reason'])

        # -------------------------
        # SAVE FILES
        # -------------------------
        valid_df.to_csv(CLEAN_OUTPUT_PATH, sep=';', index=False, encoding='utf-8')
        rejected_df.to_csv(REJECTED_OUTPUT_PATH, sep=';', index=False, encoding='utf-8')

        print(f'ETL complete: {len(df)} input → {len(valid_df)} valid → {len(rejected_df)} rejected')

        # -------------------------
        # LOAD (PostgreSQL)
        # -------------------------
        print("Starting LOAD step...")
        subprocess.run(["python", "scripts/load_products_to_db.py"], check=True)

        print("ETL pipeline finished successfully.")

    except Exception as e:
        print(f"ETL pipeline failed: {e}")


if __name__ == '__main__':
    run_etl()