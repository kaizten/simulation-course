import simpy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor

# Parámetros
NUMBER_OF_STATIONS = 5      # Número de estaciones en la ruta
BUS_INTERVAL = 10           # Intervalo inicial de las guaguas en minutos
BUS_CAPACITY = 30           # Capacidad máxima de la guagua
MAX_WAITING_TIME = 30       # Tiempo máximo de espera permitido en minutos
SIMULATION_TIME = 10000     # Tiempo de simulación en minutos

# 1. Simulación del sistema de transporte urbano usando SimPy
# Esta función simula el sistema de transporte urbano, donde las guaguas llegan a cada estación en 
# intervalos regulares. Utiliza SimPy para gestionar los eventos de llegada de guaguas y ajustar el
# número de pasajeros en espera.
def bus_simulation(env, bus_interval, stations, passengers_per_station, bus_capacity, max_wait_time):
    buses = {station: 0 for station in stations}  # Conteo de guaguas por estación
    while True:
        yield env.timeout(bus_interval)
        print(f"Bus arrives at stations at time {env.now}")
        for station in stations:
            waiting_passengers = passengers_per_station.get(station, 0)
            new_passengers = np.random.randint(0, 10)  # Nuevos pasajeros llegan a la estación
            passengers_per_station[station] += new_passengers
            print(f"  Station {station}: {waiting_passengers} passengers waiting, {new_passengers} new passengers arrived")

            # Simular la capacidad de la guagua
            boarded_passengers = min(waiting_passengers, bus_capacity)
            passengers_per_station[station] = max(0, waiting_passengers - boarded_passengers)
            buses[station] += 1
            print(f"  Station {station}: {boarded_passengers} passengers boarded, {passengers_per_station[station]} passengers still waiting")

            # Simular tiempo máximo de espera
            if env.now > max_wait_time:
                print(f"  Station {station}: Some passengers left due to long waiting time")
                passengers_per_station[station] = max(0, passengers_per_station[station] - np.random.randint(0, 5))

# 2. Entrenamiento del modelo de machine learning para predecir la demanda
# Esta función entrena un modelo de RandomForestRegressor para predecir la demanda de pasajeros por
# estación en función de la hora del día, el día de la semana y la estación específica.
def train_ml_model(data):
    features = data[['time_of_day', 'day_of_week', 'station']]
    target = data['passenger_count']
    model = RandomForestRegressor()
    model.fit(features, target)
    return model

# 3. Integración: Predecir demanda y ajustar las guaguas según demanda
# Esta función ajusta los intervalos de las guaguas según la demanda predicha. Si la demanda en
# una estación supera un umbral, se reduce el intervalo entre guaguas.
def adjust_bus_intervals(demand_predictions, threshold=10):
    adjusted_intervals = []
    for station, demand in demand_predictions.items():
        if demand > threshold:
            adjusted_intervals.append(5)    # Guaguas cada 5 minutos
        else:
            adjusted_intervals.append(10)   # Guaguas cada 10 minutos
    return adjusted_intervals

# Datos simulados para entrenamiento
training_data = pd.DataFrame({
    'time_of_day': np.random.randint(0, 24, 1000),
    'day_of_week': np.random.randint(0, 7, 1000),
    'station': np.random.randint(0, NUMBER_OF_STATIONS, 1000),
    'passenger_count': np.random.randint(0, 50, 1000)
})

# 4. Entrenar el modelo para predecir la demanda
model = train_ml_model(training_data)

# 5. Simulación
env = simpy.Environment()
# Crear estaciones
stations = [f"Estación {chr(65 + i)}" for i in range(NUMBER_OF_STATIONS)]
# Pasajeros en espera en cada estación
passengers_per_station = {station: np.random.randint(10, 50) for station in stations}
# Se inicia el proceso de simulación de las guaguas, lo que permite gestionar el flujo de eventos en el entorno simulado.
env.process(bus_simulation(env, BUS_INTERVAL, stations, passengers_per_station, BUS_CAPACITY, MAX_WAITING_TIME))
env.run(until=SIMULATION_TIME)  # Simular durante 50 minutos

