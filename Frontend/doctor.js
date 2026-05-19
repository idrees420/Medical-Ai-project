const API_BASE_URL = 'https://fyp-backend-xvuk.onrender.com';

// DOM Elements
const loginSection = document.getElementById('doctor-login-section');
const dashboardSection = document.getElementById('doctor-dashboard');
const logoutBtn = document.getElementById('doctor-logout');
const appointmentsList = document.getElementById('doctor-appointments-list');
const doctorWelcome = document.getElementById('doctor-welcome');

// Stats and Schedule Elements
const totalCountEl = document.getElementById('total-count');
const confirmedCountEl = document.getElementById('confirmed-count');
const displayAvailability = document.getElementById('display-availability');
const displayHours = document.getElementById('display-hours');
const editScheduleBtn = document.getElementById('edit-schedule-btn');
const scheduleEditForm = document.getElementById('schedule-edit-form');
const saveScheduleBtn = document.getElementById('save-schedule-btn');
const cancelScheduleBtn = document.getElementById('cancel-schedule-btn');
const editAvailabilityInput = document.getElementById('edit-availability');
const editHoursInput = document.getElementById('edit-hours');
const displayFee = document.getElementById('display-fee');
const editFeeInput = document.getElementById('edit-fee');

// Auth UI Toggles
const showLoginBtn = document.getElementById('show-login');
const showSignupBtn = document.getElementById('show-signup');
const loginForm = document.getElementById('doctor-login-form');
const signupForm = document.getElementById('doctor-signup-form');
const loginSubtitle = document.getElementById('login-subtitle');

// State
let currentDoctorId = localStorage.getItem('doctorId');

// Initial Load
if (currentDoctorId) {
    showDashboard();
}

// UI Toggles
if (showSignupBtn) {
    showSignupBtn.addEventListener('click', (e) => {
        e.preventDefault();
        loginForm.style.display = 'none';
        signupForm.style.display = 'block';
        loginSubtitle.innerText = 'Register your medical profile';
    });
}

if (showLoginBtn) {
    showLoginBtn.addEventListener('click', (e) => {
        e.preventDefault();
        signupForm.style.display = 'none';
        loginForm.style.display = 'block';
        loginSubtitle.innerText = 'Secure Access Dashboard';
    });
}

// Signup Submission
if (signupForm) {
    signupForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const signupData = {
            full_name: document.getElementById('signup-name').value,
            email: document.getElementById('signup-email').value,
            phone: document.getElementById('signup-phone').value,
            specialization: document.getElementById('signup-spec').value,
            password: document.getElementById('signup-password').value
        };

        try {
            const resp = await fetch(`${API_BASE_URL}/doctor/signup`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(signupData)
            });

            if (resp.ok) {
                alert('Account created! Please sign in.');
                showLoginBtn.click();
            } else {
                const err = await resp.json();
                alert(err.detail || 'Signup failed');
            }
        } catch (err) {
            alert('Signup error. Check console.');
        }
    });
}

