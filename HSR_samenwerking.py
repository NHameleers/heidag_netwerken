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

import pandas as pd
import data_prep
import graph_prep as gp
import namen_prep
import metrics







VASTE_STAF_NAMEN = namen_prep.get_vaste_staf_namelist('Data/HSR Vaste staf 01-05-2022.XLSX')
VASTE_STAF_DF = pd.read_excel('Data/HSR Vaste staf 01-05-2022.XLSX', sheet_name='Sheet1')





with st.expander('Disclaimer!'):
    '''
    Wees voorzichtig met interpretatie van de visualisaties en de cijfers. Denk bijvoorbeeld aan:
    * De zichtbare samenwerking is sterk afhankelijk van de definitie van een tie/edge. Let daarom steeds op hoe samenwerking is gedefiniëerd per onderwerp.
    * De visualisaties en tabellen betreffen slechts een bepaalde afgebakende periode.
    * De cijfers laten aantal samenwerkingen zien, maar niet aantal publicaties, PhD studenten, etc. Ga dus niet proberen om productie van onderzoekslijn of research unit te vergelijken m.b.v. deze cijfers.
    * Data betreffen HSR vaste staf, maar vaste staf zijn betekent niet een full-time aanstelling (dus bijv. 17 stafleden per onderzoekslijn betekent niet evenveel fte).
    * Er is geen rekening gehouden met percentage onderwijsaanstelling (of uberhaupt onderwijsaanstelling hebben)
    * Terugkomonderwijs voor de coschappen is niet meegenomen
    '''

'# Samenwerking binnen HSR'

left, right = st.columns(2)

keuze_opties = ['Onderzoek: Publicaties', 'Onderzoek: PhD Supervisie', 'Onderwijs: Blokgroepen']

with left:
    linker_graph_keuze = st.selectbox(label='Netwerk links:', options=keuze_opties)

    organisatie_eenheid = st.selectbox(label='Organisatie eenheid:',
                                       options=['Geen indeling', 'Onderzoekslijn', 'Research Unit'],
                                       index=1)

    f'## {linker_graph_keuze}'

with right:
    rechter_graph_keuze = st.selectbox(label='Netwerk rechts:', options=keuze_opties, index=1)

    # onderwijs_jaar = st.selectbox(label='Onderwijsjaar:', options=['Alle jaren', '2019-2020', '2020-2021', '2021-2022'])
    onderwijs_jaar = 'Alle jaren'


    coordinatorenoverleg_translate_dict = {"Coordinatorenoverleg includeren": False, "Coordinatorenoverleg excluderen": True}

    if rechter_graph_keuze == keuze_opties[-1]: # alleen voor onderwijs is deze enabled
        excl_coordinatorenoverleg_choice = st.selectbox(label='Samenwerking in coördinatorenoverleg:',
        options=["Coordinatorenoverleg includeren", "Coordinatorenoverleg excluderen"],
        index=1)
    else:
        excl_coordinatorenoverleg_choice = st.selectbox(label='Samenwerking in coördinatorenoverleg:',
        options=["Coordinatorenoverleg includeren", "Coordinatorenoverleg excluderen"],
        index=1, disabled=True)
    
    excl_coordinatorenoverleg = coordinatorenoverleg_translate_dict[excl_coordinatorenoverleg_choice]
    
    f'## {rechter_graph_keuze}'

names_visible = st.checkbox('Laat namen zien')
label_visibility = '#10000000'
if names_visible:
    label_visibility = 'black'

organisatie_eenheid_meervoud = 'onderzoekslijnen'
if organisatie_eenheid == 'Research Unit':
    organisatie_eenheid_meervoud = 'research units'

remove_inner_edges = st.checkbox(f'Laat alleen samenwerking tussen {organisatie_eenheid_meervoud} zien in visualisaties')




def deliver_graph(keuze):
    '''Takes option from input and returns the correct nx graph object'''
    if keuze == 'Onderzoek: Publicaties':
        return gp.create_onderzoek_graph('Data/2020_2021_HSR_publications.json', organisatie_eenheid, remove_inner_edges=remove_inner_edges)

    elif keuze == 'Onderzoek: PhD Supervisie':
        return gp.create_supervisie_graph(data_prep.prep_supervisie_data(), organisatie_eenheid, remove_inner_edges=remove_inner_edges)

    else:
        return gp.create_onderwijs_graph(data_prep.prep_onderwijs_data(), onderwijs_jaar, organisatie_eenheid, excl_coordinatorenoverleg=excl_coordinatorenoverleg, remove_inner_edges=remove_inner_edges)



def deliver_explanation(keuze):
    '''Takes option from input and returns the correct explanation of the network'''
    if keuze == 'Onderzoek: Publicaties':
        return 'Aantal gezamenlijke publicaties (volgens Pure) die vaste stafleden delen in de jaren 2020 en 2021. Samenwerking is gedefiniëerd als co-auteurschap van een publicatie.'


    elif keuze == 'Onderzoek: PhD Supervisie':        
        return 'Samenwerking is gedefiniëerd als samen in een supervisieteam van een HSR PhD student zitten (huidige en na juli 2021 gepromoveerde).'


    else:
        return '''Samenwerking op gebied van onderwijs in de jaren 2019 t/m 2022. Samenwerking is gedefiniëerd als samen in een blokplanningsgroep zitten (en coördinatorenoverleg als aangevinkt).'''





G_links = deliver_graph(linker_graph_keuze)

html_links = gp.nx_graph_to_pyvis_filepath(G_links, 'linker_net.html', font_color=label_visibility)  

# Load HTML file in HTML component for display on Streamlit page
with left:

    st.write(deliver_explanation(linker_graph_keuze))

    with open(html_links, 'r', encoding='utf-8') as HtmlFile:
        components.html(HtmlFile.read(), height=700, width=700)





G_rechts = deliver_graph(rechter_graph_keuze)

html_rechts = gp.nx_graph_to_pyvis_filepath(G_rechts, 'rechter_net.html', font_color=label_visibility)    

# Load HTML file in HTML component for display on Streamlit page
with right:

    st.write(deliver_explanation(rechter_graph_keuze))

    with open(html_rechts, 'r', encoding='utf-8') as HtmlFile:
        components.html(HtmlFile.read(), height=700, width=700)






if organisatie_eenheid is not 'Geen indeling':

    f'## Samenwerking tussen {organisatie_eenheid_meervoud} in cijfers'

    if remove_inner_edges:
        f'Deze cijfers zijn niet beschikbaar wanneer "Laat alleen samenwerking tussen {organisatie_eenheid_meervoud} zien" aan staat.'
    else:

        f'### {linker_graph_keuze}'
        linker_metrics = metrics.calc_perc_externe_interne_samenwerking(G_links, organisatie_eenheid, VASTE_STAF_DF) 
        st.table(linker_metrics)

        f'### {rechter_graph_keuze}'
        onderwijs_metrics = metrics.calc_perc_externe_interne_samenwerking(G_rechts, organisatie_eenheid, VASTE_STAF_DF)
        st.table(onderwijs_metrics)



