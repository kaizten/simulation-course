import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
import seaborn as sns

# Generate data for a normal distribution with 1000 elements
data = np.random.normal(loc=0, scale=1, size=1000)

# Create a figure with multiple subplots
fig, axs = plt.subplots(2, 2, figsize=(15, 12))

# Create Histogram Plot
axs[0, 0].hist(data, bins=30, edgecolor='black', alpha=0.7)
axs[0, 0].set_title('Histogram')
axs[0, 0].set_xlabel('Value')
axs[0, 0].set_ylabel('Frequency')
axs[0, 0].grid(axis='y', linestyle='--')

# Create Density Plot
sns.kdeplot(data, fill=True, ax=axs[0, 1])
axs[0, 1].set_title('Density plot')
axs[0, 1].set_xlabel('Value')
axs[0, 1].set_ylabel('Density')
axs[0, 1].grid(axis='y', linestyle='--')

# Create Box Plot
axs[1, 0].boxplot(data, vert=False)
axs[1, 0].set_title('Box plot')
axs[1, 0].set_xlabel('Value')
axs[1, 0].grid(axis='x', linestyle='--')

# Create Q-Q Plot
stats.probplot(data, dist="norm", plot=axs[1, 1])
axs[1, 1].set_title('Q-Q plot')
axs[1, 1].grid(axis='both', linestyle='--')

# Adjust layout and show the figure
plt.tight_layout()
plt.show()