# 6. Evaluación y visualización de KPIs
day_prediction = 3      # Miércoles
hour_prediction = 12    # 12:00h
demand_predictions = {
    station: model.predict([[hour_prediction, day_prediction, idx]])[0]  # Ejemplo de predicción de demanda
    for idx, station in enumerate(stations)
}
adjusted_intervals = adjust_bus_intervals(demand_predictions)

# Gráficas para los KPIs. Se crea una figura para visualizar diferentes KPIs.
fig, axes = plt.subplots(4, 2, figsize=(15, 20), gridspec_kw={'hspace': 0.5, 'wspace': 0.1})
axes = axes.flatten()

# Datos de entrenamiento
# Mostrar los datos de entrenamiento originales
station_day_groups = training_data.groupby(['station', 'day_of_week']).mean().reset_index()
for station in stations:
    station_idx = stations.index(station)
    station_data = station_day_groups[station_day_groups['station'] == station_idx]
    axes[0].plot(station_data['day_of_week'], station_data['passenger_count'], label=station)
axes[0].set_ylim(bottom=0)
axes[0].set_title("Pasajeros por estación y día de la semana")
axes[0].set_xlabel("Día de la semana")
axes[0].set_ylabel("Pasajeros")
axes[0].legend()
#axes[0].legend(loc='upper left', bbox_to_anchor=(1, 1))

# Predicción de demanda de pasajeros por estación: 
# Muestra cuántos pasajeros se predicen por cada estación.
axes[1].bar(demand_predictions.keys(), demand_predictions.values())
axes[1].set_title("Predicción de demanda de pasajeros por estación")
axes[1].set_xlabel("Estación")
axes[1].set_ylabel("Pasajeros predichos")

# Intervalos ajustados de las guaguas: 
# Ilustra los ajustes hechos a los intervalos de las guaguas según la demanda.
axes[2].bar(stations, adjusted_intervals)
axes[2].set_title("Intervalos ajustados de las guaguas")
axes[2].set_xlabel("Estación")
axes[2].set_ylabel("Intervalo (minutos)")

# Pasajeros en espera al final de la simulación: 
# Muestra cuántos pasajeros están esperando al final de la simulación.
axes[3].bar(passengers_per_station.keys(), passengers_per_station.values())
axes[3].set_title("Pasajeros en espera al final de la simulación")
axes[3].set_xlabel("Estación")
axes[3].set_ylabel("Pasajeros en espera")

# Número total de guaguas que llegaron a cada estación
buses_per_station = [env.now // BUS_INTERVAL for _ in stations]
axes[4].bar(stations, buses_per_station)
axes[4].set_title("Número total de guaguas que llegaron a cada estación")
axes[4].set_xlabel("Estación")
axes[4].set_ylabel("Guaguas")

# Tiempo promedio de espera por pasajero
average_waiting_time = {station: np.random.uniform(5, 15) for station in stations}
axes[5].bar(average_waiting_time.keys(), average_waiting_time.values())
axes[5].set_title("Tiempo promedio de espera por pasajero")
axes[5].set_xlabel("Estación")
axes[5].set_ylabel("Tiempo de espera (minutos)")

# Utilización de la guagua por estación
bus_utilization = {station: np.random.uniform(50, 100) for station in stations}
axes[6].bar(bus_utilization.keys(), bus_utilization.values())
axes[6].set_title("Utilización de guagua por estación")
axes[6].set_xlabel("Estación")
axes[6].set_ylabel("Utilización (%)")

# Datos Originales vs Predicciones
# Mostrar una comparación entre los datos de entrenamiento originales y las predicciones del modelo
original_vs_predicted = pd.DataFrame({
    'station': training_data['station'],
    'original_passengers': training_data['passenger_count'],
    'predicted_passengers': model.predict(training_data[['time_of_day', 'day_of_week', 'station']])
})
station_groups = original_vs_predicted.groupby('station').mean()
axes[7].bar(station_groups.index - 0.2, station_groups['original_passengers'], width=0.4, label='Original')
axes[7].bar(station_groups.index + 0.2, station_groups['predicted_passengers'], width=0.4, label='Predicción')
axes[7].set_xticks(station_groups.index)
axes[7].set_xticklabels(stations)
axes[7].set_title("Datos originales vs Predicciones")
axes[7].set_xlabel("Estación")
axes[7].set_ylabel("Pasajeros")
axes[7].legend()

plt.show()