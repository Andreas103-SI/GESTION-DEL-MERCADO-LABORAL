// static/js/charts.js
document.addEventListener('DOMContentLoaded', function() {
    if (typeof Chart === 'undefined') {
        console.error('Chart.js no está cargado. Verifica el script de Chart.js.');
        return;
    }

    // Configuración global para alta resolución
    Chart.defaults.set('devicePixelRatio', window.devicePixelRatio || 1);
    Chart.defaults.backgroundColor = '#1a1a1a';
    Chart.defaults.borderColor = '#333333';
    Chart.defaults.color = '#cccccc';

    // Debug para verificar los datos
    console.log('Chart Data:', chartData);

    // Gráfico de Habilidades más demandadas (Barra)
    new Chart(document.getElementById('skillsChart'), {
        type: 'bar',
        data: {
            labels: chartData.skills.labels,
            datasets: [{
                label: 'Ofertas',
                data: chartData.skills.data,
                backgroundColor: [
                    '#4CAF50', '#2196F3', '#FF5722', '#9C27B0', '#FFC107',
                    '#00BCD4', '#E91E63', '#8BC34A', '#FF9800', '#607D8B'
                ],
                borderColor: '#333333',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                x: { grid: { color: '#333333' }, ticks: { color: '#cccccc' } },
                y: { beginAtZero: true, grid: { color: '#333333' }, ticks: { color: '#cccccc' } }
            },
            plugins: {
                legend: { labels: { color: '#cccccc' } }
            }
        }
    });

    // Gráfico de Ofertas por fuente (Pie)
    new Chart(document.getElementById('sourcesChart'), {
        type: 'pie',
        data: {
            labels: chartData.sources.labels,
            datasets: [{
                data: chartData.sources.data,
                backgroundColor: ['#4CAF50', '#2196F3'],
                borderColor: '#333333',
                borderWidth: 1
            }]
        },
        options: {
            plugins: { legend: { labels: { color: '#cccccc' } } }
        }
    });

    // Gráfico de Habilidades futuras (Línea)
    new Chart(document.getElementById('futureSkillsChart'), {
        type: 'line',
        data: {
            labels: chartData.futureSkills.labels,
            datasets: [{
                label: 'Demanda Promedio',
                data: chartData.futureSkills.data,
                borderColor: '#4CAF50',
                backgroundColor: 'rgba(76, 175, 80, 0.2)',
                fill: true,
                borderWidth: 2,
                pointBackgroundColor: '#2196F3',
                pointBorderColor: '#333333',
                pointRadius: 4
            }]
        },
        options: {
            scales: {
                x: { grid: { color: '#333333' }, ticks: { color: '#cccccc' } },
                y: { beginAtZero: true, grid: { color: '#333333' }, ticks: { color: '#cccccc' } }
            },
            plugins: { legend: { labels: { color: '#cccccc' } } }
        }
    });

    // Gráfico de Comparación 
    if (document.getElementById('comparisonChart')) {
        new Chart(document.getElementById('comparisonChart'), {
            type: 'bar',
            data: {
                labels: chartData.comparison.labels,
                datasets: chartData.comparison.datasets.map(dataset => ({
                    ...dataset,
                    backgroundColor: dataset.backgroundColor || '#4CAF50',
                    borderColor: '#333333',
                    borderWidth: 1
                }))
            },
            options: {
                scales: {
                    x: { grid: { color: '#333333' }, ticks: { color: '#cccccc' } },
                    y: { beginAtZero: true, grid: { color: '#333333' }, ticks: { color: '#cccccc' } }
                },
                plugins: { legend: { labels: { color: '#cccccc' } } }
            }
        });   
     }
});