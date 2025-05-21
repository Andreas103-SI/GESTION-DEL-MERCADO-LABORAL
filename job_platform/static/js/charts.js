// static/js/charts.js
document.addEventListener('DOMContentLoaded', function() {
    if (typeof Chart === 'undefined') {
        console.error('Chart.js no está cargado. Verifica el script de Chart.js.');
        return;
    }

    // Gráfico de Habilidades más demandadas
    new Chart(document.getElementById('skillsChart'), {
        type: 'bar',
        data: {
            labels: chartData.skills.labels,
            datasets: [{
                label: 'Ofertas',
                data: chartData.skills.data,
                backgroundColor: ['#007bff', '#28a745', '#dc3545', '#ffc107', '#6f42c1', '#17a2b8', '#343a40', '#e83e8c', '#20c997', '#fd7e14']
            }]
        },
        options: {
            scales: { y: { beginAtZero: true } }
        }
    });

    // Gráfico de Ofertas por fuente
    new Chart(document.getElementById('sourcesChart'), {
        type: 'pie',
        data: {
            labels: chartData.sources.labels,
            datasets: [{
                data: chartData.sources.data,
                backgroundColor: ['#007bff', '#28a745']
            }]
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
                borderColor: '#007bff',
                fill: false
            }]
        },
        options: {
            scales: { y: { beginAtZero: true } }
        }
    });
});