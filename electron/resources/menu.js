const net = require('net');

var control_port = new net.Socket();
var ecg_socket = new net.Socket();
var mic_socket = new net.Socket();

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

ecg_socket.connect(65534, '127.0.0.1', function() {
    console.log('Connected to the ECG data socket');
});

ecg_socket.on('data', function(data) {
    rawData = data.toString('utf8');
    dataPoint = parseInt(rawData);
    
    ECGChart.data.labels.push("");

    ECGChart.data.datasets.forEach((dataset) => {
        dataset.data.push(dataPoint);
    });

    ECGChart.data.labels.shift();

    ECGChart.data.datasets.forEach((dataset) => {
        dataset.data.shift();
    });
    ECGChart.update();
});

ecg_socket.on('close', function() {
	console.log('ECG socket closed');
});

mic_socket.connect(65533, '127.0.0.1', function() {
    console.log('Connected to the Mic data socket');
});

mic_socket.on('data', function(data) {
    rawData = data.toString('utf8');
    dataPoint = parseInt(rawData);
    
    micChart.data.labels.push("");

    micChart.data.datasets.forEach((dataset) => {
        dataset.data.push(dataPoint);
    });

    micChart.data.labels.shift();

    micChart.data.datasets.forEach((dataset) => {
        dataset.data.shift();
    });
    micChart.update();
});

mic_socket.on('close', function() {
	console.log('ECG socket closed');
});

var startingValues = Array.apply(null, Array(250)).map(Number.prototype.valueOf,0);
var startingLabels = Array.apply(null, Array(250)).map(String.prototype.valueOf,"")

var ctx = document.getElementById('ecgData').getContext('2d');
var ECGChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: startingLabels,
        datasets: [{
            data: startingValues,
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

var ctx = document.getElementById('micData').getContext('2d');
var micChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: startingLabels,
        datasets: [{
            data: startingValues,
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