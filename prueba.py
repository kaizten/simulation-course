import simpy
import random
import matplotlib.pyplot as plt

RANDOM_SEED = 42
NUM_VEHICULOS = 10
TIEMPO_SIMULACION = 100

class Interseccion:
    def __init__(self, env, capacidad):
        self.env = env
        self.semaforo = simpy.Resource(env, capacidad)
        self.monitor = simpy.Monitor(env)

    def cruzar(self, vehiculo):
        tiempo_cruce = random.uniform(2, 5)  # Tiempo para cruzar la intersección
        yield self.env.timeout(tiempo_cruce)
        self.monitor.observe(tiempo_cruce)
        print(f'Vehículo {vehiculo} cruzó en {tiempo_cruce:.2f} minutos')

def vehiculo(env, nombre, interseccion):
    with interseccion.semaforo.request() as request:
        yield request
        print(f'Vehículo {nombre} esperando para cruzar a los {env.now:.2f} minutos')
        yield env.process(interseccion.cruzar(nombre))

def setup(env, num_vehiculos, capacidad):
    interseccion = Interseccion(env, capacidad)
    
    # Crear vehículos iniciales
    for i in range(num_vehiculos):
        env.process(vehiculo(env, i, interseccion))
    
    # Generar nuevos vehículos aleatoriamente
    while True:
        yield env.timeout(random.uniform(3, 8))
        i += 1
        env.process(vehiculo(env, i, interseccion))

# Configuración e inicio de la simulación
random.seed(RANDOM_SEED)
env = simpy.Environment()
env.process(setup(env, NUM_VEHICULOS, capacidad=2))
env.run(until=TIEMPO_SIMULACION)

# Visualización de resultados
interseccion = Interseccion(env, capacidad=2)
tiempo_cruce = [observacion for observacion in interseccion.monitor.data]

plt.plot(tiempo_cruce, marker='o')
plt.xlabel('Vehículo')
plt.ylabel('Tiempo de Cruce (minutos)')
plt.title('Tiempos de Cruce en la Intersección')
plt.grid()
plt.show()