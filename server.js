var http = require("http");
var url = require("url");
var fs = require("fs");
var path = require("path");
var mimetypes = require("mime-types");
var pagetop = fs.readFileSync('pagetop.html');
var index;
var urlpath;
var logpath = '/home/pi/usbdrv/templog';
var maxtemp, mintemp;
var maxtime, mintime;
var oldmaxtemp, oldmintemp;
var oldmaxtime, oldmintime;
var startMaxCheckTime = '06.00'; // Don't count earlier times (e.g. midnight) as today's max.

// Graph data
var data = { labels: [],
datasets:[ {
	fillColor: "rgba(220,220,220,0.2)",
	strokeColor: "rgba(220,220,220,1)",
	pointColor: "rgba(220,220,220,1)",
	pointStrokeColor: "#fff",
	pointHighlightFill: "#f66",
	pointHighlightStroke: "rgba(220,220,220,1)",
	data: [] }
    , {
	fillColor: "rgba(220,220,220,0)",
	strokeColor: "rgba(180,120,80,0.75)",
	pointColor: "rgba(180,120,80,0.75)",
	pointStrokeColor: "rgba(180,120,80,0.75)",
	pointHighlightFill: "#fff",
	pointHighlightStroke: "rgba(180,150,80,1)",
	data: [] }	] };

function colourVal(temp, ramps)
{
	var level = 1;
	for (var i = 0; i < ramps.length; i++)
	{
		var ramp = ramps[i];
		level = Math.min(level, (temp - ramp[0]) / (ramp[1] - ramp[0]));
	}
	level = Math.max(0, Math.min(1, level));
	return Math.round(level * 255);
}

function rgbVal(temp)
{
	return 'rgb(' + colourVal(temp,[[10,20]]) 
	        + ',' + colourVal(temp,[[-10,0],[30,20]]) 
			+ ',' + colourVal(temp,[[10,0]]) + ')';
}

function padded(num)
{
	var padded = '0' + num;
	return padded.substr(padded.length - 2);
}

function hhmmstring(date)
{
	return padded(date.getHours()) + '.' + padded(date.getMinutes());
}

function getLoggedReading(filename)
{
	try {
		var reading = fs.readFileSync(path.join(logpath, filename),'utf8');
		return (parseInt(reading) / 1000);
	}
	catch (e) {
		return  null;
	}
}

function addToData(filename,nowString)
{
	var reading = getLoggedReading(filename);
	var oldreading = getLoggedReading(path.join('yesterday',filename));
	if (filename <= nowString)
	{
		// For time <= now, reading is from today, and oldreading from yesterday.
		if (reading > maxtemp && filename >= startMaxCheckTime)
		{
			maxtemp = reading;
			maxtime = filename;
		}
		else if (reading < mintemp)
		{
			mintemp = reading;
			mintime = filename;
		}
		if (oldreading !== null)
		{
			if (oldreading > oldmaxtemp && filename >= startMaxCheckTime)
			{
				oldmaxtemp = oldreading;
				oldmaxtime = filename;
			}
			else if (oldreading < oldmintemp)
			{
				oldmintemp = oldreading;
				oldmintime = filename;
			}
		}
	}
	else // For time > now, reading is from yesterday.
	{
		if (reading > oldmaxtemp)
		{
			oldmaxtemp = reading;
			oldmaxtime = filename;
		}
		else if (reading < oldmintemp)
		{
			oldmintemp = reading;
			oldmintime = filename;
		}
	}
	data.labels.push(filename.substr(3) == '00' ? filename : '');
	data.datasets[0].data.push(reading.toFixed(1));
	data.datasets[1].data.push((oldreading === null ? reading : oldreading).toFixed(1));
}

function tempspan(temp)
{
	return '<span style="' +
	(temp <= 0 ? 'text-shadow:0px 0px 10px white; ': '') +
	'color:' + rgbVal(temp) + '">' + temp.toFixed(1) + '&deg;C</span>';
}

