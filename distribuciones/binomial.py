import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import binom

n, p = 10, 0.5
x = np.arange(0, n + 1)
pmf = binom.pmf(x, n, p)

plt.stem(x, pmf, use_line_collection=True)
plt.xlabel('Número de éxitos')
plt.ylabel('Probabilidad')
plt.title('Distribución Binomial')
plt.show()