import simpy
import random
import matplotlib.pyplot as plt

# Parámetros:
SIMULATION_TIME = 1 * 60 * 60                               # Tiempo de simulación (en segundos)
# Configuración de tiempos y tasas de llegada
VEHICLE_GREEN_TIME = 20                                     # Tiempo en verde para vehículos (en segundos)
PEDESTRIAN_GREEN_TIME = 10                                  # Tiempo en verde para peatones (en segundos)
CYCLE_TIME = VEHICLE_GREEN_TIME + PEDESTRIAN_GREEN_TIME     # Tiempo total del ciclo del semáforo

VEHICLE_ARRIVAL_RATE = 5                                    # Tiempo promedio de llegada de vehículos (en segundos)
PEDESTRIAN_ARRIVAL_RATE = 15                                # Tiempo promedio de llegada de peatones (en segundos)
PEAK_HOUR_MULTIPLIER = 0.5                                  # Reducción de tiempos de llegada en hora pico

# Capacidad de la intersección
VEHICLE_CAPACITY = 3                                        # Capacidad de la intersección para vehículos
PEDESTRIAN_CAPACITY = 5

# Probabilidades de comportamiento
TURN_PROBABILITY = 0.2                                      # Probabilidad de que un vehículo gire
EMERGENCY_VEHICLE_PROBABILITY = 0.05                        # Probabilidad de que un vehículo sea de emergencia

# KPIs
vehicle_times = []                                          # Registro de tiempos de cruce de vehículos
pedestrian_times = []                                       # Registro de tiempos de cruce de peatones
congestion_levels = []                                      # Registro de niveles de congestión
timestamps = []                                             # Registro de instantes de tiempo
emergency_times = []                                        # Registro de tiempos de cruce de vehículos de emergencia

def traffic_light(env):
    """
    Función que simula el comportamiento de un semáforo de tráfico.
    """
    while True:
        yield env.timeout(VEHICLE_GREEN_TIME)
        yield env.timeout(PEDESTRIAN_GREEN_TIME)

def vehicle(env, name, traffic_light, vehicle_intersection):
    """
    Función que simula el comportamiento de un vehículo en la intersección.
    """
    is_emergency = random.random() < EMERGENCY_VEHICLE_PROBABILITY
    arrival_time = env.now
    
    if is_emergency:
        crossing_time = random.uniform(1, 3)
        yield env.timeout(crossing_time)
        vehicle_times.append(env.now - arrival_time)
        emergency_times.append(env.now)  # Registrar el tiempo del vehículo de emergencia
        return

    with vehicle_intersection.request() as req:
        yield req

        while (env.now % CYCLE_TIME) >= VEHICLE_GREEN_TIME:
            yield env.timeout(1)
        
        crossing_time = random.uniform(1, 3)
        yield env.timeout(crossing_time)
        vehicle_times.append(env.now - arrival_time)

def pedestrian(env, name, traffic_light, pedestrian_intersection):
    """
    Función que simula el comportamiento de un peatón en la intersección.
    """
    arrival_time = env.now
    
    with pedestrian_intersection.request() as req:
        yield req
        
        while (env.now % CYCLE_TIME) < VEHICLE_GREEN_TIME:
            yield env.timeout(1)
        
        crossing_time = random.uniform(2, 4)
        yield env.timeout(crossing_time)
        pedestrian_times.append(env.now - arrival_time)

def vehicle_arrival(env, traffic_light, vehicle_intersection, is_peak_hour=False):
    """
    Función que genera la llegada de vehículos a la intersección.
    """
    arrival_rate = VEHICLE_ARRIVAL_RATE * (PEAK_HOUR_MULTIPLIER if is_peak_hour else 1)
    while True:
        yield env.timeout(random.expovariate(1 / arrival_rate))
        env.process(vehicle(env, f"Vehículo", traffic_light, vehicle_intersection))

