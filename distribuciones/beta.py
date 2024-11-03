import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import beta

# Parámetros de la distribución Beta
ALPHA = 2               # Parámetro alpha
BETA = 5                # Parámetro beta
NUMERO_PUNTOS = 1000    # Número de puntos para evaluar la distribución

# Creamos una secuencia de valores x entre 0 y 1, que son los posibles valores para la distribución Beta
x = np.linspace(0, 1, NUMERO_PUNTOS)

# Calculamos la función de densidad de probabilidad para cada valor de x
pdf_values = beta.pdf(x, ALPHA, BETA)

# Graficamos la función de densidad de probabilidad
plt.figure(figsize=(10, 6))
plt.plot(x, pdf_values, label=f'Beta(\u03B1={ALPHA}, \u03B2={BETA})', color='blue')
plt.xlabel('x')
plt.ylabel('Densidad de probabilidad')
plt.title('Distribución Beta')
plt.legend()
plt.grid()
plt.show()