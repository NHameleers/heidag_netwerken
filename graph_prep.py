import networkx as nx
import json
import pandas as pd
from itertools import combinations
from collections import Counter


HSR_COLORS = ['#001C3D', '#E84E10', '#00A2DB', '#F8B296', '#F8884A', '#005370', '#ABD1FF', '#A1360B']

VASTE_STAF_DF = pd.read_excel('Data/HSR Vaste staf 01-05-2022.XLSX', sheet_name='Sheet1')

def get_vaste_staf_namelist(excelfile, naam_kolom='Volledige naam'):
    namen = pd.read_excel(excelfile, sheet_name='Sheet1')

    return list(namen[naam_kolom].dropna().values)

VASTE_STAF_NAMEN = get_vaste_staf_namelist('Data/HSR Vaste staf 01-05-2022.XLSX')


def check_if_vaste_staf(naam, vaste_staf_namen=VASTE_STAF_NAMEN):

    return naam in vaste_staf_namen

def check_if_vaste_staf_achternaam(achternaam, vaste_staf_namen=VASTE_STAF_NAMEN):
    vaste_staf_achternamen = [naam.split(' ')[-1] for naam in vaste_staf_namen]

    return achternaam in vaste_staf_achternamen





def add_nodes(G, nodejson):

    for n in nodejson:

        node_name = n['properties']['name']

        if 'health services research' in node_name.lower():
            continue

        # voeg node alleen toe als het vaste staf betreft
        if check_if_vaste_staf(node_name):

            G.add_node(n['id'],
            label=node_name) # kleur kan met color='blue'
        
    return G


def add_nodes_voor_vaste_staf_nog_niet_in_netwerk(G, size=None, vaste_staf_namen=VASTE_STAF_NAMEN):

    # Voeg ook mensen toe die wel in vaste staf zitten maar niet in netwerk voorkomen (omdat geen onderzoek of onderwijs)
    namen_in_netwerk = [G.nodes[id]['label'] for id in G.nodes]
    niet_in_netwerk = [naam for naam in vaste_staf_namen if naam not in namen_in_netwerk]
    for staflid in niet_in_netwerk:
        if size:
            G.add_node(staflid, label=staflid, shape='square', size=size)
        else:
            G.add_node(staflid, label=staflid, shape='square')

    return G


def add_edges(G, edgejson):

    for e in edgejson:

        from_id = e['from']['id']
        to_id = e['to']['id']
        from_name = e['from']['properties']['name']
        to_name = e['to']['properties']['name']

        # cleaning (HSR itself does not need to be an edge)
        if 'health services research' in from_name.lower():
            continue

        if 'health services research' in to_name.lower():
            continue

        # voeg edge alleen toe als deze van een vaste staf persoon naar een vaste staf persoon gaat
        if check_if_vaste_staf(from_name) and check_if_vaste_staf(to_name):
            w = e['label']
            G.add_edge(from_id, to_id, value=w, title=f"{w} gezamenlijke publicaties", color='grey')

    return G




def create_onderzoek_graph(json_filename):

    with open(json_filename, 'r', encoding='utf-8') as infile:
        d = json.load(infile)

    G = nx.Graph()

    G = add_nodes(G, d['nodes'])
    
    G = add_nodes_voor_vaste_staf_nog_niet_in_netwerk(G)

    G = add_edges(G, d['edges'])

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
    

def create_onderwijs_graph(filename, onderwijs_jaar):

    onderwijs = pd.read_csv(filename)

    if onderwijs_jaar != 'Alle jaren':
        jaar = int(onderwijs_jaar[:4])
        onderwijs = onderwijs[onderwijs.Year == jaar]


    G = nx.Graph()

    ### NODES
    stafnamen = onderwijs.Naam.unique()
    for naam in stafnamen:
        
        units_tooltip = maak_units_tooltip_voor_naam(naam, onderwijs)

        

        G.add_node(naam, label=naam, shape='dot', title=units_tooltip)

    G = add_nodes_voor_vaste_staf_nog_niet_in_netwerk(G)

    ### EDGES
    # Verzamel samenwerkingen binnen blokken
    alle_samenwerkingen = []

    for unityear in onderwijs.UnitYear.unique():

        # for the edges:
        # get rows of that unityear
        # get staff in that unityear
        samenwerking = onderwijs.loc[onderwijs.UnitYear == unityear, 'Naam'].values

        # get all combinations of 2 of staff in that unityear
        for c in list(combinations(samenwerking, 2)):
            alle_samenwerkingen.append(c)

    # alle_samenwerkingen is nu een lijst van 2-tuples.
    # om de edges gewicht te kunnen geven moeten we tellen hoe vaak elke 2-tuple voorkomt
    count_alle_samenwerkingen = Counter(alle_samenwerkingen)
    
    # dan kunnen we de edges toevoegen aan de graph
    for k, v in count_alle_samenwerkingen.items():
        samenwerking_units_tooltip = maak_units_tooltip_voor_samenwerking(k[0], k[1], onderwijs)
        G.add_edge(k[0], k[1], weight=v, value=v, title=samenwerking_units_tooltip, color='grey')

    return G

    

def kleur_nodes_volgens_kolom(G, kolom_kleur, naam_kolom='Volledige naam', vaste_staf_df=VASTE_STAF_DF, kleurcodes=HSR_COLORS):

    # unieke waarden in kolom
    # kleur per unieke waarde
    kleurdict = {waarde: kleurcodes[i] for i, waarde in enumerate(vaste_staf_df[kolom_kleur].unique())}

    # bereid dictionary voor met id: kleur pairs
    node_kleuren = {}
    # voor elke node
    # check unieke waarde en set color attribute
    for node_id in G.nodes:

        # zoek via naam op welke affiliation iemand heeft
        node_naam = G.nodes[node_id]['label']
        try:
            affiliation = vaste_staf_df.loc[vaste_staf_df[naam_kolom] == node_naam, kolom_kleur].values[0]
            node_kleuren[node_id] = kleurdict[affiliation]
        except IndexError:
            print(node_naam)

    # set dan voor alle nodes de kleur
    nx.set_node_attributes(G, node_kleuren, name="color")


