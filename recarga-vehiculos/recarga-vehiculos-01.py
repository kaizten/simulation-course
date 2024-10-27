import simpy
import random

# Parámetros globales
NUM_STATIONS = 5                # Número de estaciones de recarga
CHARGING_SPOTS = 2              # Número de puntos de recarga por estación
SIM_TIME = 1440                 # Tiempo de simulación en minutos (1 día)
INTER_ARRIVAL_TIME = 15         # Tiempo medio entre llegadas de vehículos (minutos)
CHARGING_TIME_MEAN = 60         # Tiempo medio de carga de cada vehículo (minutos)

class EVChargingStation:
    """Estación de recarga de vehículos eléctricos"""
    def __init__(self, env, num_spots):
        self.env = env
        self.charging_spots = simpy.Resource(env, num_spots)

    def charge(self, vehicle_id, charging_time):
        yield self.env.timeout(charging_time)
        print(f'Vehicle {vehicle_id} completed charging at {self.env.now:.2f} minutes')

def vehicle(env, vehicle_id, station, arrival_delay, charging_time):
    # Simulación de llegada del vehículo
    yield env.timeout(arrival_delay)
    print(f'Vehicle {vehicle_id} arrived at {env.now:.2f} minutes')
    
    with station.charging_spots.request() as request:
        # Espera por un punto de recarga disponible
        yield request
        print(f'Vehicle {vehicle_id} started charging at {env.now:.2f} minutes')
        yield env.process(station.charge(vehicle_id, charging_time))

def setup(env, num_stations, charging_spots):
    # Crear estaciones de recarga
    stations = [EVChargingStation(env, charging_spots) for _ in range(num_stations)]
    vehicle_id = 0

    while True:
        # Tiempo de llegada del siguiente vehículo
        arrival_delay = random.expovariate(1.0 / INTER_ARRIVAL_TIME) # Distribución exponencial
        charging_time = random.expovariate(1.0 / CHARGING_TIME_MEAN) # Distribución exponencial
        selected_station = random.choice(stations)  # Selecciona una estación aleatoria
        
        # Crear un vehículo y pasarlo a la simulación
        env.process(vehicle(env, vehicle_id, selected_station, arrival_delay, charging_time))
        vehicle_id += 1

        yield env.timeout(arrival_delay)

def main():
    random.seed(42)  # Establecer semilla para reproducibilidad
    env = simpy.Environment()
    env.process(setup(env, NUM_STATIONS, CHARGING_SPOTS))
    env.run(until=SIM_TIME)

if __name__ == '__main__':
    main()