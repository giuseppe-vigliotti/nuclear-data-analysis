import pandas as pd
import sqlite3
import os
import logging

# Logging configuration — one-time setup at module level
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s"
)
logger = logging.getLogger(__name__)

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR  = os.path.join(BASE_DIR, 'data', 'raw')
DB_PATH  = os.path.join(BASE_DIR, 'db', 'nuclear.db')


def extract():
    """Read raw CSV files from data/raw/."""
    logger.info("EXTRACT — reading CSV files...")
    df_gen  = pd.read_csv(os.path.join(RAW_DIR, 'nuclear-energy-generation.csv'))
    df_owid = pd.read_csv(os.path.join(RAW_DIR, 'owid-energy-data.csv'))
    logger.info("df_gen loaded: %d rows", len(df_gen))
    logger.info("df_owid loaded: %d rows", len(df_owid))
    return df_gen, df_owid


def transform(df_gen, df_owid):
    """Clean and transform raw DataFrames into analysis-ready tables."""
    logger.info("TRANSFORM — cleaning data...")

    # --- Table 1: nuclear_generation ---
    # Rename columns to snake_case
    df_gen = df_gen.rename(columns={
        'Entity':  'country',
        'Code':    'iso_code',
        'Year':    'year',
        'Nuclear': 'nuclear_twh'
    })
    # Keep only real countries (ISO alpha-3 code)
    df_gen = df_gen[df_gen['iso_code'].str.match(r'^[A-Z]{3}$', na=False)]
    # Drop rows with no nuclear output
    df_gen = df_gen.dropna(subset=['nuclear_twh'])
    logger.info("nuclear_generation: %d rows after cleaning", len(df_gen))

    # --- Table 2: nuclear_indicators ---
    cols = ['country', 'year', 'iso_code', 'population', 'gdp',
            'nuclear_electricity', 'nuclear_share_elec',
            'nuclear_share_energy', 'nuclear_elec_per_capita']
    df_nuc = df_owid[cols].copy()
    # Keep only real countries
    df_nuc = df_nuc[df_nuc['iso_code'].str.match(r'^[A-Z]{3}$', na=False)]
    # Keep only countries that have EVER had nuclear production
    nuclear_countries = df_nuc[df_nuc['nuclear_electricity'] > 0]['iso_code'].unique()
    df_nuc = df_nuc[df_nuc['iso_code'].isin(nuclear_countries)]
    logger.info("nuclear_indicators: %d rows after cleaning", len(df_nuc))

    return df_gen, df_nuc


def load(df_gen, df_nuc):
    """Load transformed DataFrames into the SQLite database."""
    logger.info("LOAD — writing to %s...", DB_PATH)
    conn = sqlite3.connect(DB_PATH)

    # Write both tables — overwrite if they already exist
    df_gen.to_sql('nuclear_generation', conn, if_exists='replace', index=False)
    df_nuc.to_sql('nuclear_indicators', conn, if_exists='replace', index=False)

    # Verify row counts
    for table in ['nuclear_generation', 'nuclear_indicators']:
        n = pd.read_sql(f'SELECT COUNT(*) as n FROM {table}', conn).iloc[0, 0]
        logger.info("%s: %d rows loaded", table, n)

    conn.close()
    logger.info("ETL pipeline completed successfully.")


if __name__ == '__main__':
    df_gen, df_owid = extract()
    df_gen, df_nuc  = transform(df_gen, df_owid)
    load(df_gen, df_nuc)