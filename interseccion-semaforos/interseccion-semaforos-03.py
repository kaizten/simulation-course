import simpy
import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pygame
import sys

# Parameters
RANDOM_SEED = 42
SIM_TIME = 7200  # 2 hours in seconds
INTER_ARRIVAL_TIME = 30  # Average arrival time between vehicles in seconds
GREEN_LIGHT_DURATION = 60  # Green light duration in seconds
RED_LIGHT_DURATION = 60  # Red light duration in seconds
PEAK_HOUR_FACTOR = 0.5  # Reduction in inter-arrival time during peak hours

# Vehicle Types
VEHICLE_TYPES = {
    'Car': {'cross_time': (5, 10)},
    'Bus': {'cross_time': (10, 15)},
    'Truck': {'cross_time': (15, 20)}
}

# Colors for each vehicle type
VEHICLE_COLORS = {
    'Car': (0, 0, 255),
    'Bus': (0, 255, 0),
    'Truck': (255, 0, 0)
}

# Vehicle Generator
class VehicleGenerator:
    def __init__(self, env, intersection, visualization):
        self.env = env
        self.intersection = intersection
        self.visualization = visualization
        self.vehicle_count = 0
        self.env.process(self.run())

    def run(self):
        while True:
            # Adjust the inter-arrival time during peak hours
            hour = self.env.now // 3600
            if hour in [8, 9, 17, 18]:  # Assuming peak hours are 8-9 AM and 5-6 PM
                inter_arrival_time = INTER_ARRIVAL_TIME * PEAK_HOUR_FACTOR
            else:
                inter_arrival_time = INTER_ARRIVAL_TIME
            
            # Generate a vehicle
            yield self.env.timeout(random.expovariate(1.0 / inter_arrival_time))
            self.vehicle_count += 1
            vehicle_type = random.choice(list(VEHICLE_TYPES.keys()))
            print(f"Vehicle {self.vehicle_count} ({vehicle_type}) generated at time {self.env.now:.2f}")
            self.env.process(self.vehicle(self.vehicle_count, vehicle_type))

    def vehicle(self, vehicle_id, vehicle_type):
        # Each vehicle requests to cross the intersection
        arrival_time = self.env.now
        print(f"Vehicle {vehicle_id} ({vehicle_type}) arrived at intersection at time {arrival_time:.2f}")
        self.visualization.add_vehicle(vehicle_id, vehicle_type, 'waiting')
        with self.intersection.crossing.request() as request:
            yield request
            waiting_time = self.env.now - arrival_time
            self.intersection.waiting_times.append((vehicle_type, waiting_time))
            print(f"Vehicle {vehicle_id} ({vehicle_type}) started crossing at time {self.env.now:.2f} after waiting {waiting_time:.2f} seconds")
            self.visualization.remove_vehicle(vehicle_id)
            self.visualization.add_vehicle(vehicle_id, vehicle_type, 'crossing')
            yield self.env.process(self.intersection.cross(vehicle_id, vehicle_type))
            self.visualization.remove_vehicle(vehicle_id)
            self.visualization.add_vehicle(vehicle_id, vehicle_type, 'passed')

# Traffic Light Control
class TrafficLight:
    def __init__(self, env):
        self.env = env
        self.green = True
        self.action = env.process(self.run())

    def run(self):
        while True:
            # Green light phase
            self.green = True
            print(f"Traffic light turned GREEN at time {self.env.now:.2f}")
            yield self.env.timeout(GREEN_LIGHT_DURATION)
            # Red light phase
            self.green = False
            print(f"Traffic light turned RED at time {self.env.now:.2f}")
            yield self.env.timeout(RED_LIGHT_DURATION)

# Intersection with Traffic Light
class Intersection:
    def __init__(self, env):
        self.env = env
        self.crossing = simpy.Resource(env, capacity=1)
        self.traffic_light = TrafficLight(env)
        self.waiting_times = []

    def cross(self, vehicle_id, vehicle_type):
        # Only allow crossing if the light is green
        while not self.traffic_light.green:
            yield self.env.timeout(1)
        # Simulate the time it takes for a vehicle to cross
        crossing_time = random.uniform(*VEHICLE_TYPES[vehicle_type]['cross_time'])
        print(f"Vehicle {vehicle_id} ({vehicle_type}) is crossing the intersection at time {self.env.now:.2f} and will take {crossing_time:.2f} seconds")
        yield self.env.timeout(crossing_time)

