from scipy.stats import expon

lam = 1
x = np.linspace(0, 5, 100)
pdf = expon.pdf(x, scale=1/lam)

plt.plot(x, pdf)
plt.xlabel('Valor')
plt.ylabel('Densidad')
plt.title('Distribución Exponencial')
plt.show()