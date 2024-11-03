import simpy
import random

# Parámetros:
RANDOM_SEED = 42        # Para reproducibilidad
NUM_PUMPS = 2           # Número de bombas de gasolina
TOTAL_VEHICLES = 10     # Número total de vehículos que llegarán
INTER_ARRIVAL_TIME = 5  # Tiempo medio entre llegadas de vehículos
TIME_TO_REFUEL = 7      # Tiempo medio para repostar

def vehicle(name, env, gas_station):
    """Proceso para representar a un vehículo que llega a la gasolinera"""
    print(f'{name} llega a la gasolinera en {env.now:.2f} minutos')
    
    with gas_station.request() as request:
        # Esperar hasta que haya una bomba disponible
        yield request
        print(f'{name} comienza a repostar en {env.now:.2f} minutos')
        yield env.timeout(random.expovariate(1.0 / TIME_TO_REFUEL))
        print(f'{name} termina de repostar en {env.now:.2f} minutos')

def vehicle_generator(env, gas_station):
    """Generador para crear vehículos en intervalos aleatorios"""
    for i in range(TOTAL_VEHICLES):
        yield env.timeout(random.expovariate(1.0 / INTER_ARRIVAL_TIME))
        env.process(vehicle(f'Vehículo {i + 1}', env, gas_station))

# Configurar y correr la simulación
def main():
    print('Simulación de una gasolinera con SimPy')
    random.seed(RANDOM_SEED)
    # Crear entorno y recursos
    env = simpy.Environment()
    gas_station = simpy.Resource(env, NUM_PUMPS)
    # Iniciar generador de vehículos
    env.process(vehicle_generator(env, gas_station))
    # Ejecutar simulación
    env.run()

if __name__ == '__main__':
    main()