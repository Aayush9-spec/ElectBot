/**
 * ElectBot – Election Process Education Assistant
 * Frontend Application Logic
 */

// ═══ Navigation ═══
document.querySelectorAll('.nav-btn').forEach(btn => {
  btn.addEventListener('click', () => navigateTo(btn.dataset.section));
});

document.querySelectorAll('.feature-card[data-navigate]').forEach(card => {
  card.addEventListener('click', () => {
    const q = card.dataset.query;
    navigateTo(card.dataset.navigate);
    if (q) setTimeout(() => sendChat(q), 300);
  });
});

document.getElementById('hero-start-chat')?.addEventListener('click', () => navigateTo('chat'));
document.getElementById('hero-explore')?.addEventListener('click', () => navigateTo('timeline'));

function navigateTo(section) {
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
  const el = document.getElementById('section-' + section);
  const btn = document.querySelector(`[data-section="${section}"]`);
  if (el) el.classList.add('active');
  if (btn) btn.classList.add('active');
  window.scrollTo({ top: 0, behavior: 'smooth' });
  if (section === 'timeline') renderTimeline();
  if (section === 'map') initMapFallback();
}

// ═══ Accessibility ═══
document.getElementById('theme-toggle')?.addEventListener('click', () => {
  document.body.classList.toggle('high-contrast');
});

let fontLevel = 0;
document.getElementById('font-size-toggle')?.addEventListener('click', () => {
  fontLevel = (fontLevel + 1) % 3;
  document.body.classList.toggle('large-font', fontLevel > 0);
  document.body.style.fontSize = fontLevel === 2 ? '125%' : '';
});

// ═══ Stats Counter Animation ═══
const observer = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.querySelectorAll('.stat-number').forEach(el => {
        const target = parseInt(el.dataset.count);
        let current = 0;
        const step = Math.ceil(target / 40);
        const timer = setInterval(() => {
          current += step;
          if (current >= target) { current = target; clearInterval(timer); }
          el.textContent = current.toLocaleString();
        }, 30);
      });
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.5 });

const statsBar = document.querySelector('.stats-bar');
if (statsBar) observer.observe(statsBar);

// ═══ Timeline ═══
const TIMELINE_DATA = [
  { name: "Announcement & Notification", duration: "6-8 weeks before polling", desc: "Election Commission announces dates. Model Code of Conduct enforced.", details: ["Press conference by ECI", "Gazette notification published", "Model Code of Conduct takes effect", "Political parties begin preparations"] },
  { name: "Nomination Filing", duration: "7 days from notification", desc: "Candidates file nomination papers with required documents and security deposit.", details: ["Collect nomination forms", "Security deposit: ₹25,000 (General), ₹12,500 (SC/ST)", "File affidavit with personal details", "Submit to Returning Officer"] },
  { name: "Scrutiny of Nominations", duration: "1 day after filing deadline", desc: "Returning Officer examines all nominations for validity.", details: ["Document verification", "Eligibility check", "Objections by other candidates", "Invalid nominations rejected"] },
  { name: "Withdrawal of Candidature", duration: "2 days after scrutiny", desc: "Candidates may withdraw nominations before the deadline.", details: ["Written notice to Returning Officer", "Cannot be reversed", "Final candidate list prepared", "Election symbols allotted"] },
  { name: "Election Campaign", duration: "Until 48 hours before polling", desc: "Parties campaign through rallies, ads, and social media.", details: ["Rallies, roadshows, meetings", "TV, radio, digital campaigns", "Expenditure limits enforced", "48-hour silence period before voting"] },
  { name: "Polling Day", duration: "1 day (7 AM – 6 PM)", desc: "Voters cast ballots at designated polling stations using EVMs.", details: ["Voter identity verification", "Indelible ink on left index finger", "EVM + VVPAT voting", "Special provisions for disabled/elderly"] },
  { name: "Counting & Results", duration: "2-3 days after polling", desc: "Votes counted at designated centers under strict supervision.", details: ["Postal ballots counted first", "EVM counting round by round", "VVPAT random verification", "Results declared by Returning Officer"] },
  { name: "Government Formation", duration: "Within days of results", desc: "Winning party/coalition invited to form government.", details: ["Governor/President invites majority party", "Leader elected as PM/CM", "Cabinet ministers appointed", "Government sworn in"] }
];

function renderTimeline() {
  const container = document.getElementById('timeline-container');
  if (!container || container.children.length > 0) return;
  container.innerHTML = TIMELINE_DATA.map((phase, i) => `
    <div class="timeline-item" role="listitem" data-index="${i}">
      <div class="timeline-dot"></div>
      <div class="timeline-card" tabindex="0" aria-expanded="false" onclick="togglePhase(${i})" onkeydown="if(event.key==='Enter')togglePhase(${i})">
        <h3><span class="phase-num">Phase ${i + 1}</span> ${phase.name}</h3>
        <div class="duration"><i class="ri-time-line"></i> ${phase.duration}</div>
        <p>${phase.desc}</p>
        <div class="timeline-details">
          <ul>${phase.details.map(d => `<li>${d}</li>`).join('')}</ul>
        </div>
      </div>
    </div>
  `).join('');
}

