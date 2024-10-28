import simpy
import random
import pandas as pd
import matplotlib.pyplot as plt

# Definir constantes
NUM_STATIONS = 8  # Define el número de estaciones de bicicletas disponibles en el sistema. Considera ajustar este valor para simular diferentes densidades de estaciones en la ciudad.
NUM_BIKES = 20  # Define el número de bicicletas disponibles en cada estación. Modificar este valor puede ayudar a simular escenarios con mayor o menor disponibilidad de bicicletas.
DEMAND_RATE = 3  # Define la tasa promedio de llegada de usuarios para solicitar una bicicleta. Un valor más alto simulará una mayor demanda de bicicletas.
SIM_TIME = 1000  # Define el tiempo total de simulación en unidades de tiempo. Ajusta este valor según la duración que quieras simular.

# Definimos la clase que representa la ciudad y su sistema de bicicletas
class UrbanMobility:
    def __init__(self, env, num_stations, num_bikes, demand_rate):
        self.env = env
        self.stations = [simpy.Resource(env, capacity=num_bikes) for _ in range(num_stations)]
        self.num_stations = num_stations
        self.demand_rate = demand_rate
        self.data = []
        self.starting_bikes = [num_bikes for _ in range(num_stations)]
        self.ending_bikes = [num_bikes for _ in range(num_stations)]

    def request_bike(self, user_id, station_id):
        station = self.stations[station_id]
        arrival_time = self.env.now
        with station.request() as request:
            yield request
            self.ending_bikes[station_id] -= 1
            wait_time = self.env.now - arrival_time
            ride_duration = random.expovariate(1 / 20)  # Duración promedio de 20 minutos
            yield self.env.timeout(ride_duration)
            return_station_id = random.randint(0, self.num_stations - 1)
            return_station = self.stations[return_station_id]
            with return_station.request() as return_request:
                yield return_request
                self.ending_bikes[return_station_id] += 1
                # Registramos el evento en la data
                self.data.append({
                    'user_id': user_id,
                    'arrival_time': arrival_time,
                    'wait_time': wait_time,
                    'ride_duration': ride_duration,
                    'start_station': station_id,
                    'end_station': return_station_id,
                    'return_time': self.env.now
                })

    def generate_users(self):
        user_id = 0
        while True:
            yield self.env.timeout(random.expovariate(1 / self.demand_rate))
            station_id = random.randint(0, self.num_stations - 1)
            self.env.process(self.request_bike(user_id, station_id))
            user_id += 1

# Definir una función para ejecutar la simulación y visualizar los resultados
def run_simulation(num_stations=NUM_STATIONS, num_bikes=NUM_BIKES, demand_rate=DEMAND_RATE, sim_time=SIM_TIME):
    env = simpy.Environment()
    urban_mobility = UrbanMobility(env, num_stations, num_bikes, demand_rate)
    env.process(urban_mobility.generate_users())
    env.run(until=sim_time)

    # Crear un DataFrame a partir de los resultados
    df = pd.DataFrame(urban_mobility.data)

    # Mostrar métricas de interés
    print("\nEstadísticas de la simulación:\n")
    print(df.describe())

    # Visualizar el tiempo de espera y duración de los trayectos
    plt.figure(figsize=(14, 5))
    
    plt.subplot(1, 2, 1)
    plt.hist(df['wait_time'], bins=20, alpha=0.7)
    plt.xlabel('Tiempo de espera (min)')
    plt.ylabel('Frecuencia')
    plt.title('Distribución del Tiempo de Espera')

    plt.subplot(1, 2, 2)
    plt.hist(df['ride_duration'], bins=20, alpha=0.7)
    plt.xlabel('Duración del trayecto (min)')
    plt.ylabel('Frecuencia')
    plt.title('Distribución de la Duración del Trayecto')

    plt.tight_layout()
    plt.show()

    # Visualizar el número de bicicletas en cada estación al comienzo y al final de la simulación
    plt.figure(figsize=(10, 6))
    stations = range(num_stations)
    plt.bar(stations, urban_mobility.starting_bikes, alpha=0.7, label='Inicio de la simulación')
    plt.bar(stations, urban_mobility.ending_bikes, alpha=0.7, label='Final de la simulación')
    plt.xlabel('Estación')
    plt.ylabel('Número de bicicletas')
    plt.title('Número de bicicletas al comienzo y al final de la simulación')
    plt.legend()
    plt.show()

# Ejecutar la simulación
run_simulation()
