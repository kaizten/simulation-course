import numpy as np
import matplotlib.pyplot as plt

# Definir los parámetros de la distribución normal
mu = 0  # Media
sigma = 1  # Desviación estándar

# Generar una secuencia de números entre -5 y 5 con un paso de 0.01
x = np.arange(-5, 5, 0.01)

# Calcular la distribución normal utilizando la función de densidad de probabilidad
pdf = (1 / (sigma * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - mu) / sigma) ** 2)

# Configurar la figura y los ejes para graficar
plt.figure(figsize=(10, 6))

# Graficar la distribución normal
plt.plot(x, pdf, label='Distribución Normal (media=0, sigma=1)', color='blue')

# Agregar título y etiquetas
plt.title('Distribución Normal')
plt.xlabel('Valor')
plt.ylabel('Densidad de probabilidad')
plt.legend()

# Mostrar la gráfica
plt.grid()
plt.show()