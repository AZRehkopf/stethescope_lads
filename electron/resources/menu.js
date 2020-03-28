const net = require('net');

var control_port = new net.Socket();
var dataSocket = new net.Socket();

// control_port.connect(65535, '127.0.0.1', function() {
//     console.log('Connected to the python interface api');
// });

// control_port.on('data', function(data) {
//     parsedData = JSON.parse(data.toString('utf8'));
//     parseTCP(parsedData);
// });

// control_port.on('close', function() {
// 	console.log('Control port closed');
// });

dataSocket.connect(65534, '127.0.0.1', function() {
    console.log('Connected to data socket');
});

dataSocket.on('data', function(data) {
    var parsedData = JSON.parse(data.toString('utf8'));
    
    ECGChart.data.labels.push("");

    ECGChart.data.datasets.forEach((dataset) => {
        dataset.data.push(parsedData['ecg']);
    });

    ECGChart.data.labels.shift();

    ECGChart.data.datasets.forEach((dataset) => {
        dataset.data.shift();
    });
    
    ECGChart.update();

    micChart.data.labels.push("");

    micChart.data.datasets.forEach((dataset) => {
        dataset.data.push(parsedData['mic']);
    });

    micChart.data.labels.shift();

    micChart.data.datasets.forEach((dataset) => {
        dataset.data.shift();
    });
    micChart.update();
});

dataSocket.on('close', function() {
	console.log('Data socket closed');
});

var ecgStartingValues = Array.apply(null, Array(250)).map(Number.prototype.valueOf,0);
var ecgStartingLabels = Array.apply(null, Array(250)).map(String.prototype.valueOf,"")

var ctx_ecg = document.getElementById('ecgData').getContext('2d');
var ECGChart = new Chart(ctx_ecg, {
    type: 'line',
    data: {
        labels: ecgStartingLabels,
        datasets: [{
            data: ecgStartingValues,
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
                    display: false,
                    min: 0,
                    max: 4095
                },
                gridLines: {
                    display:false
                }
            }],
            xAxes: [{
                gridLines: {
                    display:false
                }
            }]
        }
    }
});

var micStartingValues = Array.apply(null, Array(250)).map(Number.prototype.valueOf,0);
var micStartingLabels = Array.apply(null, Array(250)).map(String.prototype.valueOf,"")

var ctx_mic = document.getElementById('micData').getContext('2d');
var micChart = new Chart(ctx_mic, {
    type: 'line',
    data: {
        labels: micStartingLabels,
        datasets: [{
            data: micStartingValues,
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
                    display: false,
                    min: 0,
                    max: 4095
                },
                gridLines: {
                    display:false
                }
            }],
            xAxes: [{
                gridLines: {
                    display:false
                }
            }]
        }
    }
});

// Click Events

document.getElementById("start").addEventListener("click", startRecording);
document.getElementById("stop").addEventListener("click", stopRecording);

function startRecording() {
    var tcp_command = {"cmd": "start", "data": null}
    control_port.write(JSON.stringify(tcp_command))
}

function stopRecording() {
    var tcp_command = {"cmd": "stop", "data": null}
    control_port.write(JSON.stringify(tcp_command))
}