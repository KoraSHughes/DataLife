from pyscript import display, document, when

import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt

@when('click', '#btn-plot')
def display_plot(event):
	num_points = 100
	gen = np.random.default_rng(seed=0)
	x = gen.random(num_points)
	low, high = 0, 1
	sigma = 0.2
	y = []
	for i, mu in enumerate(x):
		if i % 8 == 0:
			sigma = 1
		y_new = stats.truncnorm((low-mu)/sigma, (high-mu)/sigma, loc=mu, scale=sigma).rvs(1)
		y.append(y_new)
		if i % 12 == 0:
			sigma = 0.1
	y = np.array(y)
	y = y.reshape(y.shape[0],)

	fig, ax = plt.subplots()
	ax.set_aspect('equal')
	ax.plot(np.linspace(0, 1, 10000), np.linspace(0, 1, 10000), color='grey', linewidth=0.5)
	ax.scatter(x, y, c=y-x, cmap='RdYlGn')
	ax.set_xlabel('Overall acceptance rate')
	ax.set_ylabel('"Personalized" acceptance likelihood')

	plot = document.getElementById('plot')
	plot.classList.add('show')
	plot.classList.remove('hide')
	display(fig, target='plot', append=False)