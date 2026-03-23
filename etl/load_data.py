import pandas as pd
import sqlite3
import os

# Percorsi
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR  = os.path.join(BASE_DIR, 'data', 'raw')
DB_PATH  = os.path.join(BASE_DIR, 'db', 'nuclear.db')

def extract():
    """Legge i CSV grezzi da data/raw/"""
    print("EXTRACT — lettura CSV...")
    df_gen = pd.read_csv(os.path.join(RAW_DIR, 'nuclear-energy-generation.csv'))
    df_owid = pd.read_csv(os.path.join(RAW_DIR, 'owid-energy-data.csv'))
    print(f"  df_gen:  {len(df_gen)} righe")
    print(f"  df_owid: {len(df_owid)} righe")
    return df_gen, df_owid

def transform(df_gen, df_owid):
    """Pulisce e trasforma i dati"""
    print("\nTRANSFORM — pulizia dati...")

    # --- Tabella 1: nuclear_generation ---
    # Rinomina colonne in snake_case
    df_gen = df_gen.rename(columns={
        'Entity': 'country',
        'Code':   'iso_code',
        'Year':   'year',
        'Nuclear': 'nuclear_twh'
    })
    # Filtra solo paesi reali (codice ISO 3 lettere)
    df_gen = df_gen[df_gen['iso_code'].str.match(r'^[A-Z]{3}$', na=False)]
    # Rimuovi righe con nuclear_twh nullo
    df_gen = df_gen.dropna(subset=['nuclear_twh'])
    print(f"  nuclear_generation: {len(df_gen)} righe dopo pulizia")

    # --- Tabella 2: nuclear_indicators ---
    cols = ['country', 'year', 'iso_code', 'population', 'gdp',
            'nuclear_electricity', 'nuclear_share_elec',
            'nuclear_share_energy', 'nuclear_elec_per_capita']
    df_nuc = df_owid[cols].copy()
    # Filtra solo paesi reali
    df_nuc = df_nuc[df_nuc['iso_code'].str.match(r'^[A-Z]{3}$', na=False)]
    # Tieni solo paesi che hanno MAI avuto nucleare
    paesi_nucleari = df_nuc[df_nuc['nuclear_electricity'] > 0]['iso_code'].unique()
    df_nuc = df_nuc[df_nuc['iso_code'].isin(paesi_nucleari)]
    print(f"  nuclear_indicators: {len(df_nuc)} righe dopo pulizia")

    return df_gen, df_nuc

def load(df_gen, df_nuc):
    """Carica i dati nel database SQLite"""
    print(f"\nLOAD — caricamento in {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)

    # Carica le due tabelle — se esistono già le sovrascrive
    df_gen.to_sql('nuclear_generation',  conn, if_exists='replace', index=False)
    df_nuc.to_sql('nuclear_indicators',  conn, if_exists='replace', index=False)

    # Verifica
    for tabella in ['nuclear_generation', 'nuclear_indicators']:
        n = pd.read_sql(f'SELECT COUNT(*) as n FROM {tabella}', conn).iloc[0,0]
        print(f"  {tabella}: {n} righe caricate")

    conn.close()
    print("\nETL completato con successo.")

if __name__ == '__main__':
    df_gen, df_owid = extract()
    df_gen, df_nuc  = transform(df_gen, df_owid)
    load(df_gen, df_nuc)