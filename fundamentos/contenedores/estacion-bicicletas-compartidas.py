# La estación comienza con 5 bicicletas y tiene una capacidad máxima de 10.
# Cada usuario retira una bicicleta, la usa durante un período (simulado con timeout(5)), y luego la devuelve.
# Cuando la estación se queda sin bicicletas, los usuarios deben esperar a que alguna sea devuelta.

import simpy

def usuario(env, estacion):
    while True:
        # Simula el retiro de una bicicleta
        if estacion.level > 0:
            yield estacion.get(1)  # Retira una bicicleta
            print(f"{env.now}: Usuario retira una bicicleta. Bicicletas restantes: {estacion.level}")
        else:
            print(f"{env.now}: No hay bicicletas disponibles. Usuario espera.")
        
        # Tiempo de uso de la bicicleta antes de devolverla
        yield env.timeout(5)
        
        # Devuelve la bicicleta a la estación
        yield estacion.put(1)
        print(f"{env.now}: Usuario devuelve una bicicleta. Bicicletas disponibles: {estacion.level}")
        
        # Espera antes de que un nuevo usuario llegue
        yield env.timeout(2)

# Configuración del entorno
env = simpy.Environment()
estacion = simpy.Container(env, capacity=10, init=5)  # Capacidad máxima de 10 bicicletas, comienza con 5

# Inicio de la simulación con múltiples usuarios
for _ in range(3):  # Tres usuarios activos
    env.process(usuario(env, estacion))

env.run(until=30)