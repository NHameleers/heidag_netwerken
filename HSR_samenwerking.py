### TODO ###

# betere flow:
# 1. Data prep
# 1b. Data filteren volgens input (jaar)
# 2. Graph prep: nodes en edges met alle attributes
# 3. Draw graph


# namen overal hetzelfde (vaste staf excel, pub json, onderwijs excel)

# 3 jaar samen hetzelfde blok organiseren telt ook 3 keer mee voor de edge weight
# wellicht is dat fair

# rode knop:
# optie om alleen ties met staf uit andere organisatie-eenheid te laten zien

# metrics:
# hoeveel ties in totaal? Met hoeveel personen werk je samen?
# hoeveel ties inner/outer? Met hoeveel personen binnen je eigen organisatie-eenheid werk je samen?
# percentage outer ties van totale ties, gemiddelde per organisatie_eenheid

# Awesome feature!!
# Kan ik de 2 plaatjes verbinden? Selecteer bijv. Mark links, en zie hem dan rechts ook highlighted

import streamlit as st
import streamlit.components.v1 as components
st.set_page_config(layout='wide')

import pandas as pd
import data_prep
import graph_prep as gp
import namen_prep
import metrics







VASTE_STAF_NAMEN = namen_prep.get_vaste_staf_namelist('Data/HSR Vaste staf 01-05-2022.XLSX')
VASTE_STAF_DF = pd.read_excel('Data/HSR Vaste staf 01-05-2022.XLSX', sheet_name='Sheet1')





'# Samenwerking binnen HSR'

left, right = st.columns(2)

keuze_opties = ['Onderzoek: Publicaties', 'Onderzoek: PhD Supervisie', 'Onderwijs: Blokgroepen']

with left:
    linker_graph_keuze = st.selectbox(label='Netwerk links:', options=keuze_opties)

    organisatie_eenheid = st.selectbox(label='Organisatie eenheid:', options=['Geen indeling', 'Onderzoekslijn', 'Academische Werkplaats', 'Research Unit'])

    f'## {linker_graph_keuze}'

with right:
    rechter_graph_keuze = st.selectbox(label='Netwerk rechts:', options=keuze_opties, index=2)

    onderwijs_jaar = st.selectbox(label='Onderwijsjaar:', options=['Alle jaren', '2019-2020', '2020-2021', '2021-2022'])

    f'## {rechter_graph_keuze}'



def deliver_graph(keuze):
    '''Takes option from input and returns the correct nx graph object'''
    if keuze == 'Onderzoek: Publicaties':
        return gp.create_onderzoek_graph('Data/2020_2021_HSR_publications.json', organisatie_eenheid)

    elif keuze == 'Onderzoek: PhD Supervisie':
        return gp.create_supervisie_graph(data_prep.prep_supervisie_data(), organisatie_eenheid)

    else:
        return gp.create_onderwijs_graph(data_prep.prep_onderwijs_data(), onderwijs_jaar, organisatie_eenheid)



def deliver_explanation(keuze):
    '''Takes option from input and returns the correct explanation of the network'''
    if keuze == 'Onderzoek: Publicaties':
        return 'Aantal gezamenlijke publicaties (volgens Pure) die vaste stafleden delen in de jaren 2020 en 2021. Samenwerking is gedefiniëerd als co-auteurschap van een publicatie.'


    elif keuze == 'Onderzoek: PhD Supervisie':        
        return 'Samenwerking op gebied van supervisie van PhD studenten. Samenwerking is gedefiniëerd als samen in een supervisieteam van een PhD student zitten.'


    else:
        return '''Samenwerking op gebied van onderwijs in de jaren 2019 t/m 2022. Samenwerking is gedefiniëerd als samen in de blokplanningsgroep zitten voor een blok.'''





G_links = deliver_graph(linker_graph_keuze)

html_links = gp.nx_graph_to_pyvis_filepath(G_links, 'linker_net.html')  

# Load HTML file in HTML component for display on Streamlit page
with left:

    with open(html_links, 'r', encoding='utf-8') as HtmlFile:
        components.html(HtmlFile.read(), height=700, width=700)




G_rechts = deliver_graph(rechter_graph_keuze)

html_rechts = gp.nx_graph_to_pyvis_filepath(G_rechts, 'rechter_net.html')    

# Load HTML file in HTML component for display on Streamlit page
with right:

    with open(html_rechts, 'r', encoding='utf-8') as HtmlFile:
        components.html(HtmlFile.read(), height=700, width=700)







if organisatie_eenheid is not 'Geen indeling':

    f'## Samenwerking over {organisatie_eenheid.lower()} heen'

    f'### {linker_graph_keuze}'
    linker_metrics = metrics.calc_perc_externe_interne_samenwerking(G_links, organisatie_eenheid, VASTE_STAF_DF) 
    st.table(linker_metrics)

    f'### {rechter_graph_keuze}'
    onderwijs_metrics = metrics.calc_perc_externe_interne_samenwerking(G_rechts, organisatie_eenheid, VASTE_STAF_DF)
    st.table(onderwijs_metrics)
