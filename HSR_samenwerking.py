from venv import create

import pandas as pd
import networkx as nx
from pyvis.network import Network
import graph_prep as gp
import streamlit as st
import streamlit.components.v1 as components
st.set_page_config(layout='wide')

VASTE_STAF_NAMEN = gp.get_vaste_staf_namelist('Data/HSR Vaste staf 01-05-2022.XLSX')


'# HSR Samenwerking'

G = gp.create_graph('Data/2020_2021_HSR_publications.json')

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


namen_in_netwerk = [G.nodes[id]['label'] for id in G.nodes]
niet_in_netwerk = [naam for naam in VASTE_STAF_NAMEN if naam not in namen_in_netwerk]

st.write('Vaste staf die om een of andere reden niet in netwerk voorkomt:')
st.write(niet_in_netwerk)

print(len(G.nodes))
