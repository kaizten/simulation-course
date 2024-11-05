# La guagua consume 15 unidades de combustible por unidad de tiempo.
# Si el combustible en el tanque cae por debajo de 20 unidades, la guagua se detiene para repostar.
# El Container ayuda a modelar un ciclo típico de consumo y recarga de combustible.

import simpy

def guagua(env, tanque, consumo):
    while True:
        # Simula el consumo de combustible mientras la guagua está en ruta
        yield env.timeout(1)
        yield tanque.get(consumo)  # Consumo de combustible
        print(f"{env.now}: Consumo de {consumo} unidades. Combustible actual: {tanque.level}")
        
        # Si el nivel de combustible es bajo, la guagua va a repostar
        if tanque.level < 20:
            print(f"{env.now}: Combustible bajo. Repostando...")
            yield tanque.put(tanque.capacity - tanque.level)  # Repostaje completo
            print(f"{env.now}: Repostaje completado. Combustible actual: {tanque.level}")

# Configuración del entorno
env = simpy.Environment()
tanque = simpy.Container(env, capacity=100, init=60)  # Tanque con capacidad de 100 unidades, inicia con 60
consumo = 15  # Consumo de combustible cada unidad de tiempo

# Inicio de la simulación de la guagua
env.process(guagua(env, tanque, consumo))
env.run(until=20)
