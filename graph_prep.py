import networkx as nx
from pyvis.network import Network
import json
import pandas as pd
from itertools import combinations
from collections import Counter
import namen_prep
import streamlit as st

HSR_COLORS = ['#001C3D', '#E84E10', '#00A2DB', '#F8B296', '#F8884A', '#005370', '#ABD1FF', '#A1360B']
VASTE_STAF_DF = pd.read_excel('Data/HSR Vaste staf 01-05-2022.XLSX', sheet_name='Sheet1')
VASTE_STAF_NAMEN = namen_prep.get_vaste_staf_namelist('Data/HSR Vaste staf 01-05-2022.XLSX')






def add_nodes(G, nodejson):

    for n in nodejson:

        node_name = n['properties']['name']

        if 'health services research' in node_name.lower():
            continue

        # voeg node alleen toe als het vaste staf betreft
        if namen_prep.check_if_vaste_staf(node_name):

            G.add_node(node_name,
            label=node_name) # kleur kan met color='blue'
        
    return G

def add_nodes_voor_vaste_staf_nog_niet_in_netwerk(G, size=None, vaste_staf_namen=VASTE_STAF_NAMEN):

    # Voeg ook mensen toe die wel in vaste staf zitten maar niet in netwerk voorkomen (omdat geen onderzoek of onderwijs)
    namen_in_netwerk = [naam for naam in G.nodes]
    niet_in_netwerk = [naam for naam in vaste_staf_namen if naam not in namen_in_netwerk]
    for staflid in niet_in_netwerk:
        if size:
            G.add_node(staflid, label=staflid, shape='square', size=size)
        else:
            G.add_node(staflid, label=staflid, shape='square')

    return G



def add_node_attributes(G, vaste_staf_df=VASTE_STAF_DF):

    # set_node_attributes takes a dict of dicts {id: {"attr1": "value1", "attr2": "value2"}}

    node_attr_dict = dict()

    for i, row in vaste_staf_df.iterrows():
        node_attr_dict[row['Volledige naam']] = {'Geen indeling': '',
        'Onderzoekslijn': row['Onderzoekslijn'],
        'Research Unit': row['Research Unit'],
        'Academische Werkplaats': row['Academische Werkplaats']}

    nx.set_node_attributes(G, node_attr_dict)

    return G




def add_edges(G, edgejson):

    for e in edgejson:

        from_name = e['from']['properties']['name']
        to_name = e['to']['properties']['name']

        # cleaning (HSR itself does not need to be an edge)
        if 'health services research' in from_name.lower():
            continue

        if 'health services research' in to_name.lower():
            continue

        # voeg edge alleen toe als deze van een vaste staf persoon naar een vaste staf persoon gaat
        if namen_prep.check_if_vaste_staf(from_name) and namen_prep.check_if_vaste_staf(to_name):
            w = e['label']
            G.add_edge(from_name, to_name, value=int(w), weight=int(w), title=f"{w} gezamenlijke publicatie(s)", color='grey')

    return G


def add_edge_attributes(G, organisatie_eenheid):
    '''Neemt een edge en checkt of beide nodes bij dezelfde organisatie_eenheid werken.
    Set vervolgens is_inner en is_outer attribute op 0 (verschillende organisatie_eenheid)
     of 1 (voor gelijke organisatie_eenheid)'''
    
    edge_attr_dict = dict()
    
    for edge in G.edges:
        from_affiliation = G.nodes[edge[0]][organisatie_eenheid]
        to_affiliation = G.nodes[edge[1]][organisatie_eenheid]
        if from_affiliation == to_affiliation:
            edge_attr_dict[edge] = {'is_inner': 1, 'is_outer': 0}
        else:
            edge_attr_dict[edge] = {'is_inner': 0, 'is_outer': 1}

    nx.set_edge_attributes(G, edge_attr_dict)
    
    return G



