import simpy
import random
import numpy as np

# Parámetros:
CAPACIDAD_APARCAMIENTO = 50     # Número máximo de plazas disponibles
TASA_LLEGADA_VEHICULOS = 1/2    # Tasa de llegada de vehículos (1 cada 2 minutos)
DURACION_ESTANCIA_MIN = 10      # Estancia mínima en minutos
DURACION_ESTANCIA_MAX = 60      # Estancia máxima en minutos
TIEMPO_BUSQUEDA_LIMITE = 15     # Máximo tiempo de búsqueda antes de que el conductor se retire (minutos)
TARIFA_BASE = 2                 # Tarifa base de aparcamiento en unidades monetarias
FACTOR_DEMANDA = 0.05           # Factor de incremento de la tarifa por ocupación alta

# Estadísticas
tiempos_busqueda = []
vehiculos_retirados = 0
ingresos_totales = 0
total_vehiculos = 0

# Función para calcular la tarifa según la demanda
def calcular_tarifa(ocupacion):
    if ocupacion > 0.8:  # Si la ocupación es mayor al 80%, incrementa la tarifa
        return TARIFA_BASE + (ocupacion - 0.8) / 0.2 * TARIFA_BASE * FACTOR_DEMANDA
    else:
        return TARIFA_BASE

# Función de búsqueda de aparcamiento
def buscar_aparcamiento(env, aparcamiento, vehiculo_id):
    global tiempos_busqueda, vehiculos_retirados, ingresos_totales, total_vehiculos

    llegada = env.now  # Tiempo de llegada
    tiempo_busqueda = 0
    total_vehiculos += 1
    
    # Intento de encontrar plaza de aparcamiento
    with aparcamiento.request() as req:
        resultado = yield req | env.timeout(TIEMPO_BUSQUEDA_LIMITE)  # Máximo tiempo de búsqueda

        if req in resultado:  # Si encuentra plaza
            tiempo_busqueda = env.now - llegada
            tiempos_busqueda.append(tiempo_busqueda)
            
            # Calculamos la ocupación y ajustamos la tarifa
            ocupacion_actual = aparcamiento.count / aparcamiento.capacity
            tarifa_actual = calcular_tarifa(ocupacion_actual)
            ingresos_totales += tarifa_actual

            # El vehículo ocupa la plaza por un tiempo aleatorio
            duracion_estancia = random.randint(DURACION_ESTANCIA_MIN, DURACION_ESTANCIA_MAX)
            yield env.timeout(duracion_estancia)

            # El vehículo libera la plaza después de su estancia
        else:
            # Si no encuentra plaza en el tiempo límite, se retira
            vehiculos_retirados += 1

# Proceso principal que genera vehículos
def generar_vehiculos(env, aparcamiento):
    vehiculo_id = 0
    while True:
        yield env.timeout(random.expovariate(1 / TASA_LLEGADA_VEHICULOS))
        env.process(buscar_aparcamiento(env, aparcamiento, vehiculo_id))
        vehiculo_id += 1

# Simulación
def run_simulacion():
    global tiempos_busqueda, vehiculos_retirados, ingresos_totales, total_vehiculos
    tiempos_busqueda = []
    vehiculos_retirados = 0
    ingresos_totales = 0
    total_vehiculos = 0

    # Crear el entorno de simulación y el recurso aparcamiento
    env = simpy.Environment()
    aparcamiento = simpy.Resource(env, capacity=CAPACIDAD_APARCAMIENTO)
    
    # Iniciar la generación de vehículos
    env.process(generar_vehiculos(env, aparcamiento))
    
    # Ejecutar la simulación por un día (1440 minutos)
    env.run(until=1440)
    
    # Resultados de la simulación
    if tiempos_busqueda:
        tiempo_promedio_busqueda = np.mean(tiempos_busqueda)
    else:
        tiempo_promedio_busqueda = 0
    
    tasa_ocupacion = aparcamiento.count / aparcamiento.capacity
    tasa_abandono = (vehiculos_retirados / total_vehiculos) * 100
    ingresos_promedio = ingresos_totales / total_vehiculos

    print(f"Tiempo promedio de búsqueda de aparcamiento: {tiempo_promedio_busqueda:.2f} minutos")
    print(f"Tasa de ocupación del aparcamiento: {tasa_ocupacion * 100:.2f}%")
    print(f"Porcentaje de vehículos que abandonan la búsqueda: {tasa_abandono:.2f}%")
    print(f"Ingresos promedio por vehículo: {ingresos_promedio:.2f} unidades monetarias")
    print(f"Vehículos que se retiraron por falta de plazas: {vehiculos_retirados}")

# Ejecutar la simulación
run_simulacion()