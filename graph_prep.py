import networkx as nx
import json
import pandas as pd

def get_vaste_staf_namelist(excelfile):
    namen = pd.read_excel(excelfile, sheet_name='Sheet1')

    return list(namen['Volledige naam'].values)

VASTE_STAF_NAMEN = get_vaste_staf_namelist('Data/HSR Vaste staf 01-05-2022.XLSX')




def check_if_vaste_staf(naam, vaste_staf_namen=VASTE_STAF_NAMEN):

    return naam in vaste_staf_namen




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
            G.add_edge(from_id, to_id, weight=e['label'] )

    return G



# def save_names(G, nodejson):

#     namelist = [name['properties']['name'] for name in nodejson]

#     pd.DataFrame(namelist, columns=['naam']).to_csv('Data/namelist.csv', index=False)




def create_graph(json_filename):

    with open(json_filename, 'r', encoding='utf-8') as infile:
        d = json.load(infile)

    G = nx.Graph()

    G = add_nodes(G, d['nodes'])

    G = add_edges(G, d['edges'])

    return G




    