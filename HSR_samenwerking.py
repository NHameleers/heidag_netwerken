from venv import create

import pandas as pd
import networkx as nx
from pyvis.network import Network
from graph_prep import create_graph
import streamlit as st
import streamlit.components.v1 as components
st.set_page_config(layout='wide')


'# HSR Samenwerking'

G = create_graph()

# Initiate PyVis network object
onderzoek_net = Network(height='750px', width='750px', bgcolor='white', font_color='black')

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
components.html(HtmlFile.read(), height=750, width=750)


