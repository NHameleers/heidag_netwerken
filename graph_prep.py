import networkx as nx
import json


def add_nodes(G, nodejson):
    for n in nodejson:

        if 'health services research' in n['properties']['name'].lower():
            continue

        c = 'green'
        if 'stoffers' in n['properties']['name'].lower():
            c = 'red'

        G.add_node(n['id'],
        label=n['properties']['name'],
        color=c)


    return G

def add_edges(G, edgejson):

    for e in edgejson:

        from_id = e['from']['id']
        to_id = e['to']['id']

        # one node is added to the graph after adding all edges, but I cannot find out which one that is
        try:
            G[from_id]
        except KeyError:
            print(f"from_id of {e['from']['properties']['name']} not in nodes")

        try:
            G[to_id]
        except KeyError:
            print(f"to_id of {e['to']['properties']['name']} not in nodes")


        # cleaning (HSR itself does not need to be an edge)
        if 'health services research' in from_id.lower().strip():
            continue

        if 'health services research' in to_id.lower().strip():
            continue

        G.add_edge(from_id, to_id, weight=e['label'] )

    return G


def create_graph():

    with open('Data/2020_2021_HSR_publications.json', 'r') as infile:
        d = json.load(infile)

    G = nx.Graph()

    G = add_nodes(G, d['nodes'][:3])

    G = add_edges(G, d['edges'][:3])

    return G





