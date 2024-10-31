import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import nbinom

# Parámetros de la distribución binomial negativa
r = 5  # Número de éxitos deseados
p = 0.3  # Probabilidad de éxito en cada prueba

# Definir el rango de valores de x
x = np.arange(0, 40)  # Valores posibles de fracasos antes de alcanzar r éxitos

# Calcular la función de masa de probabilidad (PMF) de la distribución binomial negativa
pmf = nbinom.pmf(x, r, p)

# Graficar la PMF
plt.bar(x, pmf, color='blue', alpha=0.7)
plt.xlabel('Número de fracasos (x) antes de r éxitos')
plt.ylabel('Probabilidad')
plt.title('Distribución Binomial Negativa (r = {}, p = {})'.format(r, p))
plt.grid(True, linestyle='--', alpha=0.6)
plt.show()