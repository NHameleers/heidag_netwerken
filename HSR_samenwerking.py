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

from pyvis.network import Network
import pandas as pd
import data_prep
import graph_prep as gp
import namen_prep
import metrics







VASTE_STAF_NAMEN = namen_prep.get_vaste_staf_namelist('Data/HSR Vaste staf 01-05-2022.XLSX')
VASTE_STAF_DF = pd.read_excel('Data/HSR Vaste staf 01-05-2022.XLSX', sheet_name='Sheet1')





'# Samenwerking binnen HSR'

left, right = st.columns(2)


with left:
    organisatie_eenheid = st.selectbox(label='Organisatie eenheid:', options=['Geen indeling', 'Onderzoekslijn', 'Academische Werkplaats', 'Research Unit'])

    '## Onderzoek'
    'Aantal gezamenlijke publicaties (volgens Pure) die vaste stafleden delen in de jaren 2020 en 2021. Samenwerking is gedefiniëerd als co-auteurschap van een publicatie.'

with right:
    onderwijs_jaar = st.selectbox(label='Onderwijsjaar:', options=['Alle jaren', '2019-2020', '2020-2021', '2021-2022'])
    
    '## Onderwijs'
    '''Samenwerking op gebied van onderwijs in de jaren 2019 t/m 2022. Samenwerking is gedefiniëerd als samen in de blokplanningsgroep zitten voor een blok.'''












G = gp.create_onderzoek_graph('Data/2020_2021_HSR_publications.json', organisatie_eenheid)



# Initiate PyVis network object
onderzoek_net = Network(height='700px', width='700px', bgcolor='white', font_color='black')

# Take Networkx graph and translate it to a PyVis graph format
onderzoek_net.from_nx(G)

# Save and read graph as HTML file (on Streamlit Sharing)
try:
    path = './tmp'
    onderzoek_net.save_graph(f'{path}/pyvis_graph.html')
    HtmlFile = open(f'{path}/pyvis_graph.html', 'r', encoding='utf-8')

# Save and read graph as HTML file (locally)
except:
    path = './html_files'
    onderzoek_net.save_graph(f'{path}/pyvis_graph.html')
    HtmlFile = open(f'{path}/pyvis_graph.html', 'r', encoding='utf-8')

# Load HTML file in HTML component for display on Streamlit page
with left:
    components.html(HtmlFile.read(), height=700, width=700)











onderwijs_data = data_prep.prep_onderwijs_data()

H = gp.create_onderwijs_graph(onderwijs_data, onderwijs_jaar, organisatie_eenheid)


onderwijs_net = Network(height='700px', width='700px', bgcolor='white', font_color='black')

# Take Networkx graph and translate it to a PyVis graph format
onderwijs_net.from_nx(H)

# Save and read graph as HTML file (on Streamlit Sharing)
try:
    path = './tmp'
    onderwijs_net.save_graph(f'{path}/pyvis_graph.html')
    HtmlFile = open(f'{path}/pyvis_graph.html', 'r', encoding='utf-8')

# Save and read graph as HTML file (locally)
except:
    path = './html_files'
    onderwijs_net.save_graph(f'{path}/pyvis_graph.html')
    HtmlFile = open(f'{path}/pyvis_graph.html', 'r', encoding='utf-8')

# Load HTML file in HTML component for display on Streamlit page
with right:
    components.html(HtmlFile.read(), height=700, width=700)


if organisatie_eenheid is not 'Geen indeling':

    f'## Samenwerking over {organisatie_eenheid.lower()} heen'

    '### Onderzoek'
    onderzoek_metrics = metrics.calc_perc_externe_interne_samenwerking(G, organisatie_eenheid, VASTE_STAF_DF) 
    st.table(onderzoek_metrics)

    '### Onderwijs'
    onderwijs_metrics = metrics.calc_perc_externe_interne_samenwerking(H, organisatie_eenheid, VASTE_STAF_DF)
    st.table(onderwijs_metrics)
