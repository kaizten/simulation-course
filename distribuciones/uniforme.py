from scipy.stats import uniform

a, b = 0, 10
x = np.linspace(a, b, 100)
pdf = uniform.pdf(x, a, b-a)

plt.plot(x, pdf)
plt.xlabel('Valor')
plt.ylabel('Densidad')
plt.title('Distribución Uniforme')
plt.show()