#######################
# Import libraries
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import networkx as nx
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import numpy as np
import json

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
with st.sidebar:
    st.title('📚 Publication Recommendation')

    color_theme_list = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis']
    selected_color_theme = st.selectbox('Select a color theme', color_theme_list)

    # Text input for searching
    if "my_input" not in st.session_state:
        st.session_state["my_input"] = ""
    my_input = st.text_input("Input a text here", st.session_state["my_input"])
    
    submit = st.button("Search")

    # Load the data from auto_complete.json
    with open('auto_complete.json', 'r') as file:
        autocomplete_data = json.load(file)
        titles = [pub['title'] for pub in autocomplete_data['pubs']]
    
    # Dropdown menu for displaying publication titles
    selected_title = st.selectbox("Select a publication title", titles)


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

    # Extract latitudes and longitudes from the node data
    node_data = publication_data['node_graph']['node']
    node_df = pd.DataFrame(node_data)

    # Function to generate random latitude and longitude
    def generate_random_lat_lng():
        return np.random.uniform(-90, 90), np.random.uniform(-180, 180)

    # Replace null values in latitude and longitude with random values
    for i, row in node_df.iterrows():
        for affiliation in row['affilations']:
            if affiliation['lat'] is None:
                affiliation['lat'] = generate_random_lat_lng()[0]
            if affiliation['lng'] is None:
                affiliation['lng'] = generate_random_lat_lng()[1]

    # Convert nested affiliations into rows
    rows = []
    for i, row in node_df.iterrows():
        for affiliation in row['affilations']:
            rows.append({
                'title': row['title'],
                'id': row['id'],
                'affiliation': affiliation['affiliation'],
                'lat': affiliation['lat'],
                'lng': affiliation['lng']
            })

    # Create DataFrame from the flattened rows
    node_df_flat = pd.DataFrame(rows)

    # Plot the scatter plot map
    fig = px.scatter_mapbox(node_df_flat, lat="lat", lon="lng", hover_name="title",
                            hover_data=["id", "affiliation"], zoom=3, height=500)

    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    st.plotly_chart(fig, use_container_width=True)