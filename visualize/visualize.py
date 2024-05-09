#######################
# Import libraries
import requests
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import networkx as nx
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import numpy as np
import json
import pydeck as pdk
import random

#######################
# Page configuration
st.set_page_config(
    page_title="Publication Recommendation",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")


#######################
# Sidebar
import streamlit as st
import requests

link_style = "text-decoration: none; color: #1E88E5; font-weight: bold; font-size: 16px; margin-bottom: 10px;"

with st.sidebar:
    st.title('📚 Publication Recommendation')

    # Text input for searching
    if "my_input" not in st.session_state:
        st.session_state["my_input"] = ""
    my_input = st.text_input("Input a text here", st.session_state["my_input"])

    submit = st.button("Search")

    # Make request to the auto_complete endpoint only when submit button is clicked
    if submit:
        response = requests.get('http://localhost:8081/auto_complete', params={'query': my_input})
        if response.status_code == 200:
            autocomplete_data = response.json()
            pubs = autocomplete_data['pubs']
            st.markdown("Top results")
            # Display publication titles as clickable links with styling
            i = 1
            for pub in pubs:
                st.markdown(f'{i}. <a href="#{pub["id"]}" style="{link_style}">{pub["title"]}</a>', unsafe_allow_html=True)
                i += 1

#######################
# Plots

# Heatmap
def make_heatmap(input_df, input_y, input_x, input_color, input_color_theme):
    heatmap = alt.Chart(input_df).mark_rect().encode(
            y=alt.Y(f'{input_y}:O', axis=alt.Axis(title="Year", titleFontSize=18, titlePadding=15, titleFontWeight=900, labelAngle=0)),
            x=alt.X(f'{input_x}:O', axis=alt.Axis(title="", titleFontSize=18, titlePadding=15, titleFontWeight=900)),
            color=alt.Color(f'max({input_color}):Q',
                             legend=None,
                             scale=alt.Scale(scheme=input_color_theme)),
            stroke=alt.value('black'),
            strokeWidth=alt.value(0.25),
        ).properties(width=900
        ).configure_axis(
        labelFontSize=12,
        titleFontSize=12
        ) 
    # height=300
    return heatmap


def transform_data(input_data):
    transformed_data = []
    
    # Extract 'from' affiliation
    from_affiliation = input_data['affilations'][0]
    if from_affiliation['lat'] is not None and from_affiliation['lng'] is not None:
        from_data = {
            "from": {
                "name": from_affiliation['affiliation'],
                "coordinates": [
                    from_affiliation['lng'],
                    from_affiliation['lat']
                ]
            }
        }
    else:
        return []

    transformed_data.append(from_data)

    # Extract 'to' affiliations from node_graph
    node_graph = input_data.get('node_graph', {}).get('node', [])
    for node in node_graph:
        for to_affiliation in node['affilations']:
            if to_affiliation['lat'] is not None and to_affiliation['lng'] is not None:
                to_data = {
                    "to": {
                        "name": to_affiliation['affiliation'],
                        "coordinates": [
                            to_affiliation['lng'],
                            to_affiliation['lat']
                        ]
                    }
                }
                transformed_data.append({**from_data, **to_data})

    return transformed_data[1:]


# Load data from publication.json with explicit encoding
with open('publication.json', 'r', encoding='utf-8') as file:
    publication_data = json.load(file)

# Dashboard Main Panel
col = st.columns((4.5, 1), gap='medium')

with col[0]:
    st.markdown('#### Title')
    st.write(publication_data['title'])
    
    st.markdown('#### Affiliations')
    affiliations = [affiliation['affiliation'] for affiliation in publication_data['affilations']]
    st.write(affiliations)
    
    st.markdown('#### Abstract')
    st.write(publication_data['abstract'])
    
    st.markdown('#### Link')
    st.write(publication_data['link'])
    
    st.markdown('#### Recommend Publications')
    
    for rec_pub in publication_data['pub_rec']:
        publication_id = rec_pub['id']
        publication_title = rec_pub['title']
        st.markdown(f"{publication_id} : <a href='#{publication_id}'>{publication_title}</a>", unsafe_allow_html=True)

    # Plot network graph using NetworkX
    node_graph = publication_data['node_graph']
    edges = [(edge['source'], edge['target']) for edge in node_graph['edge']]
    G = nx.DiGraph()
    G.add_edges_from(edges)

    # Layout nodes using Fruchterman-Reingold force-directed algorithm
    pos = nx.spring_layout(G)

    # Use plotly to visualize the network graph created using NetworkX
    edge_trace = go.Scatter(
        x=[],
        y=[],
        line=dict(width=1, color='#888'),
        hoverinfo='text',
        mode='lines',
        text=[]  # Initialize text attribute as an empty list
    )

    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_trace['x'] += tuple([x0, x1, None])
        edge_trace['y'] += tuple([y0, y1, None])
        weight = G[edge[0]][edge[1]].get('weight', 1)  # Get the weight attribute of the edge, default to 1 if not present
        edge_trace['text'] += tuple([f'Weight: {weight}'])  # Append text to the list
    
    # Adding nodes to plotly scatter plot
    node_trace = go.Scatter(
        x=[],
        y=[],
        text=[],
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            colorscale=st.selectbox("Select Color Theme", ["Viridis", "Cividis", "YlGnBu"]),  # User-selectable color theme
            color=[],
            size=20,
            colorbar=dict(
                thickness=10,
                title='# Connections',
                xanchor='left',
                titleside='right'
            ),
            line=dict(width=0)))

    for node in G.nodes():
        x, y = pos[node]
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])

    for node, adjacencies in enumerate(G.adjacency()):
        node_trace['marker']['color'] += tuple([len(adjacencies[1])])  # Coloring each node based on the number of connections 
        node_info = f"{adjacencies[0]} # of connections: {len(adjacencies[1])}"
        node_trace['text'] += tuple([node_info])
    
    # Plot the final figure
    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title='Network Graph',
                        title_x=0.45,
                        titlefont=dict(size=25),
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20, l=5, r=5, t=40),
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))

    st.plotly_chart(fig, use_container_width=True)  # Show the graph in streamlit

    df = transform_data(publication_data)
    
    # Use pandas to prepare data for tooltip
    #df["from_name"] = df["from"].apply(lambda f: f["name"])
    #df["to_name"] = df["to"].apply(lambda t: t["name"])

    # Define a layer to display on a map
    layer = pdk.Layer(
        "GreatCircleLayer",
        df,
        pickable=True,
        get_stroke_width=12,
        get_source_position="from.coordinates",
        get_target_position="to.coordinates",
        get_source_color=[64, 255, 0],
        get_target_color=[0, 128, 200],
        auto_highlight=True,
    )

    # Set the viewport location
    view_state = pdk.ViewState(latitude=50, longitude=-40, zoom=1, bearing=0, pitch=0)

    # Render
    r = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        #tooltip={"text": "{from_name} to {to_name}"},
    )
    r.picking_radius = 10


    # Display the map in Streamlit
    st.pydeck_chart(r)