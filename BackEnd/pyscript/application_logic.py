from pyscript import window, when
from pyscript.js_modules import script as js
from pyodide.ffi import to_js

import numpy as np

import gale_shapley as gs
from oneshot import oneshot, oneshot_with_input

STUDENT_ID = 'current_user'
SEL = { 1: 'random', 2: 'popularity-based' }
RNK = { 0: 'random', 1: 'likeability-based' }
ADM = { 1: 'open', 2:'EdOpt', 3:'screen' }

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
	path_gen = f'gen_{rs}/'
	path_sim = f'sim_{rs}/'

	# If no custom data is provided, load results from previous simulation for the specified random state
	if not has_data:
		student_info = np.load(path_gen + 'student_info.npy', allow_pickle=True).item()
		school_info = np.load(path_gen + 'school_info.npy', allow_pickle=True).item()

		student_dict = {
			k: { 'lottery': v[1], 'selection': SEL.get(v[2]), 'ranking': RNK.get(v[3]), 'list_length': v[4], 'gpa': v[5] }
			for k, v in student_info.items()
		}
		school_dict = {
			k: { 'policy': ADM.get(v[2]), 'popularity': v[3], 'likeability': v[4] }
			for k, v in school_info.items()
		}

		bins = dict_to_list(np.load(path_sim + 'bins.npy', allow_pickle=True).item())
		matches = np.load(path_sim + 'matches.npy', allow_pickle=True).item()
		seats = np.load(path_sim + 'seats.npy', allow_pickle=True).item()

	# Otherwise, execute the one-shot pipeline to obtain the input, then run the simulation
	else:
		students, schools, student_info, school_info = \
			oneshot_with_input(rs, student_lottery, student_list, student_gpa or -1, student_name=STUDENT_ID)

		student_dict = {
			k: { 'lottery': v[1], 'selection': SEL.get(v[2]), 'ranking': RNK.get(v[3]), 'length': v[4], 'gpa': v[5] }
			for k, v in student_info.items()
		}
		school_dict = {
			k: { 'policy': ADM.get(v[2]), 'popularity': v[3], 'likeability': v[4] }
			for k, v in school_info.items()
		}

		bins, matches, seats = gs.run_matching(students, student_info, schools, school_info)
		bins = dict_to_list(bins)

	return student_dict, school_dict, bins, matches, seats

@when('click', '#run-simulation')
def on_click(event):
	random_state = 1  # TODO assign dynamically

	res = js.userData.getValues().to_py()
	has_data = res[0]
	lottery = res[1]
	gpa = res[2]
	preferences = res[3]

	# Load simulation results based on the provided data
	students, schools, bins, matches, seats = load_simulation_results(has_data, lottery, gpa, preferences, rs=random_state)

	window.py_students = to_js(students)
	window.py_schools = to_js(schools)
	window.py_bins = to_js(bins)
	window.py_matches = to_js(matches)
	window.py_seats = to_js(seats)
	window.dispatchEvent(js.pyDoneEvent)