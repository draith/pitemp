var http = require("http");
var url = require("url");
var fs = require("fs");
var path = require("path");
var mimetypes = require("mime-types");
var pagetop = fs.readFileSync('pagetop.html');
var index;
var urlpath;
var logpath = '/var/ram/templog';
var maxtemp;
var mintemp;
var maxtime, mintime;

// Graph data
var data = { labels: [],
datasets:[ {
	fillColor: "rgba(220,220,220,0.2)",
	strokeColor: "rgba(220,220,220,1)",
	pointColor: "rgba(220,220,220,1)",
	pointStrokeColor: "#fff",
	pointHighlightFill: "#fff",
	pointHighlightStroke: "rgba(220,220,220,1)",
	data: [] } ] };

function colourVal(temp, peak)
{
	return Math.round(Math.max(0, 255 * (1 - (Math.abs(temp - peak)  / 20))));
}

function rgbVal(temp)
{
	return 'rgb(' + colourVal(temp,30) + ',' + colourVal(temp,10) + ',' + colourVal(temp,-10) + ')';
}

function padded(num)
{
	var padded = '0' + num;
	return padded.substr(padded.length - 2);
}

function hhmmstring(date)
{
	return padded(date.getHours()) + ':' + padded(date.getMinutes());
}

function getLoggedReading(filename)
{
	var reading = fs.readFileSync(path.join(logpath, filename),'utf8');
	reading = reading.substr(reading.lastIndexOf('=')+1);
	return (parseInt(reading) / 1000);
}

function addToData(filename)
{
	var reading = getLoggedReading(filename);
	if (reading > maxtemp)
	{
		maxtemp = reading;
		maxtime = filename;
	}
	else if (reading < mintemp)
	{
		mintemp = reading;
		mintime = filename;
	}
	data.labels.push(filename.substr(3) == '00' ? filename : '');
	data.datasets[0].data.push(reading.toFixed(1));
}

function tempspan(temp)
{
	return '<span style="' +
	(temp <= 0 ? 'background-color:white; ': '') +
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
		response.write('<p style="font-size: 80px">');
		response.write('At ' + nowString + ' : ' + tempspan(value) + '</p>');
		response.write('<p>(' + fahrenheit.toFixed(1) + '&deg;F)</p>');
		
		// Get logged temps from last 24 hours....
		data.labels = [];
		data.datasets[0].data = [];
		maxtemp = -100; mintemp = 100;
		var files = fs.readdirSync(logpath);
		for (i = 0; i < files.length; i++)
		{
			// First, yesterday's files
			if (files[i] > nowString)
			{
				addToData(files[i]);
			}
		}
		for (i = 0; i < files.length; i++)
		{
			// Then, today's files
			if (files[i] <= nowString)
			{
				addToData(files[i]);
			}
		}
		response.write('<p>24-hours: Max: ' + tempspan(maxtemp) + ' (' + maxtime + ')');
		response.write(' Min: ' + tempspan(mintemp) + ' (' + mintime + ')</p>');
		response.write('<script>');
		response.write('var data = ' + JSON.stringify(data) + ';');
		response.write('window.onload = function(){');
		response.write('var ctx = document.getElementById("myChart").getContext("2d");');
		response.write('window.myLineChart = new Chart(ctx).Line(data, { ');
		response.write('scaleFontSize: 20, scaleFontColor:"#cff", responsive: true, maintainAspectRatio: false, pointHitDetectionRadius : 5 } );');
		response.write('}');
		response.write('</script>');
	    response.write('<div><canvas id="myChart" width="400" height="600"></canvas></div>');
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
