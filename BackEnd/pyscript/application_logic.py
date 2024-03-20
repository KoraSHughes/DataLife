from pyscript import display, document, when

import bisect

import numpy as np
import matplotlib.pyplot as plt

import gale_shapley as gs

def load_simulation_results(student_id, student_lottery, student_list, stage=2):
	counts = np.load(f'bin_counts_stage{stage}.npy')
	averages = np.load(f'bin_averages_stage{stage}.npy')
	ranges = np.load(f'bin_ranges_stage{stage}.npy')
	matches = np.load(f'matches_stage{stage}.npy', allow_pickle=True).item()
	return counts, averages, ranges, matches

	# Load the saved rankings
	students = np.load(f'student_rankings_stage{stage}.npy', allow_pickle=True).item()  # { 'student_XXXXX': ['YYYYYY', ...], ... }
	lottery = np.load('student_lottery_nums.npy', allow_pickle=True).item()  # { 'student_XXXXX': '...', ... }
	schools = np.load('school_rankings.npy', allow_pickle=True).item()  # { 'YYYYYY': ['lottery', ...], ... }
	capacities = np.load('school_capacities.npy', allow_pickle=True).item()

	# Add the new student
	for s_id in student_list:
		bisect.insort(schools[s_id], student_lottery)

	students[student_id] = student_list
	lottery[student_id] = student_lottery

	# Run the algorithm
	return gs.run_simulation(students, lottery, schools, capacities, stage)

@when('click', '#run-simulation')
def display_plot(event):
	student_id = None  # document.getElementById('student-id').value
	student_lottery = None  # document.getElementById('student-lottery').value
	student_list = None  # document.getElementById('student-list').value.split()

	# TODO call this asynchronously? maybe???
	counts, averages, ranges, matches = load_simulation_results(student_id, student_lottery, student_list, stage=1)
	counts = np.array(counts)
	averages = np.array(averages)
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
	# customized = document.getElementById('customized')

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

	# school, rank = matches['student_test']
	# customized.innerText = f'Test student matched to school {school}, ranked {rank} on their preference list.'

	fig, ax1 = plt.subplots()
	bins = range(1, 14)

	ax1.bar(bins, 100*counts/num_students, color='orange')
	ax1.set_xticks(bins, list(range(1, 13)) + ['U'])
	ax1.set_xlabel('Position on preference list')
	ax1.set_ylabel('Percentage of students matched')
	ax1.set_facecolor('#ffffff00')

	ax2 = ax1.twinx()
	ax2.plot(bins, averages_int, color='#37447e', marker='x', linewidth=0.5)
	bottom, top = ax2.get_ylim()
	labels = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 'a', 'b', 'c', 'd', 'e', 'f']
	label_nums = ['0x' + str(i) + '0000000' for i in labels]
	ticks = [int(l, 0) for l in label_nums]
	ax2.set_yticks(ticks, labels)
	ax2.set_ylim(bottom, top)
	ax2.set_ylabel('Average lottery number (first digit)')

	fig.set_facecolor('#ffffff00')

	display(fig, target='plot', append=False)

	results.classList.add('show')
	results.classList.remove('hide')