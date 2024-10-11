import simpy

def semaforo(env):
    while True:
        print(f"Semáforo en VERDE en el tiempo {env.now}")
        yield env.timeout(10)  # Semáforo en verde durante 10 unidades de tiempo
        print(f"Semáforo en ROJO en el tiempo {env.now}")
        yield env.timeout(5)  # Semáforo en rojo durante 5 unidades de tiempo

def vehiculo(env, nombre):
    while True:
        print(f"{nombre} esperando luz verde en el tiempo {env.now}")
        yield env.timeout(1)  # Espera antes de volver a intentar

# Crear entorno de simulación
env = simpy.Environment()

# Agregar procesos al entorno
env.process(semaforo(env))
env.process(vehiculo(env, 'Vehículo 1'))

# Ejecutar simulación
env.run(until=30)