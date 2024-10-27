import simpy
import random
import matplotlib.pyplot as plt
import numpy as np

# Parámetros globales
NUM_STATIONS = 5                # Número de estaciones de recarga
CHARGING_SPOTS = 2              # Número de puntos de recarga por estación
SIM_TIME = 1440                 # Tiempo de simulación en minutos (1 día)
INTER_ARRIVAL_TIME = 15         # Tiempo medio entre llegadas de vehículos (minutos)
CHARGING_TIME_MEAN = 60         # Tiempo medio de carga de cada vehículo (minutos)
MAX_WAIT_TIME = 30              # Tiempo máximo de espera permitido antes de abandonar (minutos)

# Variables para análisis
waiting_times = []
charging_times = []
total_vehicles = 0
vehicles_charged = 0
vehicles_waited = 0
vehicles_abandoned = 0
usage_times = []
station_usage_times = [0] * NUM_STATIONS
vehicles_per_station = [0] * NUM_STATIONS

class EVChargingStation:
    def __init__(self, env, num_spots, station_id):
        self.env = env
        self.charging_spots = simpy.Resource(env, num_spots)
        self.station_id = station_id
        self.total_usage_time = 0

    def charge(self, vehicle_id, charging_time):
        yield self.env.timeout(charging_time)
        self.total_usage_time += charging_time
        print(f'Vehicle {vehicle_id} completed charging at {self.env.now:.2f} minutes')

def vehicle(env, vehicle_id, station, arrival_delay, charging_time):
    global total_vehicles, vehicles_charged, vehicles_waited, vehicles_abandoned
    # Simulación de llegada del vehículo
    yield env.timeout(arrival_delay)
    arrival_time = env.now
    total_vehicles += 1
    print(f'Vehicle {vehicle_id} arrived at {env.now:.2f} minutes')
    
    with station.charging_spots.request() as request:
        # Espera por un punto de recarga disponible
        results = yield request | env.timeout(MAX_WAIT_TIME)
        if request not in results:
            # El vehículo abandona si espera demasiado
            vehicles_abandoned += 1
            print(f'Vehicle {vehicle_id} abandoned at {env.now:.2f} minutes after waiting too long')
            return

        waiting_time = env.now - arrival_time
        waiting_times.append(waiting_time)
        if waiting_time > 0:
            vehicles_waited += 1
        print(f'Vehicle {vehicle_id} started charging at {env.now:.2f} minutes')
        
        yield env.process(station.charge(vehicle_id, charging_time))
        charging_times.append(charging_time)
        vehicles_charged += 1
        usage_time = waiting_time + charging_time
        usage_times.append(usage_time)
        station_usage_times[station.station_id] += usage_time
        vehicles_per_station[station.station_id] += 1

def setup(env, num_stations, charging_spots):
    # Crear estaciones de recarga
    stations = [EVChargingStation(env, charging_spots, i) for i in range(num_stations)]
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
    avg_waiting_time = np.mean(waiting_times) if waiting_times else 0
    avg_charging_time = np.mean(charging_times) if charging_times else 0
    avg_usage_time = np.mean(usage_times) if usage_times else 0
    proportion_waited = (vehicles_waited / total_vehicles) * 100 if total_vehicles > 0 else 0
    station_utilization = [(usage / SIM_TIME) * 100 for usage in station_usage_times]
    abandonment_rate = (vehicles_abandoned / total_vehicles) * 100 if total_vehicles > 0 else 0

    print(f'Total vehicles: {total_vehicles}')
    print(f'Vehicles charged: {vehicles_charged}')
    print(f'Vehicles that waited: {vehicles_waited}')
    print(f'Vehicles abandoned: {vehicles_abandoned}')
    print(f'Average waiting time: {avg_waiting_time:.2f} minutes')
    print(f'Average charging time: {avg_charging_time:.2f} minutes')
    print(f'Average usage time: {avg_usage_time:.2f} minutes')
    print(f'Proportion of vehicles that waited: {proportion_waited:.2f}%')
    print(f'Abandonment rate: {abandonment_rate:.2f}%')
    for i, utilization in enumerate(station_utilization):
        print(f'Station {i} utilization: {utilization:.2f}%')
        print(f'Station {i} vehicles served: {vehicles_per_station[i]}')

    plt.figure(figsize=(18, 5))
    plt.subplot(2, 4, 1)
    plt.hist(waiting_times, bins=20, color='skyblue', edgecolor='black')
    plt.xlabel('Tiempo de Espera (minutos)')
    plt.ylabel('Frecuencia')
    plt.title('Distribución de Tiempos de Espera')
    
    plt.subplot(2, 4, 2)
    plt.hist(charging_times, bins=20, color='lightgreen', edgecolor='black')
    plt.xlabel('Tiempo de Carga (minutos)')
    plt.ylabel('Frecuencia')
    plt.title('Distribución de Tiempos de Carga')
    
    plt.subplot(2, 4, 3)
    plt.hist(usage_times, bins=20, color='lightcoral', edgecolor='black')
    plt.xlabel('Tiempo de Uso (minutos)')
    plt.ylabel('Frecuencia')
    plt.title('Distribución de Tiempos de Uso')
    
    plt.subplot(2, 4, 4)
    plt.bar(['Total Vehicles', 'Vehicles Charged', 'Vehicles Waited', 'Vehicles Abandoned'], [total_vehicles, vehicles_charged, vehicles_waited, vehicles_abandoned], color=['blue', 'green', 'red', 'orange'])
    plt.ylabel('Cantidad')
    plt.title('Estadísticas de Vehículos')
    
    plt.subplot(2, 4, 5)
    plt.bar([f'Station {i}' for i in range(NUM_STATIONS)], station_utilization, color='purple')
    plt.ylabel('Porcentaje de Utilización')
    plt.title('Utilización de Estaciones')
    
    plt.subplot(2, 4, 6)
    plt.bar([f'Station {i}' for i in range(NUM_STATIONS)], vehicles_per_station, color='orange')
    plt.ylabel('Cantidad de Vehículos Atendidos')
    plt.title('Vehículos Atendidos por Estación')
    
    plt.subplot(2, 4, 7)
    plt.bar(['Vehicles Abandoned'], [vehicles_abandoned], color='red')
    plt.ylabel('Cantidad')
    plt.title('Vehículos que Abandonaron')
    
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    main()
