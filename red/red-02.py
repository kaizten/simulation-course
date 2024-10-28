import simpy
import json
import random
import time
import matplotlib.pyplot as plt
import networkx as nx
import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString

# Constants
SPEED = 10  # units/sec
NUM_VEHICLES = 50  # Number of vehicles in the simulation
SIMULATION_TIME = 100  # Total simulation time
FUEL_COST_PER_UNIT = 0.5  # Cost per distance unit
TIME_COST_PER_UNIT = 1.0  # Cost per time unit

# Load the road network from GeoJSON using GeoPandas to create a geospatial representation of the road data
geojson_file = 'roads.geojson'
road_data = gpd.read_file(geojson_file)

# Convert GeoJSON to a NetworkX graph
G = nx.Graph()
for _, feature in road_data.iterrows():
    if isinstance(feature.geometry, LineString):
        coords = list(feature.geometry.coords)
        # Iterate over each segment of the LineString and add edges to the graph
        for i in range(len(coords) - 1):
            distance = feature.geometry.length
            travel_time = distance / SPEED
            # Calculate cost considering both fuel and time
            cost = (FUEL_COST_PER_UNIT * distance) + (TIME_COST_PER_UNIT * travel_time)
            G.add_edge(coords[i], coords[i + 1], weight=cost, distance=distance)

# Initialize the SimPy environment to manage the simulation of vehicle movements
env = simpy.Environment()

# Create a DataFrame to store the paths taken by each vehicle, including the vehicle ID, current and next nodes, and the time of movement
vehicle_paths = pd.DataFrame(columns=['vehicle_id', 'current_node', 'next_node', 'time'])
vehicle_summary = pd.DataFrame(columns=['vehicle_id', 'total_cost', 'total_time', 'edges_traversed'])

# Vehicle process
def vehicle(env, vehicle_id, start_node, end_node, graph):
    """
    Define the vehicle process that simulates the movement of a vehicle from a start node to an end node through the graph.
    The vehicle follows the path that minimizes the total cost, and the movement is recorded in the DataFrame.
    """
    # Calculate the path that minimizes the cost (weight) between the start and end nodes
    path = nx.shortest_path(graph, source=start_node, target=end_node, weight='weight')
    total_cost = 0
    for i in range(len(path) - 1):
        current_node = path[i]
        next_node = path[i + 1]
        edge_data = graph[current_node][next_node]
        travel_time = edge_data['distance'] / SPEED
        total_cost += edge_data['weight']
        # Simulate the time delay for the vehicle to move from the current node to the next node, based on the travel time
        yield env.timeout(travel_time)
        print(f"[{env.now:.2f}] Vehicle {vehicle_id} moved from {current_node} to {next_node} at time {env.now:.2f}")
        # Record the movement of the vehicle in the DataFrame, including the vehicle ID, current and next nodes, and the current simulation time
        vehicle_paths.loc[len(vehicle_paths)] = [vehicle_id, current_node, next_node, env.now]
    # Record summary information for each vehicle
    vehicle_summary.loc[len(vehicle_summary)] = [vehicle_id, total_cost, env.now, len(path) - 1]

# Create vehicles
nodes = list(G.nodes)
for i in range(NUM_VEHICLES):
    start, end = random.sample(nodes, 2)
    env.process(vehicle(env, i, start, end, G))

# Run the simulation until the specified simulation time is reached
env.run(until=SIMULATION_TIME)

# Visualization
# Create a dictionary of positions for each node in the graph to be used for visualization
pos = {node: (node[0], node[1]) for node in G.nodes}
fig, ax = plt.subplots(figsize=(10, 10))
# Draw the road network using NetworkX, displaying nodes and edges with specified visual properties
nx.draw(G, pos, ax=ax, node_size=10, edge_color='gray', with_labels=True, font_size=8, font_color='blue')

# Plot vehicle paths (static visualization)
colors = ['r', 'g', 'b', 'y', 'm']
for i in range(NUM_VEHICLES):
    start, end = random.sample(nodes, 2)
    # Recalculate the path that minimizes the cost for visualization purposes, highlighting the paths taken by the vehicles
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

# Display vehicle summary DataFrame
print(vehicle_summary)
