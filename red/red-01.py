import simpy
import random
import matplotlib.pyplot as plt
import networkx as nx
import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString

# Constants
SPEED = 10  # units/sec
NUM_VEHICLES = 50
SIMULATION_TIME = 100

# Load the road network from GeoJSON
geojson_file = 'roads.geojson'
road_data = gpd.read_file(geojson_file)

# Convert GeoJSON to a NetworkX graph
G = nx.Graph()
for _, feature in road_data.iterrows():
    if isinstance(feature.geometry, LineString):
        coords = list(feature.geometry.coords)
        for i in range(len(coords) - 1):
            G.add_edge(coords[i], coords[i + 1], weight=feature.geometry.length)

# SimPy environment
env = simpy.Environment()

# DataFrame to store vehicle paths
vehicle_paths = pd.DataFrame(columns=['vehicle_id', 'current_node', 'next_node', 'time'])

# Vehicle process
def vehicle(env, vehicle_id, start_node, end_node, graph):
    path = nx.shortest_path(graph, source=start_node, target=end_node, weight='weight')
    for i in range(len(path) - 1):
        current_node = path[i]
        next_node = path[i + 1]
        travel_time = graph[current_node][next_node]['weight'] / SPEED
        yield env.timeout(travel_time)
        print(f"[{env.now:.2f}] Vehicle {vehicle_id} moved from {current_node} to {next_node}")
        vehicle_paths.loc[len(vehicle_paths)] = [vehicle_id, current_node, next_node, env.now]

# Create vehicles
nodes = list(G.nodes)
for i in range(NUM_VEHICLES):
    start, end = random.sample(nodes, 2)
    env.process(vehicle(env, i, start, end, G))

# Run the simulation
env.run(until=SIMULATION_TIME)

# Visualization
pos = {node: (node[0], node[1]) for node in G.nodes}
fig, ax = plt.subplots(figsize=(10, 10))
nx.draw(G, pos, ax=ax, node_size=10, edge_color='gray', with_labels=True, font_size=8, font_color='blue')

# Plot vehicle paths (static visualization)
colors = ['r', 'g', 'b', 'y', 'm']
for i in range(NUM_VEHICLES):
    start, end = random.sample(nodes, 2)
    path = nx.shortest_path(G, source=start, target=end, weight='weight')
    path_edges = list(zip(path, path[1:]))
    nx.draw_networkx_edges(G, pos, edgelist=path_edges, ax=ax, edge_color=colors[i % len(colors)], width=2)

plt.title("Road Network and Vehicle Paths")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.show()

# Display vehicle paths DataFrame
vehicle_paths = vehicle_paths.sort_values(by=['vehicle_id', 'time'])
print(vehicle_paths)