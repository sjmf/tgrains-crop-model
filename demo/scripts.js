

// Use TAB10 colors for charts to aid colorblind use
window.chartColors = Object();
window.chartColors.opaque = [
    'rgba( 31, 119, 180, 1)',  // blue
    'rgba(255, 127,  14, 1)',  // orange
    'rgba( 44, 160,  44, 1)',  // green
    'rgba(214,  39,  40, 1)',  // red
    'rgba(148, 103, 189, 1)',  // purple
    'rgba(140,  86,  75, 1)',  // brown
    'rgba(227, 119, 194, 1)',  // pink
    'rgba(127, 127, 127, 1)',  // grey
    'rgba(188, 189,  34, 1)',  // lime
    'rgba( 23, 190, 207, 1)',  // turquoise
];

window.chartColors.translucent = [
    'rgba( 31, 119, 180, .3)',  // blue
    'rgba(255, 127,  14, .3)',  // orange
    'rgba( 44, 160,  44, .3)',  // green
    'rgba(214,  39,  40, .3)',  // red
    'rgba(148, 103, 189, .3)',  // purple
    'rgba(140,  86,  75, .3)',  // brown
    'rgba(227, 119, 194, .3)',  // pink
    'rgba(127, 127, 127, .3)',  // grey
    'rgba(188, 189,  34, .3)',  // lime
    'rgba( 23, 190, 207, .3)',  // turquoise
];

let charts = {};

