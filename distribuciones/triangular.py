import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import triang

# Definimos los parámetros de la distribución triangular
c = 0.5  # Parámetro de sesgo de la distribución (modo relativo)
loc = 0  # Inicio de la distribución
scale = 10  # Longitud del intervalo

# Generamos valores para la distribución triangular
x = np.linspace(loc, loc + scale, 1000)

# Calculamos la función de densidad de probabilidad (PDF) para la distribución triangular
y = triang.pdf(x, c, loc, scale)

# Creamos la figura y los ejes para la gráfica
plt.figure(figsize=(10, 6))

# Graficamos la distribución triangular
plt.plot(x, y, label='Distribución Triangular', color='b')

# Añadimos título y etiquetas a los ejes
plt.title('Distribución Triangular')
plt.xlabel('Valores')
plt.ylabel('Densidad de probabilidad')

# Añadimos una leyenda
plt.legend()

# Mostramos la gráfica
plt.grid()
plt.show()