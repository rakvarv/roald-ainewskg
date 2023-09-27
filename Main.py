import dash
from dash import dcc, html, Input, Output
import networkx as nx
from rdflib import Graph, URIRef

# Initialize Dash app
app = dash.Dash(__name__)

# Load the turtle file containing the knowledge graph
knowledge_graph = Graph()
knowledge_graph.parse("graph.ttl", format="turtle")

# Create a NetworkX directed graph from the RDF data
G = nx.DiGraph()

for s, p, o in knowledge_graph:
    if isinstance(s, URIRef) and isinstance(o, URIRef):
        G.add_edge(s, o)

# Define the dash app layout
app.layout = html.Div([
    dcc.Graph(id="knowledge-graph")
])

# Callback to update graph visualization
@app.callback(
    Output('knowledge-graph', 'figure'),
    Input('knowledge-graph', 'relayoutData')
)
def update_graph(relayoutData):
    # Use Kamada-Kawai layout to automatically position nodes
    pos = nx.kamada_kawai_layout(G)

    # Create a Plotly figure for directed graph visualization
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    node_x = []
    node_y = []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)

    figure = {
        'data': [
            {
                'x': edge_x,
                'y': edge_y,
                'mode': 'lines',
                'line': {'width': 1, 'color': 'gray'}
            },
            {
                'x': node_x,
                'y': node_y,
                'mode': 'markers+text',
                'name': 'nodes',
                'marker': {'symbol': 'circle', 'size': 10, 'color': 'blue'},
                'text': list(G.nodes),
                'textposition': 'bottom center'
            }
        ],
        'layout': {
            'title': 'Knowledge Graph Visualization (Directed)',
            'showlegend': False,
            'hovermode': 'closest',
            'xaxis': {'showgrid': False, 'zeroline': False},
            'yaxis': {'showgrid': False, 'zeroline': False}
        }
    }

    return figure

if __name__ == "__main__":
    app.run_server(debug=True)
