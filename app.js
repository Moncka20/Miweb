/**
 * Feature Flag & Theme Management System
 * Demonstrates the 3-ticket breakdown for Dark Mode Rollout.
 */

// Simulated Current User Profile
const currentUser = {
  id: 'usr_98472',
  name: 'Admin Dev',
  cohortPercentile: 7 // Falls into 0-9% (qualifies for 10% canary)
};

// State Configuration for the 3 Tickets
const TICKET_CONFIGS = {
  'ticket-1': {
    name: 'Ticket 1: Tema Raíz (Flag OFF)',
    flagEnabled: false,
    rolloutPercent: 0,
    allowPersistence: false,
    description: 'Variables CSS listas en :root, lógica lista, pero flag apagado.'
  },
  'ticket-2': {
    name: 'Ticket 2: Canary 10% (Sin Persistencia)',
    flagEnabled: true,
    rolloutPercent: 10,
    allowPersistence: false,
    description: 'Toggle visible solo al 10% de usuarios. Preferencia no persiste al recargar.'
  },
  'ticket-3': {
    name: 'Ticket 3: GA 100% + Persistencia (localStorage)',
    flagEnabled: true,
    rolloutPercent: 100,
    allowPersistence: true,
    description: 'Rollout al 100%. Preferencia guardada en localStorage.'
  }
};

const STORAGE_KEY = 'nexus_dash_theme_preference';
let currentTicket = 'ticket-3';
let activeTheme = 'light';

/**
 * Evaluates whether the current user is eligible for the feature flag
 */
function isFeatureEnabled(ticketKey, user) {
  const config = TICKET_CONFIGS[ticketKey];
  if (!config.flagEnabled) return false;
  return user.cohortPercentile < config.rolloutPercent;
}

/**
 * Applies theme to the document root (:root / <html>)
 */
function applyTheme(theme) {
  activeTheme = theme;
  document.documentElement.setAttribute('data-theme', theme);
  
  // Update toggle button text and runtime info
  const toggleLabel = document.getElementById('toggle-label');
  if (toggleLabel) {
    toggleLabel.textContent = theme === 'dark' ? 'Modo Claro' : 'Modo Oscuro';
  }
  
  const infoTheme = document.getElementById('info-theme-applied');
  if (infoTheme) {
    infoTheme.textContent = theme;
  }
}

/**
 * Toggles current theme respecting ticket persistence rules
 */
function toggleTheme() {
  const nextTheme = activeTheme === 'dark' ? 'light' : 'dark';
  applyTheme(nextTheme);

  const config = TICKET_CONFIGS[currentTicket];
  if (config.allowPersistence) {
    // Ticket 3: Persist to storage
    localStorage.setItem(STORAGE_KEY, nextTheme);
  } else {
    // Ticket 2: Clear any previous persistence
    localStorage.removeItem(STORAGE_KEY);
  }
}

/**
 * Initializes and updates UI according to active ticket phase
 */
function renderTicketPhase(ticketKey) {
  currentTicket = ticketKey;
  const config = TICKET_CONFIGS[ticketKey];
  const userEligible = isFeatureEnabled(ticketKey, currentUser);

  // 1. Update Toggle Visibility
  const toggleContainer = document.getElementById('dark-mode-toggle-container');
  if (toggleContainer) {
    if (userEligible) {
      toggleContainer.classList.remove('hidden');
    } else {
      toggleContainer.classList.add('hidden');
    }

  }

  // 2. Resolve Initial Theme
  let initialTheme = 'light';
  if (config.allowPersistence) {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      initialTheme = saved;
    }
  }
  applyTheme(initialTheme);

  // 3. Update Visual Highlight of Active Ticket Box
  ['ticket-box-1', 'ticket-box-2', 'ticket-box-3'].forEach((id, idx) => {
    const el = document.getElementById(id);
    if (el) {
      if (idx === (ticketKey === 'ticket-1' ? 0 : ticketKey === 'ticket-2' ? 1 : 2)) {
        el.classList.add('active-card');
      } else {
        el.classList.remove('active-card');
      }
    }
  });

  // 4. Update Inspector Info Panel
  document.getElementById('info-current-phase').textContent = config.name;
  document.getElementById('info-rollout-pct').textContent = `${config.rolloutPercent}%`;
  document.getElementById('info-user-bucket').textContent = 
    `${currentUser.cohortPercentile}% (${userEligible ? 'Califica para toggle' : 'Excluido / Flag OFF'})`;
  document.getElementById('info-persistence-status').textContent = 
    config.allowPersistence ? 'localStorage (Activa)' : 'Deshabilitada (En memoria temporal)';
  document.getElementById('user-cohort-badge').textContent = 
    `Cohort: ${currentUser.cohortPercentile}% (User ID: ${currentUser.id})`;
}

