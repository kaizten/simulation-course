import simpy
import random

RANDOM_SEED = 42
NUM_TAXIS = 3
SIM_TIME = 100
NUM_PASSENGERS = 5

class Taxi:
    def __init__(self, env, name):
        self.env = env
        self.name = name
        self.passengers = 0
        self.action = env.process(self.drive())

    def drive(self):
        while True:
            try:
                if self.passengers == 0:
                    # Buscar pasajeros
                    search_duration = random.randint(3, 6)
                    print(f'{self.name} está buscando pasajeros a las {self.env.now}, tomará {search_duration} unidades de tiempo.')
                    yield self.env.timeout(search_duration)
                    self.passengers = random.randint(1, NUM_PASSENGERS)
                    print(f'{self.name} ha recogido {self.passengers} pasajeros a las {self.env.now}.')
                
                # Simulamos la conducción hacia un destino
                trip_duration = random.randint(5, 10)
                print(f'{self.name} empieza un viaje a las {self.env.now}, durará {trip_duration} unidades de tiempo.')
                yield self.env.timeout(trip_duration)
                print(f'{self.name} ha terminado el viaje a las {self.env.now}.')
                self.passengers = 0
            except simpy.Interrupt as interrupt:
                # Manejo de la interrupción (emergencia)
                print(f'{self.name} ha sido interrumpido para una emergencia a las {self.env.now}!')
                emergency_duration = random.randint(2, 5)
                try:
                    yield self.env.timeout(emergency_duration)
                except simpy.Interrupt:
                    print(f'{self.name} ha sido interrumpido nuevamente durante la emergencia a las {self.env.now}!')
                print(f'{self.name} ha terminado con la emergencia a las {self.env.now}, y vuelve a su ruta normal.')

def emergency(env, taxis):
    while True:
        yield env.timeout(random.randint(7, 15))
        taxi = random.choice(taxis)
        if taxi.action.is_alive:
            taxi.action.interrupt()

def maintenance(env, taxis):
    while True:
        yield env.timeout(random.randint(20, 30))
        taxi = random.choice(taxis)
        if taxi.action.is_alive:
            print(f'{taxi.name} necesita mantenimiento a las {env.now}, suspendiendo operaciones.')
            taxi.action.interrupt()
            maintenance_duration = random.randint(5, 10)
            yield env.timeout(maintenance_duration)
            print(f'{taxi.name} ha completado el mantenimiento a las {env.now}, y está listo para operar de nuevo.')

# Configuración de la simulación
print('Simulación de movilidad con interrupciones de emergencia y mantenimiento')
random.seed(RANDOM_SEED)
env = simpy.Environment()

# Crear taxis
taxis = [Taxi(env, f'Taxi {i+1}') for i in range(NUM_TAXIS)]

# Generar interrupciones de emergencia
env.process(emergency(env, taxis))

# Generar mantenimiento
env.process(maintenance(env, taxis))

# Ejecutar la simulación
env.run(until=SIM_TIME)