// Login Submission
if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;

        try {
            const resp = await fetch(`${API_BASE_URL}/doctor/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });

            if (resp.ok) {
                const data = await resp.json();
                localStorage.setItem('doctorId', data.id);
                localStorage.setItem('doctorName', data.full_name);
                localStorage.setItem('availability', data.availability);
                localStorage.setItem('workingHours', data.working_hours);
                localStorage.setItem('fee', data.fee || '1000');
                currentDoctorId = data.id;
                showDashboard();
            } else {
                const err = await resp.json();
                alert(err.detail || 'Login failed');
            }
        } catch (err) {
            alert('Login error. Check console.');
        }
    });
}

// Schedule Management
if (editScheduleBtn) {
    editScheduleBtn.addEventListener('click', () => {
        editAvailabilityInput.value = localStorage.getItem('availability') || "Mon-Fri";
        editHoursInput.value = localStorage.getItem('workingHours') || "09:00 - 17:00";
        if(editFeeInput) editFeeInput.value = localStorage.getItem('fee') || "1000";
        scheduleEditForm.style.display = 'block';
    });
}

if (cancelScheduleBtn) {
    cancelScheduleBtn.addEventListener('click', () => {
        scheduleEditForm.style.display = 'none';
    });
}

if (saveScheduleBtn) {
    saveScheduleBtn.addEventListener('click', async () => {
        const availability = editAvailabilityInput.value;
        const workingHours = editHoursInput.value;
        const fee = editFeeInput ? editFeeInput.value : "1000";

        try {
            const resp = await fetch(`${API_BASE_URL}/doctor/${currentDoctorId}/availability`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ availability: availability, working_hours: workingHours, fee: fee })
            });

            if (resp.ok) {
                localStorage.setItem('availability', availability);
                localStorage.setItem('workingHours', workingHours);
                localStorage.setItem('fee', fee);
                displayAvailability.innerText = availability;
                displayHours.innerText = workingHours;
                if(displayFee) displayFee.innerText = fee;
                scheduleEditForm.style.display = 'none';
            } else {
                alert('Failed to update schedule');
            }
        } catch (err) {
            alert('Error updating schedule');
        }
    });
}

logoutBtn.addEventListener('click', () => {
    localStorage.clear();
    location.reload();
});

function showDashboard() {
    loginSection.style.display = 'none';
    dashboardSection.classList.remove('hidden');
    doctorWelcome.textContent = `Welcome back, Dr. ${localStorage.getItem('doctorName')}`;

    // Update schedule display
    displayAvailability.innerText = localStorage.getItem('availability') || "Mon-Fri";
    displayHours.innerText = localStorage.getItem('workingHours') || "09:00 - 17:00";
    if(displayFee) displayFee.innerText = localStorage.getItem('fee') || "1000";

    fetchDoctorAppointments();
}

async function fetchDoctorAppointments() {
    try {
        const response = await fetch(`${API_BASE_URL}/doctor/appointments/${currentDoctorId}`);
        if (!response.ok) throw new Error('Failed to fetch appointments');

        const appointments = await response.json();
        renderDoctorAppointments(appointments);
        updateStats(appointments);
    } catch (error) {
        appointmentsList.innerHTML = `<p class="empty-msg" style="color: #ef4444;">Error: ${error.message}</p>`;
    }
}

function updateStats(appointments) {
    totalCountEl.innerText = appointments.length;
    confirmedCountEl.innerText = appointments.filter(a => a.status === 'confirmed').length;
}

function renderDoctorAppointments(appointments) {
    if (appointments.length === 0) {
        appointmentsList.innerHTML = '<p class="empty-msg">No appointments assigned to you.</p>';
        return;
    }

    appointmentsList.innerHTML = '';
    appointments.forEach(app => {
        const item = document.createElement('div');
        item.className = 'appointment-card';

        const statusClass = app.status === 'pending' ? 'badge-pending' : 'badge-confirmed';

        item.innerHTML = `
            <span class="status-badge ${statusClass}">${app.status}</span>
            <div class="patient-info">
                <div style="color: #60a5fa; font-size: 0.8rem; font-weight: 700; margin-bottom: 0.25rem;">PATIENT</div>
                <h3>${app.patient_name}</h3>
            </div>
            
            <div class="info-row"><i class="far fa-calendar"></i> ${new Date(app.date).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })}</div>
            <div class="info-row"><i class="far fa-clock"></i> ${app.time}</div>
            
            ${app.predicted_disease ? `
                <div class="diagnosis-box">
                    <span class="diagnosis-label">AI Diagnosis Context</span>
                    <p style="margin:0; font-size: 0.9rem; color: #cbd5e1;">${app.predicted_disease}</p>
                </div>
            ` : ''}

            <div class="action-btns">
                ${app.status === 'pending' ? `
                    <button onclick="updateStatus(${app.id}, 'confirmed')" class="btn-primary" style="margin:0; flex: 1; padding: 0.6rem; font-size: 0.9rem; background: #10b981;">Confirm</button>
                    <button onclick="updateStatus(${app.id}, 'cancelled')" class="btn-primary" style="margin:0; flex: 1; padding: 0.6rem; font-size: 0.9rem; background: rgba(239, 68, 68, 0.2); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.2);">Decline</button>
                ` : `
                    <button disabled class="btn-primary" style="margin:0; width: 100%; padding: 0.6rem; font-size: 0.9rem; background: rgba(255,255,255,0.05); color: #64748b; cursor: default;">Action Taken</button>
                `}
            </div>
        `;
        appointmentsList.appendChild(item);
    });
}

async function updateStatus(appointmentId, status) {
    try {
        const response = await fetch(`${API_BASE_URL}/appointment/${appointmentId}/status`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status })
        });

        if (!response.ok) throw new Error('Update failed');

        fetchDoctorAppointments();
    } catch (error) {
        alert("Ops! Failed to update: " + error.message);
    }
}

window.updateStatus = updateStatus;