async function getPaymentUser() {
  return document.getElementById('payment-user-id').value.trim() || 'anonymous_user';
}

async function refreshPaymentFlag() {
  const userId = await getPaymentUser();
  const response = await fetch(`/api/flags/pagos-express-v1?userId=${encodeURIComponent(userId)}`);
  const data = await response.json();
  const enabled = data.enabled === true;
  document.getElementById('payment-flag-state').textContent = enabled ? 'ON' : 'OFF';
  document.getElementById('payments-status-badge').textContent =
    enabled ? `ON · ${data.rollout_percentage}%` : `OFF · ${data.rollout_percentage}%`;
  document.getElementById('payments-status-badge').className =
    `status-pill ${enabled ? 'active' : 'off'}`;
  document.getElementById('payment-flag-source').textContent =
    `Fuente: ${data.source} · Usuario: ${userId}`;
}

async function refreshPaymentMetrics() {
  const response = await fetch('/api/metrics/payments-express');
  const data = await response.json();
  const metrics = data.metrics;
  document.getElementById('metric-attempts').textContent = metrics.attempts;
  document.getElementById('metric-success').textContent = metrics.successful_payments;
  document.getElementById('metric-failures').textContent = metrics.failed_payments;
  document.getElementById('metric-conversion').textContent =
    `${(metrics.conversion_rate * 100).toFixed(1)}%`;
}

async function setLocalPaymentRollout(percentage) {
  const message = document.getElementById('payment-lab-message');
  const response = await fetch('/api/payments/express/test-rollout', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ percentage })
  });
  const data = await response.json();
  message.textContent = response.ok
    ? `Rollout local cambiado a ${data.rollout_percentage}%.`
    : data.error;
  await refreshPaymentFlag();
}

async function submitPaymentCheckout(event) {
  event.preventDefault();
  const result = document.getElementById('payment-result');
  const response = await fetch('/api/payments/express/checkout', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: await getPaymentUser(),
      amount: document.getElementById('payment-amount').value
    })
  });
  result.textContent = JSON.stringify(await response.json(), null, 2);
  await refreshPaymentMetrics();
}

// DOM Setup
document.addEventListener('DOMContentLoaded', () => {
  const toggleButton = document.getElementById('dark-mode-toggle');
  if (toggleButton) {
    toggleButton.addEventListener('click', toggleTheme);
  }

  const ticketSelect = document.getElementById('ticket-select');
  if (ticketSelect) {
    ticketSelect.addEventListener('change', (e) => {
      renderTicketPhase(e.target.value);
    });
  }

  document.getElementById('payment-user-id').addEventListener('change', refreshPaymentFlag);
  document.querySelectorAll('.rollout-button').forEach((button) => {
    button.addEventListener('click', () => setLocalPaymentRollout(Number(button.dataset.percentage)));
  });
  document.getElementById('payment-checkout-form').addEventListener('submit', submitPaymentCheckout);
  document.getElementById('refresh-payment-metrics').addEventListener('click', refreshPaymentMetrics);
  refreshPaymentFlag().catch((error) => {
    document.getElementById('payment-lab-message').textContent = `No se pudo consultar el toggle: ${error.message}`;
  });
  refreshPaymentMetrics().catch(() => {});

  // Initialize at Ticket 3 by default
  renderTicketPhase('ticket-3');
});
