import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import beta

# Definimos los parámetros de la distribución Beta
# alpha y beta son los parámetros que determinan la forma de la distribución
alpha, beta_param = 2, 5

# Creamos una secuencia de valores x entre 0 y 1, que son los posibles valores para la distribución Beta
x = np.linspace(0, 1, 1000)

# Calculamos la función de densidad de probabilidad para cada valor de x
pdf_values = beta.pdf(x, alpha, beta_param)

# Graficamos la función de densidad de probabilidad
plt.figure(figsize=(10, 6))
plt.plot(x, pdf_values, label=f'Beta(\u03B1={alpha}, \u03B2={beta_param})', color='blue')
plt.xlabel('x')
plt.ylabel('Densidad de probabilidad')
plt.title('Distribución Beta')
plt.legend()
plt.grid()
plt.show()