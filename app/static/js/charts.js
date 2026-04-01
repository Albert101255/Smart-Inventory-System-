// Risograph Chart.js defaults
// Called from individual template pages with their own data

function initLineChart(elementId, labels, inData, outData) {
    const ctx = document.getElementById(elementId);
    if (!ctx) return;
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Stock IN',
                    data: inData,
                    borderColor: '#4ECDC4',
                    backgroundColor: 'rgba(78,205,196,0.1)',
                    borderWidth: 3,
                    tension: 0,
                    pointBackgroundColor: '#4ECDC4',
                    pointBorderColor: '#1A237E',
                    pointBorderWidth: 1,
                    pointRadius: 4,
                    pointHoverRadius: 6
                },
                {
                    label: 'Stock OUT',
                    data: outData,
                    borderColor: '#FF6B6B',
                    backgroundColor: 'rgba(255,107,107,0.1)',
                    borderWidth: 3,
                    tension: 0,
                    pointBackgroundColor: '#FF6B6B',
                    pointBorderColor: '#1A237E',
                    pointBorderWidth: 1,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { 
                legend: { 
                    position: 'top',
                    labels: { 
                        font: { family: 'Courier New', weight: 'bold', size: 10 }, 
                        color: '#1A237E',
                        padding: 20,
                        usePointStyle: true
                    } 
                },
                tooltip: {
                    backgroundColor: '#1A237E',
                    titleFont: { family: 'Courier New' },
                    bodyFont: { family: 'Courier New' },
                    cornerRadius: 0,
                    displayColors: false
                }
            },
            scales: {
                x: { 
                    ticks: { font: { family: 'Courier New', size: 10 }, color: '#1A237E' }, 
                    grid: { color: 'rgba(26,35,126,0.06)', drawTicks: false } 
                },
                y: { 
                    beginAtZero: true,
                    ticks: { font: { family: 'Courier New', size: 10 }, color: '#1A237E' }, 
                    grid: { color: 'rgba(26,35,126,0.06)', drawTicks: false } 
                }
            }
        }
    });
}

function initBarChart(elementId, labels, data) {
    const ctx = document.getElementById(elementId);
    if (!ctx) return;
    const colors = ['#FF6B6B','#4ECDC4','#FFE66D','#6A0572','#1A237E','#FF6B6B','#4ECDC4','#FFE66D'];
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Units Consumed',
                data: data,
                backgroundColor: colors.slice(0, data.length),
                borderColor: '#1A237E',
                borderWidth: 2,
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { 
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#1A237E',
                    titleFont: { family: 'Courier New' },
                    bodyFont: { family: 'Courier New' },
                    cornerRadius: 0
                }
            },
            scales: {
                x: { 
                    ticks: { font: { family: 'Courier New', size: 10 }, color: '#1A237E' }, 
                    grid: { display: false } 
                },
                y: { 
                    beginAtZero: true,
                    ticks: { font: { family: 'Courier New', size: 10 }, color: '#1A237E' }, 
                    grid: { color: 'rgba(26,35,126,0.06)' } 
                }
            }
        }
    });
}

function initDoughnutChart(elementId, labels, data) {
    const ctx = document.getElementById(elementId);
    if (!ctx) return;
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: ['#FF6B6B','#4ECDC4','#FFE66D','#6A0572','#1A237E'],
                borderColor: '#FFF9E5',
                borderWidth: 4,
                hoverOffset: 10
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { 
                    position: 'bottom', 
                    labels: { 
                        font: { family: 'Courier New', size: 10, weight: 'bold' }, 
                        color: '#1A237E', 
                        padding: 20,
                        usePointStyle: true
                    } 
                },
                tooltip: {
                    backgroundColor: '#1A237E',
                    titleFont: { family: 'Courier New' },
                    bodyFont: { family: 'Courier New' },
                    cornerRadius: 0
                }
            },
            cutout: '65%'
        }
    });
}

// Cursor script
document.addEventListener('DOMContentLoaded', () => {
    const cursor = document.getElementById('cursor');
    const ring = document.getElementById('cursor-ring');
    const shadow = document.getElementById('cursor-shadow');
    if (!cursor) return;

    document.addEventListener('mousemove', e => {
        cursor.style.left = e.clientX + 'px';
        cursor.style.top = e.clientY + 'px';
    });

    const hoverElements = 'a, button, .riso-btn, .nav-item, .riso-card, .stat-card, input, select, textarea, .badge, .page-link';
    
    function addHoverListeners() {
        document.querySelectorAll(hoverElements).forEach(el => {
            el.addEventListener('mouseenter', () => document.body.classList.add('hovering'));
            el.addEventListener('mouseleave', () => document.body.classList.remove('hovering'));
        });
    }

    addHoverListeners();

    // Observer for dynamic content
    const observer = new MutationObserver(() => addHoverListeners());
    observer.observe(document.body, { childList: true, subtree: true });

    // Grain canvas
    const canvas = document.getElementById('grain');
    if (canvas) {
        const ctx2 = canvas.getContext('2d');
        canvas.width = 300; canvas.height = 300;
        function grain() {
            const img = ctx2.createImageData(300, 300);
            for (let i = 0; i < img.data.length; i += 4) {
                const v = Math.random() * 255 | 0;
                img.data[i] = img.data[i+1] = img.data[i+2] = v;
                img.data[i+3] = 255;
            }
            ctx2.putImageData(img, 0, 0);
        }
        grain();
        setInterval(grain, 60);
    }

    // Delete confirmation modals
    window.confirmDelete = function(message, actionUrl) {
        const modal = document.getElementById('confirm-modal');
        const msgEl = document.getElementById('confirm-message');
        const formEl = document.getElementById('confirm-form');
        
        if (modal && msgEl && formEl) {
            msgEl.textContent = message;
            formEl.action = actionUrl;
            modal.classList.add('active');
        }
    };

    document.getElementById('cancel-modal')?.addEventListener('click', () => {
        document.getElementById('confirm-modal').classList.remove('active');
    });

    // Close alert messages automatically
    setTimeout(() => {
        document.querySelectorAll('.flash').forEach(el => {
            el.style.transition = 'opacity 1s, transform 1s';
            el.style.opacity = '0';
            el.style.transform = 'translateY(-20px)';
            setTimeout(() => el.remove(), 1000);
        });
    }, 4000);
});