def create_onderzoek_graph(json_filename, organisatie_eenheid):

    with open(json_filename, 'r', encoding='utf-8') as infile:
        d = json.load(infile)

    G = nx.Graph()

    G = add_nodes(G, d['nodes'])
    
    G = add_nodes_voor_vaste_staf_nog_niet_in_netwerk(G)

    G = add_node_attributes(G, vaste_staf_df=VASTE_STAF_DF)

    G = add_edges(G, d['edges'])

    G = add_edge_attributes(G, organisatie_eenheid)
    
    if organisatie_eenheid is not 'Geen indeling':
        G = kleur_nodes_volgens_kolom(G, organisatie_eenheid)
    
    return G




##### ONDERZOEK SUPERVISIE GRAPH ####

def create_supervisie_graph(supervisie_df, organisatie_eenheid):
    
    G = nx.Graph()

    # add nodes from supervisie data
    ### NODES
    stafnamen = supervisie_df.Name.unique()
    for naam in stafnamen:
        
        # units_tooltip = maak_units_tooltip_voor_naam(naam, supervisie_df)

        G.add_node(naam, label=naam, shape='dot') # , title=units_tooltip)
    
    G = add_nodes_voor_vaste_staf_nog_niet_in_netwerk(G)

    G = add_node_attributes(G, vaste_staf_df=VASTE_STAF_DF)

    # add edges
    # Verzamel samenwerkingen binnen supervisie teams
    alle_samenwerkingen = []

    for phd in supervisie_df['PhD name'].unique():

        # for the edges:
        # get rows of that phd student
        # get staff supervising that student
        samenwerking = sorted(supervisie_df.loc[supervisie_df['PhD name'] == phd, 'Name'].values)

        # get all combinations of 2 of staff supervising the phd student
        for c in list(combinations(samenwerking, 2)):
            alle_samenwerkingen.append(c)

    # alle_samenwerkingen is nu een lijst van 2-tuples.
    # om de edges gewicht te kunnen geven moeten we tellen hoe vaak elke 2-tuple voorkomt
    count_alle_samenwerkingen = Counter(alle_samenwerkingen)
    
    # dan kunnen we de edges toevoegen aan de graph
    for k, v in count_alle_samenwerkingen.items():
        G.add_edge(k[0], k[1], value=int(v), weight=int(v), color='grey', title=f'Begeleiden samen {v} PhD(s)')

    G = add_edge_attributes(G, organisatie_eenheid)

    if organisatie_eenheid is not 'Geen indeling':
        G = kleur_nodes_volgens_kolom(G, organisatie_eenheid)
    
    return G



########## ONDERWIJS GRAPH

def maak_units_tooltip_voor_naam(naam, onderwijs):
    onderwijs_gegeven_door_naam = onderwijs[onderwijs.Naam == naam].copy()
    units_tooltip = ''
    if not onderwijs_gegeven_door_naam.empty:
        units = sorted([f'{unit} ({jaar})' for unit, jaar in zip(onderwijs_gegeven_door_naam.Unit.values, onderwijs_gegeven_door_naam.Year.values)])
        n_units = len(onderwijs_gegeven_door_naam.Unit.unique())
        units_tooltip = f"{n_units} uniek(e) blok(ken):\n" + "\n".join(units)

    return units_tooltip

def maak_units_tooltip_voor_samenwerking(from_naam, to_naam, onderwijs):

    # haal units op van beide namen
    onderwijs_from_naam = onderwijs.loc[onderwijs.Naam == from_naam, 'UnitYear'].values
    onderwijs_to_naam = onderwijs.loc[onderwijs.Naam == to_naam, 'UnitYear'].values

    unityear_set = set(onderwijs_from_naam) & set(onderwijs_to_naam)

    formatted_list = []

    # nice format: from Unit_Year to Unit (Year)
    if unityear_set:
        formatted_list = sorted([f"{unityear[:-5]} ({unityear[-4:]})" for unityear in unityear_set])
    
    tooltip = f"{len(unityear_set)} samenwerkingen:\n" + "\n".join(formatted_list)

    return tooltip
    