// Request handler callback
function onRequest(request, response) 
{
	var requestURL = url.parse(request.url,true);
	if (requestURL.pathname == '/')
	{
		// Get current reading.
		var reading = fs.readFileSync('/sys/bus/w1/devices/28-000007099503/w1_slave','utf8');
		reading = reading.substr(reading.lastIndexOf('=')+1);
		var value = parseInt(reading) / 1000;
		var fahrenheit = (value * 1.8) + 32;

		// Display page..
		var now = new Date();
		var nowString = hhmmstring(now);

		response.writeHead(200, {"Content-Type": "text/html"});
		response.write(pagetop);
		response.write('<body style="background-color:#036; color:white">');
		response.write('<p><span style="font-size: 80px">');
		response.write('At ' + nowString + ' : ' + tempspan(value) + '</span>');
		response.write(' (' + fahrenheit.toFixed(1) + '&deg;F) <a href=".">(Refresh)</a></p>');
		
		// Get logged temps from last 24 hours....
		data.labels = [];
		data.datasets[0].data = [];
		data.datasets[1].data = [];
		maxtemp = -100; mintemp = 100;
		oldmaxtemp = -100; oldmintemp = 100;
		var files = fs.readdirSync(logpath);
		// First, yesterday's files (time > now)
		var i = 0;
		while (files[i] <= nowString && i < files.length)
		{
			i++;
		}
		for (; i < files.length; i++)
		{
			if (files[i] != 'yesterday')
			{
				addToData(files[i],nowString);
			}
		}
		// Then, today's files
		for (i = 0; i < files.length && files[i] <= nowString; i++)
		{
			addToData(files[i],nowString);
		}
		response.write('<p>Today:');
		if (nowString > startMaxCheckTime)
		{
			response.write(' Max: ' + tempspan(maxtemp) + ' (' + maxtime + ')');
		}
		response.write(' Min: ' + tempspan(mintemp) + ' (' + mintime + ')</p>');
		response.write('<p class="old">Yesterday: Max: ' + tempspan(oldmaxtemp) + ' (' + oldmaxtime + ')');
		response.write(' Min: ' + tempspan(oldmintemp) + ' (' + oldmintime + ')</p>');
		response.write('<script>');
		response.write('var data = ' + JSON.stringify(data) + ';');
		response.write('window.onload = function(){');
		response.write('var ctx = document.getElementById("myChart").getContext("2d");');
		response.write('window.myLineChart = new Chart(ctx).Line(data, { ');
		response.write('scaleFontSize: 30, scaleFontColor:"#cff", responsive: true, maintainAspectRatio: false, pointHitDetectionRadius : 5 } );');
		response.write('}');
		response.write('</script>');
	    response.write('<div><canvas id="myChart" width="400" height="600"></canvas></div>');
		response.write('<p class="credits">Graph powered by <a target="_blank" href="http://www.chartjs.org">Chart.js</a></p>');
		response.end('</body></html>');
	}
	else
	{
		// Handle requests for files: return them if they exist.
		var filename = path.join(process.cwd(), unescape(requestURL.pathname));
		var stats;
		var mimeType;

		try {
			stats = fs.lstatSync(filename); // throws if path doesn't exist
			mimeType = mimetypes.lookup(filename);
		} catch (e) {
			console.log('Non-existent file request: ' + filename);
			response.writeHead(404, {'Content-Type': 'text/plain'});
			response.write('404 Not Found\n');
			response.end();
			return;
		}

		if (stats.isFile() && mimeType) {
			response.writeHead(200, {"Content-Type": mimeType});
			var fileStream = fs.createReadStream(filename);
			fileStream.pipe(response);
		} else {
			console.log('Bad file request: ' + filename);
			response.writeHead(500, {'Content-Type': 'text/plain'});
			response.write('500 Internal server error\n');
			response.end();
		}
	}
	
} // onRequest


http.createServer(onRequest).listen(8787);
console.log("piTemp server started.");
