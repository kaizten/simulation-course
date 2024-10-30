import simpy
import random

# Parameters
SIMULATION_TIME = 100  # Simulation time in minutes
VEHICLES = 3  # Number of available shared vehicles
ARRIVAL_INTERVAL = 8  # Average interval between passenger arrival (in minutes)
RIDE_DURATION_RANGE = (5, 15)  # Duration of rides in minutes (min, max)

class UrbanMobilitySimulation:
    def __init__(self, env, num_vehicles, ride_duration_range, arrival_interval):
        self.env = env
        self.vehicle = simpy.Resource(env, num_vehicles)
        self.ride_duration_range = ride_duration_range
        self.arrival_interval = arrival_interval

    def request_ride(self, passenger_id):
        print(f"{env.now:.2f}: Passenger {passenger_id} arrives and requests a ride")
        with self.vehicle.request() as request:
            yield request
            ride_duration = random.uniform(*self.ride_duration_range)
            print(f"{env.now:.2f}: Passenger {passenger_id} starts ride for {ride_duration:.2f} minutes")
            yield self.env.timeout(ride_duration)
            print(f"{env.now:.2f}: Passenger {passenger_id} ends ride")

def generate_passengers(env, urban_mobility_simulation):
    passenger_id = 1
    while True:
        yield env.timeout(random.expovariate(1.0 / urban_mobility_simulation.arrival_interval))
        env.process(urban_mobility_simulation.request_ride(passenger_id))
        passenger_id += 1

# Setup and start the simulation
env = simpy.Environment()
urban_mobility_simulation = UrbanMobilitySimulation(env, VEHICLES, RIDE_DURATION_RANGE, ARRIVAL_INTERVAL)
env.process(generate_passengers(env, urban_mobility_simulation))

# Run the simulation for 100 time units
env.run(until=SIMULATION_TIME)