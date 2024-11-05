import simpy
import random
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# Parameters:
NUM_BUSES = 3                   # number of buses in the system
MAX_PASSENGERS = 50             # maximum number of passengers a bus can carry
NUM_STOPS = 5                   # number of stops on the bus route
BUS_INTERVAL = 30               # interval between buses (minutes)
SIMULATION_TIME = 24 * 60       # total simulation time (minutes)
MIN_TIME_BETWEEN_STOPS = 20     # minimum time between stops (minutes)
MAX_TIME_BETWEEN_STOPS = 40     # maximum time between stops (minutes)
MIN_BOARDING_TIME = 1           # minimum boarding time (minutes)
MAX_BOARDING_TIME = 3           # maximum boarding time (minutes)

stops = [f"Stop {i + 1}" for i in range(NUM_STOPS)]

# DataFrame to store bus arrival times
arrival_times = pd.DataFrame(columns=['Bus', 'Stop', 'Arrival Time', 'Departure Time', 'Passengers Arrival', 'Passengers Departure'])

# DataFrame to store passenger journey details
passenger_journeys = pd.DataFrame(columns=['Passenger ID', 'Arrival Time at Stop', 'Boarding Time', 'Bus', 'Destination Stop', 'Alighting Time', 'Waiting Time', 'Travel Time'])

class BusSystem:
    """
    Class to represent the bus system with multiple buses and passengers.
    """
    def __init__(self, env):
        """
        Initialize the bus system with the given simulation environment.
        """
        self.env = env
        self.buses = [env.process(self.bus_process(env, f"Bus {i + 1}", i * BUS_INTERVAL)) for i in range(NUM_BUSES)]
        self.passenger_generator = env.process(self.generate_passengers(env))

    def bus_process(self, env, bus_name, initial_delay):
        """
        Process that simulates the bus behavior.
        """
        yield env.timeout(initial_delay)  # Initial delay for staggered bus starts
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
                passengers_arrival = len(passengers)

                # Drop off passengers
                passengers = [p for p in passengers if not self.drop_off_passenger(p, stop, bus_name)]

                # Pick up passengers waiting at the stop
                while len(passengers) < MAX_PASSENGERS and not stop_queue[stop].is_empty():
                    passenger = stop_queue[stop].get()
                    passenger['boarding_time'] = env.now
                    passenger['bus'] = bus_name
                    boarding_time = random.randint(MIN_BOARDING_TIME, MAX_BOARDING_TIME)
                    yield env.timeout(boarding_time)  # Time taken for passenger to board
                    print(f"Passenger {passenger['id']} boards {bus_name} at {stop} at {self.time_to_string(env.now)} (Boarding time: {boarding_time} minutes)")
                    passengers.append(passenger)

                passengers_departure = len(passengers)
                departure_time = env.now + random.randint(MIN_BOARDING_TIME, MAX_BOARDING_TIME)  # Example departure time calculation
                arrival_times.loc[len(arrival_times)] = [bus_name, stop, self.time_to_string(arrival_time), self.time_to_string(departure_time), passengers_arrival, passengers_departure]

            # Return to central station
            yield env.timeout(random.randint(MIN_TIME_BETWEEN_STOPS, MAX_TIME_BETWEEN_STOPS))  # Random time back to central station
            arrival_time = env.now
            passengers_arrival = len(passengers)
            print(f"{bus_name} returns to Central Station at {self.time_to_string(arrival_time)}")
            arrival_times.loc[len(arrival_times)] = [bus_name, 'Central Station', self.time_to_string(arrival_time), 'N/A', passengers_arrival, 'N/A']
            yield env.timeout(BUS_INTERVAL)

    def drop_off_passenger(self, passenger, stop, bus_name):
        """
        Check if the passenger needs to get off at the current stop and update the passenger journey details.
        """
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
        """
        Generate passengers at random stops with random destinations.
        """
        passenger_id = 1
        while True:
            yield env.timeout(random.randint(1, 10))  # Randomly generate passengers
            stop = random.choice(stops)
            destination = random.choice([s for s in stops if s != stop])
            has_luggage = random.choice([True, False])
            boarding_time_multiplier = 2 if has_luggage else 1
            passenger = {
                'id': passenger_id,
                'arrival_time': env.now,
                'stop': stop,
                'destination': destination,
                'has_luggage': has_luggage,
                'boarding_time_multiplier': boarding_time_multiplier
            }
            passenger_id += 1
            stop_queue[stop].put(passenger)
            luggage_info = "with luggage" if has_luggage else "without luggage"
            print(f"Passenger {passenger['id']} arrives at {stop} at {self.time_to_string(env.now)}, destination: {destination} ({luggage_info})")

    @staticmethod
    def time_to_string(minutes):
        """
        Convert time in minutes to HH:MM format.
        """
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours:02}:{mins:02}"

class StopQueue:
    """
    Class to represent a queue of passengers at a bus stop.
    """
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

# Plot a Sankey diagram showing the flow of passengers between stops
def plot_sankey_diagram(passenger_journeys):
    if passenger_journeys.empty:
        print("No data available for Sankey diagram.")
        return

    source_stops = passenger_journeys['Arrival Time at Stop'].tolist()