import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import geom

# Parámetros de la distribución geométrica
p_values = [0.2, 0.5, 0.8]  # Probabilidades de éxito para diferentes distribuciones
x = np.arange(1, 20)  # Valores posibles de la variable aleatoria geométrica (comienzan en 1)

# Crear una figura con subgráficas para las distribuciones
plt.figure(figsize=(10, 6))

for i, p in enumerate(p_values):
    # Calcular la probabilidad geométrica para cada valor de x y cada p
    pmf_values = geom.pmf(x, p)
    
    # Añadir cada distribución a la misma figura
    plt.plot(x, pmf_values, marker='o', linestyle='-', label=f'p = {p}')

# Añadir título y etiquetas
plt.title('Distribuciones Geométricas con Diferentes Valores de p')
plt.xlabel('Número de Intentos')
plt.ylabel('Probabilidad (PMF)')
plt.legend()
plt.grid()

# Mostrar la gráfica
plt.show()