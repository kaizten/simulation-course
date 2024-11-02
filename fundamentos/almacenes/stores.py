import simpy

def productor(env, store):
    for i in range(5):
        print(f"Productor agrega elemento {i} en el instante {env.now}")
        yield store.put(i)
        yield env.timeout(1)

def consumidor(env, store):
    while True:
        item = yield store.get()
        print(f"Consumidor retira {item} en el instante {env.now}")
        yield env.timeout(2)

env = simpy.Environment()
store = simpy.Store(env, capacity=3)
env.process(productor(env, store))
env.process(consumidor(env, store))
env.run(until=10)