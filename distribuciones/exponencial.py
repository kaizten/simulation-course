import numpy as np
import matplotlib.pyplot as plt

# Parámetros de la distribución exponencial
lambda_param = 1.0  # Tasa de decaimiento (lambda)
n_muestras = 1000  # Número de muestras a generar

# Generación de muestras de la distribución exponencial
# Utilizamos la función exponencial de numpy para generar muestras aleatorias
muestras_exponenciales = np.random.exponential(1/lambda_param, n_muestras)

# Creación de un histograma para visualizar la distribución de las muestras
plt.hist(muestras_exponenciales, bins=50, density=True, alpha=0.7, color='blue', edgecolor='black')
plt.xlabel('Valor de la variable aleatoria')
plt.ylabel('Frecuencia relativa')
plt.title(f'Distribución Exponencial con lambda={lambda_param}')

# Dibujamos la función de densidad teórica para comparar
x = np.linspace(0, np.max(muestras_exponenciales), 1000)
funcion_densidad = lambda_param * np.exp(-lambda_param * x)
plt.plot(x, funcion_densidad, color='red', linewidth=2, label='Función de densidad teórica')
plt.legend()

# Mostrar la gráfica
plt.show()