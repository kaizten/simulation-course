import simpy

class Car(object):
    def __init__(self, env):
        self.env = env
        # Comienza el proceso de ejecución cada vez que se crea una instancia.
        self.action = env.process(self.run())

    def run(self):
        while True:
            print('Comienza a aparcar y cargar a las %d' % self.env.now)
            charge_duration = 5
            # Esperamos hasta que el proceso de carga termine
            yield self.env.process(self.charge(charge_duration))
            # El proceso de carga ha terminado y podemos empezar a conducir de nuevo.
            print('Comienza a conducir a las %d' % self.env.now)
            trip_duration = 2
            yield self.env.timeout(trip_duration)

    def charge(self, duration):
        print('Comienza a cargar a las %d' % self.env.now)
        yield self.env.timeout(duration)
        
env = simpy.Environment()
car = Car(env)
env.run(until=15)