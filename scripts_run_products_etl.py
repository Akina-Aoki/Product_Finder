import pandas as pd

INPUT_PATH = 'data/raw/products_dirty.csv'
OUTPUT_PATH = 'data/processed/products_clean.csv'

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


def normalize_active(value):
    text = str(value).strip().lower()
    if text in {'true', '1', 'yes', 'y', 't'}:
        return True
    if text in {'false', '0', 'no', 'n', 'f'}:
        return False
    return True


def run_etl():
    df = pd.read_csv(INPUT_PATH, sep=';')

    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f'Missing required columns in {INPUT_PATH}: {missing}')

    df = df[REQUIRED_COLUMNS].copy()

    df['product_name'] = (
        df['product_name']
        .astype(str)
        .str.strip()
        .str.replace(r'\s+', ' ', regex=True)
        .str.title()
    )

    for int_column in ['product_code', 'brand_id', 'category_id', 'colour_id', 'size_id', 'gender_id']:
        df[int_column] = pd.to_numeric(df[int_column], errors='coerce')

    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df['active'] = df['active'].apply(normalize_active)

    df = df.dropna(subset=['product_code', 'product_name', 'brand_id', 'category_id', 'colour_id', 'size_id', 'gender_id', 'price'])

    df = df[df['price'] >= 0]

    for int_column in ['product_code', 'brand_id', 'category_id', 'colour_id', 'size_id', 'gender_id']:
        df = df[df[int_column] > 0]
        df[int_column] = df[int_column].astype(int)

    df = df.sort_values(['product_code']).drop_duplicates(subset=['product_code'], keep='last')

    df = df.reset_index(drop=True)
    df['product_id'] = df.index + 1

    df.to_csv(OUTPUT_PATH, sep=';', index=False)

    print(f'ETL complete. Wrote {len(df)} clean products to {OUTPUT_PATH}')


if __name__ == '__main__':
    run_etl()
