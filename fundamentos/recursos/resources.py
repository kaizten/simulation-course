import simpy
import random
import matplotlib.pyplot as plt

# Parameters:
TRIP_DURATION_MEAN = 30  # Average duration of each trip
TRIP_DURATION_SD = 5     # Standard deviation of trip duration
INTER_ARRIVAL_TIME = 10  # Time between successive arrival of people at the vehicle station
SIMULATION_TIME = 1000   # Total time to run the simulation
NUM_VEHICLES = 5         # Total number of vehicles available

# Data collection lists:
trip_start_times = []
trip_end_times = []
wait_times = []
person_ids = []

class MobilityModel:
    def __init__(self, env, num_vehicles):
        self.env = env
        self.vehicle_resource = simpy.Resource(env, num_vehicles)
    
    def trip(self, person):
        """A person uses a vehicle to complete a trip."""
        trip_duration = max(0, random.gauss(TRIP_DURATION_MEAN, TRIP_DURATION_SD))
        trip_start_time = env.now
        trip_start_times.append(trip_start_time)
        yield self.env.timeout(trip_duration)
        trip_end_time = env.now
        trip_end_times.append(trip_end_time)
        print(f"{env.now:.2f}: {person} completes the trip")

def person_generator(env, mobility_model):
    """Generate people who arrive and request a vehicle for their trips."""
    person_id = 0
    while True:
        yield env.timeout(random.expovariate(1 / INTER_ARRIVAL_TIME))
        person_id += 1
        env.process(person_trip(env, person_id, mobility_model))

def person_trip(env, person_id, mobility_model):
    """A person's process to request a vehicle and complete a trip."""
    person_name = f"Person {person_id}"
    arrival_time = env.now
    print(f"{env.now:.2f}: {person_name} arrives and requests a vehicle.")
    with mobility_model.vehicle_resource.request() as request:
        yield request
        wait_time = env.now - arrival_time
        wait_times.append(wait_time)
        person_ids.append(person_id)  # Store the person ID for this wait time
        print(f"{env.now:.2f}: {person_name} acquired a vehicle.")
        yield env.process(mobility_model.trip(person_name))

# Set up and run the simulation
random.seed(42)  # Seed for reproducibility
env = simpy.Environment()
mobility_model = MobilityModel(env, NUM_VEHICLES)

# Start the person generator
env.process(person_generator(env, mobility_model))

# Run the simulation
env.run(until=SIMULATION_TIME)

# Plotting the results
# Plot trip start and end times
plt.figure(figsize=(14, 5))

plt.subplot(1, 2, 1)
plt.plot(trip_start_times, range(len(trip_start_times)), label="Trip start times")
plt.plot(trip_end_times, range(len(trip_end_times)), label="Trip end times")
plt.xlabel("Time")
plt.ylabel("Trip count")
plt.title("Trip start and end times")
plt.legend()

# Plot waiting times with person IDs on the x-axis
plt.subplot(1, 2, 2)
plt.bar(person_ids, wait_times, color='skyblue', edgecolor='black')
plt.xlabel("Person Id")
plt.ylabel("Waiting time")
plt.title("Waiting times by person")
plt.xticks(person_ids)  # Display each person ID on the x-axis

plt.show()