from scipy.stats import poisson

lam = 3
x = np.arange(0, 15)
pmf = poisson.pmf(x, lam)

plt.stem(x, pmf, use_line_collection=True)
plt.xlabel('Número de eventos')
plt.ylabel('Probabilidad')
plt.title('Distribución de Poisson')
plt.show()