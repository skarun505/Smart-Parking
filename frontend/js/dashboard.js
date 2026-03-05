function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    let icon = 'ℹ️';
    if (type === 'success') icon = '✅';
    if (type === 'error') icon = '❌';
    if (type === 'warning') icon = '⚠️';

    toast.innerHTML = `<span>${icon}</span> <span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease reverse forwards';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Mobile sidebar support
document.addEventListener('DOMContentLoaded', () => {
    // Only proceed if there's a header and sidebar
    const headerTitle = document.querySelector('.header-title');
    const sidebar = document.querySelector('.sidebar');

    if (headerTitle && sidebar) {
        // Create hamburger button
        const hamburger = document.createElement('button');
        hamburger.className = 'hamburger';
        hamburger.innerHTML = '☰';

        // Ensure flex layout for header to fit hamburger
        const header = document.querySelector('.header');
        header.style.display = 'flex';
        header.style.flexDirection = 'row';
        header.style.alignItems = 'center';
        header.style.gap = '1rem';

        // Insert hamburger before title
        header.insertBefore(hamburger, headerTitle);

        // Create overlay
        const overlay = document.createElement('div');
        overlay.className = 'sidebar-overlay';
        document.querySelector('.app-container').appendChild(overlay);

        const toggleMenu = () => {
            sidebar.classList.toggle('open');
            overlay.classList.toggle('open');
        };

        hamburger.addEventListener('click', toggleMenu);
        overlay.addEventListener('click', toggleMenu);
    }
});

document.addEventListener('DOMContentLoaded', () => {
    // Check auth and fetch user data to show name
    fetch(`${API_BASE}/auth/me`)
        .then(res => {
            if (!res.ok) {
                window.location.href = '../index.html';
                throw new Error('Unauthorized');
            }
            return res.json();
        })
        .then(data => {
            const userNameEl = document.getElementById('userName');
            if (userNameEl) userNameEl.textContent = data.user.name;
        })
        .catch(err => console.error(err));

    fetchDashboardData();
    setInterval(fetchDashboardData, 30000); // refresh every 30s
});

async function fetchDashboardData() {
    const loader = document.getElementById('loader');
    if (loader) loader.style.display = 'block';

    try {
        const res = await fetch(`${API_BASE}/user/dashboard`);
        if (!res.ok) throw new Error('Failed to fetch stats');
        const data = await res.json();

        // Update DOM
        updateElement('bikeTotal', data.bike_total);
        updateElement('bikeAvailable', data.bike_available);
        updateElement('bikeOccupied', data.bike_occupied);

        updateElement('carTotal', data.car_total);
        updateElement('carAvailable', data.car_available);
        updateElement('carOccupied', data.car_occupied);

        updateElement('totalSlots', data.total_slots);
        updateElement('availableSlots', data.available_slots);
        updateElement('occupiedSlots', data.occupied_slots);

    } catch (err) {
        showToast('Error fetching dashboard data', 'error');
        console.error(err);
    } finally {
        if (loader) loader.style.display = 'none';
    }
}

function updateElement(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
}
