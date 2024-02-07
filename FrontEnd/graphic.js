// derivative source: https://observablehq.com/@korashughes/lifelane


const csvUrl = 'https://gist.githubusercontent.com/tanmayasang/b07e0ac7713a3deadd690c2b0ed27453/raw/unemployment-dec-2019@2.csv';
const jsonUrl = 'https://gist.githubusercontent.com/tanmayasang/d647d7831a558aa047cb09dc0c8beec5/raw/gz_2010_us_040_00_20m.json';
// DATA: https://www.bls.gov/web/laus/laumstrk.htm

// Define a light gray background color to be used for the SVG.
// You can change this if you want another background color.
backgroundColors = ['#dcdcdc', '#FFFFFF', '#000000', '#d4d4d4']


// Window stuff
width = 1000
height = 1000
margin = {top: 50, bottom: 50, left: 130, right: 20, title: 60}
visWidth = width - margin.left - margin.right
visHeight = 800 - margin.top - margin.bottom
font_size = [] // small, med, large


// Guidelines: make 4 different visualizations; each with 3 different channels, 3 different marks
// for each visdescribe which channesla nd marks and why and is it good/bad

// load the CSV file
d3.csv(csvUrl).then(function(unemployment) {
	// if the CSV file was loaded: the JSON file
	d3.json(jsonUrl).then(function (usaGeo) {
		// single object where the keys are the state names and the values are the unemployment rates
		stateToRate = Object.fromEntries(new Map(unemployment.map(d => [d.state, d.rate])))
		states = Array.from(unemployment.map(d => d.state))
		console.log(unemployment)
				
		// calculate the min and max unemployment rates:
		rateExtent = d3.extent(unemployment, d => d.rate)
		console.log("Rate Extent: " + rateExtent)
		
		// scale stuff
		stateScale = d3.scaleBand().domain(states).range([0, visHeight]).padding(0.2)
		rateScale = d3.scaleLinear().domain([2, rateExtent[1]]).range([0, visWidth])
		xAxis = d3.axisBottom(rateScale).tickFormat(d3.format('~s'))
		yAxis = d3.axisLeft(stateScale)

		rateColor = d3.scaleDivergingSqrt().domain([rateExtent[0], rateExtent[1]+1])  // scaleSequential
		.interpolator(d3.interpolateWarm)
		rateColor2 = d3.scaleDivergingSqrt().domain([rateExtent[0]-1, rateExtent[1]+1])
		.interpolator(d3.interpolateGreys)
		rateColor3 = d3.scaleDivergingSqrt().domain([rateExtent[0], rateExtent[1]+1])
		.interpolator(d3.interpolateReds)

		const myfont = {type: "Times New Roman", small: 14, med: 20, large: 30};

		document.getElementById("intro").innerHTML = "Basic Header Test\n";


		// *****GRAPH 1*****
		svg1 = d3.select("body")
			.append("svg")
			.attr('width', visWidth + margin.left + margin.right)
		 	.attr('height', visHeight + margin.top + margin.bottom)
			.attr("font-size", myfont.small)
			.attr("style", "background-color:" + backgroundColors[0]);
		// Rectangles		
		const g1 = svg1.append("g")
			.attr('transform', `translate(${margin.left}, ${margin.top})`);
		// bind our data to rectangles
		g1.selectAll('rect').data(unemployment).join('rect')
			// set attributes for each bar
			.attr('x', 0)
			.attr('y', d => stateScale(d.state))
			.attr('width', d => rateScale(d.rate))
			.attr('height', stateScale.bandwidth())
			.attr('fill', d => rateColor(d.rate));

		// add a group for the y-axis
		g1.append('g')
			.call(yAxis)
			.call(g => g.select('.domain').remove())
		// add a label for the y-axis
		.append('text')
			.attr('fill', 'black')
			.attr('x', -80)
			.attr('y', visHeight/2)
			.attr("font-family", myfont.type)
			.attr("font-size", myfont.med)
			.text("State");
		// add a group for the x-axis
		g1.append('g')
			// we have to move this group down to the bottom of the vis
			.attr('transform', `translate(0, ${visHeight})`)
			.call(xAxis)
			.call(g => g.select('.domain').remove())
		// add a label for the x-axis
		.append('text')
			.attr('fill', 'black')
			.attr('x', visWidth/2)
			.attr('y', 35)
			.attr("font-family", myfont.type)
			.attr("font-size", myfont.med)
			.text("Unemployment Rate");
		// title
		svg1.append('text')
			.attr('fill', 'black')
			.attr('x', visWidth/2 - margin.title)
			.attr('y', 40)
			.attr("font-family", myfont.type)
			.attr("font-size", myfont.large)
			.text("Unemployment Rate By State");
		// color legend
		g1.append("text")
		  .attr("font-family", myfont.type)
		  .attr("font-size", myfont.med)
		  .attr("x", visWidth-200)
		  .attr("y", 180)
		  .text("Rate:");
		g1.append("text")  // text
		  .attr("font-family", myfont.type)
		  .attr("font-size", myfont.med)
		  .attr("x", visWidth-150)
		  .attr("y", 213)
		  .attr('fill', rateColor(2))
		  .text("2%");
		g1.append("text")  // text
		  .attr("font-family", myfont.type)
		  .attr("font-size", myfont.med)
		  .attr("x", visWidth-150)
		  .attr("y", 270)
		  .attr('fill', rateColor(4))
		  .text("4%");
		g1.append("text")  // text
		  .attr("font-family", myfont.type)
		  .attr("font-size", myfont.med)
		  .attr("x", visWidth-150)
		  .attr("y", 328)
		  .attr('fill', rateColor(6))
		  .text("6%");
		const colorlegend = g1.append("g")
		  .selectAll("g")
		  .data([2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6])
		  .join("g")
		  .attr("transform", (d, i) => `translate(680, ${200 + i*5*2.8})`);
		colorlegend.append("rect")  // squares
		  .attr("width",17)
		  .attr("height",17)
		  .attr("fill", d => rateColor(d));
          
	}, function(reason) {
		console.log(reason); // Error!
		d3.select("body")
			.append("p")
			.text("Could not load JSON data set. See console for more information.");
})
}, function(reason) {
	console.log(reason); // Error!
	d3.select("body")
		.append("p")
		.text("Could not load CSV data set. See console for more information.");
});


