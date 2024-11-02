import simpy

def proceso(env, container):
    # Agrega recursos al container cada 2 unidades de tiempo
    while True:
        yield env.timeout(2)
        yield container.put(10)
        print(f"{env.now}: Añadidas 10 unidades. Nivel actual: {container.level}")

env = simpy.Environment()
container = simpy.Container(env, capacity=100, init=50)
env.process(proceso(env, container))
env.run(until=100)