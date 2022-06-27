import numpy as np
import pandas as pd
import math

def calc_perc_externe_interne_samenwerking(G, organisatie_eenheid, vaste_staf_df, verbose=False):
    
    organisatie_eenheid_meervoud = 'onderzoekslijnen'
    if organisatie_eenheid == 'Research Unit':
        organisatie_eenheid_meervoud = 'research units'


    # paar dingen nodig:
    # per affiliation (dat is een value binnen organisatie_eenheid):
        # telling van aantal personen binnen deze affiliation (om te normaliseren)
        # telling van aantal 
    unique_affiliations = vaste_staf_df[organisatie_eenheid].unique()
    all_metrics = [f'Alle samenwerkingen binnen {organisatie_eenheid.lower()}',
     f'Samenwerkingen binnen {organisatie_eenheid.lower()}',
     f'Samenwerkingen tussen {organisatie_eenheid_meervoud}',
     f'Aantal stafleden binnen {organisatie_eenheid.lower()}',
     f'Percentage samenwerking tussen {organisatie_eenheid_meervoud} (van alle samenwerkingen']
    result = pd.DataFrame(index=unique_affiliations,
    columns=all_metrics,
    data=np.zeros((len(unique_affiliations), len(all_metrics))))

    if verbose:
        print(result)

    for affiliation in unique_affiliations:

        # all nodes with that affiliation
        aff_nodes = [node for node, aff in G.nodes(data=organisatie_eenheid) if aff == affiliation]

        result.loc[affiliation, f'Aantal stafleden binnen {organisatie_eenheid.lower()}'] = len(aff_nodes)
        # result[affiliation] = {f'Alle samenwerkingen binnen {organisatie_eenheid.lower()}': 0,
        # f'Samenwerkingen binnen {organisatie_eenheid.lower()}': 0,
        # f'Samenwerkingen tussen {organisatie_eenheid_meervoud}': 0,
        # f'Aantal stafleden binnen {organisatie_eenheid.lower()}': len(aff_nodes)}

        for node in aff_nodes:

            # bereken de som van alle interne samenwerkingen (weights van inner edges)
            #  voor deze node en deel door 2 omdat anders de inner nodes van een organisatie_eenheid/affiliation
            #  dubbel geteld worden
            weights_inner_edges = [d['weight'] for u, v, d in G.edges(node, data=True) if d['is_inner'] == 1]
            aff_inner_sum = sum(weights_inner_edges) / 2 # /2 omdat we anders de inner edges dubbel tellen
            result.loc[affiliation, f'Samenwerkingen binnen {organisatie_eenheid.lower()}'] += aff_inner_sum

            # som van alle samenwerkingen across organisatie_eenheid
            weights_outer_edges = [d['weight'] for u, v, d in G.edges(node, data=True) if d['is_outer'] == 1]
            aff_outer_sum = sum(weights_outer_edges)
            result.loc[affiliation, f'Samenwerkingen tussen {organisatie_eenheid_meervoud}'] += aff_outer_sum

            # totale samenwerkingen
            result.loc[affiliation, f'Alle samenwerkingen binnen {organisatie_eenheid.lower()}'] += aff_inner_sum + aff_outer_sum 

            if verbose:
                print(node)
                print('edges van node: ', G.edges(node, data=True))
                print()
                print('weights van inner edges (dus alle interne samenwerkingen van deze persoon', weights_inner_edges)
                print()
                print(result)
                print()
                print()
        try:
            result.loc[affiliation, f'Percentage samenwerking tussen {organisatie_eenheid_meervoud} (van alle samenwerkingen'] = round(100 * result.loc[affiliation, f'Samenwerkingen tussen {organisatie_eenheid_meervoud}'] / result.loc[affiliation, f'Alle samenwerkingen binnen {organisatie_eenheid.lower()}']) 
        except ZeroDivisionError:
            result.loc[affiliation, f'Percentage samenwerking tussen {organisatie_eenheid_meervoud} (van alle samenwerkingen'] = 0
        except ValueError:
            result.loc[affiliation, f'Percentage samenwerking tussen {organisatie_eenheid_meervoud} (van alle samenwerkingen'] = np.nan

          
    result[f'Percentage samenwerking tussen {organisatie_eenheid_meervoud} (van alle samenwerkingen'] = [f'{d}%' if not math.isnan(d) else 'n.v.t.' for d in result[f'Percentage samenwerking tussen {organisatie_eenheid_meervoud} (van alle samenwerkingen'].values]   

    
    result = result.style.format("{:.0f}", subset=all_metrics[:-1])

    return result