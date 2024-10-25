import random

# Genera una cantidad de peatones
def generar_peatones(cantidad):
    for i in range(cantidad):
        # Asignamos atributos aleatorios a cada peatón:
        # Asignamos la velocidad
        velocidad = round(random.uniform(0.5,1.5),2)
        # Asignamos la dirección
        direccion = random.choice(["Norte","Sur","Este","Oeste"])
        # Asignamos la posición
        posicion_x = random.randint(0, 100)
        posicion_y = random.randint(0, 100)        
        # Yield crea un peatón con atributos
        yield {
            "id": i + 1,
            "velocidad": velocidad,
            "direccion": direccion,
            "posicion": (posicion_x, posicion_y)
        }

# Usamos el generador
for peaton in generar_peatones(5):
    print(peaton)