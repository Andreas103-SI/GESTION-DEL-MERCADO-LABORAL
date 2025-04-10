// static/js/charts.js
document.addEventListener('DOMContentLoaded', function() {
    console.log("Charts.js cargado");
    console.log("skillsLabels desde JS:", window.skillsLabels);
    console.log("skillsData desde JS:", window.skillsData);
    console.log("sourcesLabels desde JS:", window.sourcesLabels);
    console.log("sourcesData desde JS:", window.sourcesData);

    const skillsCtx = document.getElementById('skillsChart').getContext('2d');
    const skillsChart = new Chart(skillsCtx, {
        type: 'bar',
        data: {
            labels: window.skillsLabels,
            datasets: [{
                label: 'Número de Ofertas',
                data: window.skillsData,
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: { beginAtZero: true }
            }
        }
    });

    const sourcesCtx = document.getElementById('sourcesChart').getContext('2d');
    const sourcesChart = new Chart(sourcesCtx, {
        type: 'pie',
        data: {
            labels: window.sourcesLabels,
            datasets: [{
                label: 'Ofertas por Fuente',
                data: window.sourcesData,
                backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56'],
            }]
        }
    });
});