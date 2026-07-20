// ─── NAVBAR SCROLL ───────────────────────────
const navbar = document.querySelector('.navbar');
window.addEventListener('scroll', () => {
  navbar.classList.toggle('scrolled', window.scrollY > 40);
});

// ─── COUNTDOWN ───────────────────────────────
function updateCountdown() {
  const worldCup = new Date('2026-07-19T15:00:00');
  const now = new Date();
  const diff = worldCup - now;

  if (diff <= 0) {
    document.getElementById('cd-days').textContent  = '00';
    document.getElementById('cd-hours').textContent = '00';
    document.getElementById('cd-mins').textContent  = '00';
    document.getElementById('cd-secs').textContent  = '00';
    return;
  }

  const days  = Math.floor(diff / (1000 * 60 * 60 * 24));
  const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  const mins  = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
  const secs  = Math.floor((diff % (1000 * 60)) / 1000);

  document.getElementById('cd-days').textContent  = String(days).padStart(2, '0');
  document.getElementById('cd-hours').textContent = String(hours).padStart(2, '0');
  document.getElementById('cd-mins').textContent  = String(mins).padStart(2, '0');
  document.getElementById('cd-secs').textContent  = String(secs).padStart(2, '0');
}
updateCountdown();
setInterval(updateCountdown, 1000);

// ─── SCROLL REVEAL ───────────────────────────
const revealEls = document.querySelectorAll('.card, .content-card, .social-card, .grupo-card, .section-header');
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.style.opacity = '1';
      entry.target.style.transform = entry.target.style.transform.replace('translateY(30px)', 'translateY(0)');
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.1 });

revealEls.forEach(el => {
  el.style.opacity = '0';
  el.style.transform = (el.style.transform || '') + ' translateY(30px)';
  el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
  observer.observe(el);
});

