from pyscript import display, document, when

import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt

from gale_shapley import run_simulation

@when('click', '#run-simulation')
def display_plot(event):
	counts = np.load('bin_counts_stage1.npy')
	averages = np.load('bin_averages_stage1.npy')
	cumulative_counts = np.cumsum(counts[:-1])
	num_students = np.sum(counts)

	averages_int = np.array([int('0x' + avg, 0) for avg in averages])
	fractions = np.zeros((12, 12))
	for i in range(12):
		fractions[i] += (counts[i] / cumulative_counts) * np.hstack((np.zeros(i), np.ones(12 - i))) * averages_int[i]
	cumulative_averages = fractions.sum(axis=0)

	students_top_choice = counts[0]
	students_top_five_choice = cumulative_counts[4]
	students_unmatched = counts[-1]

	avg_top_choice = averages_int[0]
	avg_top_five_choice = int(cumulative_averages[4])
	avg_unmatched = averages_int[-1]

	results = document.getElementById('simulation-results')

	top_choice = document.getElementById('top-choice')
	top_five_choice = document.getElementById('top-five-choice')
	unmatched = document.getElementById('unmatched')

	top_choice.innerText = (
		f'{100*students_top_choice/num_students:.1f}% of the students were matched to their top choice '
		f'({students_top_choice:,} out of {num_students:,}). Their average lottery number starts with the digits '
		f'{avg_top_choice:x}.'
	)

	top_five_choice.innerText = (
		f'{100*students_top_five_choice/num_students:.1f}% of the students were matched to one of their top five choices '
		f'({students_top_five_choice:,} out of {num_students:,}). Their average lottery number starts with the digits '
		f'{avg_top_five_choice:x}.'
	)

	unmatched.innerText = (
		f'{100*students_unmatched/num_students:.1f}% of the students were unmatched '
		f'({students_unmatched:,} out of {num_students:,}). Their average lottery number starts with the digits '
		f'{avg_unmatched:x}.'
	)

	fig, ax1 = plt.subplots()
	bins = range(1, 14)

	ax1.bar(bins, 100*counts/num_students, color='orange')
	ax1.set_xticks(bins, list(range(1, 13)) + ['U'])
	ax1.set_xlabel('Position on preference list')
	ax1.set_ylabel('Percentage of students matched')

	ax2 = ax1.twinx()
	ax2.plot(bins, averages_int, color='steelblue', marker='x', linewidth=0.5)
	bottom, top = ax2.get_ylim()
	labels = [4, 5, 6, 7, 8, 9, 'a', 'b', 'c', 'd', 'e', 'f']
	label_nums = ['0x' + str(i) + '0000000' for i in labels]
	ticks = [int(l, 0) for l in label_nums]
	ax2.set_yticks(ticks, labels)
	ax2.set_ylim(bottom, top)
	ax2.set_ylabel('Average lottery number (first digit)')

	display(fig, target='plot', append=False)

	results.classList.add('show')
	results.classList.remove('hide')