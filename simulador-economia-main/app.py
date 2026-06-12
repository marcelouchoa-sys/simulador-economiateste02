# app.py — OikosLab Laboratório Didático
from pathlib import Path
import streamlit as st
import base64

BASE_DIR  = Path(__file__).parent
LOGO_PATH = BASE_DIR / "assets" / "logo.webp"

def _logo_base64() -> str:
    try:
        with open(LOGO_PATH, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return ""

st.set_page_config(
    page_title="OikosLab — Laboratório Didático",
    page_icon=str(LOGO_PATH),
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800&display=swap');

* { font-family: 'Montserrat', -apple-system, sans-serif !important; }

.stApp { background: #0b0f19 !important; }
#MainMenu, footer, header { visibility: hidden; }
section[data-testid="stSidebar"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* HEADER */
.oikos-header {
    position: fixed;
    top: 0; left: 0; right: 0;
    z-index: 9999;
    background: rgba(11,15,25,0.85);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-bottom: 1px solid rgba(255,255,255,0.08);
    padding: 0 48px;
    height: 56px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.oikos-logo {
    display: flex;
    align-items: center;
    gap: 10px;
    text-decoration: none;
}
.oikos-logo img { height: 28px; width: auto; object-fit: contain; }
.oikos-logo span {
    font-size: 1.1rem;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: -0.02em;
}
.header-right {
    display: flex;
    align-items: center;
    gap: 12px;
}
.btn-plataforma {
    background: #2563eb;
    color: #ffffff !important;
    padding: 8px 18px;
    border-radius: 10px;
    font-size: 0.82rem;
    font-weight: 600;
    text-decoration: none;
    transition: background 0.2s;
}
.btn-plataforma:hover { background: #1d4ed8 !important; }
.header-spacer { height: 80px; }

/* HERO MINIMO */
.hero-min {
    padding: 60px 48px 40px;
    text-align: center;
}
.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 100px;
    padding: 6px 16px;
    margin-bottom: 24px;
}
.badge-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #4ade80;
}
.badge-text {
    font-size: 0.78rem;
    color: #9ca3af;
    font-weight: 500;
}
.hero-titulo {
    font-size: 2.6rem;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.04em;
    line-height: 1.15;
    margin-bottom: 16px;
}
.hero-titulo span {
    background: linear-gradient(90deg, #60a5fa, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-sub {
    font-size: 1rem;
    color: #6b7280;
    max-width: 480px;
    margin: 0 auto;
    line-height: 1.65;
}

/* GRID DE SIMULADORES */
.simuladores-section {
    padding: 20px 48px 80px;
}
.section-label {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #4b5563;
    margin-bottom: 24px;
    text-align: center;
}
.simuladores-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
    max-width: 960px;
    margin: 0 auto;
}
.sim-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-top: 2px solid transparent;
    border-radius: 20px;
    padding: 28px;
    transition: background 0.2s, transform 0.2s, box-shadow 0.2s;
    position: relative;
    overflow: hidden;
}
.sim-card:hover {
    background: rgba(255,255,255,0.08);
    transform: translateY(-3px);
    box-shadow: 0 20px 40px rgba(0,0,0,0.3);
}
.sim-card.blue  { border-top-color: #3b82f6; }
.sim-card.purple { border-top-color: #8b5cf6; }
.sim-card.green  { border-top-color: #10b981; }
.sim-card.cyan   { border-top-color: #06b6d4; }
.sim-card.orange { border-top-color: #f59e0b; }
.sim-card.muted  { border-top-color: #374151; opacity: 0.6; }

.sim-icon {
    width: 44px; height: 44px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.3rem;
    margin-bottom: 16px;
}
.icon-blue   { background: rgba(59,130,246,0.15); }
.icon-purple { background: rgba(139,92,246,0.15); }
.icon-green  { background: rgba(16,185,129,0.15); }
.icon-cyan   { background: rgba(6,182,212,0.15); }
.icon-orange { background: rgba(245,158,11,0.15); }
.icon-muted  { background: rgba(55,65,81,0.3); }

.sim-tag {
    display: inline-block;
    font-size: 0.68rem;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 100px;
    margin-bottom: 12px;
}
.tag-blue   { background: rgba(59,130,246,0.15);  color: #93c5fd; }
.tag-purple { background: rgba(139,92,246,0.15); color: #c4b5fd; }
.tag-green  { background: rgba(16,185,129,0.15); color: #6ee7b7; }
.tag-cyan   { background: rgba(6,182,212,0.15);  color: #67e8f9; }
.tag-orange { background: rgba(245,158,11,0.15); color: #fcd34d; }
.tag-muted  { background: rgba(55,65,81,0.3);    color: #6b7280; }

.sim-titulo {
    font-size: 1rem;
    font-weight: 700;
    color: #f9fafb;
    margin-bottom: 8px;
    letter-spacing: -0.01em;
}
.sim-desc {
    font-size: 0.82rem;
    color: #6b7280;
    line-height: 1.6;
    margin-bottom: 20px;
}
.sim-btn {
    display: block;
    text-align: center;
    padding: 10px 16px;
    border-radius: 12px;
    font-size: 0.82rem;
    font-weight: 600;
    text-decoration: none;
    transition: background 0.2s;
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.1);
    color: #e5e7eb;
}
.sim-btn:hover {
    background: rgba(255,255,255,0.12);
    color: #ffffff;
}
.sim-btn-disabled {
    display: block;
    text-align: center;
    padding: 10px 16px;
    border-radius: 12px;
    font-size: 0.82rem;
    font-weight: 600;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.05);
    color: #374151;
    cursor: not-allowed;
}

/* FOOTER */
.oikos-footer {
    border-top: 1px solid rgba(255,255,255,0.06);
    padding: 28px 48px;
    text-align: center;
}
.footer-text {
    font-size: 0.78rem;
    color: #374151;
}
</style>
""", unsafe_allow_html=True)

logo_b64 = _logo_base64()
logo_html = f'<img src="data:image/webp;base64,{logo_b64}" alt="OikosLab"/>' if logo_b64 else ''

st.markdown(f"""
<div class="oikos-header">
    <a class="oikos-logo" href="#">
        {logo_html}
        <span>OikosLab</span>
    </a>
    <div class="header-right">
        <a href="https://oikoslab-platform.vercel.app" target="_blank" class="btn-plataforma">
            Acessar Plataforma
        </a>
    </div>
</div>
<div class="header-spacer"></div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero-min">
    <div class="hero-badge">
        <div class="badge-dot"></div>
        <span class="badge-text">Laboratório Didático — UFRRJ</span>
    </div>
    <div class="hero-titulo">
        Escolha um<br>
        <span>simulador</span>
    </div>
    <div class="hero-sub">
        Explore os modelos econômicos disponíveis. Sem cadastro, sem login.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="simuladores-section">
    <div class="section-label">Simuladores disponíveis</div>
    <div class="simuladores-grid">

        <div class="sim-card blue">
            <div class="sim-icon icon-blue">📈</div>
            <span class="sim-tag tag-blue">Disponível</span>
            <div class="sim-titulo">Funções Econômicas</div>
            <div class="sim-desc">Analise individualmente as funções macroeconômicas: consumo, investimento, oferta agregada, demanda por moeda e mais.</div>
            <a href="/Funcoes" class="sim-btn">Acessar →</a>
        </div>

        <div class="sim-card purple">
            <div class="sim-icon icon-purple">🏫</div>
            <span class="sim-tag tag-purple">Disponível</span>
            <div class="sim-titulo">Escolas Econômicas</div>
            <div class="sim-desc">Compare as grandes correntes do pensamento econômico: Clássica, Keynesiana, Monetarista e Pós-Keynesiana.</div>
            <a href="/Escolas_Economicas" class="sim-btn">Acessar →</a>
        </div>

        <div class="sim-card green">
            <div class="sim-icon icon-green">🌐</div>
            <span class="sim-tag tag-green">Disponível</span>
            <div class="sim-titulo">Economia Aberta</div>
            <div class="sim-desc">Modelo IS-LM-BP (Mundell-Fleming). Câmbio fixo e flexível, mobilidade de capital e choques de política.</div>
            <a href="/Economia_Aberta" class="sim-btn">Acessar →</a>
        </div>

    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="oikos-footer">
    <div class="footer-text">OikosLab · Marcelo de Salles Cunha Uchôa · UFRRJ · 2026</div>
</div>
""", unsafe_allow_html=True)
