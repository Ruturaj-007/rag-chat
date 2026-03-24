import streamlit as st
import streamlit.components.v1 as components
import os

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")


def _read(filename: str) -> str:
    with open(os.path.join(ASSETS_DIR, filename), "r", encoding="utf-8") as f:
        return f.read()


# inject_ui call ONCE at the very top of every page 
def inject_ui():
    css = _read("style.css")

    # 1. CSS + canvas element — st.markdown 
    st.markdown(f"""
<style>
{css}
</style>
<style>
.appview-container .main .block-container {{
    padding-top: 0 !important;
    padding-left: 0 !important;
    padding-right: 0 !important;
    max-width: 100% !important;
}}
section[data-testid="stSidebar"] > div {{
    padding-top: 20px;
}}
</style>
<canvas id="neural-canvas"></canvas>
""", unsafe_allow_html=True)

    # 2. JS — MUST use components.html, Streamlit strips <script> from st.markdown
    #    height=0 + scrolling=False = invisible iframe that just runs the script
    components.html("""
<script>
(function() {
    // All DOM work targets the parent Streamlit window, not this hidden iframe
    var P = window.parent;
    var D = P.document;

    // ── Wait for canvas to exist, then start neural network ──────
    function initCanvas() {
        var canvas = D.getElementById('neural-canvas');
        if (!canvas) { setTimeout(initCanvas, 150); return; }
        var ctx = canvas.getContext('2d');
        var W, H, pts = [];
        var COLORS = ['#7c3aed','#4f46e5','#06b6d4','#ec4899'];

        function resize() {
            W = canvas.width  = P.innerWidth;
            H = canvas.height = P.innerHeight;
        }
        function rnd(a,b) { return a + Math.random()*(b-a); }
        function mkPt() {
            return { x:rnd(0,W), y:rnd(0,H), vx:rnd(-.25,.25), vy:rnd(-.25,.25),
                     r:rnd(1.5,3.5), col:COLORS[Math.floor(Math.random()*4)],
                     pulse:Math.random()*Math.PI*2, ps:rnd(.01,.03) };
        }

        function loop() {
            ctx.clearRect(0,0,W,H);
            // connections
            for(var i=0;i<pts.length;i++) {
                for(var j=i+1;j<pts.length;j++) {
                    var a=pts[i], b=pts[j];
                    var dx=a.x-b.x, dy=a.y-b.y, d=Math.sqrt(dx*dx+dy*dy);
                    if(d<140) {
                        var al=1-d/140;
                        ctx.beginPath(); ctx.moveTo(a.x,a.y); ctx.lineTo(b.x,b.y);
                        ctx.strokeStyle='rgba(124,58,237,'+(al*0.35)+')';
                        ctx.lineWidth=al*1.2; ctx.stroke();
                    }
                }
            }
            // particles
            pts.forEach(function(p) {
                p.pulse += p.ps;
                var al = 0.5 + 0.5*Math.sin(p.pulse);
                ctx.beginPath(); ctx.arc(p.x,p.y,p.r,0,Math.PI*2);
                ctx.fillStyle = p.col + Math.floor(al*200).toString(16).padStart(2,'0');
                ctx.shadowBlur=10; ctx.shadowColor=p.col; ctx.fill(); ctx.shadowBlur=0;
                p.x+=p.vx; p.y+=p.vy;
                if(p.x<-10) p.x=W+10; if(p.x>W+10) p.x=-10;
                if(p.y<-10) p.y=H+10; if(p.y>H+10) p.y=-10;
            });
            requestAnimationFrame(loop);
        }

        resize();
        pts = Array.from({length:80}, mkPt);
        P.addEventListener('resize', resize);

        D.addEventListener('mousemove', function(e) {
            pts.forEach(function(p) {
                var dx=p.x-e.clientX, dy=p.y-e.clientY;
                var d=Math.sqrt(dx*dx+dy*dy);
                if(d<80) {
                    p.vx += (dx/d)*0.3; p.vy += (dy/d)*0.3;
                    p.vx = Math.max(-1.5,Math.min(1.5,p.vx));
                    p.vy = Math.max(-1.5,Math.min(1.5,p.vy));
                }
            });
        });

        loop();
    }

    // ── Cursor glow ──────────────────────────────────────────────
    function initCursorGlow() {
        if (D.getElementById('nm-cursor-glow')) return;
        var g = D.createElement('div');
        g.id = 'nm-cursor-glow';
        g.style.cssText = 'position:fixed;width:300px;height:300px;border-radius:50%;pointer-events:none;z-index:9999;background:radial-gradient(circle,rgba(124,58,237,0.08) 0%,transparent 70%);transform:translate(-50%,-50%);mix-blend-mode:screen;top:0;left:0;';
        D.body.appendChild(g);
        D.addEventListener('mousemove', function(e) {
            g.style.left = e.clientX + 'px';
            g.style.top  = e.clientY + 'px';
        });
    }

    // ── Web Audio ────────────────────────────────────────────────
    function setupAudio() {
        var ac = null;
        function getAC() { return ac || (ac = new (P.AudioContext || P.webkitAudioContext)()); }
        function playTone(freq, type, duration, gain, attack, decay) {
            freq = freq||440; type=type||'sine'; duration=duration||0.12;
            gain=gain||0.08; attack=attack||0.01; decay=decay||0.08;
            try {
                var c=getAC(), o=c.createOscillator(), g=c.createGain();
                o.connect(g); g.connect(c.destination);
                o.type=type; o.frequency.setValueAtTime(freq,c.currentTime);
                o.frequency.exponentialRampToValueAtTime(freq*0.5,c.currentTime+duration);
                g.gain.setValueAtTime(0,c.currentTime);
                g.gain.linearRampToValueAtTime(gain,c.currentTime+attack);
                g.gain.exponentialRampToValueAtTime(0.001,c.currentTime+attack+decay);
                o.start(); o.stop(c.currentTime+duration+0.05);
            } catch(e) {}
        }
        P.NM = P.NM || {};
        P.NM.soundHover   = function(){ playTone(660,'sine',.08,.04); };
        P.NM.soundClick   = function(){ playTone(880,'triangle',.12,.07); };
        P.NM.soundSend    = function(){
            [523,659,784].forEach(function(f,i){
                setTimeout(function(){ playTone(f,'sine',.08,.05); }, i*60);
            });
        };
        P.NM.soundSuccess = function(){
            [523,659,784,1047].forEach(function(f,i){
                setTimeout(function(){ playTone(f,'sine',.18,.04); }, i*80);
            });
        };
        P.NM.soundError   = function(){ playTone(220,'sawtooth',.3,.05); };
    }

    // ── Scroll reveal ────────────────────────────────────────────
    function initScrollReveal() {
        if (!D.querySelectorAll) return;
        var io = new IntersectionObserver(function(entries) {
            entries.forEach(function(e) {
                if(e.isIntersecting) { e.target.classList.add('visible'); io.unobserve(e.target); }
            });
        }, {threshold:0.1});
        D.querySelectorAll('.reveal').forEach(function(el){ io.observe(el); });
    }

    // ── Button sound hooks ───────────────────────────────────────
    function hookSounds() {
        D.querySelectorAll('.stButton > button').forEach(function(btn) {
            if(btn.dataset.nmHooked) return;
            btn.dataset.nmHooked = '1';
            btn.addEventListener('mouseenter', function(){ P.NM && P.NM.soundHover(); });
            btn.addEventListener('click',      function(){ P.NM && P.NM.soundClick(); });
        });
    }

    // ── Re-hook after Streamlit re-renders ───────────────────────
    new MutationObserver(function() { hookSounds(); initScrollReveal(); })
        .observe(D.body, {childList:true, subtree:true});

    // ── Boot ─────────────────────────────────────────────────────
    setupAudio();
    initCanvas();
    initCursorGlow();
    initScrollReveal();
    hookSounds();
})();
</script>
""", height=0, scrolling=False)


