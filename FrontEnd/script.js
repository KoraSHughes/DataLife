import * as d3 from 'https://cdn.jsdelivr.net/npm/d3@7/+esm';

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

const schoolNames = [
	'John F. Kennedy HS (1)',
	'Stuyvesant HS (2)',
	'Marie Curie Scientific HS (3)',
	'Staten Island HS for Ferry Captains (4)'
];

const removeIcon = 'cancel';

const pyDoneEvent = new Event('py-backend-done');
let userData = null;

class LotteryNumberExamples {
	constructor() {
		this.el = document.getElementById('lottery-example');
		this.point = 0;
	}

	updateLotteryNumber() {
		this.el.innerText = lotteryNumbers[this.point];
		if (this.point < lotteryNumbers.length - 1)
			this.point++;
		else
			this.point = 0;
	}

	iterate() {
		const self = this;
		setInterval(self.updateLotteryNumber.bind(self), 3000);
	}
}

class SchoolChoice {
	constructor(num) {
		this.num = num;

		this.el = document.createElement('li');
		this.el.id = 'choice-' + num;
		this.el.classList.add('flex-row', 'input');
		this.el.draggable = true;

		const icon_drag = document.createElement('span');
		icon_drag.classList.add('material-symbols-outlined', 'draggable');
		icon_drag.innerHTML = 'drag_indicator';
		this.el.appendChild(icon_drag);

		const input = document.createElement('input');
		input.name = 'choice-' + num;
		input.placeholder = 'Select a school';
		input.size = 40;
		input.setAttribute('list', 'school-list');
		this.el.appendChild(input);

		const icon_del = document.createElement('span');
		icon_del.classList.add('material-symbols-outlined', 'clickable');
		icon_del.innerHTML = removeIcon;
		icon_del.addEventListener('click', this.removeSchoolChoice);
		this.el.appendChild(icon_del);
	}

	getElement() {
		return this.el;
	}
}

class SchoolList {
	constructor() {
		this.el = document.getElementById('choices').children[0];
		this.addChoiceItem = document.getElementById('add-choice-li');
		this.addChoiceBtn = document.getElementById('add-choice');

		this.attachDeleteEventListener();
		this.attachButtonEventListener();

		this.dragged = null;
		this.attachInputEventListeners();
	}

	attachDeleteEventListener() {
		const self = this;

		this.el.addEventListener('click', e => {
			if (e.target.innerText !== removeIcon)
				return;

			self.el.removeChild(e.target.parentNode);

			let hasEmpty = false;
			for (let item of self.el.children) {
				if (item.children[0].id !== 'add-choice')
					hasEmpty = hasEmpty || (item.children[1].value === '');
			}

			if (!hasEmpty)
				self.addChoiceBtn.classList.remove('disabled');
		});
	}

	attachButtonEventListener() {
		const self = this;

		this.addChoiceBtn.addEventListener('click', () => {
			if (self.addChoiceBtn.classList.contains('disabled'))
				return;

			const numChoices = self.el.childElementCount - 1;
			const newChoice = new SchoolChoice(numChoices + 1).getElement();

			self.el.insertBefore(newChoice, self.addChoiceItem);
			self.addChoiceBtn.classList.add('disabled');

			self.attachInputEventListeners();
		});
	}

	attachInputEventListeners() {
		const self = this;
		let dragged = null;

		for (let item of this.el.children) {
			if (item.children[0].id !== 'add-choice') {

				item.addEventListener('change', () => {
					const numChoices = self.el.childElementCount - 1;
					if (numChoices >= 12)
						return;

					let hasEmpty = false;
					for (let item of self.el.children) {
						if (item.children[0].id !== 'add-choice')
							hasEmpty = hasEmpty || (item.children[1].value === '');
					}

					if (!hasEmpty)
						self.addChoiceBtn.classList.remove('disabled');
				});

				item.addEventListener('dragstart', e => dragged = e.target);
				item.addEventListener('dragover', e => e.preventDefault());

				item.addEventListener('drop', e => {
					let rows = Array.from(self.el.children);
					let destination = e.target.closest('li');

					if (dragged == null || destination == null)
						return;

					if (rows.indexOf(destination) > rows.indexOf(dragged))
						destination.after(dragged);
					else
						destination.before(dragged);
				});
			}
		}
	}

	getValues() {
		let res = [];
		for (let item of this.el.children) {
			if (item.children[0].id !== 'add-choice') {
				let val = item.children[1].value;
				if (val !== '')
					res.push(val);
			}
		}
		return (res.length === 0 ? null : res);
	}
}