function togglePhase(index) {
  const items = document.querySelectorAll('.timeline-item');
  items.forEach((item, i) => {
    const isTarget = i === index;
    const wasActive = item.classList.contains('active');
    item.classList.toggle('active', isTarget && !wasActive);
    item.querySelector('.timeline-card')?.setAttribute('aria-expanded', isTarget && !wasActive);
  });
}

// ═══ Chat ═══
const chatMessages = document.getElementById('chat-messages');
const chatForm = document.getElementById('chat-form');
const chatInput = document.getElementById('chat-input');
const chatStatus = document.getElementById('chat-status');

chatForm?.addEventListener('submit', e => {
  e.preventDefault();
  const msg = chatInput.value.trim();
  if (msg) sendChat(msg);
});

document.querySelectorAll('.quick-q-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    sendChat(btn.dataset.query);
  });
});

document.getElementById('clear-chat-btn')?.addEventListener('click', async () => {
  chatMessages.innerHTML = `<div class="chat-welcome"><div class="chat-welcome-icon">🗳️</div><h3>Welcome to ElectBot!</h3><p>Ask me anything about elections.</p></div>`;
  await fetch('/api/clear-history', { method: 'POST' });
});

async function sendChat(message) {
  // Remove welcome
  const welcome = chatMessages.querySelector('.chat-welcome');
  if (welcome) welcome.remove();

  // Add user message
  addMessage(message, 'user');
  chatInput.value = '';
  chatStatus.textContent = 'Thinking...';

  // Add typing indicator
  const typing = document.createElement('div');
  typing.className = 'typing-indicator';
  typing.innerHTML = '<div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>';
  chatMessages.appendChild(typing);
  chatMessages.scrollTop = chatMessages.scrollHeight;

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    });
    const data = await res.json();
    typing.remove();

    if (data.error) {
      addMessage('Sorry, something went wrong. Please try again.', 'bot');
    } else {
      addMessage(data.response, 'bot');
    }
  } catch (err) {
    typing.remove();
    addMessage('Connection error. Please check your internet and try again.', 'bot');
  }

  chatStatus.textContent = 'Ready to help';
}