# Navbar
def render_navbar(active_page: str = "chat"):
    pages = [
        ("chat",    "⚡ Chat",         "/"),
        ("vectors", "🔮 Vector Space", "/vector_graph"),
    ]
    links_html = "".join(
        f'<li><a href="{p[2]}" class="{"active" if active_page == p[0] else ""}">{p[1]}</a></li>'
        for p in pages
    )
    st.markdown(f"""
<nav class="nm-nav">
  <div class="nm-nav-logo">
    <div class="nm-nav-logo-icon">🧠</div>
    <span class="nm-nav-logo-text">Neural Mind</span>
  </div>
  <ul class="nm-nav-links">{links_html}</ul>
  <div class="nm-nav-status">
    <span class="nm-status-dot"></span>
    RAG • Gemini 2.5 Flash
  </div>
</nav>
""", unsafe_allow_html=True)


# Hero 
def render_hero():
    st.markdown("""
<section class="nm-hero">
  <div>
    <div class="nm-hero-eyebrow reveal">✦ RETRIEVAL AUGMENTED GENERATION</div>
    <h1 class="nm-hero-title reveal">Talk to your<br><span>knowledge base.</span></h1>
    <p class="nm-hero-desc reveal">
      Upload any text as your context. Ask questions in natural language.
      Watch the AI retrieve, reason, and respond — all in real-time.
    </p>
    <div class="nm-hero-stats reveal">
      <div class="nm-stat"><span class="nm-stat-num">768</span><span class="nm-stat-label">Dimensions</span></div>
      <div class="nm-stat"><span class="nm-stat-num">all-mpnet</span><span class="nm-stat-label">Embeddings</span></div>
      <div class="nm-stat"><span class="nm-stat-num">Gemini</span><span class="nm-stat-label">LLM</span></div>
    </div>
  </div>
  <div class="nm-hero-visual">
    <div class="nm-orbit nm-orbit-1"><span class="nm-orbit-dot"></span></div>
    <div class="nm-orbit nm-orbit-2"><span class="nm-orbit-dot" style="background:var(--accent-cyan)"></span></div>
    <div class="nm-robot-card">
      <div class="nm-robot-emoji">🤖</div>
      <div class="nm-robot-speech">
        <strong>Ready to assist</strong>
        Upload your knowledge base,<br>then ask me anything.
      </div>
      <div class="nm-pills">
        <span class="nm-pill nm-pill-violet">✦ RAG Pipeline</span>
        <span class="nm-pill nm-pill-cyan">MongoDB Atlas</span>
        <span class="nm-pill nm-pill-pink">HuggingFace</span>
      </div>
    </div>
  </div>
</section>
""", unsafe_allow_html=True)


