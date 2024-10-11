import simpy
import random
import statistics

# Parámetros de la simulación
TIEMPO_SIMULACION = 120  # Duración de la simulación (minutos)
TIEMPO_CRUZAR_SEMAFORO = 10  # Tiempo promedio para cruzar un semáforo (segundos)
PROBABILIDAD_EMBOTELLAMIENTO = 0.2  # Probabilidad de embotellamiento en puntos críticos

# Definimos las franjas horarias
HORARIO_PICO = [(7, 9), (17, 19)]  # Horas de tráfico intenso
FLUJO_PICO = 10  # Ciclistas por minuto en horario pico
FLUJO_NORMAL = 2  # Ciclistas por minuto en horario normal

# Lista para registrar tiempos de viaje
tiempos_viaje = []

def llegada_ciclistas(env, semaforos, embotellamientos, hora_pico):
    """
    Genera ciclistas de acuerdo a la franja horaria.
    """
    while True:
        if any(h[0] <= env.now // 60 < h[1] for h in HORARIO_PICO):
            # Más ciclistas en horas pico
            tiempo_entre_ciclistas = random.expovariate(FLUJO_PICO / 60)
        else:
            # Flujo normal fuera de horas pico
            tiempo_entre_ciclistas = random.expovariate(FLUJO_NORMAL / 60)
        
        yield env.timeout(tiempo_entre_ciclistas)
        env.process(ciclista(env, semaforos, embotellamientos))

def ciclista(env, semaforos, embotellamientos):
    """
    Simula el trayecto de un ciclista por la ciclovía.
    """
    hora_inicio = env.now
    print(f"Ciclista comienza su trayecto a los {hora_inicio:.2f} segundos")

    # Ciclista se enfrenta a varios semáforos en su trayecto
    for semaforo in semaforos:
        with semaforo.request() as req:
            yield req
            tiempo_espera_semaforo = random.expovariate(1.0 / TIEMPO_CRUZAR_SEMAFORO)
            print(f"Ciclista espera {tiempo_espera_semaforo:.2f} segundos en el semáforo")
            yield env.timeout(tiempo_espera_semaforo)
    
    # Posibilidad de embotellamiento en puntos críticos
    for punto_critico in embotellamientos:
        if random.uniform(0, 1) < PROBABILIDAD_EMBOTELLAMIENTO:
            tiempo_espera_embotellamiento = random.expovariate(30)  # Retardo aleatorio
            print(f"Embudo en punto crítico, ciclista espera {tiempo_espera_embotellamiento:.2f} segundos")
            yield env.timeout(tiempo_espera_embotellamiento)

    hora_fin = env.now
    tiempo_total = hora_fin - hora_inicio
    tiempos_viaje.append(tiempo_total)
    print(f"Ciclista termina su trayecto en {tiempo_total:.2f} segundos")

def crear_semaforos(env, num_semaforos):
    """
    Crea los semáforos por los que pasan los ciclistas.
    """
    return [simpy.Resource(env, capacity=1) for _ in range(num_semaforos)]

def crear_puntos_criticos(env, num_puntos):
    """
    Crea los puntos críticos donde pueden ocurrir embotellamientos.
    """
    return [simpy.Resource(env, capacity=1) for _ in range(num_puntos)]

def ejecutar_simulacion():
    """
    Configura y ejecuta la simulación.
    """
    # Crear el entorno de SimPy
    env = simpy.Environment()

    # Crear semáforos y puntos críticos
    semaforos = crear_semaforos(env, num_semaforos=3)  # Tres semáforos en la ruta
    embotellamientos = crear_puntos_criticos(env, num_puntos=2)  # Dos puntos críticos

    # Iniciar la generación de ciclistas
    env.process(llegada_ciclistas(env, semaforos, embotellamientos, HORARIO_PICO))

    # Ejecutar la simulación durante TIEMPO_SIMULACION minutos
    env.run(until=TIEMPO_SIMULACION * 60)  # Convertir minutos a segundos

    # Resultados de la simulación
    if tiempos_viaje:
        print(f"\nPromedio de tiempo de viaje: {statistics.mean(tiempos_viaje):.2f} segundos")
        print(f"Tiempo máximo de viaje: {max(tiempos_viaje):.2f} segundos")
        print(f"Tiempo mínimo de viaje: {min(tiempos_viaje):.2f} segundos")
    else:
        print("No hubo ciclistas en la simulación")

# Ejecutar la simulación
if __name__ == '__main__':
    ejecutar_simulacion()
