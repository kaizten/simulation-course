# Cada unidad de tiempo, el vehículo consume 5 unidades de batería.
# Cuando la batería cae por debajo de 10 unidades, el vehículo se detiene y se recarga hasta su capacidad máxima.

import simpy

def carga_vehiculo(env, bateria, consumo):
    while True:
        # Simula el consumo de batería durante el uso del vehículo
        yield env.timeout(1)
        yield bateria.get(consumo)  # Consumo de la batería cada unidad de tiempo
        print(f"{env.now}: Consumo de {consumo} unidades. Batería actual: {bateria.level}")
        
        # Si la batería está baja, se detiene el vehículo para cargarlo
        if bateria.level < 10:
            print(f"{env.now}: Batería baja. Comenzando recarga.")
            yield bateria.put(bateria.capacity - bateria.level)  # Recarga completa
            print(f"{env.now}: Recarga completa. Batería actual: {bateria.level}")

# Configuración del entorno
env = simpy.Environment()
bateria = simpy.Container(env, capacity=100, init=50)  # Capacidad total de 100, inicia con 50
consumo = 5  # Consumo de 5 unidades por intervalo

# Inicio de la simulación
env.process(carga_vehiculo(env, bateria, consumo))
env.run(until=20)