class UserData {
	constructor() {
		this.datalist = document.getElementById('school-list');
		this.addDataBtn = document.getElementById('btn-add-data');
		this.removeDataBtn = document.getElementById('btn-remove-data');
		this.customData = document.getElementById('custom-data');

		this.lotteryInput = document.getElementById('custom-lottery-input');
		this.gpaInput = document.getElementById('custom-gpa-input');

		this.choicesList = new SchoolList();

		this.hasCustomData = false;

		this.addDataBtn.addEventListener('click', () => {
			this.customData.classList.remove('hide');
			this.addDataBtn.classList.add('hide');
			this.removeDataBtn.classList.remove('hide');
			this.hasCustomData = true;
		});

		this.removeDataBtn.addEventListener('click', () => {
			this.customData.classList.add('hide');
			this.removeDataBtn.classList.add('hide');
			this.addDataBtn.classList.remove('hide');
			this.hasCustomData = false;
		});

		this.initializeDatalist();
	}

	initializeDatalist() {
		schoolNames.forEach(opt => {
			let option = document.createElement('option');
			option.value = opt
			this.datalist.appendChild(option);
		});
	}

	getValues() {
		if (!this.hasCustomData)
			return [false, null, null, 0, null];

		const userLottery = this.lotteryInput.value === '' ? null : this.lotteryInput.value;
		const userGPA = this.gpaInput.value === '' ? null : this.gpaInput.value;
		const userPreferences = this.choicesList.getValues();

		const securityCheck = (userLottery === null) && (userGPA === null) && (userPreferences === null);

		return [!securityCheck, userLottery, userGPA, userPreferences];
	}
}

class DataVisualizer {
	constructor(bins, matches, seats) {
		this.bins = bins.map(bin => bin.map(num => num.replaceAll('-', '')));;
		this.matches = matches;
		this.seats = seats;

		this.el = document.getElementById('simulation-results');

		this.pTotalStudents = document.getElementById('total-applicants').childNodes[0];
		this.pTotalSchools = document.getElementById('total-schools').childNodes[0];
		this.pTotalCapacity = document.getElementById('total-capacity').childNodes[0];
		this.pPreferenceStrategy = document.getElementById('preference-strategy').childNodes[0];
		this.pListLength = document.getElementById('average-list-length').childNodes[0];
		this.pAdmissionPolicy = document.getElementById('admission-policies').childNodes[0];
		this.pStudentsTop = document.getElementById('students-top').childNodes[0];
		this.pStudentsFive = document.getElementById('students-top-5').childNodes[0];
		this.pStudentsUnmatched = document.getElementById('students-unmatched').childNodes[0];
		this.pSchoolsUnfilled = document.getElementById('schools-unfilled').childNodes[0];
		this.pSeatsUnfilled = document.getElementById('seats-unfilled').childNodes[0];

		this.focusSection = document.getElementById('focus');
		this.focusNumber = document.getElementById('focus-number');
		this.focusSubtitle = document.getElementById('focus-subtitle');
		this.focusPar1 = document.getElementById('focus-par-1');
		this.focusPar2 = document.getElementById('focus-par-2');
		this.plot = document.getElementById('plot');

		this.computeAggregateStats();
		this.attachListeners();
	}

	computeAggregateStats() {
		this.counts = this.bins.map(bin => bin.length);
		this.totalStudents = this.counts.reduce((a, b) => a + b, 0);
		this.ratios = this.bins.map(bin => bin.length / this.totalStudents);

		this.totalSchools = this.seats.size;

		let totalCapacity = 0;
		let seatsUnfilled = 0;
		let schoolsUnfilled = 0;
		for (let val of this.seats.values()) {
			let offers = val.get('accepted_students');
			let seats = val.get('total_seats');
			totalCapacity += seats;
			seatsUnfilled += (seats - offers);
			schoolsUnfilled += (seats - offers) > 0 ? 1 : 0;
		}
		this.totalCapacity = totalCapacity;
		this.seatsUnfilled = seatsUnfilled;
		this.schoolsUnfilled = schoolsUnfilled;

		this.ratioFive = [0, 1, 2, 3, 4].map(idx => this.ratios[idx]).reduce((a, b) => a + b, 0);
		this.countFive = [0, 1, 2, 3, 4].map(idx => this.counts[idx]).reduce((a, b) => a + b, 0);
	}

