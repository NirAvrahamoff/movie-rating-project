/* ── Gauge constants ─────────────────────────────────────────────── */
const GAUGE_R = 108;
const GAUGE_C = 2 * Math.PI * GAUGE_R; // 678.58

/* ── DOM refs ────────────────────────────────────────────────────── */
const form            = document.getElementById('prediction-form');
const submitBtn       = document.getElementById('predict-btn');
const resultSection   = document.getElementById('result');
const resultTitle     = document.getElementById('result-title');
const resultChips     = document.getElementById('result-chips');
const gaugeArc        = document.getElementById('gauge-arc');
const gaugeScore      = document.getElementById('gauge-score');
const gaugeGlow       = document.getElementById('gauge-glow');
const fillStop1       = document.getElementById('gs1');
const fillStop2       = document.getElementById('gs2');
const starsRow        = document.getElementById('stars-row');
const ratingBadge     = document.getElementById('rating-badge');
const errorBanner     = document.getElementById('error-banner');
const predictAgainBtn = document.getElementById('predict-again-btn');

/* ── Build star scaffold once ────────────────────────────────────── */
for (let i = 0; i < 5; i++) {
    const w = document.createElement('div');
    w.className = 'star-wrap';
    w.innerHTML = '<span class="star-bg">★</span><span class="star-fill">★</span>';
    starsRow.appendChild(w);
}

/* ── Genre toggle — :has() + class fallback ──────────────────────── */
document.querySelectorAll('.gpill input[type="checkbox"]').forEach(cb => {
    cb.addEventListener('change', () =>
        cb.closest('.gpill').classList.toggle('on', cb.checked)
    );
});

/* ── Smooth scroll CTA ───────────────────────────────────────────── */
document.getElementById('begin-cta').addEventListener('click', e => {
    e.preventDefault();
    document.getElementById('predict').scrollIntoView({ behavior: 'smooth', block: 'start' });
});

/* ── Rating metadata ─────────────────────────────────────────────── */
function ratingMeta(s) {
    if (s >= 9.5) return { label: 'MASTERPIECE',   color: '#1abc9c', glow: 'rgba(26,188,156,0.16)'  };
    if (s >= 8.5) return { label: 'EXCELLENT',     color: '#27ae60', glow: 'rgba(39,174,96,0.16)'   };
    if (s >= 7.5) return { label: 'VERY GOOD',     color: '#2ecc71', glow: 'rgba(46,204,113,0.14)'  };
    if (s >= 6.5) return { label: 'GOOD',          color: '#d4ac0d', glow: 'rgba(212,172,13,0.16)'  };
    if (s >= 5.5) return { label: 'AVERAGE',       color: '#e67e22', glow: 'rgba(230,126,34,0.14)'  };
    if (s >= 4.0) return { label: 'BELOW AVERAGE', color: '#d35400', glow: 'rgba(211,84,0,0.14)'    };
    return               { label: 'POOR',          color: '#e74c3c', glow: 'rgba(231,76,60,0.14)'   };
}

/* ── Easing ──────────────────────────────────────────────────────── */
const easeOutExpo = t => t === 1 ? 1 : 1 - Math.pow(2, -10 * t);

