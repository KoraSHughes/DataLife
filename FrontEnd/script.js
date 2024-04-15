const lotteryNumbers = [
	'3a4bdc7f-8e91-0c2a-6f5d-1b9e6a38d047',
	'0c68f153-12e5-3e7f-2234-6517592f1763',
	'9568a214-f388-402d-4145-45e8138643e',
	'7833cfd2-93c5-b281-407b-c3b96160ea3f',
	'd8b0965e-9e71-c53b-f849-953a82e164d1',
	'211cee28-3c31-bf81-4a16-6f39344b9f97',
	'cb6e6546-cfd6-0134-d85a-5e8041f8b06c',
	'4f6bd3ef-2929-d7c0-8215-c4065d0109b4'
];
let point = 0;

const schoolNames = [
	'John F. Kennedy HS (1)',
	'Stuyvesant HS (2)',
	'Marie Curie Scientific HS (3)',
	'Staten Island HS for Ferry Captains (4)'
];

let customData = false;

function updateLotteryNumber() {
	let el = document.getElementById('lottery-example');
	el.innerText = lotteryNumbers[point];
	if (point < lotteryNumbers.length - 1)
		point++;
	else
		point = 0;
}

function displayAddButton(event) {
	let addButton = document.getElementById('add-choice');
	let choices = document.getElementById('choices');
	let lastChoice = choices.children[choices.children.length - 2];

	if (lastChoice.value !== '' && choices.childElementCount < 15)
		addButton.classList.remove('hide');
}

function addSchoolChoice(event) {
	let addButton = document.getElementById('add-choice');
	let choices = document.getElementById('choices');
	let numChoices = choices.childElementCount - 3;

	let newChoice = document.createElement('div');
	newChoice.id = 'choice-' + String(numChoices + 1);
	newChoice.classList.add('btn-secondary', 'input');

	let icon = document.createElement('span');
	icon.classList.add('material-symbols-outlined');
	icon.innerHTML = 'search';
	icon.addEventListener('click', () => input.focus());
	newChoice.appendChild(icon);

	let input = document.createElement('input');
	input.name = 'choice-' + String(numChoices + 1);
	input.placeholder = 'Choice ' + String(numChoices + 1);
	input.size = 18;
	input.setAttribute('list', 'school-list');
	newChoice.appendChild(input);

	newChoice.addEventListener('change', displayAddButton);

	choices.insertBefore(newChoice, addButton);
	addButton.classList.add('hide');
}

window.addEventListener('load', () => {
	updateLotteryNumber();
	setInterval(updateLotteryNumber, 3000);

	const addDataBtn = document.getElementById('btn-add-data');
	const removeDataBtn = document.getElementById('btn-remove-data');
	addDataBtn.addEventListener('click', () => {
		document.getElementById('choices').classList.remove('hide')
		addDataBtn.classList.add('hide');
		removeDataBtn.classList.remove('hide');
		customData = true;
	});
	removeDataBtn.addEventListener('click', () => {
		document.getElementById('choices').classList.add('hide')
		removeDataBtn.classList.add('hide');
		addDataBtn.classList.remove('hide');
		customData = false;
	});

	document.getElementById('run-simulation').addEventListener('click', () => {
		console.log('Click captured');
	});

	document.getElementById('add-choice').addEventListener('click', addSchoolChoice);
	document.getElementById('choice-1').addEventListener('change', displayAddButton);

	const schoolList = document.getElementById('school-list');
	schoolNames.forEach(opt => {
		let option = document.createElement('option');
		option.value = opt
		schoolList.appendChild(option);
	});
});

export { customData };