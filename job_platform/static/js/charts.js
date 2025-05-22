// static/js/charts.js
document.addEventListener('DOMContentLoaded', function() {
    if (typeof Chart === 'undefined') {
        console.error('Chart.js no está cargado. Verifica el script de Chart.js.');
        return;
    }

    // Configuración global de Chart.js para el tema oscuro
    Chart.defaults.color = '#cccccc';
    Chart.defaults.borderColor = '#333333';
    Chart.defaults.font.family = 'system-ui, -apple-system, sans-serif';

    // Debug para verificar los datos
    console.log('Chart Data:', chartData);

    // Gráfico de Habilidades más demandadas
    new Chart(document.getElementById('skillsChart'), {
        type: 'bar',
        data: {
            labels: chartData.skills.labels,
            datasets: [{
                label: 'Ofertas',
                data: chartData.skills.data,
                backgroundColor: '#4CAF50',
                borderColor: '#333333',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    labels: {
                        color: '#cccccc'
                    }
                },
                title: {
                    display: true,
                    text: 'Habilidades más demandadas',
                    color: '#4CAF50',
                    font: {
                        size: 16
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: '#333333'
                    },
                    ticks: {
                        color: '#cccccc'
                    }
                },
                x: {
                    grid: {
                        color: '#333333'
                    },
                    ticks: {
                        color: '#cccccc'
                    }
                }
            }
        }
    });

    // Gráfico de Ofertas por fuente
    const sourcesChart = new Chart(document.getElementById('sourcesChart'), {
        type: 'pie',
        data: {
            labels: chartData.sources.labels,
            datasets: [{
                data: chartData.sources.data,
                backgroundColor: ['#4CAF50', '#2196F3', '#FFC107', '#E91E63', '#9C27B0'],
                borderColor: '#333333',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        color: '#cccccc'
                    }
                },
                title: {
                    display: true,
                    text: 'Distribución de ofertas por fuente',
                    color: '#4CAF50',
                    font: {
                        size: 16
                    }
                }
            }
        }
    });

    // Gráfico de Habilidades futuras
    new Chart(document.getElementById('futureSkillsChart'), {
        type: 'line',
        data: {
            labels: chartData.futureSkills.labels,
            datasets: [{
                label: 'Demanda Promedio',
                data: chartData.futureSkills.data,
                borderColor: '#4CAF50',
                backgroundColor: 'rgba(76, 175, 80, 0.1)',
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    labels: {
                        color: '#cccccc'
                    }
                },
                title: {
                    display: true,
                    text: 'Tendencias de habilidades futuras',
                    color: '#4CAF50',
                    font: {
                        size: 16
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: '#333333'
                    },
                    ticks: {
                        color: '#cccccc'
                    }
                },
                x: {
                    grid: {
                        color: '#333333'
                    },
                    ticks: {
                        color: '#cccccc'
                    }
                }
            }
        }
    });

    // Gráfico de Comparación entre plataformas
    const comparisonChartElement = document.getElementById('comparisonChart');
    if (comparisonChartElement) {
        console.log('Creating comparison chart with data:', chartData.comparison);
        const comparisonChart = new Chart(comparisonChartElement, {
            type: 'bar',
            data: {
                ...chartData.comparison,
                datasets: chartData.comparison.datasets.map(dataset => ({
                    ...dataset,
                    borderColor: '#333333',
                    borderWidth: 1
                }))
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            color: '#cccccc'
                        }
                    },
                    title: {
                        display: true,
                        text: 'Comparación de habilidades demandadas por plataforma',
                        color: '#4CAF50',
                        font: {
                            size: 16
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: '#333333'
                        },
                        ticks: {
                            color: '#cccccc'
                        },
                        title: {
                            display: true,
                            text: 'Número de ofertas',
                            color: '#cccccc'
                        }
                    },
                    x: {
                        grid: {
                            color: '#333333'
                        },
                        ticks: {
                            color: '#cccccc'
                        },
                        title: {
                            display: true,
                            text: 'Habilidades',
                            color: '#cccccc'
                        }
                    }
                }
            }
        });
    }
});