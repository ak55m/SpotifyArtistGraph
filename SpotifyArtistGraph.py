import networkx as nx
import matplotlib.pyplot as plt
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Set up Spotify authentication
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id='bd41c61ece9d4df1b8b3f087569d3871',
                                               client_secret='3ad6f1d80607404c85ac104bca4a3b45',
                                               redirect_uri='http://localhost:7000/callback',
                                               scope='user-library-read'))

# Create a NetworkX graph
G = nx.Graph()

# Search for an artist's name
artist_name = input("Enter artist name: ")

search_results = sp.search(q=artist_name, type='artist', limit=1)

# Check if any search results were found
if search_results['artists']['items']:
    artist_info = search_results['artists']['items'][0]
    artist_id = artist_info['id']

    # Add the artist as a node
    G.add_node(artist_id, name=artist_name)

    # Fetch data about related artists
    max_iterations = 6
    current_iteration = 1
    related_artists = sp.artist_related_artists(artist_id)

    while related_artists['artists'] and current_iteration <= max_iterations:
        for related in related_artists['artists']:
            G.add_node(related['id'], name=related['name'])
            G.add_edge(artist_id, related['id'])

            # Fetch top tracks for the related artist
            top_tracks = sp.artist_top_tracks(related['id'])
            if top_tracks['tracks']:
                top_track_name = top_tracks['tracks'][0]['name']
                nx.set_node_attributes(G, {related['id']: top_track_name}, name='top_track')

        # Fetch data about related artists for the next iteration
        current_iteration += 1
        related_artists = sp.artist_related_artists(related_artists['artists'][0]['id'])

    # Prepare a dictionary of node labels (IDs mapped to names and top tracks)
    node_labels = {node_id: f"{G.nodes[node_id]['name']} - {G.nodes[node_id].get('top_track', '')}" for node_id in G.nodes}

    # Customize node and edge colors
    node_colors = ['grey' if node_id == artist_id else 'green' for node_id in G.nodes]
    edge_colors = ['gray' for _ in G.edges]

    # Customize font color for node labels
    font_color = 'black'

    # Visualize the graph with updated node labels
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G, seed=42)
    nx.draw(G, pos, labels=node_labels, node_color=node_colors, edge_color=edge_colors,
            node_size=1000, font_size=10, font_color=font_color, with_labels=True)
    plt.title("Related Artists Graph")
    plt.show()
else:
    print("No artist found with the given name.")
