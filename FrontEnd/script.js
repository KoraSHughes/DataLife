function submitForm() {
	form = document.getElementById('search-form')
	console.log('Function call: submitForm()')
}

function checkPlaceholder(selectElement) {
	if (selectElement.value !== '')
		selectElement.classList.remove('select-no-option');
}

function onWindowLoad() {
	console.log('onWindowLoad')

	document.getElementById('btn-about').addEventListener('click', () => alert('About'));
	document.getElementById('btn-how').addEventListener('click', () => alert('How it works'));
	document.getElementById('btn-qa').addEventListener('click', () => alert('Q&A'));

	districtSelect = document.getElementById('input-district-no');
	districtSelect.addEventListener('change', (event) => checkPlaceholder(event.srcElement));

	screenGroupSelect = document.getElementById('input-screen-group');
	screenGroupSelect.addEventListener('change', (event) => checkPlaceholder(event.srcElement));

	searchButton = document.getElementById('search-btn');
	searchButton.addEventListener('click', submitForm);
}

window.onload = onWindowLoad;