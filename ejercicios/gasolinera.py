import simpy
import random
import matplotlib.pyplot as plt

# Parámetros:
TIEMPO_DE_SIMULACION = 1 * 60   # Tiempo de simulación en minutos
TIEMPO_MIN_SERVICIO = 2         # Tiempo mínimo de servicio
TIEMPO_MAX_SERVICIO = 5         # Tiempo máximo de servicio
TIEMPO_LLEGADA_CLIENTES = 3     # Intervalo de tiempo en que llegan clientes
NUMERO_SURTIDORES = 3           # Número de surtidores en la gasolinera
NUMERO_EMPLEADOS = 2            # Número de empleados atendiendo en la gasolinera

tiempo_uso_empleados = {}
tiempo_uso_surtidores = {}
tiempo_espera_vehiculos = {}
tiempo_servicio_vehiculos = {}

def surtidor(env, nombre, empleados):
    """Proceso que simula el servicio de un vehículo en la gasolinera."""
    llegada = env.now
    print(f'{llegada:.2f}: {nombre} llegó a la gasolinera.')
    
    # Solicita un surtidor
    with surtidores.request() as surtidor:
        yield surtidor  # Espera a que haya un surtidor libre
        surtidor_id = surtidor.resource.count - 1
        nombre_surtidor = f'Surtidor {surtidor_id}'
        print(f'{llegada:.2f}: {nombre} está en el {nombre_surtidor}')

        # Solicita un empleado para llenar combustible
        with empleados.request() as empleado:
            yield empleado  # Espera a que haya un empleado libre
            empleado_id = empleado.resource.count - 1
            nombre_empleado = f'Empleado {empleado_id}'
            tiempo_servicio = random.uniform(TIEMPO_MIN_SERVICIO, TIEMPO_MAX_SERVICIO)
            yield env.timeout(tiempo_servicio)

            # Registrar el uso del empleado y el surtidor
            if (nombre_empleado in tiempo_uso_empleados):
                tiempo_uso_empleados[nombre_empleado] += tiempo_servicio
            else:
                tiempo_uso_empleados[nombre_empleado] = tiempo_servicio
            if (nombre_surtidor in tiempo_uso_surtidores):
                tiempo_uso_surtidores[nombre_surtidor] += tiempo_servicio
            else:
                tiempo_uso_surtidores[nombre_surtidor] = tiempo_servicio           
            tiempo_espera_vehiculos[nombre] = env.now - llegada
            tiempo_servicio_vehiculos[nombre] = tiempo_servicio
            print(f'{llegada:.2f}: {nombre} ha terminado de llenar combustible en {nombre_surtidor} mediante {nombre_empleado}.')

def llegada_vehiculos(env, surtidores, empleados):
    """Proceso que simula la llegada de vehículos a la gasolinera."""
    contador = 0
    while True:
        yield env.timeout(random.expovariate(1.0 / TIEMPO_LLEGADA_CLIENTES))  # Llegadas cada ciertos minutos en promedio
        env.process(surtidor(env, f'Vehículo {contador}', empleados))
        contador += 1

# Inicialización del entorno de simulación
env = simpy.Environment()
# Recursos de la gasolinera
surtidores = simpy.Resource(env, NUMERO_SURTIDORES)
empleados = simpy.Resource(env, NUMERO_EMPLEADOS)
# Inicialización de la simulación
env.process(llegada_vehiculos(env, surtidores, empleados))
# Ejecución de la simulación
env.run(until=TIEMPO_DE_SIMULACION)

# Graficar los resultados
plt.figure(figsize=(10, 5))

# Gráfico del uso de los empleados
plt.subplot(1, 3, 1)
plt.bar(tiempo_uso_empleados.keys(), tiempo_uso_empleados.values())
plt.ylabel('Tiempo de uso (minutos)')
plt.title('Uso de los empleados')
plt.xticks(rotation=90)

# Gráfico del uso de los surtidores
plt.subplot(1, 3, 2)
plt.bar(tiempo_uso_surtidores.keys(), tiempo_uso_surtidores.values())
plt.ylabel('Tiempo de uso (minutos)')
plt.title('Uso de los surtidores')
plt.xticks(rotation=90)

# Gráfico del tiempo de servicio de cada vehículo
plt.subplot(1, 3, 3)
plt.bar(tiempo_espera_vehiculos.keys(), tiempo_espera_vehiculos.values())
plt.bar(tiempo_servicio_vehiculos.keys(), tiempo_servicio_vehiculos.values())
plt.ylabel('Tiempo de servicio (minutos)')
plt.title('Tiempo de servicio de cada vehículo')
plt.legend(["Espera", "Servicio"])
plt.xticks(rotation=90)

plt.show()