def create_onderwijs_graph(onderwijsdata, onderwijs_jaar, organisatie_eenheid, excl_coordinatorenoverleg):

    onderwijs = onderwijsdata.copy()

    if onderwijs_jaar != 'Alle jaren':
        jaar = int(onderwijs_jaar[:4])
        onderwijs = onderwijs[onderwijs.Year == jaar]

    if excl_coordinatorenoverleg:
        onderwijs = onderwijs.loc[~onderwijs.Unit.str.contains('COOR', na=False), ]

    G = nx.Graph()

    ### NODES
    stafnamen = onderwijs.Naam.unique()
    for naam in stafnamen:
        
        units_tooltip = maak_units_tooltip_voor_naam(naam, onderwijs)

        

        G.add_node(naam, label=naam, shape='dot', title=units_tooltip)

    G = add_nodes_voor_vaste_staf_nog_niet_in_netwerk(G)

    G = add_node_attributes(G, vaste_staf_df=VASTE_STAF_DF)

    ### EDGES
    # Verzamel samenwerkingen binnen blokken
    alle_samenwerkingen = []

    for unityear in onderwijs.UnitYear.unique():

        # for the edges:
        # get rows of that unityear
        # get staff in that unityear
        samenwerking = sorted(onderwijs.loc[onderwijs.UnitYear == unityear, 'Naam'].values)

        # get all combinations of 2 of staff in that unityear
        for c in list(combinations(samenwerking, 2)):
            alle_samenwerkingen.append(c)

    # alle_samenwerkingen is nu een lijst van 2-tuples.
    # om de edges gewicht te kunnen geven moeten we tellen hoe vaak elke 2-tuple voorkomt
    count_alle_samenwerkingen = Counter(alle_samenwerkingen)
    
    # dan kunnen we de edges toevoegen aan de graph
    for k, v in count_alle_samenwerkingen.items():
        if k[0]!= k[1]: # als het een tie is tussen 2 verschillende personen, en niet met zichzelf
            samenwerking_units_tooltip = maak_units_tooltip_voor_samenwerking(k[0], k[1], onderwijs)
            G.add_edge(k[0], k[1], value=int(v), weight=int(v), title=samenwerking_units_tooltip, color='grey')

    G = add_edge_attributes(G, organisatie_eenheid)
    
    if organisatie_eenheid is not 'Geen indeling':
        G = kleur_nodes_volgens_kolom(G, organisatie_eenheid)
    
    return G

    

def kleur_nodes_volgens_kolom(G, kolom_kleur, naam_kolom='Volledige naam', vaste_staf_df=VASTE_STAF_DF, kleurcodes=HSR_COLORS):

    # unieke waarden in kolom
    # kleur per unieke waarde
    kleurdict = {waarde: kleurcodes[i] for i, waarde in enumerate(vaste_staf_df[kolom_kleur].unique())}

    # bereid dictionary voor met id: kleur pairs
    node_kleuren = {}
    # voor elke node
    # check unieke waarde en set color attribute
    for node_naam in G.nodes:

        # zoek via naam op welke affiliation iemand heeft
        try:
            affiliation = vaste_staf_df.loc[vaste_staf_df[naam_kolom] == node_naam, kolom_kleur].values[0]
            node_kleuren[node_naam] = kleurdict[affiliation]
        except IndexError:
            print(node_naam)

    # set dan voor alle nodes de kleur
    nx.set_node_attributes(G, node_kleuren, name="color")
    
    return G




def nx_graph_to_pyvis_filepath(G, filename):
    '''Takes a networkx graph object and filename as input, converts the nx graph to pyvis Network object
    and saves that as html file for use on streamlit. Returns the filepath to the html file'''

    # Initiate PyVis network object
    onderzoek_net = Network(height='700px', width='700px', bgcolor='white', font_color='black')

    # Take Networkx graph and translate it to a PyVis graph format
    onderzoek_net.from_nx(G)

    # Save and read graph as HTML file (on Streamlit Sharing)
    try:
        path = f'./tmp/{filename}'
        onderzoek_net.save_graph(path)
        return path

    # Save and read graph as HTML file (locally)
    except:
        path = f'./html_files/{filename}'
        onderzoek_net.save_graph(path)
        return path