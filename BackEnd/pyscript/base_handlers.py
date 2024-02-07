
from js import alert, console
from pyscript import document, when

@when('click', '#btn-about')
def about(event):
	alert('About')

@when('click', '#btn-how')
def about(event):
	alert('How it works')

@when('click', '#btn-qa')
def about(event):
	alert('Q&A')

@when('change', '#input-district-no')
@when('change', '#input-screen-group')
def check_placeholder(event):
	dropdown = event.srcElement
	if (dropdown.value != ''):
		dropdown.classList.remove('select-no-option')

@when('click', '#search-btn')
def submit_form(event):
	form = document.getElementById('search-form')
	console.log('Function call: submitForm()')
	console.log(form)