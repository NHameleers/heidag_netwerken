
def calc_outer_inner_ratio(G, organisatie_eenheid, vaste_staf_df):
    
    # paar dingen nodig:
    # per affiliation (dat is een value binnen organisatie_eenheid):
        # telling van aantal personen binnen deze affiliation (om te normaliseren)
        # telling van aantal 
    result = dict()
    
    for affiliation in vaste_staf_df[organisatie_eenheid].unique():



        # all nodes with that affiliation
        aff_nodes = [node for node, aff in G.nodes(data=organisatie_eenheid) if aff == affiliation]

        result[affiliation] = {'total_edges': 0,
        'total_inner': 0,
        'total_outer': 0,
        'total_staff': len(aff_nodes)}

        for node in aff_nodes:
            print('edges upcoming of...', node)
            print(G.edges(node, data='is_inner'))
            aff_inner_sum = sum([is_inner / 2 for f, t, is_inner in G.edges(node, data='is_inner')]) # /2 omdat we anders de inner edges dubbel tellen
            result[affiliation]['total_inner'] += aff_inner_sum

            aff_outer_sum = sum([is_outer for f, t, is_outer in G.edges(node, data='is_outer')])
            result[affiliation]['total_outer'] += aff_outer_sum

            result[affiliation]['total_edges'] += aff_inner_sum + aff_outer_sum 

        try:
            result[affiliation]['outer_inner_ratio'] = round(result[affiliation]['total_outer'] / result[affiliation]['total_edges'], 2) 
        except ZeroDivisionError:
            result[affiliation]['outer_inner_ratio'] = 0
            
    return result