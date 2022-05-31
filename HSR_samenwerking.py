### TODO ###

# 3 jaar samen hetzelfde blok organiseren telt ook 3 keer mee voor de edge weight

# blokken in tooltip van node
# aantal unieke blokken --> node size

# namen van blokken waarin wordt samengewerkt in edge tooltip






from venv import create

import random
import pandas as pd
import networkx as nx
from pyvis.network import Network
import graph_prep as gp
import streamlit as st
import streamlit.components.v1 as components
st.set_page_config(layout='wide')

random.seed(10)

VASTE_STAF_NAMEN = gp.get_vaste_staf_namelist('Data/HSR Vaste staf 01-05-2022.XLSX')







with st.sidebar:
    'Onderzoek:'
    onderzoek_kleur = st.selectbox(label='Kleur de nodes naar...:',
    options=['Geen indeling', 'Onderzoekslijn', 'Academische Werkplaats', 'Research Unit'])

    'Onderwijs'
    onderwijs_kleur = st.selectbox(label='Kleur de nodes naar...:',
    options=['Geen indeling', 'Onderzoekslijn', 'Academische Werkplaats', 'Research Unit', 'GW'])

    onderwijs_jaar = st.selectbox(label='Jaar:',
    options=['Alle jaren', '2019-2020', '2020-2021', '2021-2022'])










'# HSR Samenwerking'

G = gp.create_onderzoek_graph('Data/2020_2021_HSR_publications.json')

if onderzoek_kleur is not 'Geen indeling':
    gp.kleur_nodes_volgens_kolom(G, onderzoek_kleur)


# Initiate PyVis network object
onderzoek_net = Network(height='600px', width='1000px', bgcolor='white', font_color='black')

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

'## Onderzoek'
'Aantal gezamenlijke publicaties (volgens Pure) die vaste stafleden delen in de jaren 2020 en 2021'
# Load HTML file in HTML component for display on Streamlit page
components.html(HtmlFile.read(), height=600, width=1000)











'## Onderwijs'
'''Samenwerking op gebied van onderwijs in de jaren 2019 t/m 2022. Samenwerking is gedefiniëerd als samen in de blokplanningsgroep zitten voor een blok.'''


H = gp.create_onderwijs_graph('Data/onderwijs.csv', onderwijs_jaar=onderwijs_jaar)

if onderwijs_kleur is not 'Geen indeling':
    gp.kleur_nodes_volgens_kolom(H, onderwijs_kleur)


onderwijs_net = Network(height='600px', width='1000px', bgcolor='white', font_color='black')

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
components.html(HtmlFile.read(), height=600, width=1000)

