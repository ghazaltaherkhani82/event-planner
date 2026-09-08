const API_BASE = '/api';
let isRegisterMode = false;

// 1. Session Storage Helpers
function getToken() {
  return localStorage.getItem('token');
}

function getUser() {
  const user = localStorage.getItem('user');
  return user ? JSON.parse(user) : null;
}

function setAuth(token, user) {
  localStorage.setItem('token', token);
  localStorage.setItem('user', JSON.stringify(user));
  renderNav();
  loadEvents();
}

function clearAuth() {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  renderNav();
  loadEvents();
}

// 2. Navigation Bar UI
function renderNav() {
  const nav = document.getElementById('nav-actions');
  const user = getUser();
  const createBtn = document.getElementById('btn-open-create');

  if (user) {
    if (user.role === 'ORGANIZER') {
      createBtn.style.display = 'inline-block';
    } else {
      createBtn.style.display = 'none';
    }

    nav.innerHTML = `
      <span style="font-size: 0.9rem; color: var(--text-secondary);">
        Welcome, <strong style="color: var(--text-primary);">${user.username}</strong> (${user.role})
      </span>
      <button class="btn btn-outline" onclick="clearAuth()">Sign Out</button>
    `;
  } else {
    createBtn.style.display = 'none';
    nav.innerHTML = `
      <button class="btn btn-primary" onclick="openAuthModal()">Sign In / Register</button>
    `;
  }
}

// 3. Modal Controllers
function openAuthModal() {
  document.getElementById('auth-modal').classList.add('active');
}

function closeAuthModal() {
  document.getElementById('auth-modal').classList.remove('active');
}

function toggleAuthMode() {
  isRegisterMode = !isRegisterMode;
  const title = document.getElementById('auth-modal-title');
  const roleGroup = document.getElementById('role-group');
  const submitBtn = document.getElementById('auth-submit-btn');
  const toggleLink = document.getElementById('auth-toggle-link');

  if (isRegisterMode) {
    title.innerText = 'Create Account';
    roleGroup.style.display = 'block';
    submitBtn.innerText = 'Sign Up';
    toggleLink.innerText = 'Already have an account? Sign In';
  } else {
    title.innerText = 'Sign In';
    roleGroup.style.display = 'none';
    submitBtn.innerText = 'Sign In';
    toggleLink.innerText = 'Need an account? Sign Up';
  }
}

function openCreateModal() {
  document.getElementById('create-event-modal').classList.add('active');
}

function closeCreateModal() {
  document.getElementById('create-event-modal').classList.remove('active');
}

// 4. API Actions: Authentication
async function handleAuthSubmit(e) {
  e.preventDefault();
  const username = document.getElementById('auth-username').value;
  const password = document.getElementById('auth-password').value;

  const endpoint = isRegisterMode ? `${API_BASE}/accounts/register/` : `${API_BASE}/accounts/login/`;
  const payload = { username, password };

  if (isRegisterMode) {
    payload.role = document.getElementById('auth-role').value;
  }

  try {
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    if (res.ok) {
      setAuth(data.token, data.user);
      closeAuthModal();
    } else {
      alert(JSON.stringify(data));
    }
  } catch (err) {
    alert('Failed to connect to backend server.');
  }
}

// 5. API Actions: Load & Render Events
async function loadEvents() {
  const container = document.getElementById('events-container');
  const headers = {};
  const token = getToken();
  if (token) {
    headers['Authorization'] = `Token ${token}`;
  }

  try {
    const res = await fetch(`${API_BASE}/events/`, { headers });
    const events = await res.json();

    if (!events.length) {
      container.innerHTML = '<p style="color: var(--text-secondary);">No events found.</p>';
      return;
    }

    container.innerHTML = events.map(evt => {
      const user = getUser();
      const isOrganizer = user && user.role === 'ORGANIZER';
      const isParticipant = user && user.role === 'PARTICIPANT';

      return `
        <div class="event-card">
          <div>
            <div class="card-header">
              <span class="badge badge-${evt.status.toLowerCase()}">${evt.status}</span>
              <span style="font-size: 0.8rem; color: var(--text-secondary);">By ${evt.organizer_username}</span>
            </div>
            <h3 class="card-title">${evt.title}</h3>
            <p class="card-desc">${evt.description}</p>
            <div class="card-meta">
              <span><strong>Capacity:</strong> ${evt.registered_count} / ${evt.capacity}</span>
              <span><strong>Starts:</strong> ${new Date(evt.start_time).toLocaleString()}</span>
              <span><strong>Ends:</strong> ${new Date(evt.end_time).toLocaleString()}</span>
            </div>
          </div>
          <div>
            ${isParticipant && evt.status === 'PUBLISHED' ? `
              <button class="btn btn-primary" style="width: 100%;" onclick="registerForEvent(${evt.id})">Register Now</button>
            ` : ''}
            ${isOrganizer && evt.organizer_username === user?.username && evt.status === 'DRAFT' ? `
              <button class="btn btn-primary" style="width: 100%;" onclick="publishEvent(${evt.id})">Publish Event</button>
            ` : ''}
          </div>
        </div>
      `;
    }).join('');
  } catch (err) {
    container.innerHTML = '<p style="color: var(--danger);">Failed to load events list.</p>';
  }
}

// 6. Event Actions
async function registerForEvent(eventId) {
  const token = getToken();
  if (!token) return openAuthModal();

  try {
    const res = await fetch(`${API_BASE}/relations/registrations/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Token ${token}`
      },
      body: JSON.stringify({ event: eventId })
    });

    const data = await res.json();
    if (res.ok) {
      alert('Registered successfully!');
      loadEvents();
    } else {
      alert(JSON.stringify(data));
    }
  } catch (err) {
    alert('Registration error.');
  }
}

async function publishEvent(eventId) {
  const token = getToken();
  try {
    const res = await fetch(`${API_BASE}/events/${eventId}/status/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Token ${token}`
      },
      body: JSON.stringify({ status: 'PUBLISHED' })
    });

    if (res.ok) {
      alert('Event published successfully!');
      loadEvents();
    } else {
      const data = await res.json();
      alert(JSON.stringify(data));
    }
  } catch (err) {
    alert('Error updating status.');
  }
}

async function handleCreateEvent(e) {
  e.preventDefault();
  const token = getToken();
  const payload = {
    title: document.getElementById('event-title').value,
    description: document.getElementById('event-desc').value,
    capacity: parseInt(document.getElementById('event-capacity').value),
    start_time: document.getElementById('event-start').value,
    end_time: document.getElementById('event-end').value
  };

  try {
    const res = await fetch(`${API_BASE}/events/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Token ${token}`
      },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    if (res.ok) {
      closeCreateModal();
      loadEvents();
    } else {
      alert(JSON.stringify(data));
    }
  } catch (err) {
    alert('Error creating event.');
  }
}

window.onload = () => {
  renderNav();
  loadEvents();
};
