from pyscript import display, document, when
from pyscript.js_modules import script as js

import bisect

import numpy as np
import matplotlib.pyplot as plt

import gale_shapley as gs

STUDENT_ID = 'current_user'

def dict_to_list(dictionary, sort=True) -> list:
	lst = [None] * len(dictionary.keys())
	for i in range(len(lst)):
		val = dictionary.get(i)
		if len(val) == 0:
			val = ['0000']
		lst[i] = sorted(val) if sort else val
	return lst

def hex_to_int(numbers: list[str]) -> np.array:
	numbers_truncated = [num[:8] if len(num) > 8 else num for num in numbers]
	return np.array([int('0x' + num, 0) for num in numbers_truncated])

def load_simulation_results(student_lottery, student_list, range_pct=0, rs=2):
	bins = dict_to_list(np.load(f'sim/bins.npy', allow_pickle=True).item())
	matches = np.load(f'sim/matches.npy', allow_pickle=True).item()

	counts = np.array([len(bin) for bin in bins])
	medians = [bin[len(bin)//2] for bin in bins]
	range_mins = [min(bin) if range_pct == 0 else bin[int(len(bin) * (range_pct/100))] for bin in bins]
	range_maxs = [max(bin) if range_pct == 0 else bin[int(-len(bin) * (range_pct/100))] for bin in bins]

	print(counts)
	return counts, medians, range_mins, range_maxs, matches

	# Load the saved rankings
	students = np.load(f'student_rankings_stage{rs}.npy', allow_pickle=True).item()  # { 'student_XXXXX': ['YYYYYY', ...], ... }
	lottery = dict(np.load('student_demographics.npy', allow_pickle=True)[:, (0, 17)])  # { 'student_XXXXX': '...', ... }
	schools = np.load('school_rankings.npy', allow_pickle=True).item()  # { 'YYYYYY': ['lottery', ...], ... }
	capacities = np.load('school_capacities.npy', allow_pickle=True).item()

	# Add the new student
	for s_id in student_list:
		bisect.insort(schools[s_id], student_lottery)

	students[STUDENT_ID] = student_list
	lottery[STUDENT_ID] = student_lottery

	# Run the algorithm
	return gs.run_simulation(students, lottery, schools, capacities, rs)

def display_plot(event):
	student_lottery = None  # document.getElementById('student-lottery').value
	student_list = None  # document.getElementById('student-list').value.split()

	counts, medians, range_mins, range_maxs, matches = load_simulation_results(student_lottery, student_list, rs=1)
	num_students = np.sum(counts)

	students_unmatched = counts[-1]
	median_unmatched = medians[-1]

	pct_unmatched = document.getElementById('pct-unmatched')
	num_unmatched = document.getElementById('num-unmatched')
	med_unmatched = document.getElementById('med-unmatched')

	pct_unmatched.innerText = f'{100*students_unmatched/num_students:.1f}%'
	num_unmatched.innerText = f'That\'s {students_unmatched:,} students out of {num_students:,}.'
	med_unmatched.innerText = f'Their median lottery number starts with the digits {median_unmatched[:4]}.'

	# school, rank = matches['student_test']
	# customized.innerText = f'Test student matched to school {school}, ranked {rank} on their preference list.'

	fig, ax1 = plt.subplots()
	bins = range(1, 14)

	ax1.bar(bins, 100*counts/num_students, color='orange')
	ax1.set_xticks(bins, list(range(1, 13)) + ['U'])
	ax1.set_xlabel('Position on preference list')
	ax1.set_ylabel('Percentage of students matched')
	ax1.set_facecolor('#ffffff00')

	fig.set_facecolor('#ffffff00')
	display(fig, target='plot', append=False)

@when('click', '#run-simulation-py')
def on_click(event):
	if event.target.id != 'run-simulation':
		print('Event ignored')
		return

	print(js.customData)
	# loader = document.getElementById('simulation-loader')
	# results = document.getElementById('simulation-results')

	# # Hide simulation results (if applicable)
	# # print('Hide results')
	# results.classList.add('hide')
	# results.classList.remove('show')

	# # Display loading animation
	# # print('Show loader')
	# loader.classList.add('show')
	# loader.classList.remove('hide')

	# Schedule the simulation (slow task) on a different thread, so the UI thread is not blocked
	# simulation_task = asyncio.to_thread(display_plot, None)
	# await simulation_task
	display_plot(None)

	# # Hide loading animation
	# # print('Hide loader')
	# loader.classList.add('hide')
	# loader.classList.remove('show')

	# # Display simulation results
	# # print('Show results')
	# results.classList.add('show')
	# results.classList.remove('hide')