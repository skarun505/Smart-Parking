const API_BASE = 'http://localhost:5001/api';

// Global Fetch Interceptor to always include cross-origin credentials (cookies)
const originalFetch = window.fetch;
window.fetch = async function () {
    let [resource, config] = arguments;
    if (typeof resource === 'string' && resource.startsWith(API_BASE)) {
        if (!config) config = {};
        config.credentials = 'include';
    }
    return originalFetch(resource, config);
};

// Handle Registration
const registerForm = document.getElementById('registerForm');
if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const name = document.getElementById('name').value;
        const email = document.getElementById('email').value;
        const phone = document.getElementById('phone').value;
        const password = document.getElementById('password').value;
        const confirm_password = document.getElementById('confirm_password').value;
        const errorDiv = document.getElementById('registerError');
        const btn = document.getElementById('registerBtn');

        if (password !== confirm_password) {
            errorDiv.textContent = 'Passwords do not match';
            errorDiv.style.display = 'block';
            return;
        }

        btn.disabled = true;
        btn.textContent = 'Registering...';

        try {
            const res = await fetch(`${API_BASE}/auth/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, email, phone, password })
            });

            const data = await res.json();

            if (res.ok && data.success) {
                window.location.href = 'index.html';
            } else {
                errorDiv.textContent = data.message || 'Registration failed';
                errorDiv.style.display = 'block';
            }
        } catch (err) {
            errorDiv.textContent = 'Network error. Please try again.';
            errorDiv.style.display = 'block';
        } finally {
            btn.disabled = false;
            btn.textContent = 'Register';
        }
    });
}

// Handle Login
const loginForm = document.getElementById('loginForm');
if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const errorDiv = document.getElementById('loginError');
        const btn = document.getElementById('loginBtn');

        btn.disabled = true;
        btn.textContent = 'Logging in...';

        try {
            const res = await fetch(`${API_BASE}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });

            const data = await res.json();

            if (res.ok && data.success) {
                // Determine base path to redirect correctly based on current location
                const pathParts = window.location.pathname.split('/');
                pathParts.pop(); // remove index.html
                const basePath = pathParts.join('/');

                // Redirect logic
                // Provide a cleaner URL assuming from root
                window.location.href = data.redirect_url.startsWith('/') ? `.${data.redirect_url}` : data.redirect_url;
            } else {
                errorDiv.textContent = data.message || 'Invalid credentials';
                errorDiv.style.display = 'block';
            }
        } catch (err) {
            errorDiv.textContent = 'Network error. Please try again.';
            errorDiv.style.display = 'block';
        } finally {
            btn.disabled = false;
            btn.textContent = 'Login';
        }
    });
}

// Handle Logout globally
async function logout() {
    try {
        await fetch(`${API_BASE}/auth/logout`, { method: 'POST' });
        window.location.href = '../index.html';
    } catch (err) {
        console.error('Logout error', err);
        window.location.href = '../index.html';
    }
}
