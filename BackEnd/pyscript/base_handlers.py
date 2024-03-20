from pyscript import PyWorker, when

@when('click', '#run-simulation')
def run_simulation(event):
	worker = PyWorker('./application_logic.py')
	# TODO what's going on????