from pyscript import document

def print(event):
	output_div = document.querySelector('#text-output-1')
	if output_div.innerText == '':
		output_div.innerText = 'This is main.py'
	else:
		output_div.innerText = ''