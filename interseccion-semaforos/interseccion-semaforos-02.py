import simpy
import random
import matplotlib.pyplot as plt

# Parameters:
RANDOM_SEED = 42
SIMULATION_TIME = 2 * 60 * 60   # 2 hours (in seconds)
INTER_ARRIVAL_TIME = 30         # Average arrival time between vehicles in seconds
GREEN_LIGHT_DURATION = 60       # Green light duration in seconds
RED_LIGHT_DURATION = 60         # Red light duration in seconds
PEAK_HOUR_FACTOR = 0.5          # Reduction in inter-arrival time during peak hours

# Vehicle types:
VEHICLE_TYPES = {
    'Car': {'cross_time': (5, 10)},
    'Bus': {'cross_time': (10, 15)},
    'Truck': {'cross_time': (15, 20)}
}

# Vehicle generator:
class VehicleGenerator:
    def __init__(self, env, intersection):
        self.env = env
        self.intersection = intersection
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
            print(f"{self.env.now:.2f}: Vehicle {self.vehicle_count} ({vehicle_type}) generated")
            self.env.process(self.vehicle(self.vehicle_count, vehicle_type))

    def vehicle(self, vehicle_id, vehicle_type):
        # Each vehicle requests to cross the intersection
        arrival_time = self.env.now
        print(f"{self.env.now:.2f}: Vehicle {vehicle_id} ({vehicle_type}) arrived at intersection")
        with self.intersection.crossing.request() as request:
            yield request
            waiting_time = self.env.now - arrival_time
            self.intersection.waiting_times.append((vehicle_type, waiting_time))
            print(f"{self.env.now:.2f}: Vehicle {vehicle_id} ({vehicle_type}) started crossing after waiting {waiting_time:.2f} seconds")
            yield self.env.process(self.intersection.cross(vehicle_id, vehicle_type))

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
            print(f"{self.env.now:.2f}: Traffic light turned GREEN")
            yield self.env.timeout(GREEN_LIGHT_DURATION)
            # Red light phase
            self.green = False
            print(f"{self.env.now:.2f}: Traffic light turned RED")
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
        print(f"{self.env.now:.2f}: Vehicle {vehicle_id} ({vehicle_type}) is crossing the intersection and will take {crossing_time:.2f} seconds")
        yield self.env.timeout(crossing_time)

# Setup and Run Simulation
def run_simulation():
    random.seed(RANDOM_SEED)
    env = simpy.Environment()
    intersection = Intersection(env)
    vehicle_generator = VehicleGenerator(env, intersection)
    env.run(until=SIMULATION_TIME)
    return intersection.waiting_times

# Run the simulation and collect results
waiting_times = run_simulation()

# Analyze and visualize results by vehicle type
vehicle_types = list(VEHICLE_TYPES.keys())
waiting_times_by_type = {vehicle_type: [] for vehicle_type in vehicle_types}
for vehicle_type, waiting_time in waiting_times:
    waiting_times_by_type[vehicle_type].append(waiting_time)

plt.subplot(1, 2, 1)
for vehicle_type in vehicle_types:
    plt.hist(waiting_times_by_type[vehicle_type], bins=30, alpha=0.5, label=vehicle_type, edgecolor='black')

plt.xlabel('Waiting time (seconds)')
plt.ylabel('Number of vehicles')
plt.title('Distribution of vehicle waiting times at the intersection by vehicle type')
plt.legend()
plt.grid(True)

# Boxplot of waiting times by vehicle type
plt.subplot(1, 2, 2)
plt.boxplot([waiting_times_by_type[vehicle_type] for vehicle_type in vehicle_types], tick_labels=vehicle_types, vert=False)
plt.xlabel('Waiting time (seconds)')
plt.title('Boxplot of vehicle waiting times at the intersection by vehicle type')
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
    print(f"  Minimum waiting time: {min_waiting_time:.2f} seconds")
    print(f"  Average waiting time: {average_waiting_time:.2f} seconds")
    print(f"  Maximum waiting time: {max_waiting_time:.2f} seconds")