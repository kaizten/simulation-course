# Transporte público: Simulación de una línea de autobuses

# Modela una ruta de autobús con varias paradas, considerando la capacidad del autobús, los tiempos
# de llegada y salida, y los retrasos en cada parada, optimizando la frecuencia de autobuses.

import simpy
import random

# Parámetros de la simulación
NUM_PARADAS = 10  # Número de paradas de la ruta
TIEMPO_ENTRE_PARADAS = 5  # Tiempo de viaje entre paradas en minutos
CAPACIDAD_BUS = 50  # Capacidad máxima del autobús
TIEMPO_SUBIDA = 2  # Tiempo en segundos que tarda un pasajero en subir/bajar del bus
INTERVALO_AUTOBUSES = 15  # Tiempo en minutos entre autobuses
RETRASO_MAXIMO = 3  # Tiempo de retraso en minutos que puede ocurrir en cada parada

# Generación de pasajeros
TASA_LLEGADA_PASAJEROS = 10  # Número promedio de pasajeros por minuto en cada parada


class Pasajero:
    def __init__(self, env, id, origen, destino):
        self.env = env
        self.id = id
        self.origen = origen
        self.destino = destino


class Parada:
    def __init__(self, env, id):
        self.env = env
        self.id = id
        self.cola_pasajeros = []

    def generar_pasajeros(self):
        # Simular la llegada de pasajeros a la parada
        while True:
            yield self.env.timeout(random.expovariate(1 / TASA_LLEGADA_PASAJEROS))
            destino = random.randint(self.id + 1, NUM_PARADAS)  # Eligen una parada al azar después de la actual
            pasajero = Pasajero(self.env, f'P{len(self.cola_pasajeros)}', self.id, destino)
            self.cola_pasajeros.append(pasajero)
            print(f"Pasajero {pasajero.id} llega a la parada {self.id} con destino {pasajero.destino} en el tiempo {self.env.now:.2f}.")


class Autobus:
    def __init__(self, env, id, paradas):
        self.env = env
        self.id = id
        self.paradas = paradas
        self.capacidad = CAPACIDAD_BUS
        self.pasajeros = []

    def circular(self):
        # El autobús sigue recorriendo las paradas de la ruta
        while True:
            for parada in self.paradas:
                yield from self.procesar_parada(parada)
                yield self.env.timeout(TIEMPO_ENTRE_PARADAS + random.uniform(0, RETRASO_MAXIMO))

    def procesar_parada(self, parada):
        print(f"Autobús {self.id} llega a la parada {parada.id} en el tiempo {self.env.now:.2f}.")
        yield self.env.timeout(1)  # Simula que el autobús se detiene en la parada

        # Bajar pasajeros en la parada actual
        bajan = [p for p in self.pasajeros if p.destino == parada.id]
        for pasajero in bajan:
            print(f"Pasajero {pasajero.id} baja en la parada {parada.id} en el tiempo {self.env.now:.2f}.")
            self.pasajeros.remove(pasajero)
            yield self.env.timeout(TIEMPO_SUBIDA)

        # Subir pasajeros en la parada actual (si hay espacio en el bus)
        suben = 0
        while parada.cola_pasajeros and len(self.pasajeros) < self.capacidad:
            pasajero = parada.cola_pasajeros.pop(0)
            self.pasajeros.append(pasajero)
            print(f"Pasajero {pasajero.id} sube al autobús {self.id} en la parada {parada.id} con destino {pasajero.destino} en el tiempo {self.env.now:.2f}.")
            yield self.env.timeout(TIEMPO_SUBIDA)
            suben += 1

        print(f"Autobús {self.id} deja la parada {parada.id} con {len(self.pasajeros)} pasajeros en el tiempo {self.env.now:.2f}.")


def generar_autobuses(env, paradas):
    bus_id = 0
    while True:
        autobus = Autobus(env, f'Bus{bus_id}', paradas)
        env.process(autobus.circular())
        yield env.timeout(INTERVALO_AUTOBUSES)
        bus_id += 1


def simulacion(env):
    # Crear las paradas y generar pasajeros
    paradas = [Parada(env, i) for i in range(NUM_PARADAS)]
    for parada in paradas:
        env.process(parada.generar_pasajeros())

    # Generar autobuses que circulan en la ruta
    env.process(generar_autobuses(env, paradas))


# Ejecutar la simulación
env = simpy.Environment()
env.process(simulacion(env))
env.run(until=200)  # Simulación durante 200 minutos