// Onload
document.addEventListener('DOMContentLoaded', function() {
    charts.bauChangeChart = new Chart('percentage-chart', {
        type: 'bar',
        data: {
            labels: ['GHG', 'Fertilizer leeching', 'Profit', 'Calorie Production'],
            datasets: [{
                label: '% change from BAU state',
                data: [40, 20, -26, 17],
                backgroundColor: window.chartColors.translucent[2],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            legend: {
                display: false
            },
            scales: {
                yAxes: [{
                    scaleLabel: {
                        display: true,
                        labelString: '% change from BAU state',
                        fontSize: 14
                    },
                    ticks: {
                        suggestedMax: 50,
                        suggestedMin: -50,
                    },
                    type: 'linear',
                    gridLines: {
                        zeroLineWidth: .5,
                        lineWidth: 0
                    }
                }],
                xAxes: [{
                    position: 'top',
                    offset: true,
                    ticks: {
                        beginAtZero: false,
                        fontSize: 14
                    },
                    gridLines: {
                        zeroLineWidth: .5,
                        lineWidth: 0
                    }
                }]
            }
        }
    });


    charts.nutritionChart = new Chart('nutrition-chart', {
        type: 'outlabeledPie',
        data: {
            labels: ['Whole Grains', 'Tubers', 'Vegetables', 'Fruits', 'Dairy',
                'Added Fats', 'Saturated Fats', 'Sugars', 'Animal Protein', 'Vegetable Protein'],
            datasets: [{
                data: [12, 8, 33, 12, 10, 10, 5, 5, 3, 2],
                backgroundColor: window.chartColors.opaque,
                borderWidth: 1,
            }],
        },
        options: {
            responsive: true,          // Changed as responsive doesn't work properly with tabs (display:none)
            maintainAspectRatio: true,  //
            legend: {
                display: false
            },
            tooltips: {
                enabled: false
            },
            zoomOutPercentage: 50,
            //rotation: .5* Math.PI,
            plugins: {
                outlabels: {
                    display: true,
                    text: '%l\n%p',
                    borderWidth: 0,
                    lineWidth: 0,
                    padding: 3,
                    stretch: 20,
                    //color: 'white',
                    //backgroundColor: "",
                    //lineColor: "rgba(255, 255, 255, 0)",  // hide lines
                }
            },
            // font: {
            //     size:16,
            //     resizable: true,
            //     minSize: 12,
            //     maxSize: 18
            // }
        }
    });


    charts.nutritionChangeChart = new Chart('nutrition-change-chart', {
        type: 'bar',
        data: {
            labels: ['Whole Grains', 'Tubers', 'Vegetables', 'Fruits', 'Dairy',
                'Added Fats', 'Saturated Fats', 'Sugars', 'Animal Protein', 'Vegetable Protein'],
            datasets: [{
                data: [-6, 14, -2, 3, 10, 4, -5, -4, 4, 2],
                backgroundColor: window.chartColors.translucent,
                //backgroundColor: 'rgba(27, 94, 32, 0.2)',
                borderWidth: 1
            }]
        },
        options: {
            legend: {
                display: false
            },
            scales: {
                yAxes: [{
                    scaleLabel: {
                        display: true,
                        labelString: '% change from BAU state',
                        fontSize: 14
                    },
                    ticks: {
                        suggestedMax: 20,
                        suggestedMin: -20,
                    },
                    type: 'linear',
                    gridLines: {
                        zeroLineWidth: .5,
                        lineWidth: 0
                    }
                }],
                xAxes: [{
                    position: 'top',
                    offset: true,
                    ticks: {
                        beginAtZero: false,
                        fontSize: 14
                    },
                    gridLines: {
                        zeroLineWidth: .5,
                        lineWidth: 0
                    }
                }]
            }
        }
    });


    charts.healthChart = new Chart('health-chart', {
        type: 'bar',
        data: {
            labels: ['Stroke', 'Cancer', 'Heart Disease', 'Diabetes'],
            datasets: [{
                label: '% change from BAU state',
                data: [ 20, -26, 17, 40],
                backgroundColor: window.chartColors.translucent[3],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            legend: {
                display: false
            },
            scales: {
                yAxes: [{
                    scaleLabel: {
                        display: true,
                        labelString: '% change from BAU state',
                        fontSize: 14
                    },
                    ticks: {
                        suggestedMax: 50,
                        suggestedMin: -50,
                    },
                    type: 'linear',
                    gridLines: {
                        zeroLineWidth: .5,
                        lineWidth: 0
                    }
                }],
                xAxes: [{
                    position: 'top',
                    offset: true,
                    ticks: {
                        beginAtZero: false,
                        fontSize: 14
                    },
                    gridLines: {
                        zeroLineWidth: .5,
                        lineWidth: 0
                    }
                }]
            }
        }
    });


    charts.pesticidesChart = new Chart('pesticides-chart', {
        type: 'bar',
        data: {
            labels: ['Ground Water', 'Fish', 'Birds', 'Bees', 'Beneficial Arthropods'],
            datasets: [{
                label: '% change from BAU state',
                data: [30, 20, -26, 17, -8],
                backgroundColor: window.chartColors.translucent[4],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            legend: {
                display: false
            },
            scales: {
                yAxes: [{
                    scaleLabel: {
                        display: true,
                        labelString: '% change from BAU state',
                        fontSize: 14
                    },
                    ticks: {
                        suggestedMax: 50,
                        suggestedMin: -50,
                    },
                    type: 'linear',
                    gridLines: {
                        zeroLineWidth: .5,
                        lineWidth: 0
                    }
                }],
                xAxes: [{
                    position: 'top',
                    offset: true,
                    ticks: {
                        beginAtZero: false,
                        fontSize: 14
                    },
                    gridLines: {
                        zeroLineWidth: .5,
                        lineWidth: 0
                    }
                }]
            }
        }
    });
});


// Demo-only on-change handlers (modify values with random data)
const randomiseData = function() {
    for (const key in charts) {
        let chart = charts[key];
        let positive = (chart.config.type == 'outlabeledPie');
        chart.data.datasets.forEach(function(dataset) {
            dataset.data = dataset.data.map(function(d) {
                let v = d + Math.floor(5 - Math.random() * 10);
                return positive ? Math.abs(v) : v;
            });
        });
        chart.update();
    }
}

const selectElement = document.querySelector('#area');
selectElement.addEventListener('change', (event) => {
    document.querySelector('h1#area-header').textContent = `${event.target[event.target.selectedIndex].label}`;
    randomiseData();
});

const inputBoxes = document.querySelectorAll('.variable-row > input');
inputBoxes.forEach((input) => {
    input.addEventListener('change', () => {
        randomiseData();  // Add or subtract random amounts from data in all graphs
    });
});

const toggleCommentForm = function() {
    document.querySelectorAll('.comment-form').forEach((e) => {
        e.classList.toggle('hide');
    })
    document.querySelectorAll('.socialmedia-login').forEach((e) => {
        e.classList.toggle('hide');
    })
}

// Welcome-message modal. Show on page open (hide with cookie on final version)
document.addEventListener('DOMContentLoaded', function() {
    let elem = document.querySelector('#modal-welcome');
    let instance = M.Modal.getInstance(elem);
    instance.open();
});