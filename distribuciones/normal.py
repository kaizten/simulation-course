from scipy.stats import norm

mu, sigma = 0, 1
x = np.linspace(-4, 4, 100)
pdf = norm.pdf(x, mu, sigma)

plt.plot(x, pdf)
plt.xlabel('Valor')
plt.ylabel('Densidad')
plt.title('Distribución Normal')
plt.show()