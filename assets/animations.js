(function () {
  'use strict';

  /* 1. NEURAL PARTICLE CANVAS */
  function initNeuralCanvas() {
    const canvas = document.getElementById('neural-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    let W, H, particles = [], animId;
    const PARTICLE_COUNT = 80;
    const CONNECTION_DIST = 140;
    const COLORS = ['#7c3aed', '#4f46e5', '#06b6d4', '#ec4899'];

    function resize() {
      W = canvas.width  = window.innerWidth;
      H = canvas.height = window.innerHeight;
    }

    function randomBetween(a, b) { return a + Math.random() * (b - a); }

    function createParticle() {
      return {
        x:   randomBetween(0, W),
        y:   randomBetween(0, H),
        vx:  randomBetween(-0.25, 0.25),
        vy:  randomBetween(-0.25, 0.25),
        r:   randomBetween(1.5, 3.5),
        color: COLORS[Math.floor(Math.random() * COLORS.length)],
        pulse: Math.random() * Math.PI * 2,
        pulseSpeed: randomBetween(0.01, 0.03),
      };
    }

    function init() {
      resize();
      particles = Array.from({ length: PARTICLE_COUNT }, createParticle);
    }

    function drawParticle(p) {
      p.pulse += p.pulseSpeed;
      const alpha = 0.5 + 0.5 * Math.sin(p.pulse);
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = p.color + Math.floor(alpha * 200).toString(16).padStart(2, '0');
      ctx.shadowBlur = 10;
      ctx.shadowColor = p.color;
      ctx.fill();
      ctx.shadowBlur = 0;
    }

    function drawConnections() {
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const a = particles[i], b = particles[j];
          const dx = a.x - b.x, dy = a.y - b.y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < CONNECTION_DIST) {
            const alpha = 1 - dist / CONNECTION_DIST;
            ctx.beginPath();
            ctx.moveTo(a.x, a.y);
            ctx.lineTo(b.x, b.y);
            ctx.strokeStyle = `rgba(124, 58, 237, ${alpha * 0.35})`;
            ctx.lineWidth = alpha * 1.2;
            ctx.stroke();
          }
        }
      }
    }

    function update() {
      particles.forEach(p => {
        p.x += p.vx;
        p.y += p.vy;
        if (p.x < -10) p.x = W + 10;
        if (p.x > W + 10) p.x = -10;
        if (p.y < -10) p.y = H + 10;
        if (p.y > H + 10) p.y = -10;
      });
    }

    function draw() {
      ctx.clearRect(0, 0, W, H);
      drawConnections();
      particles.forEach(drawParticle);
    }

    function loop() {
      update();
      draw();
      animId = requestAnimationFrame(loop);
    }

    window.addEventListener('resize', () => { resize(); });

    /* Mouse interaction: push particles */
    let mx = -9999, my = -9999;
    document.addEventListener('mousemove', e => {
      mx = e.clientX; my = e.clientY;
      particles.forEach(p => {
        const dx = p.x - mx, dy = p.y - my;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 80) {
          p.vx += (dx / dist) * 0.3;
          p.vy += (dy / dist) * 0.3;
          p.vx = Math.max(-1.5, Math.min(1.5, p.vx));
          p.vy = Math.max(-1.5, Math.min(1.5, p.vy));
        }
      });
    });

    init();
    loop();
  }


  /* 2. WEB AUDIO SOUND FX */
  let audioCtx = null;

  function getAudioCtx() {
    if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    return audioCtx;
  }

  function playTone({ freq = 440, type = 'sine', duration = 0.12, gain = 0.08, attack = 0.01, decay = 0.08 } = {}) {
    try {
      const ctx = getAudioCtx();
      const osc = ctx.createOscillator();
      const g = ctx.createGain();
      osc.connect(g);
      g.connect(ctx.destination);
      osc.type = type;
      osc.frequency.setValueAtTime(freq, ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(freq * 0.5, ctx.currentTime + duration);
      g.gain.setValueAtTime(0, ctx.currentTime);
      g.gain.linearRampToValueAtTime(gain, ctx.currentTime + attack);
      g.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + attack + decay);
      osc.start(ctx.currentTime);
      osc.stop(ctx.currentTime + duration + 0.05);
    } catch (_) {}
  }

  window.NM = window.NM || {};

  window.NM.soundHover  = () => playTone({ freq: 660, type: 'sine',     duration: 0.08, gain: 0.04 });
  window.NM.soundClick  = () => playTone({ freq: 880, type: 'triangle', duration: 0.12, gain: 0.07 });
  window.NM.soundSend   = () => {
    playTone({ freq: 523, type: 'sine', duration: 0.06, gain: 0.06 });
    setTimeout(() => playTone({ freq: 659, type: 'sine', duration: 0.06, gain: 0.05 }), 60);
    setTimeout(() => playTone({ freq: 784, type: 'sine', duration: 0.10, gain: 0.04 }), 120);
  };
  window.NM.soundSuccess = () => {
    [523, 659, 784, 1047].forEach((f, i) =>
      setTimeout(() => playTone({ freq: f, type: 'sine', duration: 0.18, gain: 0.05 }), i * 80)
    );
  };
  window.NM.soundError = () => playTone({ freq: 220, type: 'sawtooth', duration: 0.3, gain: 0.05 });
  window.NM.soundUpload = () => {
    [400, 600, 800].forEach((f, i) =>
      setTimeout(() => playTone({ freq: f, type: 'triangle', duration: 0.1, gain: 0.06 }), i * 60)
    );
  };
  window.NM.soundThink = () => {
    let i = 0;
    const freqs = [300, 350, 400, 350];
    const interval = setInterval(() => {
      playTone({ freq: freqs[i % freqs.length], type: 'sine', duration: 0.2, gain: 0.03 });
      i++;
    }, 350);
    setTimeout(() => clearInterval(interval), 2800);
  };


  /* 3. CURSOR GLOW  */
  function initCursorGlow() {
    const glow = document.createElement('div');
    glow.id = 'nm-cursor-glow';
    glow.style.cssText = `
      position: fixed;
      width: 300px; height: 300px;
      border-radius: 50%;
      pointer-events: none;
      z-index: 9999;
      background: radial-gradient(circle, rgba(124,58,237,0.08) 0%, transparent 70%);
      transform: translate(-50%, -50%);
      transition: opacity 0.3s ease;
      mix-blend-mode: screen;
    `;
    document.body.appendChild(glow);

    document.addEventListener('mousemove', e => {
      glow.style.left = e.clientX + 'px';
      glow.style.top  = e.clientY + 'px';
    });
  }


  /* 4. SCROLL REVEAL */
  function initScrollReveal() {
    const io = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

    document.querySelectorAll('.reveal').forEach(el => io.observe(el));
  }


  /* 5. BUTTON SOUND HOOKS */
  function hookButtonSounds() {
    document.querySelectorAll('.nm-btn, .stButton > button').forEach(btn => {
      btn.addEventListener('mouseenter', () => window.NM.soundHover());
      btn.addEventListener('click', () => window.NM.soundClick());
    });

    const sendBtn = document.querySelector('.nm-send-btn');
    if (sendBtn) {
      sendBtn.addEventListener('click', () => window.NM.soundSend());
    }
  }


  /* 6. TYPING COUNTER (for textareas) */
  function initCharCounters() {
    document.querySelectorAll('[data-char-counter]').forEach(ta => {
      const counter = ta.nextElementSibling;
      if (!counter) return;
      ta.addEventListener('input', () => {
        counter.textContent = `${ta.value.length} chars`;
      });
    });
  }


  /* 7. WAVEFORM VISUALIZER  */
  window.NM.createWaveform = function (containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const canvas = document.createElement('canvas');
    canvas.width = container.offsetWidth || 600;
    canvas.height = 80;
    canvas.style.width = '100%';
    canvas.style.borderRadius = '12px';
    container.appendChild(canvas);

    const ctx = canvas.getContext('2d');
    let t = 0;

    function drawWave() {
      const W = canvas.width, H = canvas.height;
      ctx.clearRect(0, 0, W, H);

      // gradient line
      const grad = ctx.createLinearGradient(0, 0, W, 0);
      grad.addColorStop(0,   '#7c3aed');
      grad.addColorStop(0.5, '#06b6d4');
      grad.addColorStop(1,   '#ec4899');

      ctx.beginPath();
      ctx.moveTo(0, H / 2);
      for (let x = 0; x < W; x++) {
        const y = H / 2
          + Math.sin((x / W) * Math.PI * 4 + t) * 18
          + Math.sin((x / W) * Math.PI * 8 + t * 1.3) * 8
          + Math.sin((x / W) * Math.PI * 2 + t * 0.7) * 12;
        ctx.lineTo(x, y);
      }
      ctx.strokeStyle = grad;
      ctx.lineWidth = 2.5;
      ctx.shadowBlur = 12;
      ctx.shadowColor = '#7c3aed';
      ctx.stroke();
      ctx.shadowBlur = 0;

      t += 0.04;
      requestAnimationFrame(drawWave);
    }

    drawWave();
  };


  /* INIT */
  function init() {
    initNeuralCanvas();
    initCursorGlow();
    initScrollReveal();
    hookButtonSounds();
    initCharCounters();

    const observer = new MutationObserver(() => {
      hookButtonSounds();
      initScrollReveal();
      initCharCounters();
    });
    observer.observe(document.body, { childList: true, subtree: true });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();