	attachListeners() {
		const self = this;

		this.pPreferenceStrategy.nextSibling.addEventListener('click', () => self.showFocus('preference-strategy'));
		this.pAdmissionPolicy.nextSibling.addEventListener('click', () => self.showFocus('admission-policies'));

		this.pStudentsTop.nextSibling.addEventListener('click', () => self.showFocus('students-top'));
		this.pStudentsFive.nextSibling.addEventListener('click', () => self.showFocus('students-top-5'));
		this.pStudentsUnmatched.nextSibling.addEventListener('click', () => self.showFocus('students-unmatched'));

		this.pSchoolsUnfilled.nextSibling.addEventListener('click', () => self.showFocus('schools-unfilled'));
		this.pSeatsUnfilled.nextSibling.addEventListener('click', () => self.showFocus('seats-unfilled'));
	}

	showFocus(targetData) {
		let number, subtitle, par1, par2, plot, index;
		let medianTop, combinedBins, medianTopFive, medianUnmatched;

		switch (targetData) {
			case 'students-top':
				medianTop = this.bins[0][Math.floor(this.bins[0].length / 2)];

				number = (100 * this.ratios[0]).toFixed(1) + '%';
				subtitle = 'of the applicants were matched to their top choice.';
				par1 = 'That\'s ' + this.counts[0].toLocaleString() + ' students out of ' + this.totalStudents.toLocaleString() + '.';
				par2 = 'Their median lottery number starts with the digits ' + medianTop.substring(0, 4).toUpperCase() + '.';
				plot = 'counts';
				index = 1;
				break;

			case 'students-top-5':
				combinedBins = [0, 1, 2, 3, 4].map(idx => this.bins[idx]).reduce((x, y) => x.concat(y), []).sort();
				medianTopFive = combinedBins[Math.floor(combinedBins.length / 2)];

				number = (100 * this.ratioFive).toFixed(1) + '%';
				subtitle = 'of the applicants were matched to one of their top 5 choices.';
				par1 = 'That\'s ' + this.countFive.toLocaleString() + ' students out of ' + this.totalStudents.toLocaleString() + '.';
				par2 = 'Their median lottery number starts with the digits ' + medianTopFive.substring(0, 4).toUpperCase() + '.';
				plot = 'counts-cumulative';
				index = 5;
				break;

			case 'students-unmatched':
				medianUnmatched = this.bins[12][Math.floor(this.bins[12].length / 2)];

				number = (100 * this.ratios[12]).toFixed(1) + '%';
				subtitle = 'of the applicants were not matched to any of their choices.';
				par1 = 'That\'s ' + this.counts[12].toLocaleString() + ' students out of ' + this.totalStudents.toLocaleString() + '.';
				par2 = 'Their median lottery number starts with the digits ' + medianUnmatched.substring(0, 4).toUpperCase() + '.';
				plot = 'counts';
				index = 13;
				break;

			default:
				break;
		}

		this.refreshFocus(number, subtitle, par1, par2, plot, index);
	}

	show() {
		this.el.classList.remove('hide');
	}

	hide() {
		this.el.classList.add('hide');
	}

	plotLotteryRange(index) {
		const margin = { top: 30, right: 30, bottom: 30, left: 30 };
		const width = 460;
		const height = 120;

		const hexDigits = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 'a', 'b', 'c', 'd', 'e', 'f'];
		const bin = this.bins[index - 1];
		const range_min = bin[0].replaceAll('-', '');
		const range_max = bin[bin.length - 1].replaceAll('-', '');
		const median = bin[Math.floor(bin.length / 2)].replaceAll('-', '');
		const data = [{
			index: 1,
			min: Number('0x' + range_min.substring(0, 8)),
			max: Number('0x' + range_max.substring(0, 8)),
			med: Number('0x' + median.substring(0, 8))
		}];

		// Define the X axis scale
		let x = d3.scaleLinear()
			.domain([0, Number('0xffffffff')])
			.range([margin.left, width - margin.right]);

		// Define the Y axis scale
		let y = d3.scaleBand()
			.domain(d3.range(1, 2))
			.range([height - margin.bottom, margin.top])
			.padding(0.2);

		// Append the SVG container
		const svg = d3.select('#plot')
			.append('svg')
			.attr('width', width)
			.attr('height', height)
			.attr('viewBox', [0, 0, width, height]);

		// Add a rect for each bar
		svg.append('g')
			.attr('fill', '#4036ed')
			.selectAll()
			.data(data)
			.join('rect')
			.attr('x', d => x(d.min))
			.attr('y', d => y(d.index))
			.attr('height', y.bandwidth())
			.attr('width', d => x(d.max) - x(d.min));

		// Add the X axis
		svg.append('g')
			.attr('transform', 'translate(0,' + (height - margin.bottom) + ')')
			.call(d3.axisBottom(x)
				.tickValues(hexDigits.map(n => Number('0x' + n + '0000000')))
				.tickSizeOuter(0)
				.tickFormat(x => x.toString(16).substring(0, 1)));

