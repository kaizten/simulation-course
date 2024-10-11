# Simulación de tráfico en una intersección con semáforos

# Se modelan las dinámicas de los vehículos en una intersección regulada por semáforos, donde cada
# vehículo espera su turno en función de la luz verde, y se analizan los tiempos de espera y la 
# congestión en horas pico.

# Se incluyen giros a la izquierda y a la derecha, diferentes tipos de vehículos (automóviles, 
# camiones y motocicletas), y cambios de ciclo de semáforo dinámicos según la densidad del tráfico.

import simpy
import random

# Parámetros globales
VEHICULOS_POR_MINUTO = 5  # Promedio de vehículos que llegan por minuto
TIEMPO_VERDE_INICIAL = 30  # Duración inicial del semáforo en verde (en segundos)
TIEMPO_AMARILLO = 5  # Duración del semáforo en amarillo (en segundos)
TIEMPO_ROJO = 30  # Duración del semáforo en rojo (en segundos)
DURACION_SIMULACION = 3600  # Tiempo total de simulación en segundos (1 hora)
CARRILES = 2  # Número de carriles en la intersección

# Proporciones de tipos de vehículos
TIPOS_VEHICULOS = {
    "auto": 0.7,
    "camion": 0.2,
    "moto": 0.1
}

# Tiempo extra para cada tipo de vehículo al cruzar la intersección
TIEMPOS_CRUCE = {
    "auto": 3,
    "camion": 6,
    "moto": 2
}

# Función para simular el comportamiento de un vehículo
def vehiculo(env, nombre, tipo, giro, semaforo, tiempo_espera):
    # Llegada a la intersección
    llegada = env.now
    print(f'{nombre} ({tipo}) llega a la intersección girando {giro} en el tiempo {llegada:.1f} s')

    # Esperar a que el semáforo esté verde
    with semaforo.request() as req:
        yield req
        yield env.timeout(tiempo_espera + TIEMPOS_CRUCE[tipo])  # Tiempo de cruce según el tipo de vehículo

    # Salida de la intersección
    salida = env.now
    tiempo_total = salida - llegada
    print(f'{nombre} ({tipo}) cruza la intersección en el tiempo {salida:.1f} s tras esperar {tiempo_total:.1f} s')

# Función para controlar el ciclo del semáforo, ajustándolo según la densidad del tráfico
def ciclo_semaforo(env, semaforo, ciclo_amarillo, ciclo_rojo, densidad_vehiculos):
    ciclo_verde = TIEMPO_VERDE_INICIAL
    while True:
        # Ajustar la duración del verde según la densidad de vehículos en cola
        ciclo_verde = min(60, max(20, len(semaforo.queue) * 5))  # De 20 a 60 segundos
        print(f'Semáforo verde durante {ciclo_verde} s en el tiempo {env.now:.1f} s (densidad: {len(semaforo.queue)} vehículos)')

        semaforo.capacity = CARRILES
        yield env.timeout(ciclo_verde)

        print(f'Semáforo amarillo durante {ciclo_amarillo} s en el tiempo {env.now:.1f} s')
        semaforo.capacity = 0
        yield env.timeout(ciclo_amarillo)

        print(f'Semáforo rojo durante {ciclo_rojo} s en el tiempo {env.now:.1f} s')
        semaforo.capacity = 0
        yield env.timeout(ciclo_rojo)

# Función para generar vehículos aleatoriamente con diferentes tipos y giros
def llegada_vehiculos(env, semaforo):
    i = 0
    while True:
        i += 1
        tipo = random.choices(list(TIPOS_VEHICULOS.keys()), list(TIPOS_VEHICULOS.values()))[0]
        giro = random.choice(['derecha', 'izquierda', 'recto'])  # Dirección aleatoria
        tiempo_espera = random.uniform(2, 5)  # Tiempo de espera antes de cruzar
        yield env.timeout(random.expovariate(VEHICULOS_POR_MINUTO / 60.0))
        env.process(vehiculo(env, f'Vehículo {i}', tipo, giro, semaforo, tiempo_espera))

# Función principal para ejecutar la simulación
def ejecutar_simulacion():
    # Crear el entorno de simulación
    env = simpy.Environment()

    # Crear el recurso del semáforo (maneja el número de vehículos que pueden pasar)
    semaforo = simpy.Resource(env, capacity=CARRILES)

    # Proceso de control del semáforo con ajuste dinámico según la densidad de tráfico
    env.process(ciclo_semaforo(env, semaforo, TIEMPO_AMARILLO, TIEMPO_ROJO, densidad_vehiculos=VEHICULOS_POR_MINUTO))

    # Proceso de llegada de vehículos con giros y diferentes tipos de vehículos
    env.process(llegada_vehiculos(env, semaforo))

    # Ejecutar la simulación
    env.run(until=DURACION_SIMULACION)

# Ejecutar la simulación
if __name__ == '__main__':
    ejecutar_simulacion()
