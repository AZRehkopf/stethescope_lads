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
    
    ECGChart.data.datasets.forEach((dataset) => {
        dataset.data = dataset.data.concat(parsedData['ecg']);
        dataset.data.splice(0,parsedData['ecg'].length);
    });    
    
    ECGChart.update({
        duration: 0
    });

    micChart.data.datasets.forEach((dataset) => {
        dataset.data = dataset.data.concat(parsedData['mic']);
        dataset.data.splice(0,parsedData['mic'].length);
    });    
    
    micChart.update({
        duration: 0
    });
});

dataSocket.on('close', function() {
	console.log('Data socket closed');
});

var ecgStartingValues = Array.apply(null, Array(1250)).map(Number.prototype.valueOf,2000);
var ecgStartingLabels = Array.apply(null, Array(1250)).map(String.prototype.valueOf,"")

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
        animation: false,
        legend: {
            display: false
        },
        
        elements: {
            point:{
                radius: 0
            },
            line:{
                tension: 0,
                fill: false,
                stepped: false,
                borderDash: []
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

var micStartingValues = Array.apply(null, Array(1250)).map(Number.prototype.valueOf,2000);
var micStartingLabels = Array.apply(null, Array(1250)).map(String.prototype.valueOf,"")

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
        animation: false,
        legend: {
            display: false
        },
        
        elements: {
            point:{
                radius: 0
            },
            line:{
                tension: 0,
                fill: false,
                stepped: false,
                borderDash: []
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