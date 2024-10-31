import numpy as np
import matplotlib.pyplot as plt

# Definimos los parámetros de las distribuciones uniformes
params = [
    (0, 1),      # Uniforme estándar entre 0 y 1
    (-2, 2),     # Uniforme entre -2 y 2
    (1, 10),     # Uniforme entre 1 y 10
    (5, 15),     # Uniforme entre 5 y 15
]

# Preparamos los valores de la x para graficar las distribuciones
x = np.linspace(-5, 20, 1000)

# Crear la figura para colocar las subgráficas
plt.figure(figsize=(10, 8))

# Iterar sobre los parámetros de las distribuciones y graficar cada una
for i, (a, b) in enumerate(params):
    # Generar la función de densidad de la distribución uniforme con los parámetros dados
    pdf = np.piecewise(x, [x < a, (x >= a) & (x <= b), x > b], [0, 1/(b-a), 0])
    
    # Crear una subgrafica para cada distribución
    plt.subplot(2, 2, i + 1)
    plt.plot(x, pdf, label=f'Uniforme({a}, {b})', color=f'C{i}')
    plt.fill_between(x, pdf, alpha=0.2, color=f'C{i}')  # sombrear debajo de la curva
    plt.title(f'Distribución Uniforme({a}, {b})')
    plt.xlabel('x')
    plt.ylabel('f(x)')
    plt.grid(True)
    plt.legend()

# Ajustar el espaciado entre las subgráficas
plt.tight_layout()

# Mostrar la gráfica final con todas las distribuciones
plt.show()