function addMessage(text, type) {
  const div = document.createElement('div');
  div.className = `msg msg-${type === 'user' ? 'user' : 'bot'}`;
  div.setAttribute('role', 'article');
  div.innerHTML = type === 'user' ? escapeHtml(text) : renderMarkdown(text);
  chatMessages.appendChild(div);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function escapeHtml(str) {
  const d = document.createElement('div');
  d.textContent = str;
  return d.innerHTML;
}

function renderMarkdown(text) {
  return text
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^# (.+)$/gm, '<h2>$1</h2>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/`(.+?)`/g, '<code>$1</code>')
    .replace(/^\- (.+)$/gm, '<li>$1</li>')
    .replace(/^\d+\. (.+)$/gm, '<li>$1</li>')
    .replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>')
    .replace(/\[(.+?)\]\((.+?)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>')
    .replace(/\n\n/g, '<br><br>')
    .replace(/\n/g, '<br>');
}

// ═══ Quiz ═══
let quizQuestions = [];
let currentQ = 0;
let score = 0;

document.getElementById('start-quiz-btn')?.addEventListener('click', startQuiz);
document.getElementById('retake-quiz-btn')?.addEventListener('click', startQuiz);
document.getElementById('next-question-btn')?.addEventListener('click', nextQuestion);

async function startQuiz() {
  try {
    const res = await fetch('/api/quiz');
    const data = await res.json();
    quizQuestions = data.questions;
  } catch {
    quizQuestions = [{ id: 1, question: "Quiz unavailable. Please try again.", options: [], correct: -1, explanation: "" }];
  }
  currentQ = 0;
  score = 0;
  document.getElementById('quiz-start')?.classList.add('hidden');
  document.getElementById('quiz-results')?.classList.add('hidden');
  document.getElementById('quiz-active')?.classList.remove('hidden');
  showQuestion();
}

function showQuestion() {
  const q = quizQuestions[currentQ];
  const progress = ((currentQ) / quizQuestions.length) * 100;
  document.getElementById('quiz-progress-fill').style.width = progress + '%';
  document.getElementById('quiz-counter').textContent = `Question ${currentQ + 1} of ${quizQuestions.length}`;
  document.getElementById('quiz-question').textContent = q.question;
  document.getElementById('quiz-explanation')?.classList.add('hidden');

  const optContainer = document.getElementById('quiz-options');
  const letters = ['A', 'B', 'C', 'D'];
  optContainer.innerHTML = q.options.map((opt, i) => `
    <button class="quiz-option" onclick="selectAnswer(${i})" aria-label="Option ${letters[i]}: ${opt}">
      <span class="opt-letter">${letters[i]}</span>
      ${escapeHtml(opt)}
    </button>
  `).join('');
}

function selectAnswer(index) {
  const q = quizQuestions[currentQ];
  const opts = document.querySelectorAll('.quiz-option');
  opts.forEach((opt, i) => {
    opt.classList.add('disabled');
    if (i === q.correct) opt.classList.add('correct');
    if (i === index && i !== q.correct) opt.classList.add('wrong');
  });
  if (index === q.correct) score++;

  const expEl = document.getElementById('quiz-explanation');
  document.getElementById('quiz-explanation-content').innerHTML =
    `<strong>${index === q.correct ? '✅ Correct!' : '❌ Incorrect.'}</strong> ${q.explanation}`;
  expEl.classList.remove('hidden');

  const nextBtn = document.getElementById('next-question-btn');
  nextBtn.textContent = currentQ === quizQuestions.length - 1 ? 'See Results' : 'Next Question';
}
window.selectAnswer = selectAnswer;

function nextQuestion() {
  currentQ++;
  if (currentQ >= quizQuestions.length) {
    showResults();
  } else {
    showQuestion();
  }
}

function showResults() {
  document.getElementById('quiz-active')?.classList.add('hidden');
  const resultsEl = document.getElementById('quiz-results');
  resultsEl?.classList.remove('hidden');

  const pct = Math.round((score / quizQuestions.length) * 100);
  const circumference = 2 * Math.PI * 54; // 339.292
  const offset = circumference - (pct / 100) * circumference;

  document.getElementById('score-text').textContent = pct + '%';
  setTimeout(() => {
    document.getElementById('score-circle').style.strokeDashoffset = offset;
  }, 100);

  let icon, title, msg;
  if (pct >= 80) { icon = '🏆'; title = 'Excellent!'; msg = 'You have a great understanding of the election process!'; }
  else if (pct >= 50) { icon = '👍'; title = 'Good job!'; msg = 'You know the basics. Explore more topics to improve!'; }
  else { icon = '📚'; title = 'Keep learning!'; msg = 'Use ElectBot to learn more about elections and try again!'; }

  document.getElementById('quiz-results-icon').textContent = icon;
  document.getElementById('quiz-results-title').textContent = title;
  document.getElementById('quiz-results-message').textContent = `You scored ${score}/${quizQuestions.length}. ${msg}`;
}

// ═══ Map ═══
let map = null;
let mapInitialized = false;

window.initMap = function () {
  mapInitialized = true;
};

function initMapFallback() {
  const overlay = document.getElementById('map-overlay');
  if (!mapInitialized) {
    if (overlay) overlay.classList.remove('hidden');
    initBasicMap();
    return;
  }
  if (overlay) overlay.classList.add('hidden');
  if (!map) {
    map = new google.maps.Map(document.getElementById('google-map'), {
      center: { lat: 20.5937, lng: 78.9629 },
      zoom: 5,
      styles: [
        { elementType: 'geometry', stylers: [{ color: '#1a1a3e' }] },
        { elementType: 'labels.text.stroke', stylers: [{ color: '#0a0a1a' }] },
        { elementType: 'labels.text.fill', stylers: [{ color: '#6a6a88' }] },
        { featureType: 'road', elementType: 'geometry', stylers: [{ color: '#2a2a5e' }] },
        { featureType: 'water', elementType: 'geometry', stylers: [{ color: '#0e0e2a' }] }
      ]
    });
  }
}

function initBasicMap() {
  const mapEl = document.getElementById('google-map');
  if (!mapEl) return;
  mapEl.innerHTML = '<div style="display:grid;place-items:center;height:100%;color:#9a9ab8;text-align:center;padding:40px"><i class="ri-map-pin-line" style="font-size:3rem;color:#6366f1;margin-bottom:16px"></i><h3>Map Preview</h3><p>Configure GOOGLE_MAPS_API_KEY to enable the interactive map.<br>Visit <a href="https://electoralsearch.eci.gov.in/" target="_blank" style="color:#818cf8">electoralsearch.eci.gov.in</a> to find your polling station.</p></div>';
}

document.getElementById('map-search-btn')?.addEventListener('click', searchLocation);
document.getElementById('map-search')?.addEventListener('keydown', e => { if (e.key === 'Enter') searchLocation(); });

function searchLocation() {
  const query = document.getElementById('map-search')?.value;
  if (!query || !map) return;
  const service = new google.maps.places.PlacesService(map);
  service.textSearch({ query: query + ' polling station election office' }, (results, status) => {
    if (status === google.maps.places.PlacesServiceStatus.OK && results.length) {
      map.setCenter(results[0].geometry.location);
      map.setZoom(13);
      results.forEach(place => {
        new google.maps.Marker({ map, position: place.geometry.location, title: place.name });
      });
    }
  });
}

document.getElementById('map-locate-btn')?.addEventListener('click', () => {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(pos => {
      const loc = { lat: pos.coords.latitude, lng: pos.coords.longitude };
      if (map) {
        map.setCenter(loc);
        map.setZoom(13);
        new google.maps.Marker({ map, position: loc, title: 'Your Location' });
      }
    });
  }
});

// ═══ Init ═══
document.addEventListener('DOMContentLoaded', () => {
  console.log('🗳️ ElectBot initialized');
});