// ─── SMOOTH SCROLL ───────────────────────────
document.querySelectorAll('a[href^="#"]').forEach(link => {
  link.addEventListener('click', e => {
    e.preventDefault();
    const target = document.querySelector(link.getAttribute('href'));
    if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
});

// ─── NEWSLETTER FORM ─────────────────────────
const form = document.getElementById('newsletter-form');
if (form) {
  form.addEventListener('submit', e => {
    e.preventDefault();
    const input = form.querySelector('input');
    const btn   = form.querySelector('button');
    btn.textContent = '✓ ¡Suscrito!';
    btn.style.background = 'linear-gradient(135deg, #00e676, #00b050)';
    input.value = '';
    setTimeout(() => {
      btn.textContent = 'Suscribirme';
      btn.style.background = '';
    }, 3000);
  });
}

// ─── MODAL IA & DATA SCIENCE INTERACTION ─────
const cardIaDs = document.getElementById('card-ia-ds');
const modalIaDs = document.getElementById('modal-ia-ds');
const closeBtn = document.getElementById('modal-close-btn');

// ─── MODAL ANÁLISIS TÁCTICO INTERACTION ────────
const cardAnalisisTactico = document.getElementById('card-analisis-tactico');
const modalAnalisisTactico = document.getElementById('modal-analisis-tactico');
const closeBtnTactico = document.getElementById('modal-close-tactico-btn');

let radarChartInstance = null;
let barChartInstance = null;
let momentumChartInstance = null;

function initCharts() {
  if (typeof Chart === 'undefined') return;

  // Radar Chart
  const radarCtx = document.getElementById('radarChart');
  if (radarCtx) {
    if (radarChartInstance) radarChartInstance.destroy();
    radarChartInstance = new Chart(radarCtx, {
      type: 'radar',
      data: {
        labels: ['xG (Goles)', 'xA (Asist)', 'Pases Clave', 'xG Chain', 'xG Buildup'],
        datasets: [{
          label: 'Jugador Élite (IA)',
          data: [0.85, 0.70, 0.90, 0.78, 0.60],
          backgroundColor: 'rgba(0, 149, 255, 0.2)',
          borderColor: 'rgba(0, 149, 255, 0.8)',
          pointBackgroundColor: 'rgba(0, 149, 255, 1)',
          pointBorderColor: '#fff',
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: 'rgba(0, 149, 255, 1)',
          borderWidth: 2
        }, {
          label: 'Jugador Promedio',
          data: [0.30, 0.25, 0.40, 0.35, 0.42],
          backgroundColor: 'rgba(0, 230, 118, 0.15)',
          borderColor: 'rgba(0, 230, 118, 0.7)',
          pointBackgroundColor: 'rgba(0, 230, 118, 1)',
          pointBorderColor: '#fff',
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: 'rgba(0, 230, 118, 1)',
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        layout: {
          padding: 0
        },
        plugins: {
          legend: {
            labels: { color: 'rgba(255, 255, 255, 0.7)', font: { family: 'Inter', size: 10 } }
          }
        },
        scales: {
          r: {
            angleLines: { color: 'rgba(255, 255, 255, 0.1)' },
            grid: { color: 'rgba(255, 255, 255, 0.1)' },
            pointLabels: { 
              color: 'rgba(255, 255, 255, 0.6)', 
              font: { family: 'Exo 2', size: 9.5 },
              padding: 4
            },
            ticks: { display: false },
            suggestedMin: 0,
            suggestedMax: 1
          }
        }
      }
    });
  }

  // Bar Chart
  const barCtx = document.getElementById('barChart');
  if (barCtx) {
    if (barChartInstance) barChartInstance.destroy();
    barChartInstance = new Chart(barCtx, {
      type: 'bar',
      data: {
        labels: ['Precisión de Scouting', 'Velocidad de Análisis', 'Detección de Talento Oculto', 'Predicción de Escenarios'],
        datasets: [{
          label: 'Incremento con Inteligencia Artificial',
          data: [85, 95, 70, 90],
          backgroundColor: [
            'rgba(0, 149, 255, 0.75)',
            'rgba(0, 230, 118, 0.75)',
            'rgba(0, 212, 255, 0.75)',
            'rgba(0, 230, 118, 0.75)'
          ],
          borderColor: [
            'rgba(0, 149, 255, 1)',
            'rgba(0, 230, 118, 1)',
            'rgba(0, 212, 255, 1)',
            'rgba(0, 230, 118, 1)'
          ],
          borderWidth: 1,
          borderRadius: 4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          x: {
            grid: { color: 'rgba(255, 255, 255, 0.05)' },
            ticks: { color: 'rgba(255, 255, 255, 0.6)', font: { family: 'Inter', size: 9 } }
          },
          y: {
            grid: { color: 'rgba(255, 255, 255, 0.05)' },
            ticks: { 
              color: 'rgba(255, 255, 255, 0.6)', 
              font: { family: 'Inter', size: 10 },
              callback: function(value) { return '+' + value + '%'; }
            }
          }
        }
      }
    });
  }
}

function initTacticoCharts() {
  if (typeof Chart === 'undefined') return;

  // Match Momentum (xG Flow) Chart
  const momentumCtx = document.getElementById('momentumChart');
  if (momentumCtx) {
    if (momentumChartInstance) momentumChartInstance.destroy();
    momentumChartInstance = new Chart(momentumCtx, {
      type: 'line',
      data: {
        labels: ['0\'', '15\'', '30\'', '45\'', '60\'', '75\'', '90\''],
        datasets: [{
          label: 'Equipo Local',
          data: [0, 0.25, 0.45, 0.80, 1.10, 1.45, 1.80],
          borderColor: 'rgba(0, 149, 255, 1)',
          backgroundColor: 'rgba(0, 149, 255, 0.05)',
          fill: true,
          tension: 0.3,
          borderWidth: 2,
          pointRadius: 2
        }, {
          label: 'Equipo Visitante',
          data: [0, 0.10, 0.15, 0.40, 0.90, 1.10, 1.15],
          borderColor: 'rgba(0, 230, 118, 1)',
          backgroundColor: 'rgba(0, 230, 118, 0.05)',
          fill: true,
          tension: 0.3,
          borderWidth: 2,
          pointRadius: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        layout: { padding: 0 },
        plugins: {
          legend: {
            labels: { color: 'rgba(255, 255, 255, 0.7)', font: { family: 'Inter', size: 9 } }
          }
        },
        scales: {
          x: {
            grid: { color: 'rgba(255, 255, 255, 0.05)' },
            ticks: { color: 'rgba(255, 255, 255, 0.6)', font: { family: 'Inter', size: 9 } }
          },
          y: {
            grid: { color: 'rgba(255, 255, 255, 0.05)' },
            ticks: { color: 'rgba(255, 255, 255, 0.6)', font: { family: 'Inter', size: 9 } }
          }
        }
      }
    });
  }
}

// ─── EVENT LISTENERS: IA & DATA SCIENCE ──────
if (cardIaDs && modalIaDs) {
  cardIaDs.addEventListener('click', () => {
    modalIaDs.classList.add('active');
    document.body.style.overflow = 'hidden';
    setTimeout(initCharts, 50);
  });

  if (closeBtn) {
    closeBtn.addEventListener('click', () => {
      modalIaDs.classList.remove('active');
      document.body.style.overflow = '';
    });
  }

  modalIaDs.addEventListener('click', (e) => {
    if (e.target === modalIaDs) {
      modalIaDs.classList.remove('active');
      document.body.style.overflow = '';
    }
  });

  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modalIaDs.classList.contains('active')) {
      modalIaDs.classList.remove('active');
      document.body.style.overflow = '';
    }
  });
}

// ─── EVENT LISTENERS: ANÁLISIS TÁCTICO ────────
if (cardAnalisisTactico && modalAnalisisTactico) {
  cardAnalisisTactico.addEventListener('click', () => {
    modalAnalisisTactico.classList.add('active');
    document.body.style.overflow = 'hidden';
    setTimeout(initTacticoCharts, 50);
  });

  if (closeBtnTactico) {
    closeBtnTactico.addEventListener('click', () => {
      modalAnalisisTactico.classList.remove('active');
      document.body.style.overflow = '';
    });
  }

  modalAnalisisTactico.addEventListener('click', (e) => {
    if (e.target === modalAnalisisTactico) {
      modalAnalisisTactico.classList.remove('active');
      document.body.style.overflow = '';
    }
  });

  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modalAnalisisTactico.classList.contains('active')) {
      modalAnalisisTactico.classList.remove('active');
      document.body.style.overflow = '';
    }
  });
}

// ─── EVENT LISTENERS: NUEVOS LINKS DEL HUB ───
const linkMetodologia = document.getElementById('link-metodologia');
const linkAlgoritmo = document.getElementById('link-algoritmo');
const linkGlosario = document.getElementById('link-glosario');
const modalGlosario = document.getElementById('modal-glosario');
const closeBtnGlosario = document.getElementById('modal-close-glosario-btn');

if (linkMetodologia && modalAnalisisTactico) {
  linkMetodologia.addEventListener('click', (e) => {
    e.preventDefault();
    modalAnalisisTactico.classList.add('active');
    document.body.style.overflow = 'hidden';
    setTimeout(initTacticoCharts, 50);
  });
}

if (linkAlgoritmo && modalIaDs) {
  linkAlgoritmo.addEventListener('click', (e) => {
    e.preventDefault();
    modalIaDs.classList.add('active');
    document.body.style.overflow = 'hidden';
    setTimeout(initCharts, 50);
  });
}

if (linkGlosario && modalGlosario) {
  linkGlosario.addEventListener('click', (e) => {
    e.preventDefault();
    modalGlosario.classList.add('active');
    document.body.style.overflow = 'hidden';
  });

  if (closeBtnGlosario) {
    closeBtnGlosario.addEventListener('click', () => {
      modalGlosario.classList.remove('active');
      document.body.style.overflow = '';
    });
  }

  modalGlosario.addEventListener('click', (e) => {
    if (e.target === modalGlosario) {
      modalGlosario.classList.remove('active');
      document.body.style.overflow = '';
    }
  });

  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modalGlosario.classList.contains('active')) {
      modalGlosario.classList.remove('active');
      document.body.style.overflow = '';
    }
  });
}

// ─── EVENT LISTENER: MODAL CASO DE ESTUDIO ───
const linkCasoEstudio = document.getElementById('link-caso-estudio');
const modalCasoEstudio = document.getElementById('modal-caso-estudio');
const closeBtnCaso = document.getElementById('modal-close-caso-btn');

if (linkCasoEstudio && modalCasoEstudio) {
  linkCasoEstudio.addEventListener('click', (e) => {
    e.preventDefault();
    modalCasoEstudio.classList.add('active');
    document.body.style.overflow = 'hidden';
  });

  if (closeBtnCaso) {
    closeBtnCaso.addEventListener('click', () => {
      modalCasoEstudio.classList.remove('active');
      document.body.style.overflow = '';
    });
  }

  modalCasoEstudio.addEventListener('click', (e) => {
    if (e.target === modalCasoEstudio) {
      modalCasoEstudio.classList.remove('active');
      document.body.style.overflow = '';
    }
  });

  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modalCasoEstudio.classList.contains('active')) {
      modalCasoEstudio.classList.remove('active');
      document.body.style.overflow = '';
    }
  });
}

// Bar heights are set in HTML for a deliberate chart silhouette
