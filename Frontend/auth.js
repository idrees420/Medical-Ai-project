const API_BASE_URL = 'https://fyp-backend-xvuk.onrender.com';

// DOM Elements
const loginCard = document.getElementById('login-card');
const signupCard = document.getElementById('signup-card');
const showSignupBtn = document.getElementById('show-signup');
const showLoginBtn = document.getElementById('show-login');

// Forms & Inputs
const loginForm = document.getElementById('login-form');
const signupForm = document.getElementById('signup-form');
const loginError = document.getElementById('login-error');
const signupError = document.getElementById('signup-error');

// Buttons
const loginBtn = document.getElementById('login-btn');
const signupBtn = document.getElementById('signup-btn');
const loginLoader = document.getElementById('login-loader');
const signupLoader = document.getElementById('signup-loader');

// Toggle Views
showSignupBtn.addEventListener('click', (e) => {
    e.preventDefault();
    loginCard.classList.add('hidden');
    signupCard.classList.remove('hidden');
    signupError.classList.add('hidden');
});

showLoginBtn.addEventListener('click', (e) => {
    e.preventDefault();
    signupCard.classList.add('hidden');
    loginCard.classList.remove('hidden');
    loginError.classList.add('hidden');
});

// Generic generic submit logic
async function handleAuth(url, credentials, formType) {
    const errorEl = formType === 'login' ? loginError : signupError;
    const btnText = (formType === 'login' ? loginBtn : signupBtn).querySelector('.btn-text');
    const loader = formType === 'login' ? loginLoader : signupLoader;
    const btn = formType === 'login' ? loginBtn : signupBtn;

    // Reset UI
    errorEl.classList.add('hidden');
    btn.disabled = true;
    btnText.classList.add('hidden');
    loader.classList.remove('hidden');

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(credentials)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Authentication failed');
        }

        // Save full name or user ID locally
        localStorage.setItem('userFullName', data.full_name);
        localStorage.setItem('userEmail', data.email);

        // Redirect to main app
        window.location.href = 'index.html';

    } catch (error) {
        errorEl.textContent = error.message;
        errorEl.classList.remove('hidden');
    } finally {
        btn.disabled = false;
        btnText.classList.remove('hidden');
        loader.classList.add('hidden');
    }
}

// Event Listeners
loginForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const email = document.getElementById('login-email').value.trim();
    const password = document.getElementById('login-password').value.trim();

    if (!email || !password) return;

    handleAuth(`${API_BASE_URL}/login`, { email, password }, 'login');
});

signupForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const full_name = document.getElementById('signup-full-name').value.trim();
    const email = document.getElementById('signup-email').value.trim();
    const phone = document.getElementById('signup-phone').value.trim();
    const password = document.getElementById('signup-password').value.trim();

    if (!full_name || !email || !password) return;

    handleAuth(`${API_BASE_URL}/signup`, { full_name, email, phone, password }, 'signup');
});