def pedestrian_arrival(env, traffic_light, pedestrian_intersection):
    """
    Función que genera la llegada de peatones a la intersección.
    """
    while True:
        yield env.timeout(random.expovariate(1 / PEDESTRIAN_ARRIVAL_RATE))
        env.process(pedestrian(env, f"Peatón", traffic_light, pedestrian_intersection))

def congestion_monitor(env, intersection, threshold):
    """
    Función que monitoriza el nivel de congestión en la intersección.
    """
    while True:
        yield env.timeout(5)
        congestion_levels.append(len(intersection.queue))
        timestamps.append(env.now)

# Simulación
env = simpy.Environment()   # Crear el entorno de simulación

vehicle_intersection = simpy.Resource(env, capacity=VEHICLE_CAPACITY)       # Intersección para vehículos
pedestrian_intersection = simpy.Resource(env, capacity=PEDESTRIAN_CAPACITY) # Intersección para peatones

env.process(traffic_light(env)) # Iniciar el semáforo
env.process(vehicle_arrival(env, traffic_light, vehicle_intersection, is_peak_hour=True)) # Generar llegada de vehículos
env.process(pedestrian_arrival(env, traffic_light, pedestrian_intersection))          # Generar llegada de peatones
env.process(congestion_monitor(env, vehicle_intersection, threshold=5))             # Monitorizar la congestión

env.run(until=SIMULATION_TIME)  # Ejecutar la simulación

# Mostrar resumen de KPIs
print("Resumen de KPIs:")
print(f"Tiempo promedio de cruce de vehículos: {sum(vehicle_times)/len(vehicle_times):.2f} segundos" if vehicle_times else "No hubo vehículos.")
print(f"Tiempo promedio de cruce de peatones: {sum(pedestrian_times)/len(pedestrian_times):.2f} segundos" if pedestrian_times else "No hubo peatones.")
print(f"Nivel de congestión máximo: {max(congestion_levels) if congestion_levels else 0}")
print(f"Nivel de congestión promedio: {sum(congestion_levels)/len(congestion_levels):.2f}" if congestion_levels else "Sin datos de congestión.")
print(f"Total de vehículos de emergencia que cruzaron: {len(emergency_times)}")
print(f"Instante de cruce de vehículos de emergencia: {emergency_times}")

# Graficar los KPI
fig, axes = plt.subplots(2, 2, figsize=(15, 10))

# Gráfico de tiempo promedio de cruce de vehículos
axes[0, 0].plot(vehicle_times, label="Tiempo de cruce de vehículos")
axes[0, 0].set_title("Tiempo de cruce de vehículos")
axes[0, 0].set_xlabel("Vehículo")
axes[0, 0].set_ylabel("Tiempo (segundos)")
axes[0, 0].legend()

# Gráfico de tiempo promedio de cruce de peatones
axes[0, 1].plot(pedestrian_times, label="Tiempo de cruce de peatones", color='orange')
axes[0, 1].set_title("Tiempo de cruce de peatones")
axes[0, 1].set_xlabel("Peatón")
axes[0, 1].set_ylabel("Tiempo (segundos)")
axes[0, 1].legend()

# Gráfico de niveles de congestión en la intersección
axes[1, 0].plot(timestamps, congestion_levels, label="Niveles de congestión", color='green')
axes[1, 0].set_title("Niveles de congestión en la tntersección")
axes[1, 0].set_xlabel("Tiempo (segundos)")
axes[1, 0].set_ylabel("Congestión (vehículos en cola)")
axes[1, 0].legend()

# Gráfico de momentos de cruce de vehículos de emergencia
axes[1, 1].plot(emergency_times, [1]*len(emergency_times), 'ro', label="Vehículos de emergencia")
axes[1, 1].set_title("Momentos de cruce de vehículos de emergencia")
axes[1, 1].set_xlabel("Tiempo (segundos)")
axes[1, 1].set_yticks([])  # Ocultar el eje Y ya que solo mostramos eventos
axes[1, 1].legend()

plt.tight_layout()
plt.show()