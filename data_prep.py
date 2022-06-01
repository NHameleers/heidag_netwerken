import pandas as pd
import namen_prep
import streamlit as st

def drop_niet_blokken(df):
    '''Unit is een combinatie van 4 cijfers als het om een overkoepelende term gaat.
    Door alleen de regels over te houden waar unit uit meer dan 4 characters bestaat,
    houden we de regels over blokken over.'''
    dataf = df.copy()
    return dataf.loc[dataf.Unit.str.len() > 4, ]

@st.cache(suppress_st_warning=True)
def prep_onderwijs_data():
    files = ['Data/BROS HSR realisations 2019-2020, 14.5.2022-Blokcoordinatoren en planningsgroepsleden.xlsx',
            'Data/BROS HSR realisations 2020-2021, 11.2.2022-Blokcoordinatoren en planningsgroepsleden.xlsx',
            'Data/BROS HSR realisations 2021-2022, 14.5.2022-Blokcoordinatoren en planningsgroepsleden.xlsx']

    onderwijs = pd.DataFrame()

    # zet alle jaren in 1 df
    for jaar, filename in zip(range(2019, 2022), files):
        onderwijs = pd.concat([onderwijs, (pd.read_excel(filename,
                                                        sheet_name='Realisations')
                                        .dropna(subset=['Unit'])
                                        .assign(Year=jaar)
                                        .pipe(drop_niet_blokken)
                                        .drop_duplicates())],
                            axis=0)
        
    onderwijs['UnitYear'] = [f"{unit}_{year}" for unit, year in zip(onderwijs['Unit'], onderwijs['Year'])]
    onderwijs['Prefix'] = onderwijs['Prefix'].fillna('')
    onderwijs['Naam'] = (onderwijs.Initials + " " + onderwijs.Prefix + " " + onderwijs.Name).str.replace("  ", " ").str.replace("  ", " ")

    # selecteer alleen vaste staf
    onderwijs['is_vaste_staf'] = onderwijs.Name.apply(namen_prep.check_if_vaste_staf_achternaam)
    onderwijs = onderwijs.loc[onderwijs.is_vaste_staf, ]

    # zorg dat namen gelijk geschreven zijn als in Pure/Onderzoek
    missing_before = onderwijs['Naam'].isnull().sum()
    onderwijs['Naam'] = [namen_prep.onderwijsnaam_naar_onderzoeksnaam(naam) for naam in onderwijs['Naam'].values]
    missing_after = onderwijs['Naam'].isnull().sum()
    assert missing_before == missing_after

    return onderwijs