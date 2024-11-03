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
ACCESS_CONTROL_TIME = 1         # Tiempo promedio para pasar el control de acceso (minutos)
EXIT_CONTROL_TIME = 0.5         # Tiempo promedio para pasar el control de salida (minutos)

class ParkingLot:
    def __init__(self, env, total_spots, demand_base_rate):
        self.env = env
        self.spots = simpy.Resource(env, capacity=total_spots)
        self.access_control = simpy.Resource(env, capacity=1)  # Control de acceso con capacidad para un vehículo a la vez
        self.exit_control = simpy.Resource(env, capacity=1)  # Control de salida con capacidad para un vehículo a la vez
        self.total_spots = total_spots
        self.demand_base_rate = demand_base_rate
        self.occupied_spots = 0
        self.revenue = 0
        self.vehicles_turned_away = 0
        self.vehicles_parked = 0
        self.occupancy_history = []
        self.revenue_history = []
        self.vehicles_parked_history = []
        self.access_control_time_history = []
        self.exit_control_time_history = []
        self.spot_occupancy_times = [[] for _ in range(total_spots)]

    def park(self, vehicle_id, duration):
        with self.access_control.request() as access_request:
            # El vehículo llega al control de acceso
            yield access_request
            access_time = random.expovariate(1.0 / ACCESS_CONTROL_TIME)
            yield self.env.timeout(access_time)
            self.access_control_time_history.append(access_time)
            print(f"{self.env.now:.2f}: Vehículo {vehicle_id} pasó el control de acceso.")

        with self.spots.request() as request:
            # Intentamos estacionar el vehículo
            result = yield request | self.env.timeout(SEARCH_TIME)
            if request in result:
                spot_index = self.spots.users.index(request)  # Utilizamos el índice del recurso como referencia de la plaza
                self.occupied_spots += 1
                self.vehicles_parked += 1
                self.record_occupancy()
                self.record_vehicles_parked()
                rate = self.calculate_dynamic_rate()
                cost = rate * duration
                self.revenue += cost
                self.record_revenue()
                self.spot_occupancy_times[spot_index].append(duration)
                print(f"Plaza {spot_index + 1} ocupada por vehículo {vehicle_id}.")
                print(f"{self.env.now:.2f}: Vehículo {vehicle_id} está estacionado. Tarifa: {rate:.2f} €/min, Duración: {duration:.2f} min, Coste total: {cost:.2f} €")
                yield self.env.timeout(duration)
                self.occupied_spots -= 1
                self.record_occupancy()
            else:
                # El vehículo no encuentra lugar para estacionar
                self.vehicles_turned_away += 1
                print(f"{self.env.now:.2f}: Vehículo {vehicle_id} no pudo encontrar estacionamiento y se retiró.")
            
            with self.exit_control.request() as exit_request:
                # El vehículo pasa por el control de salida
                yield exit_request
                exit_time = random.expovariate(1.0 / EXIT_CONTROL_TIME)
                yield self.env.timeout(exit_time)
                self.exit_control_time_history.append(exit_time)
                print(f"{self.env.now:.2f}: Vehículo {vehicle_id} pasó el control de salida y salió del estacionamiento.")

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
        yield env.timeout(ARRIVAL_INTERVAL)
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

plt.subplot(2, 3, 1)
plt.plot(times, occupancies, label='Nivel de ocupación', color='b')
plt.xlabel('Tiempo (minutos)')
plt.ylabel('Número de plazas ocupadas')
plt.title('Nivel de ocupación')
plt.legend()
plt.grid(True)

# Gráfica de la recaudación a lo largo del tiempo
times, revenues = zip(*parking_lot.revenue_history)
plt.subplot(2, 3, 2)
plt.plot(times, revenues, label='Ingresos acumulados', color='g')
plt.xlabel('Tiempo (minutos)')
plt.ylabel('Ingresos (€)')
plt.title('Recaudación')
plt.legend()
plt.grid(True)

# Gráfica del número de vehículos atendidos a lo largo del tiempo
times, vehicles_parked = zip(*parking_lot.vehicles_parked_history)
plt.subplot(2, 3, 3)
plt.plot(times, vehicles_parked, label='Vehículos atendidos', color='r')
plt.xlabel('Tiempo (minutos)')
plt.ylabel('Número de vehículos atendidos')
plt.title('Vehículos atendidos')
plt.legend()
plt.grid(True)

# Gráfica del número de vehículos que no encontraron estacionamiento a lo largo del tiempo
#times, vehicles_turned_away = zip(*parking_lot.vehicles_turned_away_history)
plt.subplot(2, 3, 4)
plt.bar(x=" ", height=parking_lot.vehicles_turned_away, label='Vehículos rechazados', color='orange')
plt.xlim(xmin=0)
plt.xlabel('')
plt.ylabel('Número de vehículos rechazados')
plt.title('Número de vehículos que no encontraron estacionamiento')
plt.grid(True)

# Gráfica comparativa del tiempo promedio en el control de acceso y el control de salida
average_access_time = np.mean(parking_lot.access_control_time_history)
average_exit_time = np.mean(parking_lot.exit_control_time_history)
plt.subplot(2, 3, 5)
plt.bar(['Control de acceso', 'Control de salida'], [average_access_time, average_exit_time], color=['blue', 'red'])
plt.ylabel('Tiempo promedio (minutos)')
plt.title('Tiempo promedio en el control de acceso y salida')
plt.grid(True, axis='y')

# Gráfica del tiempo de ocupación de las plazas de aparcamiento
average_occupancy_times = [np.sum(times) for times in parking_lot.spot_occupancy_times]
plt.subplot(2, 3, 6)
plt.bar(range(TOTAL_SPOTS), average_occupancy_times, color='purple')
plt.xlabel('Número de plazas ocupadas')
plt.ylabel('Tiempo total de ocupación (minutos)')
plt.title('Tiempo total de ocupación de las plazas de aparcamiento')
plt.grid(True, axis='y')

plt.show()