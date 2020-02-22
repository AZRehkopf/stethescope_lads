const net = require('net');

var client = new net.Socket();

client.connect(65535, '127.0.0.1', function() {
    console.log('Connected to the python interface api');
    //client.write('log');
});

client.on('data', function(data) {
    parsedData = JSON.parse(data.toString('utf8'));
    parseTCP(parsedData);
});

client.on('close', function() {
	console.log('Connection closed');
});

var ctx = document.getElementById('ecgData').getContext('2d');
var myChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: ['5 sec', '10 sec', '15 sec', '20 sec', '25 sec', '30 sec'],
        datasets: [{
            data: [12, 19, 3, 5, 2, 3],
            borderColor: 'rgba(84, 153, 199, 1)',
            borderWidth: 1
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        legend: {
            display: false
        },
        elements: {
                    point:{
                        radius: 0
                    }
        },
        scales: {
            yAxes: [{
                ticks: {
                    display: false
                }
            }]
        }
    }
});

var ctx = document.getElementById('micData').getContext('2d');
var myChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: ['5 sec', '10 sec', '15 sec', '20 sec', '25 sec', '30 sec'],
        datasets: [{
            data: [12, 19, 3, 5, 2, 3],
            borderColor: 'rgba(0, 150, 136, 1)',
            borderWidth: 1
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        legend: {
            display: false
        },
        elements: {
                    point:{
                        radius: 0
                    }
        },
        scales: {
            
            yAxes: [{
                ticks: {
                    display: false
                }
            }]
        },
        
    }
});

// Click Events

document.getElementById("start").addEventListener("click", startRecording);
document.getElementById("stop").addEventListener("click", stopRecording);

function startRecording() {
    var tcp_command = {"cmd": "start", "data": null}
    client.write(JSON.stringify(tcp_command))
}

function stopRecording() {
    var tcp_command = {"cmd": "stop", "data": null}
    client.write(JSON.stringify(tcp_command))
}