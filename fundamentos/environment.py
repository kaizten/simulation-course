import simpy

def vehiculo(env, nombre, tiempo_recarga):
    print(f"{nombre} llega a la estación de recarga en el minuto {env.now}")
    yield env.timeout(tiempo_recarga)
    print(f"{nombre} sale de la estación de recarga en el minuto {env.now}")

# Crear el entorno de simulación
env = simpy.Environment()

# Agregar vehículos a la simulación
env.process(vehiculo(env, 'Vehículo 1', 4))
env.process(vehiculo(env, 'Vehículo 2', 6))

# Ejecutar la simulación
env.run(until=15)