# Visualization using Pygame
class Visualization:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1000, 800))
        pygame.display.set_caption("Traffic Intersection Simulation")
        self.clock = pygame.time.Clock()
        self.vehicles = {'waiting': {}, 'crossing': {}, 'passed': {}}
        self.traffic_light_status = 'GREEN'
        self.font = pygame.font.Font(None, 36)

    def add_vehicle(self, vehicle_id, vehicle_type, state):
        if state == 'waiting':
            self.vehicles['waiting'][vehicle_id] = {'type': vehicle_type, 'position': (100, 375)}
        elif state == 'crossing':
            self.vehicles['crossing'][vehicle_id] = {'type': vehicle_type, 'position': (500, 375)}
        elif state == 'passed':
            self.vehicles['passed'][vehicle_id] = {'type': vehicle_type, 'position': (800, 375)}

    def remove_vehicle(self, vehicle_id):
        for state in self.vehicles:
            if vehicle_id in self.vehicles[state]:
                del self.vehicles[state][vehicle_id]
                break

    def update_traffic_light(self, status):
        self.traffic_light_status = status

    def update(self):
        self.screen.fill((245, 245, 245))  # Light grey background for better contrast
        # Draw roads
        pygame.draw.rect(self.screen, (100, 100, 100), (0, 375, 1000, 50))  # Horizontal road
        pygame.draw.rect(self.screen, (100, 100, 100), (475, 0, 50, 800))  # Vertical road
        # Draw intersection
        pygame.draw.rect(self.screen, (169, 169, 169), (450, 350, 100, 100))  # Intersection area
        # Draw traffic light status
        traffic_light_color = (0, 255, 0) if self.traffic_light_status == 'GREEN' else (255, 0, 0)
        pygame.draw.circle(self.screen, traffic_light_color, (750, 150), 30)
        traffic_light_text = self.font.render('Traffic Light', True, (0, 0, 0))
        self.screen.blit(traffic_light_text, (750, 100))
        # Draw vehicles
        for state in ['waiting', 'crossing', 'passed']:
            for vehicle_id, vehicle in self.vehicles[state].items():
                vehicle_type = vehicle['type']
                color = VEHICLE_COLORS[vehicle_type]
                position = vehicle['position']
                pygame.draw.rect(self.screen, color, (*position, 40, 20))
                vehicle_label = self.font.render(f'{vehicle_type} {vehicle_id}', True, (0, 0, 0))
                #self.screen.blit(vehicle_label, (position[0], position[1] - 20))
        # Draw text for vehicle counts
        waiting_count = len(self.vehicles['waiting'])
        crossing_count = len(self.vehicles['crossing'])
        passed_count = len(self.vehicles['passed'])
        waiting_text = self.font.render(f'Waiting: {waiting_count}', True, (0, 0, 0))
        crossing_text = self.font.render(f'Crossing: {crossing_count}', True, (0, 0, 0))
        passed_text = self.font.render(f'Passed: {passed_count}', True, (0, 0, 0))
        self.screen.blit(waiting_text, (50, 50))
        self.screen.blit(crossing_text, (50, 100))
        self.screen.blit(passed_text, (50, 150))
        # Draw lane markers
        for i in range(0, 1000, 60):
            pygame.draw.line(self.screen, (255, 255, 255), (i, 400), (i + 30, 400), 5)  # Dashed lines on horizontal road
        for i in range(0, 800, 60):
            pygame.draw.line(self.screen, (255, 255, 255), (500, i), (500, i + 30), 5)  # Dashed lines on vertical road
        pygame.display.flip()
        self.clock.tick(60)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

# Setup and Run Simulation
def run_simulation():
    random.seed(RANDOM_SEED)
    env = simpy.Environment()
    visualization = Visualization()
    intersection = Intersection(env)
    vehicle_generator = VehicleGenerator(env, intersection, visualization)
    
    # Run simulation with real-time visualization
    while env.now < SIM_TIME:
        env.step()
        visualization.update()
        visualization.handle_events()
        # Update traffic light status in visualization
        visualization.update_traffic_light('GREEN' if intersection.traffic_light.green else 'RED')
    
    return intersection.waiting_times

# Run the simulation and collect results
waiting_times = run_simulation()

# Analyze and visualize results by vehicle type
vehicle_types = list(VEHICLE_TYPES.keys())
waiting_times_by_type = {vehicle_type: [] for vehicle_type in vehicle_types}
for vehicle_type, waiting_time in waiting_times:
    waiting_times_by_type[vehicle_type].append(waiting_time)

for vehicle_type in vehicle_types:
    plt.hist(waiting_times_by_type[vehicle_type], bins=30, alpha=0.5, label=vehicle_type, edgecolor='black')

plt.xlabel('Waiting Time (seconds)')
plt.ylabel('Number of Vehicles')
plt.title('Distribution of Vehicle Waiting Times at the Intersection by Vehicle Type')
plt.legend()
plt.grid(True)
plt.show()

# Boxplot of waiting times by vehicle type
plt.boxplot([waiting_times_by_type[vehicle_type] for vehicle_type in vehicle_types], labels=vehicle_types, vert=False)
plt.xlabel('Waiting Time (seconds)')
plt.title('Boxplot of Vehicle Waiting Times at the Intersection by Vehicle Type')
plt.grid(True)
plt.show()

# Print summary of main KPIs by vehicle type
print("\nSummary of Main KPIs by Vehicle Type:")
for vehicle_type in vehicle_types:
    times = waiting_times_by_type[vehicle_type]
    average_waiting_time = sum(times) / len(times) if times else 0
    max_waiting_time = max(times) if times else 0
    min_waiting_time = min(times) if times else 0
    total_vehicles = len(times)
    print(f"\n{vehicle_type}: ")
    print(f"  Total number of vehicles: {total_vehicles}")
    print(f"  Average waiting time: {average_waiting_time:.2f} seconds")
    print(f"  Maximum waiting time: {max_waiting_time:.2f} seconds")
    print(f"  Minimum waiting time: {min_waiting_time:.2f} seconds")
