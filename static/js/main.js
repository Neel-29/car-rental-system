// Main JavaScript for Car Rental System

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Form validation
    initializeFormValidation();
    
    // Initialize dashboard features
    initializeDashboard();
});

// Form validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
}

// Dashboard initialization
function initializeDashboard() {
    // Initialize charts if they exist
    if (typeof Chart !== 'undefined') {
        initializeCharts();
    }
    
    // Initialize real-time updates
    initializeRealTimeUpdates();
}

// Chart initialization
function initializeCharts() {
    // Revenue chart
    const revenueCtx = document.getElementById('revenueChart');
    if (revenueCtx) {
        new Chart(revenueCtx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Revenue',
                    data: [12000, 19000, 3000, 5000, 2000, 3000],
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
}

// Real-time updates
function initializeRealTimeUpdates() {
    // Update dashboard stats every 30 seconds
    setInterval(updateDashboardStats, 30000);
}

// Update dashboard statistics
async function updateDashboardStats() {
    try {
        const response = await fetch('/api/dashboard/stats');
        if (response.ok) {
            const stats = await response.json();
            updateStatsDisplay(stats);
        }
    } catch (error) {
        console.error('Error updating dashboard stats:', error);
    }
}

// Update stats display
function updateStatsDisplay(stats) {
    // Update various stat elements
    const elements = {
        'totalUsers': stats.total_users,
        'totalCars': stats.total_cars,
        'activeRentals': stats.active_rentals,
        'totalRevenue': stats.total_revenue
    };
    
    Object.keys(elements).forEach(key => {
        const element = document.getElementById(key);
        if (element) {
            animateNumber(element, elements[key]);
        }
    });
}

// Animate number changes
function animateNumber(element, targetNumber) {
    const currentNumber = parseInt(element.textContent) || 0;
    const increment = (targetNumber - currentNumber) / 20;
    let current = currentNumber;
    
    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= targetNumber) || 
            (increment < 0 && current <= targetNumber)) {
            current = targetNumber;
            clearInterval(timer);
        }
        element.textContent = Math.floor(current);
    }, 50);
}

// Utility functions
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function formatDateTime(dateString) {
    return new Date(dateString).toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Car management functions
function viewCar(carId) {
    // Implement car details modal or page
    console.log('Viewing car:', carId);
    // You can implement a modal or redirect to car details page
}

function editCar(carId) {
    // Implement car edit functionality
    console.log('Editing car:', carId);
    // Redirect to edit car page or open edit modal
    window.location.href = `/cars/edit/${carId}`;
}

function deleteCar(carId) {
    if (confirm('Are you sure you want to delete this car?')) {
        fetch(`/api/cars/${carId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Error deleting car: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error deleting car');
        });
    }
}

// Rental management functions
function cancelRental(rentalId) {
    if (confirm('Are you sure you want to cancel this rental?')) {
        fetch(`/api/rentals/${rentalId}/cancel`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Error canceling rental: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error canceling rental');
        });
    }
}

// Monitoring functions
function startDriverMonitoring(rentalId) {
    window.location.href = `/monitor/${rentalId}`;
}

// Search and filter functions
function initializeSearch() {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(performSearch, 300));
    }
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function performSearch(event) {
    const query = event.target.value;
    // Implement search functionality
    console.log('Searching for:', query);
}

// Notification functions
function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        const bsAlert = new bootstrap.Alert(alertDiv);
        bsAlert.close();
    }, 5000);
}

// API helper functions
async function apiCall(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}

// Export functions for global use
window.CarRental = {
    formatCurrency,
    formatDate,
    formatDateTime,
    viewCar,
    editCar,
    deleteCar,
    cancelRental,
    startDriverMonitoring,
    showNotification,
    apiCall
};
