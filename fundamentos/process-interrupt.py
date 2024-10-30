import simpy
import random

def boy_walks(env, bus_stop_event):
    print(f"{env.now:.2f}: The boy starts walking to the bus stop.")
    walking_duration = random.randint(5, 10)
    yield env.timeout(walking_duration)
    print(f"{env.now:.2f}: The boy arrives at the bus stop and starts using his phone.")
    # Start using the phone until the bus arrives
    phone_process = env.process(boy_uses_phone(env))
    # Wait until bus arrives
    yield bus_stop_event
    # Bus arrives and interrupts the phone process
    phone_process.interrupt()

def boy_uses_phone(env):
    try:
        while True:
            print(f"{env.now:.2f}: The boy is using his phone.")
            yield env.timeout(1)
    except simpy.Interrupt:
        print(f"{env.now:.2f}: The bus arrives and the boy stops using his phone.")

def bus_arrives(env, bus_stop_event):
    bus_arrival_time = random.randint(8, 15)
    yield env.timeout(bus_arrival_time)
    print(f"{env.now:.2f}: The bus arrives at the bus stop.")
    bus_stop_event.succeed()

# Create the simulation environment
env = simpy.Environment()
# Event that signals when the bus arrives
bus_stop_event = env.event()
# Start the processes
env.process(boy_walks(env, bus_stop_event))
env.process(bus_arrives(env, bus_stop_event))
# Run the simulation
env.run()