import simpy
import random
import pandas as pd
import matplotlib.pyplot as plt

# Constants
NUM_BUSES = 3
MAX_PASSENGERS = 50
NUM_STOPS = 5
BUS_INTERVAL = 20  # minutes
SIMULATION_TIME = 24 * 60  # minutes in a day
MIN_TIME_BETWEEN_STOPS = 20  # minimum time between stops (minutes)
MAX_TIME_BETWEEN_STOPS = 40  # maximum time between stops (minutes)

stops = [f"Stop {i + 1}" for i in range(NUM_STOPS)]

# DataFrame to store bus arrival times
arrival_times = pd.DataFrame(columns=['Bus', 'Stop', 'Arrival Time'])

# DataFrame to store passenger journey details
passenger_journeys = pd.DataFrame(columns=['Passenger ID', 'Arrival Time at Stop', 'Boarding Time', 'Bus', 'Destination Stop', 'Alighting Time', 'Waiting Time', 'Travel Time'])

class BusSystem:
    def __init__(self, env):
        self.env = env
        self.buses = [env.process(self.bus_process(env, f"Bus {i + 1}")) for i in range(NUM_BUSES)]
        self.passenger_generator = env.process(self.generate_passengers(env))

    def bus_process(self, env, bus_name):
        while True:
            # Bus starts at the central station
            departure_time = env.now
            print(f"{bus_name} departs from Central Station at {self.time_to_string(departure_time)}")

            # Bus visits each stop
            passengers = []
            for stop in stops:
                yield env.timeout(random.randint(MIN_TIME_BETWEEN_STOPS, MAX_TIME_BETWEEN_STOPS))  # Random time between stops
                arrival_time = env.now
                print(f"{bus_name} arrives at {stop} at {self.time_to_string(arrival_time)}")
                
                # Record arrival time in DataFrame
                arrival_times.loc[len(arrival_times)] = [bus_name, stop, self.time_to_string(arrival_time)]

                # Drop off passengers
                passengers = [p for p in passengers if not self.drop_off_passenger(p, stop, bus_name)]

                # Pick up passengers waiting at the stop
                while len(passengers) < MAX_PASSENGERS and not stop_queue[stop].is_empty():
                    passenger = stop_queue[stop].get()
                    passenger['boarding_time'] = env.now
                    passenger['bus'] = bus_name
                    print(f"Passenger {passenger['id']} boards {bus_name} at {stop} at {self.time_to_string(env.now)}")
                    passengers.append(passenger)

            # Return to central station
            yield env.timeout(random.randint(MIN_TIME_BETWEEN_STOPS, MAX_TIME_BETWEEN_STOPS))  # Random time back to central station
            arrival_time = env.now
            print(f"{bus_name} returns to Central Station at {self.time_to_string(arrival_time)}")
            arrival_times.loc[len(arrival_times)] = [bus_name, 'Central Station', self.time_to_string(arrival_time)]
            yield env.timeout(BUS_INTERVAL)

    def drop_off_passenger(self, passenger, stop, bus_name):
        if stop == passenger['destination']:
            alighting_time = env.now
            waiting_time = passenger['boarding_time'] - passenger['arrival_time']
            travel_time = alighting_time - passenger['boarding_time']
            print(f"Passenger {passenger['id']} gets off {bus_name} at {stop} at {self.time_to_string(alighting_time)}")
            passenger_journeys.loc[len(passenger_journeys)] = [
                passenger['id'],
                self.time_to_string(passenger['arrival_time']),
                self.time_to_string(passenger['boarding_time']),
                bus_name,
                stop,
                self.time_to_string(alighting_time),
                waiting_time,
                travel_time
            ]
            return True
        return False

    def generate_passengers(self, env):
        passenger_id = 1
        while True:
            yield env.timeout(random.randint(1, 10))  # Randomly generate passengers
            stop = random.choice(stops)
            destination = random.choice([s for s in stops if s != stop])
            passenger = {
                'id': passenger_id,
                'arrival_time': env.now,
                'stop': stop,
                'destination': destination
            }
            passenger_id += 1
            stop_queue[stop].put(passenger)
            print(f"Passenger {passenger['id']} arrives at {stop} at {self.time_to_string(env.now)}, destination: {destination}")

    @staticmethod
    def time_to_string(minutes):
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours:02}:{mins:02}"

class StopQueue:
    def __init__(self):
        self.queue = []

    def put(self, passenger):
        self.queue.append(passenger)

    def get(self):
        return self.queue.pop(0)

    def is_empty(self):
        return len(self.queue) == 0

# Initialize stop queues
stop_queue = {stop: StopQueue() for stop in stops}

# Run the simulation
env = simpy.Environment()
bus_system = BusSystem(env)
env.run(until=SIMULATION_TIME)

# Display arrival times table
print("\nBus Arrival Times Table:")
print(arrival_times)

# Check if the DataFrame is empty
if arrival_times.empty:
    print("No bus arrival times were recorded.")
else:
    print(arrival_times)

# Display passenger journey details table
print("\nPassenger Journeys Table:")
print(passenger_journeys)

# Check if the DataFrame is empty
if passenger_journeys.empty:
    print("No passenger journeys were recorded.")
else:
    print(passenger_journeys)

# Plot the bus routes
def plot_bus_routes(arrival_times):
    plt.figure(figsize=(10, 6))
    for bus in arrival_times['Bus'].unique():
        bus_data = arrival_times[arrival_times['Bus'] == bus]
        times = bus_data['Arrival Time'].apply(lambda x: int(x.split(':')[0]) * 60 + int(x.split(':')[1]))
        plt.plot(bus_data['Stop'], times, marker='o', label=bus)
    
    plt.xlabel('Stop')
    plt.ylabel('Time (minutes from start of day)')
    plt.title('Bus Routes Throughout the Day')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

plot_bus_routes(arrival_times)

# Plot the waiting times for each passenger
def plot_passenger_waiting_times(passenger_journeys):
    plt.figure(figsize=(10, 6))
    plt.bar(passenger_journeys['Passenger ID'], passenger_journeys['Waiting Time'], color='blue')
    plt.xlabel('Passenger ID')
    plt.ylabel('Waiting Time (minutes)')
    plt.title('Passenger Waiting Times at Stops')
    plt.grid(axis='y')
    plt.tight_layout()
    plt.show()

plot_passenger_waiting_times(passenger_journeys)