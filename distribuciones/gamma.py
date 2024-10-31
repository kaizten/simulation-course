from scipy.stats import gamma

k, theta = 2, 1
x = np.linspace(0, 10, 100)
pdf = gamma.pdf(x, k, scale=theta)

plt.plot(x, pdf)
plt.xlabel('Valor')
plt.ylabel('Densidad')
plt.title('Distribución Gamma')
plt.show()