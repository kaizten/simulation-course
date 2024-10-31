from scipy.stats import nbinom

r, p = 5, 0.5
x = np.arange(0, 20)
pmf = nbinom.pmf(x, r, p)

plt.stem(x, pmf, use_line_collection=True)
plt.xlabel('Número de ensayos')
plt.ylabel('Probabilidad')
plt.title('Distribución Binomial Negativa')
plt.show()