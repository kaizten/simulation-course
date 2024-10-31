# Importar las bibliotecas necesarias
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import binom

# Definir los parámetros de la distribución binomial
n = 10  # Número de ensayos
p = 0.5  # Probabilidad de éxito en cada ensayo

# Crear una lista de valores posibles para el número de éxitos
x = np.arange(0, n + 1)

# Calcular la función de masa de probabilidad (PMF, por sus siglas en inglés) para cada valor posible
pmf = binom.pmf(x, n, p)

# Graficar la función de masa de probabilidad
plt.figure(figsize=(10, 6))
plt.bar(x, pmf, color='skyblue')
plt.xlabel('Número de éxitos')
plt.ylabel('Probabilidad')
plt.title(f'Distribución Binomial (n={n}, p={p})')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.show()

# Calcular algunas métricas estadísticas de la distribución
media = binom.mean(n, p)  # Media de la distribución
varianza = binom.var(n, p)  # Varianza de la distribución

# Mostrar la media y la varianza
print(f"Media de la distribución binomial: {media}")
print(f"Varianza de la distribución binomial: {varianza}")