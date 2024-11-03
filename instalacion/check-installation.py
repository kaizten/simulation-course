import simpy
import random

# Parámetros:
RANDOM_SEED = 42            # Semilla para reproducibilidad
INTERVAL_PASSENGERS = 5     # Tiempo promedio entre llegadas de pasajeros (minutos)
BUS_CAPACITY = 20           # Capacidad de cada guagua
BUS_INTERVAL = 15           # Intervalo entre llegadas de guaguas (minutos)
SIMULATION_TIME = 100       # Tiempo de simulación (minutos)

def passenger(env, name, bus_stop):
    """Genera un pasajero que llega a la estación de guaguas."""
    arrival_time = env.now
    print(f"{arrival_time:.2f}: {name} llega a la estación.")
    with bus_stop.request() as request:
        yield request
        waiting_time = env.now - arrival_time
        print(f"{name} se subió a la guagua después de esperar {waiting_time:.2f} minutos.")

def bus(env, bus_stop):
    """Proceso que representa la llegada de una guagua a la estación."""
    while True:
        print(f"{env.now:.2f}: Guagua llega a la estación.")
        with bus_stop.request() as request:
            yield request
            yield env.timeout(1)  # Tiempo que toma abordar a los pasajeros
            print(f"{env.now:.2f}: Guagua sale de la estación.")
        yield env.timeout(BUS_INTERVAL)

def passenger_arrival(env, bus_stop):
    """Proceso que genera la llegada de pasajeros a la estación."""
    i = 0
    while True:
        yield env.timeout(random.expovariate(1.0 / INTERVAL_PASSENGERS))
        i += 1
        env.process(passenger(env, f"Pasajero {i}", bus_stop))

# Configurar la simulación
print("Simulación de movilidad de pasajeros en una estación de guaguas")
print("===============================================================")
random.seed(RANDOM_SEED)  # Semilla para reproducibilidad
env = simpy.Environment()
bus_stop = simpy.Resource(env, capacity=BUS_CAPACITY)

# Iniciar los procesos de simulación
env.process(passenger_arrival(env, bus_stop))
env.process(bus(env, bus_stop))

# Ejecutar la simulación
env.run(until=SIMULATION_TIME)