# Section header 
def render_section_header(title: str):
    st.markdown(f"""
<div class="nm-section-header reveal">
  <span class="nm-section-title">{title}</span>
  <div class="nm-section-line"></div>
</div>
""", unsafe_allow_html=True)


# Toasts 
def toast_success(msg: str):
    st.markdown(f'<div class="nm-toast nm-toast-success"><span>✓</span> {msg}</div>',
                unsafe_allow_html=True)

def toast_info(msg: str):
    st.markdown(f'<div class="nm-toast nm-toast-info"><span>◎</span> {msg}</div>',
                unsafe_allow_html=True)


# Chat message renderer 
def render_message(role: str, content: str, sources=None):
    if role == "user":
        st.markdown(f"""
<div class="nm-message user">
  <div class="nm-msg-avatar user">👤</div>
  <div class="nm-msg-bubble">{content}</div>
</div>""", unsafe_allow_html=True)
    else:
        sources_html = ""
        if sources:
            items = "".join(
                f'<div class="nm-source-item">◈ {s.page_content[:180]}{"…" if len(s.page_content)>180 else ""}</div>'
                for s in sources
            )
            sources_html = f"""
<details>
  <summary class="nm-sources-header">▸ {len(sources)} sources retrieved</summary>
  <div class="nm-sources">{items}</div>
</details>"""
        st.markdown(f"""
<div class="nm-message">
  <div class="nm-msg-avatar ai">🧠</div>
  <div>
    <div class="nm-msg-bubble">{content}</div>
    {sources_html}
  </div>
</div>""", unsafe_allow_html=True)


# Vector page hero 
def render_vector_hero():
    st.markdown("""
<div class="nm-vector-hero">
  <h1 class="nm-vector-title reveal">Vector Space</h1>
  <p class="nm-vector-sub reveal">
    Enter a query to see how it relates to your stored documents
    in high-dimensional semantic space. 768D → 2D via PCA.
  </p>
</div>
""", unsafe_allow_html=True)