/* ── Gauge arc sweep ─────────────────────────────────────────────── */
function animateGauge(score, color) {
    const targetOffset = GAUGE_C * (1 - score / 10);

    fillStop1.setAttribute('stop-color', color);
    fillStop2.setAttribute('stop-color', color);
    gaugeArc.style.stroke          = color;
    gaugeArc.style.strokeDasharray  = GAUGE_C;
    gaugeArc.style.strokeDashoffset = GAUGE_C;

    const dur = 1500, t0 = performance.now();
    const tick = now => {
        const p = Math.min((now - t0) / dur, 1);
        const e = easeOutExpo(p);
        gaugeArc.style.strokeDashoffset = GAUGE_C - (GAUGE_C - targetOffset) * e;
        if (p < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
}

/* ── Score counter ───────────────────────────────────────────────── */
function animateCounter(score) {
    const dur = 1500, t0 = performance.now();
    const tick = now => {
        const p = Math.min((now - t0) / dur, 1);
        gaugeScore.textContent = (easeOutExpo(p) * score).toFixed(1);
        if (p < 1) requestAnimationFrame(tick);
        else gaugeScore.textContent = score.toFixed(1);
    };
    requestAnimationFrame(tick);
}

/* ── Star fill ───────────────────────────────────────────────────── */
function animateStars(score) {
    const outOf5 = score / 2;
    document.querySelectorAll('.star-wrap').forEach((w, i) => {
        const pct = Math.min(Math.max(outOf5 - i, 0), 1) * 100;
        setTimeout(() => (w.querySelector('.star-fill').style.width = pct + '%'), 300 + i * 120);
    });
}

/* ── Build metadata chips ────────────────────────────────────────── */
function buildChips(fd) {
    resultChips.innerHTML = '';
    const items = [
        ...fd.genres.slice(0, 3),
        ...(fd.genres.length > 3 ? [`+${fd.genres.length - 3}`] : []),
        fd.startYear,
        fd.runtimeMinutes ? formatRuntime(Number(fd.runtimeMinutes)) : null,
    ].filter(Boolean);

    items.forEach(txt => {
        const s = document.createElement('span');
        s.className = 'rchip';
        s.textContent = txt;
        resultChips.appendChild(s);
    });
}

function formatRuntime(min) {
    if (min < 60) return `${min} MIN`;
    const h = Math.floor(min / 60), m = min % 60;
    return m > 0 ? `${h}H ${m}M` : `${h}H`;
}

/* ── Show result ─────────────────────────────────────────────────── */
function showResult(data, fd) {
    const meta = ratingMeta(data.rating);

    resultTitle.textContent = data.title;
    buildChips(fd);

    ratingBadge.textContent   = meta.label;
    ratingBadge.style.color   = meta.color;
    ratingBadge.style.borderColor = meta.color;

    // Update CSS vars for card top-stripe and result::after glow
    document.documentElement.style.setProperty('--rc', meta.color);
    gaugeGlow.style.background =
        `radial-gradient(circle, ${meta.glow} 0%, transparent 66%)`;

    // Reveal
    resultSection.style.display = 'block';
    requestAnimationFrame(() => requestAnimationFrame(() => {
        resultSection.classList.add('visible');
        resultSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }));

    // Animate after card has slid in
    setTimeout(() => {
        animateGauge(data.rating, meta.color);
        animateCounter(data.rating);
        animateStars(data.rating);
    }, 400);
}

/* ── Layer 1: frontend validation ───────────────────────────────── */
// Reads min/max bounds directly from HTML attributes so the two layers
// share a single source of truth — change the attribute, JS adapts.
function validateForm() {
    // Rule 1 — Film title
    const title = document.getElementById('primaryTitle').value.trim();
    if (!title) {
        showError('FILM TITLE IS REQUIRED.');
        return false;
    }

    // Rule 2 — Release year
    const yearEl  = document.getElementById('startYear');
    const year    = parseInt(yearEl.value, 10);
    if (isNaN(year) || year < +yearEl.min || year > +yearEl.max) {
        showError(`RELEASE YEAR MUST BE BETWEEN ${yearEl.min} AND ${yearEl.max}.`);
        return false;
    }

    // Rule 3 — Runtime
    const rtEl    = document.getElementById('runtimeMinutes');
    const runtime = parseInt(rtEl.value, 10);
    if (isNaN(runtime) || runtime < +rtEl.min || runtime > +rtEl.max) {
        showError(`RUNTIME MUST BE BETWEEN ${rtEl.min} AND ${rtEl.max} MINUTES.`);
        return false;
    }

    // Rule 4 — At least one genre
    const checked = document.querySelectorAll('input[name="genres"]:checked');
    if (checked.length === 0) {
        showError('PLEASE SELECT AT LEAST ONE GENRE.');
        return false;
    }

    return true;
}

/* ── Error display ───────────────────────────────────────────────── */
let errTimer;
function showError(msg) {
    errorBanner.textContent = msg;
    errorBanner.classList.add('show');
    clearTimeout(errTimer);
    errTimer = setTimeout(() => errorBanner.classList.remove('show'), 5000);
}

/* ── Loading state ───────────────────────────────────────────────── */
function setLoading(on) {
    submitBtn.disabled = on;
    submitBtn.classList.toggle('loading', on);
}

/* ── Form submit ─────────────────────────────────────────────────── */
form.addEventListener('submit', async e => {
    e.preventDefault();
    errorBanner.classList.remove('show');

    const title  = document.getElementById('primaryTitle').value.trim();
    const genres = [...document.querySelectorAll('input[name="genres"]:checked')].map(c => c.value);

    const fd = {
        primaryTitle:   title,
        startYear:      document.getElementById('startYear').value,
        runtimeMinutes: document.getElementById('runtimeMinutes').value,
        genres,
        language: document.getElementById('language').value,
        country:  document.getElementById('country').value,
    };

    if (!validateForm()) return;    // Layer 1 gate — stops request on bad input

    setLoading(true);
    try {
        const res  = await fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(fd),
        });
        const data = await res.json();
        if (data.success) {
            showResult(data, fd);
        } else {
            showError(data.error || 'PREDICTION FAILED. PLEASE TRY AGAIN.');
        }
    } catch {
        showError('NETWORK ERROR. CHECK YOUR CONNECTION.');
    } finally {
        setLoading(false);
    }
});

/* ── Reset ───────────────────────────────────────────────────────── */
predictAgainBtn.addEventListener('click', () => {
    resultSection.classList.remove('visible');
    setTimeout(() => {
        resultSection.style.display = 'none';

        // Reset gauge
        gaugeArc.style.strokeDashoffset = GAUGE_C;
        gaugeScore.textContent          = '0.0';

        // Reset stars
        document.querySelectorAll('.star-fill').forEach(s => s.style.width = '0%');

        document.getElementById('predict').scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 550);
});
