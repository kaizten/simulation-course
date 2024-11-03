import simpy.rt

# Parámetros de la simulación
TIEMPO_SIMULACION = 10      # Tiempo de simulación en segundos
INTERVALO_GENERACION = 1    # Intervalo de generación de vehículos
TIEMPO_VIAJE = 3            # Tiempo que toma un viaje

# Definición del entorno en tiempo real
env = simpy.rt.RealtimeEnvironment(factor=1, strict=False)

# Definición del proceso de vehículo
def vehiculo(env, nombre):
    print(f'{nombre} inicia su recorrido a los {env.now:.2f} segundos')
    yield env.timeout(TIEMPO_VIAJE)
    print(f'{nombre} finaliza su recorrido a los {env.now:.2f} segundos')

# Proceso de generación de vehículos
def generador_vehiculos(env):
    contador = 0
    while True:
        contador += 1
        nombre_vehiculo = f'Vehículo {contador}'
        env.process(vehiculo(env, nombre_vehiculo))
        yield env.timeout(INTERVALO_GENERACION)

# Inicialización de la simulación
env.process(generador_vehiculos(env))
print('Inicio de la simulación de movilidad urbana')

# Ejecución de la simulación
env.run(until=TIEMPO_SIMULACION)