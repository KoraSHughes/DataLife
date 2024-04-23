from pyscript import document, window, when
from pyscript.js_modules import script as js
from pyodide.ffi import to_js

import numpy as np

import gale_shapley as gs
from oneshot import oneshot, oneshot_with_input

STUDENT_ID = 'current_user'

def dict_to_list(dictionary, sort=True) -> list:
	lst = [None] * len(dictionary.keys())
	for i in range(len(lst)):
		val = dictionary.get(i)
		if len(val) == 0:
			val = ['0000']
		lst[i] = sorted(val) if sort else val
	return lst

def generate_hex_labels():
	labels = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 'a', 'b', 'c', 'd', 'e', 'f']
	ticks = [int('0x' + str(l) + '0000000', 0) for l in labels]
	return ticks, labels

def load_simulation_results(has_data, student_lottery, student_gpa, student_list, rs=1):
	path = f'sim_{rs}/'

	# If no custom data is provided, load results from previous simulation for the specified random state
	if not has_data:
		bins = dict_to_list(np.load(path + 'bins.npy', allow_pickle=True).item())
		matches = np.load(path + 'matches.npy', allow_pickle=True).item()
		seats = np.load(path + 'seats.npy', allow_pickle=True).item()

	# Otherwise, execute the one-shot pipeline to obtain the input, then run the simulation
	else:
		students, schools, student_info, school_info = \
			oneshot_with_input(rs, student_lottery, student_list, student_gpa or -1, student_name=STUDENT_ID)
		bins, matches, seats = gs.run_matching(students, student_info, schools, school_info)
		bins = dict_to_list(bins)

	return bins, matches, seats

@when('click', '#run-simulation')
def on_click(event):
	random_state = 1  # TODO assign dynamically

	res = js.userData.getValues().to_py()
	has_data = res[0]
	lottery = res[1]
	gpa = res[2]
	preferences = res[3]

	loader = document.getElementById('simulation-loader')
	results = document.getElementById('simulation-results')

	# Hide simulation results (if applicable)
	results.classList.add('hide')
	results.classList.remove('show')

	# Display loading animation
	loader.classList.add('show')
	loader.classList.remove('hide')

	# Load simulation results based on the provided data
	bins, matches, seats = load_simulation_results(has_data, lottery, gpa, preferences, rs=random_state)

	window.py_bins = to_js(bins)
	window.py_matches = to_js(matches)
	window.py_seats = to_js(seats)
	window.dispatchEvent(js.pyDoneEvent)

	# Hide loading animation
	loader.classList.add('hide')
	loader.classList.remove('show')

	# Display simulation results
	results.classList.add('show')
	results.classList.remove('hide')