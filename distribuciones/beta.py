import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import beta

alpha, beta_param = 2, 5
x = np.linspace(0, 1, 100)
pdf = beta.pdf(x, alpha, beta_param)

plt.plot(x, pdf)
plt.xlabel('Valor')
plt.ylabel('Densidad')
plt.title('Distribución Beta')
plt.show()