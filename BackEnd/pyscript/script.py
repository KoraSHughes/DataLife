from pyscript import document

def print_alt(event):
	output_div = document.querySelector('#text-output-2')
	if output_div.innerText == '':
		output_div.innerText = 'This is script.py'
	else:
		output_div.innerText = ''