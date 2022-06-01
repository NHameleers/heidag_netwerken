import pandas as pd
import streamlit as st

NAAM_MAPPING = pd.read_excel('Data/HSR Vaste staf 01-05-2022.XLSX', sheet_name='NaamMapping')

@st.cache(suppress_st_warning=True)
def onderwijsnaam_naar_onderzoeksnaam(naam, naam_mapping=NAAM_MAPPING):

    return naam_mapping.loc[naam_mapping.OnderwijsNaam == naam, 'Volledige naam'].values[0]


@st.cache(suppress_st_warning=True)
def get_vaste_staf_namelist(excelfile, naam_kolom='Volledige naam'):
    namen = pd.read_excel(excelfile, sheet_name='Sheet1')

    return list(namen[naam_kolom].dropna().values)

VASTE_STAF_NAMEN = get_vaste_staf_namelist('Data/HSR Vaste staf 01-05-2022.XLSX')



def check_if_vaste_staf(naam, vaste_staf_namen=VASTE_STAF_NAMEN):

    return naam in vaste_staf_namen



def check_if_vaste_staf_achternaam(achternaam, vaste_staf_namen=VASTE_STAF_NAMEN):
    vaste_staf_achternamen = [naam.split(' ')[-1] for naam in vaste_staf_namen]

    return achternaam in vaste_staf_achternamen




