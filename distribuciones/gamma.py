import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gamma

# Parámetros para la distribución gamma
alpha_values = [1, 2, 3, 5]  # Parámetros de forma (k) para la distribución gamma
beta = 1  # Parámetro de escala (θ), asumido constante para todos los casos

# Generar los valores del eje X
x = np.linspace(0, 20, 1000)

# Crear la figura y los ejes para la gráfica
plt.figure(figsize=(10, 6))

# Graficar la distribución gamma para diferentes valores de alpha
for alpha in alpha_values:
    # Calcular la función de densidad de probabilidad para cada valor de alpha
    y = gamma.pdf(x, a=alpha, scale=beta)
    
    # Graficar la densidad de probabilidad
    plt.plot(x, y, label=f'Gamma (alpha={alpha}, beta={beta})')

# Añadir título y etiquetas
plt.title('Distribuciones Gamma con diferentes valores de alpha')
plt.xlabel('x')
plt.ylabel('Densidad de probabilidad')
plt.legend()

# Mostrar la gráfica
plt.grid()
plt.show()