		// Add the Y axis
		svg.append('g')
			.attr('transform', 'translate(' + margin.left + ',0)')
			.call(d3.axisLeft(y).tickFormat(y => index));
	}

	plotCounts(indexFocused, cumulative=false) {
		// Clear any existing plots
		this.plot.innerHTML = '';

		// set the dimensions and margins of the graph
		const margin = { top: 30, right: 30, bottom: 30, left: 30 };
		const width = 460;
		const height = 400;

		const ratiosMap = this.ratios.keys().toArray().map(k => { return { index: k + 1, ratio: this.ratios[k] } });

		const self = this;
		const clickHandler = idx => self.plotLotteryRange(idx);

		// Define the X axis scale
		let x = d3.scaleBand()
			.domain(d3.range(1, 14))
			.range([margin.left, width - margin.right])
			.padding(0.2);

		// Define the Y axis scale
		let y = d3.scaleLinear()
			.domain([0, d3.max(ratiosMap, d => d.ratio)])
			.range([height - margin.bottom, margin.top]);

		// Append the SVG container
		const svg = d3.select('#plot')
			.append('svg')
			.attr('width', width)
			.attr('height', height)
			.attr('viewBox', [0, 0, width, height]);

		// Add a rect for each bar
		svg.append('g')
			.selectAll()
			.data(ratiosMap)
			.join('rect')
			.attr('x', d => x(d.index))
			.attr('y', d => y(d.ratio))
			.attr('height', d => y(0) - y(d.ratio))
			.attr('width', x.bandwidth())
			.attr('fill', d => {
				if (cumulative)
					return (d.index <= indexFocused) ? 'orange' : '#4036ed';
				return (d.index === indexFocused) ? 'orange' : '#4036ed'
			})
			.on('click', (e, d) => clickHandler(d.index));

		// Add the X axis
		svg.append('g')
			.attr('transform', 'translate(0,' + (height - margin.bottom) + ')')
			.call(d3.axisBottom(x).tickSizeOuter(0).tickFormat(x => x <= 12 ? x : 'Unmatched'));

		// Add the Y axis
		svg.append('g')
			.attr('transform', 'translate(' + margin.left + ',0)')
			.call(d3.axisLeft(y).tickFormat(y => (100 * y).toFixed(0) + '%'))
			.call(g => g.append('text')
				.attr('x', -margin.left)
				.attr('y', 10)
				.attr('fill', '#000000')
				.attr('text-anchor', 'start')
				.text('Matched students'));
	}

	refreshNutritionalLabel() {
		this.pTotalStudents.nodeValue = this.totalStudents.toLocaleString();
		this.pTotalSchools.nodeValue = this.totalSchools.toLocaleString();
		this.pTotalCapacity.nodeValue = this.totalCapacity.toLocaleString();

		this.pStudentsTop.nodeValue = (100 * this.ratios[0]).toFixed(0) + '% (' + this.counts[0].toLocaleString() + ')';
		this.pStudentsFive.nodeValue = (100 * this.ratioFive).toFixed(0) + '% (' + this.countFive.toLocaleString() + ')';
		this.pStudentsUnmatched.nodeValue = (100 * this.ratios[12]).toFixed(0) + '% (' + this.counts[12].toLocaleString() + ')';

		this.pSchoolsUnfilled.nodeValue = (100 * this.schoolsUnfilled / this.totalSchools).toFixed(0) + '% (' + this.schoolsUnfilled + ')';
		this.pSeatsUnfilled.nodeValue = this.seatsUnfilled.toLocaleString();
	}

	refreshFocus(number, subtitle, par1, par2, plot, index) {
		this.focusNumber.innerText = number;
		this.focusSubtitle.innerText = subtitle;
		this.focusPar1.innerText = par1;
		this.focusPar2.innerText = par2;

		if (plot === 'counts')
			this.plotCounts(index);
		else if (plot === 'counts-cumulative')
			this.plotCounts(index, true);

		this.focusSection.classList.remove('hide');
	}
}

window.addEventListener('load', () => {
	const lotteryNums = new LotteryNumberExamples();
	lotteryNums.iterate();

	userData = new UserData();

	document.getElementById('run-simulation').addEventListener('click', e => {
		console.log('JS event listener');
		document.getElementById('plot').innerHTML = '';
	});
});

window.addEventListener('py:all-done', () => {
	document.getElementById('run-simulation').classList.remove('disabled');
});

window.addEventListener('py-backend-done', () => {
	const visualizer =
		new DataVisualizer(window.py_bins, window.py_matches, window.py_seats);

	visualizer.refreshNutritionalLabel();
	visualizer.show();
})

export { pyDoneEvent, userData };