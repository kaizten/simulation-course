import simpy

class Car(object):
    def __init__(self, env):
        self.env = env
        # Comienza el proceso de ejecución cada vez que se crea una instancia.
        self.action = env.process(self.run())

    def run(self):
        while True:
            print(f'{self.env.now:.2f}: Comienza a aparcar')
            charge_duration = 10
            # Esperamos hasta que el proceso de carga termine
            yield self.env.process(self.charge(charge_duration))
            # El proceso de carga ha terminado y podemos empezar a conducir de nuevo.
            print(f'{self.env.now:.2f}: Comienza a conducir')
            trip_duration = 50
            yield self.env.timeout(trip_duration)

    def charge(self, duration):
        print(f'{self.env.now:.2f}: Comienza a cargar')
        yield self.env.timeout(duration)
        
env = simpy.Environment()
car = Car(env)
env.run(until=1000)