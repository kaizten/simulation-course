from scipy.stats import triang

a, b, c = 0, 10, 5
c_scaled = (c - a) / (b - a)
x = np.linspace(a, b, 100)
pdf = triang.pdf(x, c_scaled, loc=a, scale=b-a)

plt.plot(x, pdf)
plt.xlabel('Valor')
plt.ylabel('Densidad')
plt.title('Distribución Triangular')
plt.show()