// static/js/charts.js
document.addEventListener('DOMContentLoaded', function() {
    console.log("Charts.js cargado");
    console.log("Datos de gráficos:", chartData);

    // Gráfico de Habilidades más demandadas
    if (document.getElementById('skillsChart')) {
        try {
            const ctx = document.getElementById('skillsChart').getContext('2d');
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: chartData.skills.labels,
                    datasets: [{
                        label: 'Habilidades más demandadas',
                        data: chartData.skills.data,
                        backgroundColor: '#007bff',
                        borderColor: '#0056b3',
                        borderWidth: 1
                    }]
                },
                options: {
                    scales: { y: { beginAtZero: true } },
                    plugins: { legend: { display: true } }
                }
            });
        } catch (e) {
            console.error('Error rendering skills chart:', e);
        }
    }

    // Gráfico de Ofertas por fuente
    if (document.getElementById('sourcesChart')) {
        try {
            const ctx = document.getElementById('sourcesChart').getContext('2d');
            new Chart(ctx, {
                type: 'pie',
                data: {
                    labels: chartData.sources.labels,
                    datasets: [{
                        label: 'Ofertas por fuente',
                        data: chartData.sources.data,
                        backgroundColor: ['#007bff', '#0056b3'],
                        borderColor: '#ffffff',
                        borderWidth: 1
                    }]
                },
                options: {
                    plugins: { legend: { display: true } }
                }
            });
        } catch (e) {
            console.error('Error rendering sources chart:', e);
        }
    }

    // Gráfico de Habilidades futuras
    if (document.getElementById('futureSkillsChart')) {
        try {
            const ctx = document.getElementById('futureSkillsChart').getContext('2d');
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: chartData.futureSkills.labels,
                    datasets: [{
                        label: 'Demanda Promedio (próximos 30 días)',
                        data: chartData.futureSkills.data,
                        backgroundColor: '#007bff',
                        borderColor: '#0056b3',
                        borderWidth: 1
                    }]
                },
                options: {
                    scales: { y: { beginAtZero: true } },
                    plugins: { legend: { display: true } }
                }
            });
        } catch (e) {
            console.error('Error rendering future skills chart:', e);
        }
    }
});