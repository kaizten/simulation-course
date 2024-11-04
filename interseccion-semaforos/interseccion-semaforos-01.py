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

# Vehicle generator
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
            print(f"{self.env.now:.2f}: Vehicle {self.vehicle_count} generated")
            self.env.process(self.vehicle(self.vehicle_count))

    def vehicle(self, vehicle_id):
        # Each vehicle requests to cross the intersection
        arrival_time = self.env.now
        print(f"{self.env.now:.2f}: Vehicle {vehicle_id} arrived at intersection")
        with self.intersection.crossing.request() as request:
            yield request
            waiting_time = self.env.now - arrival_time
            self.intersection.waiting_times.append(waiting_time)
            print(f"{self.env.now:.2f}: Vehicle {vehicle_id} started crossing after waiting {waiting_time:.2f} seconds")
            yield self.env.process(self.intersection.cross(vehicle_id))

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

    def cross(self, vehicle_id):
        # Only allow crossing if the light is green
        while not self.traffic_light.green:
            yield self.env.timeout(1)
        # Simulate the time it takes for a vehicle to cross
        crossing_time = random.uniform(5, 10)
        print(f"{self.env.now:.2f}: Vehicle {vehicle_id} is crossing the intersection and will take {crossing_time:.2f} seconds")
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

# Analyze and visualize results
plt.subplot(1, 2, 1)
plt.hist(waiting_times, bins=30, edgecolor='black')
plt.xlabel('Waiting time (seconds)')
plt.ylabel('Number of vehicles')
plt.title('Distribution of vehicle waiting times at the intersection')
plt.grid(True)

# Boxplot of waiting times
plt.subplot(1, 2, 2)
plt.boxplot(waiting_times, vert=False)
plt.xlabel('Waiting time (seconds)')
plt.title('Boxplot of vehicle waiting times at the intersection')
plt.grid(True)

plt.show()

# Print summary of main KPIs
min_waiting_time = min(waiting_times) if waiting_times else 0
average_waiting_time = sum(waiting_times) / len(waiting_times) if waiting_times else 0
max_waiting_time = max(waiting_times) if waiting_times else 0
total_vehicles = len(waiting_times)
print("\nSummary of Main KPIs:")
print(f"Total number of vehicles: {total_vehicles}")
print(f"Minimum waiting time: {min_waiting_time:.2f} seconds")
print(f"Average waiting time: {average_waiting_time:.2f} seconds")
print(f"Maximum waiting time: {max_waiting_time:.2f} seconds")