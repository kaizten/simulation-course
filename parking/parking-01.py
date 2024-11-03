import simpy
import random
import numpy as np
import matplotlib.pyplot as plt

# Parámetros:
SIMULATION_TIME = 8 * 60        # Tiempo de simulación en minutos
TOTAL_SPOTS = 50                # Total de plazas de estacionamiento disponibles
ARRIVAL_INTERVAL = 2            # Tiempo promedio entre llegadas de vehículos (minutos)
SEARCH_TIME = 5                 # Tiempo promedio para encontrar un estacionamiento disponible (minutos)
PARKING_DURATION = 30           # Duración promedio de estacionamiento (minutos)
DEMAND_BASE_RATE = 0.15         # Tarifa base por minuto de estacionamiento (euros)

class ParkingLot:
    def __init__(self, env, total_spots, demand_base_rate):
        self.env = env
        self.spots = simpy.Resource(env, capacity=total_spots)
        self.total_spots = total_spots
        self.demand_base_rate = demand_base_rate
        self.occupied_spots = 0
        self.revenue = 0
        self.vehicles_turned_away = 0
        self.vehicles_parked = 0
        self.occupancy_history = []
        self.revenue_history = []
        self.vehicles_parked_history = []
        self.vehicles_turned_away_history = []

    def park(self, vehicle_id, duration):
        with self.spots.request() as request:
            # Intentamos estacionar el vehículo
            result = yield request | self.env.timeout(SEARCH_TIME)
            if request in result:
                self.occupied_spots += 1
                self.vehicles_parked += 1
                self.record_occupancy()
                self.record_vehicles_parked()
                rate = self.calculate_dynamic_rate()
                cost = rate * duration
                self.revenue += cost
                self.record_revenue()
                print(f"{self.env.now:.2f}: Vehículo {vehicle_id} está estacionado. Tarifa: {rate:.2f} €/min, Duración: {duration:.2f} min, Coste total: {cost:.2f} €")
                yield self.env.timeout(duration)
                self.occupied_spots -= 1
                self.record_occupancy()
            else:
                # El vehículo no encuentra lugar para estacionar
                self.vehicles_turned_away += 1
                self.vehicles_turned_away_history.append((self.env.now, self.vehicles_turned_away))
                print(f"{self.env.now:.2f}: Vehículo {vehicle_id} no pudo encontrar estacionamiento y se retiró.")

    def calculate_dynamic_rate(self):
        # Calculamos la tarifa dinámica según la ocupación actual
        occupancy_rate = self.occupied_spots / self.total_spots
        dynamic_rate = self.demand_base_rate * (1 + occupancy_rate)
        return dynamic_rate

    def record_occupancy(self):
        # Registramos el nivel de ocupación actual
        self.occupancy_history.append((self.env.now, self.occupied_spots))

    def record_revenue(self):
        # Registramos el ingreso acumulado actual
        self.revenue_history.append((self.env.now, self.revenue))

    def record_vehicles_parked(self):
        # Registramos el número de vehículos atendidos
        self.vehicles_parked_history.append((self.env.now, self.vehicles_parked))

def vehicle_generator(env, parking_lot):
    vehicle_id = 0
    while True:
        # Cada nuevo vehículo intenta estacionarse
        yield env.timeout(random.expovariate(1.0 / ARRIVAL_INTERVAL))
        parking_duration = random.expovariate(1.0 / PARKING_DURATION)
        env.process(parking_lot.park(vehicle_id, parking_duration))
        vehicle_id += 1

# Configuración del entorno de simulación
env = simpy.Environment()
parking_lot = ParkingLot(env, TOTAL_SPOTS, DEMAND_BASE_RATE)

# Iniciamos el generador de vehículos
env.process(vehicle_generator(env, parking_lot))

# Ejecutamos la simulación
env.run(until=SIMULATION_TIME)

# Resultados
print("\nResultados finales:")
print(f"Ingresos totales: {parking_lot.revenue:.2f} €")
print(f"Vehículos rechazados por falta de espacio: {parking_lot.vehicles_turned_away}")

# Gráfica del nivel de ocupación a lo largo del tiempo
times, occupancies = zip(*parking_lot.occupancy_history)
plt.figure(figsize=(10, 6))

plt.subplot(2, 2, 1)
plt.plot(times, occupancies, label='Nivel de ocupación', color='b')
plt.xlabel('Tiempo (minutos)')
plt.ylabel('Número de plazas ocupadas')
plt.title('Nivel de ocupación')
plt.legend()
plt.grid(True)

# Gráfica de la recaudación a lo largo del tiempo
times, revenues = zip(*parking_lot.revenue_history)
plt.subplot(2, 2, 2)
plt.plot(times, revenues, label='Ingresos acumulados', color='g')
plt.xlabel('Tiempo (minutos)')
plt.ylabel('Ingresos (€)')
plt.title('Recaudación')
plt.legend()
plt.grid(True)

# Gráfica del número de vehículos atendidos a lo largo del tiempo
times, vehicles_parked = zip(*parking_lot.vehicles_parked_history)
plt.subplot(2, 2, 3)
plt.plot(times, vehicles_parked, label='Vehículos atendidos', color='r')
plt.xlabel('Tiempo (minutos)')
plt.ylabel('Número de vehículos atendidos')
plt.title('Vehículos atendidos')
plt.legend()
plt.grid(True)

# Gráfica del número de vehículos que no encontraron estacionamiento a lo largo del tiempo
#times, vehicles_turned_away = zip(*parking_lot.vehicles_turned_away_history)
plt.subplot(2, 2, 4)
plt.bar(x=" ", height=parking_lot.vehicles_turned_away, label='Vehículos rechazados', color='orange')
plt.xlim(xmin=0)
plt.xlabel('')
plt.ylabel('Número de vehículos rechazados')
plt.title('Número de vehículos que no encontraron estacionamiento')
plt.grid(True)

plt.show()