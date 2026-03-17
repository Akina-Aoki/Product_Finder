import pandas as pd

INPUT_PATH = 'data/raw/products_dirty.csv'
CLEAN_OUTPUT_PATH = 'data/processed/products_clean.csv'
REJECTED_OUTPUT_PATH = 'data/processed/products_rejected.csv'

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

ID_COLUMNS = ['product_id', 'product_code', 'brand_id', 'category_id', 'colour_id', 'size_id', 'gender_id']


def normalize_active(value):
    text = str(value).strip().lower()
    if text in {'true', '1', 'yes', 'y', 't'}:
        return True
    if text in {'false', '0', 'no', 'n', 'f'}:
        return False
    return True


def add_rejection_reason(df, condition, reason):
    needs_separator = df['rejection_reason'].notna() & condition
    df.loc[needs_separator, 'rejection_reason'] = df.loc[needs_separator, 'rejection_reason'] + '|'
    df.loc[condition, 'rejection_reason'] = df.loc[condition, 'rejection_reason'].fillna('') + reason

def clean_name(value):
    if pd.isna(value):
        return value
    
    return " ".join(str(value).split()).title()

def run_etl():
    df = pd.read_csv(INPUT_PATH, sep=';')

    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f'Missing required columns in {INPUT_PATH}: {missing}')

    df = df[REQUIRED_COLUMNS].copy()

    df['product_name'] = df['product_name'].apply(clean_name)

    numeric_values = {}
    for int_column in ID_COLUMNS:
        numeric_values[int_column] = pd.to_numeric(df[int_column], errors='coerce')

    price_numeric = pd.to_numeric(df['price'], errors='coerce')

    df['rejection_reason'] = pd.NA

    add_rejection_reason(df, numeric_values['product_code'].isna(), 'invalid_product_code')
    add_rejection_reason(df, price_numeric.isna() | (price_numeric < 0), 'invalid_price')
    add_rejection_reason(df, df[REQUIRED_COLUMNS].isna().any(axis=1), 'missing_required_field')

    invalid_foreign_key = pd.Series(False, index=df.index)
    for id_column in ID_COLUMNS:
        invalid_foreign_key = invalid_foreign_key | (numeric_values[id_column].notna() & (numeric_values[id_column] <= 0))
    add_rejection_reason(df, invalid_foreign_key, 'invalid_foreign_key')

    rejected_df = df[df['rejection_reason'].notna()].copy()
    valid_df = df[df['rejection_reason'].isna()].copy()

    valid_df['active'] = valid_df['active'].apply(normalize_active)
    valid_df['price'] = price_numeric[valid_df.index]

    for int_column in ['product_code', 'brand_id', 'category_id', 'colour_id', 'size_id', 'gender_id']:
        valid_df[int_column] = numeric_values[int_column][valid_df.index].astype(int)

    valid_df = valid_df.sort_values(['product_code']).drop_duplicates(subset=['product_code'], keep='last')

    valid_df = valid_df.reset_index(drop=True)
    valid_df['product_id'] = valid_df.index + 1

    rejected_df = rejected_df.sort_values(['rejection_reason', 'product_code'], na_position='last')

    valid_df = valid_df.drop(columns=['rejection_reason'])

    valid_df.to_csv(CLEAN_OUTPUT_PATH, sep=';', index=False, encoding='utf-8')
    rejected_df.to_csv(REJECTED_OUTPUT_PATH, sep=';', index=False, encoding='utf-8')

    total_input = len(df)
    total_valid = len(valid_df)
    total_rejected = len(rejected_df)
    print(f'ETL complete: {total_input} input → {total_valid} valid → {total_rejected} rejected')


if __name__ == '__main__':
    run_etl()
