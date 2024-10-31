import numpy as np
import matplotlib.pyplot as plt

# Generar datos aleatorios
np.random.seed(42)  # Para reproducibilidad
data = np.random.uniform(0, 10, 30)  # 30 puntos aleatorios entre 0 y 10

# Imprimir el número de datos en la serie original
print(f'Número de datos en la serie original: {len(data)}')

# Número de muestras bootstrap
num_samples = 5

# Crear las muestras bootstrap
bootstrap_samples = [np.random.choice(data, size=len(data), replace=True) for _ in range(num_samples)]

# Imprimir el número de datos en cada serie de bootstrap
for i, sample in enumerate(bootstrap_samples):
    print(f'Número de datos en la muestra Bootstrap {i+1}: {len(sample)}')

# Visualización de los datos originales y las muestras bootstrap
plt.figure(figsize=(10, 6))

# Graficar los datos originales
plt.plot(data, np.zeros_like(data), 'o', label='Datos originales', color='blue', markersize=8)

# Graficar cada muestra de bootstrap
for i, sample in enumerate(bootstrap_samples):
    plt.plot(sample, np.full_like(sample, -0.5 - i), 'o', label=f'Muestra Bootstrap {i+1}', alpha=0.7)

plt.axhline(0, color='black', linestyle='--', linewidth=0.8)
plt.xlabel('Valor de los datos')
plt.ylabel('Muestras Bootstrap')
plt.title('Datos Originales y Muestras de Bootstrap')
plt.legend()
plt.grid(True)
plt.show()