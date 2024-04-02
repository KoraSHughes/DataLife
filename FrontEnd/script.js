const lotteryNumbers = [
	'3a4bdc7f-8e91-0c2a-6f5d-1b9e6a38d047',
	'3833cfd2-93c5-b281-407b-c3b96160ea3f',
	'9568a214-f388-402d-4145-45e8138643e',
	'cb6e6546-cfd6-0134-d85a-5e8041f8b06c',
	'd8b0965e-9e71-c53b-f849-953a82e164d1',
	'0c68f153-12e5-3e7f-2234-6517592f1763',
	'211cee28-3c31-bf81-4a16-6f39344b9f97',
	'4f6bd3ef-2929-d7c0-8215-c4065d0109b4'
];
let point = 0;

function updateLotteryNumber() {
	el = document.getElementById('lottery-example');
	el.innerText = lotteryNumbers[point];
	if (point < lotteryNumbers.length - 1)
		point++;
	else
		point = 0;
}

window.onload = () => {
	console.log('onWindowLoad')
	updateLotteryNumber();
	setInterval(updateLotteryNumber, 3000);
};