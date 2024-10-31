from scipy.stats import geom

p = 0.3
x = np.arange(1, 15)
pmf = geom.pmf(x, p)

plt.stem(x, pmf, use_line_collection=True)
plt.xlabel('Número de ensayos hasta el primer éxito')
plt.ylabel('Probabilidad')
plt.title('Distribución Geométrica')
plt.show()