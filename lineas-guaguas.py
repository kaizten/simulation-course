# Transporte público: Simulación de una línea de autobuses
# Modela una ruta de autobús con varias paradas, considerando la capacidad del autobús, los tiempos
# de llegada y salida, y los retrasos en cada parada, optimizando la frecuencia de autobuses

import simpy
import random

# Parámetros globales
NUM_PARADAS = 5  # Número de paradas en la línea de autobús
CAPACIDAD_AUTOBUS = 30  # Capacidad máxima del autobús
TIEMPO_ENTRE_PARADAS = 5  # Tiempo promedio entre paradas en minutos
TIEMPO_EN_PARADA = 2  # Tiempo promedio que el autobús pasa en cada parada en minutos
INTERVALO_ENTRE_AUTOBUSES = 10  # Frecuencia de autobuses en minutos
TIEMPO_SIMULACION = 100  # Tiempo total de la simulación en minutos

# Función para simular la llegada del autobús a una parada
def autobus(env, nombre_autobus, paradas, capacidad):
    # Recorremos todas las paradas
    for i in range(NUM_PARADAS):
        # Simulamos el tiempo de viaje entre paradas
        yield env.timeout(TIEMPO_ENTRE_PARADAS)
        print(f'{nombre_autobus} llega a la parada {i+1} en el tiempo {env.now}')
        
        # Pasajeros que intentan subir y bajar
        pasajeros_bajando = random.randint(0, min(capacidad.level, 5))  # Pasajeros bajando
        pasajeros_subiendo = random.randint(0, min(capacidad.capacity - capacidad.level, 10))  # Pasajeros subiendo
        
        # Bajan los pasajeros
        with capacidad.get(pasajeros_bajando) as baja:
            yield baja
            print(f'{pasajeros_bajando} pasajeros bajan del {nombre_autobus} en la parada {i+1}')
        
        # Suben nuevos pasajeros
        with capacidad.put(pasajeros_subiendo) as sube:
            yield sube
            print(f'{pasajeros_subiendo} pasajeros suben al {nombre_autobus} en la parada {i+1}')
        
        # Simulamos el tiempo que el autobús pasa en la parada
        yield env.timeout(TIEMPO_EN_PARADA)

# Función para generar autobuses en la línea a intervalos regulares
def generador_autobuses(env, intervalo):
    numero_autobus = 0
    while True:
        numero_autobus += 1
        capacidad_autobus = simpy.Container(env, CAPACIDAD_AUTOBUS, init=0)  # Contenedor para contar los pasajeros
        env.process(autobus(env, f'Autobús {numero_autobus}', NUM_PARADAS, capacidad_autobus))
        
        # Se generan autobuses a intervalos regulares
        yield env.timeout(intervalo)

# Configuración y ejecución de la simulación
env = simpy.Environment()

# Generamos los autobuses a intervalos de 10 minutos
env.process(generador_autobuses(env, INTERVALO_ENTRE_AUTOBUSES))

# Ejecutamos la simulación durante 100 minutos
env.run(until=TIEMPO_SIMULACION)
