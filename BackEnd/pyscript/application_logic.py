from pyscript import window, when
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
	path_gen = f'gen_{rs}/'
	path_sim = f'sim_{rs}/'

	# If no custom data is provided, load results from previous simulation for the specified random state
	if not has_data:
		student_info = np.load(path_gen + 'student_info.npy', allow_pickle=True).item()
		school_info = np.load(path_gen + 'school_info.npy', allow_pickle=True).item()

		student_dict = {
			k: { 'lottery': v[1], 'selection': v[2], 'ranking': v[3], 'list_length': v[4], 'gpa': v[5] }
			for k, v in student_info.items()
		}
		school_dict = {
			k: { 'policy': v[2], 'popularity': v[3], 'likeability': v[4] }
			for k, v in school_info.items()
		}

		bins = dict_to_list(np.load(path_sim + 'bins.npy', allow_pickle=True).item())
		matches = np.load(path_sim + 'matches.npy', allow_pickle=True).item()
		school_outcome = np.load(path_sim + 'school_outcome.npy', allow_pickle=True).item()

	# Otherwise, execute the one-shot pipeline to obtain the input, then run the simulation
	else:
		students, schools, student_info, school_info = \
			oneshot_with_input(rs, student_lottery, student_list, float(student_gpa or -1), student_name=STUDENT_ID, return_list=True)

		student_dict = {
			k: { 'lottery': v[1], 'selection': v[2], 'ranking': v[3], 'list_length': v[4], 'gpa': v[5] }
			for k, v in student_info.items()
		}
		school_dict = {
			k: { 'policy': v[2], 'popularity': v[3], 'likeability': v[4] }
			for k, v in school_info.items()
		}

		bins, matches, school_outcome = gs.run_matching(students, student_info, schools, school_info)
		bins = dict_to_list(bins)

	return student_dict, school_dict, bins, matches, school_outcome

@when('click', '#run-simulation')
def on_click(event):
	res = js.userData.getValues(True).to_py()
	has_data = res.get('hasData')
	lottery = res.get('lottery')
	gpa = res.get('gpa')
	preferences = res.get('preferences')
	random_state = res.get('rs')

	# Load simulation results based on the provided data
	students, schools, bins, matches, school_outcome = load_simulation_results(has_data, lottery, gpa, preferences, rs=random_state)

	window.py_students = to_js(students)
	window.py_schools = to_js(schools)
	window.py_bins = to_js(bins)
	window.py_matches = to_js(matches)
	window.py_school_outcome = to_js(school_outcome)
	window.dispatchEvent(js.pyDoneEvent)