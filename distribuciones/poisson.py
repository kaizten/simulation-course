import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import poisson

# Parámetros para la distribución de Poisson
lambdas = [1, 4, 10]  # Valores de lambda para diferentes distribuciones
x = np.arange(0, 20, 1)  # Rango de valores para los que se evaluará la distribución

# Crear una figura y ejes para graficar
plt.figure(figsize=(10, 6))

# Graficar la distribución de Poisson para cada valor de lambda
enum_labels = ['Lambda = 1', 'Lambda = 4', 'Lambda = 10']
for lam, label in zip(lambdas, enum_labels):
    # Calcular la distribución de Poisson
    pmf = poisson.pmf(x, lam)
    # Graficar la distribución
    plt.plot(x, pmf, marker='o', linestyle='-', label=label)

# Configuración del gráfico
plt.xlabel('Número de eventos (k)')
plt.ylabel('Probabilidad')
plt.title('Distribuciones de probabilidad de Poisson para diferentes valores de Lambda')
plt.legend()
plt.grid(True)

# Mostrar la figura con todas las distribuciones
plt.show()