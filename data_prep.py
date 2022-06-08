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


@st.cache(suppress_st_warning=True)
def prep_supervisie_data():

    sv1 = pd.read_excel('Data/Promovendi HSR 20220602.xlsx', sheet_name='PhD programme')
    sv2 = (pd.read_excel('Data/HSR promoties 01012021 tot 01072022.xlsx', sheet_name='PhD programme')
        .drop(['PhD defense date', 'Duration from PhD starting date until PhD defense date'], axis=1))

    assert (sv1.columns.values == sv2.columns.values).all()

    # Combineer huidige PhDs en in afgelopen jaar gepromoveerde PhDs
    sv = pd.concat([sv1, sv2], axis=0)

    # maak dummy kolommen voor de 4 supervisors en verbindt deze met PhD naam
    supervisor_df = sv['Assigned supervisors'].str.split(',', expand=True)
    ties_prep = pd.concat([sv['Full name'], supervisor_df], axis=1)

    # van breed naar long (met kolommen PhD name en Name (v supervisor))
    ties_long = (pd.melt(ties_prep, id_vars='Full name',
                    value_vars=supervisor_df.columns,
                    var_name='supervisor_nr',
                     value_name='Name')
             .sort_values('Full name')
            .rename(columns={'Full name': 'PhD name'})
            .drop('supervisor_nr', axis=1)
            .dropna())

    # selecteer alleen rijen met vaste stafleden
    ties_long['achternaam'] = ties_long['Name'].str.split().str[-1]
    ties_long['is_vaste_staf'] = ties_long['achternaam'].apply(namen_prep.check_if_vaste_staf_achternaam)
    ties_long = ties_long.loc[ties_long.is_vaste_staf, ]

    # alle PhDs waar slechts 1 HSR vaste staf supervisor is kunnen weg, want daar is geen 'samenwerking'
    # koppel hiervoor de value counts van de PhD naam (op dit moment zijn er alleen regels met vaste staf supervisors in de long data)
    vc = ties_long['PhD name'].value_counts().to_frame('nr_of_HSR_supervisors')
    vc.index.name='PhD name'
    ties = ties_long.merge(vc, on='PhD name', how='left')
    ties = ties[ties['nr_of_HSR_supervisors'] > 1]

    # zorg dat namen gelijk geschreven zijn als in Pure/Onderzoek
    ties['Name'] = ties['Name'].str.replace('.', '').str.strip()
    missing_before = ties['Name'].isnull().sum()
    ties['Name'] = [namen_prep.supervisornaam_naar_onderzoeksnaam(naam) for naam in ties['Name'].values]
    missing_after = ties['Name'].isnull().sum()
    assert missing_before == missing_after

    return ties