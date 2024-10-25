import simpy
import random
import matplotlib.pyplot as plt

# Definimos parámetros globales
NUM_STATIONS = 5                # Número de estaciones de recarga
CHARGING_SPOTS = 2              # Número de puntos de recarga por estación
SIM_TIME = 1440                 # Tiempo de simulación en minutos (1 día)
INTER_ARRIVAL_TIME = 15         # Tiempo medio entre llegadas de vehículos (minutos)
CHARGING_TIME_MEAN = 60         # Tiempo medio de carga de cada vehículo (minutos)

# Variables para análisis
waiting_times = []
charging_times = []

class EVChargingStation:
    def __init__(self, env, num_spots):
        self.env = env
        self.charging_spots = simpy.Resource(env, num_spots)

    def charge(self, vehicle_id, charging_time):
        yield self.env.timeout(charging_time)
        print(f'Vehicle {vehicle_id} completed charging at {self.env.now:.2f} minutes')

def vehicle(env, vehicle_id, station, arrival_delay, charging_time):
    # Simulación de llegada del vehículo
    yield env.timeout(arrival_delay)
    arrival_time = env.now
    print(f'Vehicle {vehicle_id} arrived at {env.now:.2f} minutes')
    
    with station.charging_spots.request() as request:
        # Espera por un punto de recarga disponible
        yield request
        waiting_time = env.now - arrival_time
        waiting_times.append(waiting_time)
        print(f'Vehicle {vehicle_id} started charging at {env.now:.2f} minutes')
        
        yield env.process(station.charge(vehicle_id, charging_time))
        charging_times.append(charging_time)

def setup(env, num_stations, charging_spots):
    # Crear estaciones de recarga
    stations = [EVChargingStation(env, charging_spots) for _ in range(num_stations)]
    vehicle_id = 0

    while True:
        # Tiempo de llegada del siguiente vehículo
        arrival_delay = random.expovariate(1.0 / INTER_ARRIVAL_TIME)
        charging_time = random.expovariate(1.0 / CHARGING_TIME_MEAN)
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
    
    # Análisis de resultados
    plt.figure(figsize=(10, 5))
    plt.subplot(1, 2, 1)
    plt.hist(waiting_times, bins=20, color='skyblue', edgecolor='black')
    plt.xlabel('Tiempo de Espera (minutos)')
    plt.ylabel('Frecuencia')
    plt.title('Distribución de Tiempos de Espera')
    
    plt.subplot(1, 2, 2)
    plt.hist(charging_times, bins=20, color='lightgreen', edgecolor='black')
    plt.xlabel('Tiempo de Carga (minutos)')
    plt.ylabel('Frecuencia')
    plt.title('Distribución de Tiempos de Carga')
    
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    main()