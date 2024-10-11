# Simulación de tráfico en una intersección con semáforos
# Se modelan las dinámicas de los vehículos en una intersección regulada por semáforos, donde cada
# vehículo espera su turno en función de la luz verde, y se analizan los tiempos de espera y la 
# congestión en horas pico.

import simpy
import random

# Parámetros globales
VEHICULOS_POR_MINUTO = 5  # Promedio de vehículos que llegan por minuto
TIEMPO_VERDE = 30  # Duración del semáforo en verde (en segundos)
TIEMPO_AMARILLO = 5  # Duración del semáforo en amarillo (en segundos)
TIEMPO_ROJO = 30  # Duración del semáforo en rojo (en segundos)
DURACION_SIMULACION = 3600  # Tiempo total de simulación en segundos (1 hora)
CARRILES = 2  # Número de carriles en la intersección

# Función para simular el comportamiento de un vehículo
def vehiculo(env, nombre, semaforo, tiempo_espera):
    # Llegada a la intersección
    llegada = env.now
    print(f'{nombre} llega a la intersección en el tiempo {llegada:.1f} s')

    # Esperar a que el semáforo esté verde
    with semaforo.request() as req:
        yield req
        yield env.timeout(tiempo_espera)

    # Salida de la intersección
    salida = env.now
    tiempo_total = salida - llegada
    print(f'{nombre} cruza la intersección en el tiempo {salida:.1f} s tras esperar {tiempo_total:.1f} s')

# Función para controlar el ciclo del semáforo
def ciclo_semaforo(env, semaforo, ciclo_verde, ciclo_amarillo, ciclo_rojo):
    while True:
        print(f'Semáforo verde en el tiempo {env.now:.1f} s')
        semaforo.capacity = CARRILES
        yield env.timeout(ciclo_verde)

        print(f'Semáforo amarillo en el tiempo {env.now:.1f} s')
        semaforo.capacity = 0  # En amarillo no pasan más vehículos, pero los que ya están pueden cruzar
        yield env.timeout(ciclo_amarillo)

        print(f'Semáforo rojo en el tiempo {env.now:.1f} s')
        semaforo.capacity = 0  # En rojo no pasa ningún vehículo
        yield env.timeout(ciclo_rojo)

# Función para generar vehículos aleatoriamente
def llegada_vehiculos(env, semaforo):
    i = 0
    while True:
        i += 1
        tiempo_espera = random.uniform(2, 5)  # Tiempo de cruce de la intersección
        yield env.timeout(random.expovariate(VEHICULOS_POR_MINUTO / 60.0))
        env.process(vehiculo(env, f'Vehículo {i}', semaforo, tiempo_espera))

# Función principal para ejecutar la simulación
def ejecutar_simulacion():
    # Crear el entorno de simulación
    env = simpy.Environment()

    # Crear el recurso del semáforo (maneja el número de vehículos que pueden pasar)
    semaforo = simpy.Resource(env, capacity=CARRILES)

    # Proceso de control del semáforo
    env.process(ciclo_semaforo(env, semaforo, TIEMPO_VERDE, TIEMPO_AMARILLO, TIEMPO_ROJO))

    # Proceso de llegada de vehículos
    env.process(llegada_vehiculos(env, semaforo))

    # Ejecutar la simulación
    env.run(until=DURACION_SIMULACION)

# Ejecutar la simulación
if __name__ == '__main__':
    ejecutar_simulacion()
