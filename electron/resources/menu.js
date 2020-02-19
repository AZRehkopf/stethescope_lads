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