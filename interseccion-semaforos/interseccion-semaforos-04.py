import simpy
import random
import matplotlib.pyplot as plt

# Parameters
RANDOM_SEED = 42
SIM_TIME = 7200  # 2 hours in seconds
INTER_ARRIVAL_TIME = 10  # Average arrival time between vehicles in seconds
MIN_GREEN_LIGHT_DURATION = 30  # Minimum green light duration in seconds
MAX_GREEN_LIGHT_DURATION = 120  # Maximum green light duration in seconds
RED_LIGHT_DURATION = 60  # Red light duration in seconds
PEAK_HOUR_FACTOR = 0.5  # Reduction in inter-arrival time during peak hours
THRESHOLD_VEHICLES = 5  # Threshold of vehicles to adjust green light duration

# Vehicle Types
VEHICLE_TYPES = {
    'Car': {'cross_time': (5, 10)},
    'Bus': {'cross_time': (10, 15)},
    'Truck': {'cross_time': (15, 20)}
}

# Vehicle Generator
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
            print(f"Vehicle {self.vehicle_count} ({vehicle_type}) generated at time {self.env.now:.2f}")
            self.env.process(self.vehicle(self.vehicle_count, vehicle_type))

    def vehicle(self, vehicle_id, vehicle_type):
        # Each vehicle requests to cross the intersection
        arrival_time = self.env.now
        print(f"Vehicle {vehicle_id} ({vehicle_type}) arrived at intersection at time {arrival_time:.2f}")
        with self.intersection.crossing.request() as request:
            yield request
            waiting_time = self.env.now - arrival_time
            self.intersection.waiting_times.append((vehicle_type, waiting_time))
            print(f"Vehicle {vehicle_id} ({vehicle_type}) started crossing at time {self.env.now:.2f} after waiting {waiting_time:.2f} seconds")
            yield self.env.process(self.intersection.cross(vehicle_id, vehicle_type))

# Traffic Light Control with Sensors
class TrafficLight:
    def __init__(self, env, intersection):
        self.env = env
        self.intersection = intersection
        self.green = True
        self.total_green_time = 0
        self.total_red_time = 0
        self.adjustment_count = 0
        self.action = env.process(self.run())

    def run(self):
        while True:
            # Green light phase
            green_duration = self.adjust_green_light_duration()
            self.green = True
            print(f"Traffic light turned GREEN at time {self.env.now:.2f} for {green_duration} seconds")
            self.total_green_time += green_duration
            yield self.env.timeout(green_duration)
            # Red light phase
            self.green = False
            print(f"Traffic light turned RED at time {self.env.now:.2f} for {RED_LIGHT_DURATION} seconds")
            self.total_red_time += RED_LIGHT_DURATION
            yield self.env.timeout(RED_LIGHT_DURATION)

    def adjust_green_light_duration(self):
        # Adjust the green light duration based on the number of vehicles waiting
        num_vehicles_waiting = len(self.intersection.crossing.queue)
        if num_vehicles_waiting >= THRESHOLD_VEHICLES:
            self.adjustment_count += 1
            return min(MAX_GREEN_LIGHT_DURATION, MIN_GREEN_LIGHT_DURATION + 10 * num_vehicles_waiting)
        return MIN_GREEN_LIGHT_DURATION

# Intersection with Traffic Light
class Intersection:
    def __init__(self, env):
        self.env = env
        self.crossing = simpy.Resource(env, capacity=1)
        self.traffic_light = TrafficLight(env, self)
        self.waiting_times = []

    def cross(self, vehicle_id, vehicle_type):
        # Only allow crossing if the light is green
        while not self.traffic_light.green:
            yield self.env.timeout(1)
        # Simulate the time it takes for a vehicle to cross
        crossing_time = random.uniform(*VEHICLE_TYPES[vehicle_type]['cross_time'])
        print(f"Vehicle {vehicle_id} ({vehicle_type}) is crossing the intersection at time {self.env.now:.2f} and will take {crossing_time:.2f} seconds")
        yield self.env.timeout(crossing_time)

# Setup and Run Simulation
def run_simulation():
    random.seed(RANDOM_SEED)
    env = simpy.Environment()
    intersection = Intersection(env)
    vehicle_generator = VehicleGenerator(env, intersection)
    env.run(until=SIM_TIME)
    return intersection.waiting_times, intersection.traffic_light

# Run the simulation and collect results
waiting_times, traffic_light = run_simulation()

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

# Print summary of traffic light timings
print("\nTraffic Light Summary:")
print(f"Total time the light was GREEN: {traffic_light.total_green_time} seconds")
print(f"Total time the light was RED: {traffic_light.total_red_time} seconds")
print(f"Number of times green light duration was adjusted: {traffic_light.adjustment_count}")

# Bar chart of traffic light timings
time_labels = ['Green Light', 'Red Light']
time_values = [traffic_light.total_green_time, traffic_light.total_red_time]
plt.bar(time_labels, time_values, color=['green', 'red'])
plt.xlabel('Traffic Light State')
plt.ylabel('Total Time (seconds)')
plt.title('Total Time Traffic Light Was Green and Red')
plt.grid(axis='y')
plt.show()