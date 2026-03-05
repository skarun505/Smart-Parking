// General utilities or global admin scripts can go here
// Currently, most page-specific logic is embedded in the HTML files for simplicity
// But we keep this file as structured in the spec for future expansions.

document.addEventListener('DOMContentLoaded', () => {
    // Check auth for admin pages
    fetch(`${API_BASE}/auth/me`)
        .then(res => {
            if (!res.ok) {
                window.location.href = '../index.html';
                throw new Error('Unauthorized');
            }
            return res.json();
        })
        .then(data => {
            if (data.user.role !== 'admin') {
                window.location.href = '../user/dashboard.html';
            }
        })
        .catch(err => console.error(err));
});

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
