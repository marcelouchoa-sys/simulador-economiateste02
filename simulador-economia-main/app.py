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

logo_b64 = _logo_base64()
logo_html = f'<img src="data:image/webp;base64,{logo_b64}" style="height:28px;width:auto;object-fit:contain;" alt="OikosLab"/>' if logo_b64 else ''

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800&display=swap');
* { font-family: 'Montserrat', sans-serif !important; }
.stApp { background: #0b0f19 !important; }
#MainMenu, footer, header { visibility: hidden; }
section[data-testid="stSidebar"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
.block-container { padding: 2rem 3rem !important; max-width: 100% !important; }
div[data-testid="column"] { padding: 0 8px !important; }

.oikos-header {
    position: fixed; top: 0; left: 0; right: 0; z-index: 9999;
    background: rgba(11,15,25,0.9);
    backdrop-filter: blur(16px);
    border-bottom: 1px solid rgba(255,255,255,0.08);
    padding: 0 48px; height: 56px;
    display: flex; align-items: center; justify-content: space-between;
}
.oikos-logo { display: flex; align-items: center; gap: 10px; text-decoration: none; }
.oikos-logo-text { font-size: 1.1rem; font-weight: 700; color: #fff; letter-spacing: -0.02em; }
.btn-plataforma {
    background: #2563eb; color: #fff !important;
    padding: 8px 18px; border-radius: 10px;
    font-size: 0.82rem; font-weight: 600;
    text-decoration: none;
}

.hero-wrap { text-align: center; padding: 40px 0 32px; }
.hero-badge {
    display: inline-flex; align-items: center; gap: 8px;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 100px; padding: 6px 16px; margin-bottom: 20px;
}
.badge-dot { width: 8px; height: 8px; border-radius: 50%; background: #4ade80; display: inline-block; }
.badge-text { font-size: 0.78rem; color: #9ca3af; font-weight: 500; }
.hero-titulo { font-size: 2.8rem; font-weight: 800; color: #fff; letter-spacing: -0.04em; line-height: 1.15; margin-bottom: 14px; }
.hero-titulo span { background: linear-gradient(90deg, #60a5fa, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.hero-sub { font-size: 0.95rem; color: #6b7280; max-width: 440px; margin: 0 auto; line-height: 1.65; }

.section-label { font-size: 0.68rem; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: #4b5563; text-align: center; margin-bottom: 8px; }

.sim-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px; padding: 28px;
    height: 100%;
    transition: background 0.2s, transform 0.2s;
}
.sim-card:hover { background: rgba(255,255,255,0.08); }
.sim-card.blue  { border-top: 2px solid #3b82f6; }
.sim-card.purple { border-top: 2px solid #8b5cf6; }
.sim-card.green  { border-top: 2px solid #10b981; }

.sim-icon { font-size: 1.6rem; margin-bottom: 14px; }
.sim-tag {
    display: inline-block; font-size: 0.68rem; font-weight: 600;
    padding: 3px 10px; border-radius: 100px; margin-bottom: 12px;
}
.tag-blue   { background: rgba(59,130,246,0.15); color: #93c5fd; }
.tag-purple { background: rgba(139,92,246,0.15); color: #c4b5fd; }
.tag-green  { background: rgba(16,185,129,0.15); color: #6ee7b7; }

.sim-titulo { font-size: 1.05rem; font-weight: 700; color: #f9fafb; margin-bottom: 10px; }
.sim-desc   { font-size: 0.82rem; color: #6b7280; line-height: 1.6; margin-bottom: 20px; min-height: 64px; }

.sim-btn {
    display: block; text-align: center; padding: 10px 16px;
    border-radius: 12px; font-size: 0.82rem; font-weight: 600;
    text-decoration: none; color: #e5e7eb;
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.1);
}
.sim-btn:hover { background: rgba(255,255,255,0.12); color: #fff; }

.oikos-footer { border-top: 1px solid rgba(255,255,255,0.06); padding: 24px; text-align: center; margin-top: 60px; }
.footer-text  { font-size: 0.75rem; color: #374151; }
</style>
""", unsafe_allow_html=True)

# HEADER
st.markdown(f"""
<div class="oikos-header">
    <div class="oikos-logo">
        {logo_html}
        <span class="oikos-logo-text">OikosLab</span>
    </div>
    <a href="https://oikoslab-platform.vercel.app" target="_blank" class="btn-plataforma">
        Acessar Plataforma
    </a>
</div>
<div style="height:72px"></div>
""", unsafe_allow_html=True)

# HERO
st.markdown("""
<div class="hero-wrap">
    <div class="hero-badge">
        <span class="badge-dot"></span>
        <span class="badge-text">Laboratório Didático — UFRRJ</span>
    </div>
    <div class="hero-titulo">Escolha um<br><span>simulador</span></div>
    <div class="hero-sub">Explore os modelos econômicos disponíveis. Sem cadastro, sem login.</div>
</div>
""", unsafe_allow_html=True)

# LABEL
st.markdown('<div class="section-label">Simuladores disponíveis</div>', unsafe_allow_html=True)

# CARDS com st.columns
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="sim-card blue">
        <div class="sim-icon">📈</div>
        <span class="sim-tag tag-blue">Disponível</span>
        <div class="sim-titulo">Funções Econômicas</div>
        <div class="sim-desc">Analise individualmente as funções macroeconômicas: consumo, investimento, oferta agregada, demanda por moeda e mais.</div>
        <a href="/Funcoes" target="_self" class="sim-btn">Acessar →</a>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="sim-card purple">
        <div class="sim-icon">🏛️</div>
        <span class="sim-tag tag-purple">Disponível</span>
        <div class="sim-titulo">Escolas Econômicas</div>
        <div class="sim-desc">Compare as grandes correntes do pensamento econômico: Clássica, Keynesiana, Monetarista e Pós-Keynesiana.</div>
        <a href="/Escolas_Economicas" target="_self" class="sim-btn">Acessar →</a>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="sim-card green">
        <div class="sim-icon">🌐</div>
        <span class="sim-tag tag-green">Disponível</span>
        <div class="sim-titulo">Economia Aberta</div>
        <div class="sim-desc">Modelo IS-LM-BP (Mundell-Fleming). Câmbio fixo e flexível, mobilidade de capital e choques de política.</div>
        <a href="/Economia_Aberta" target="_self" class="sim-btn">Acessar →</a>
    </div>
    """, unsafe_allow_html=True)

# FOOTER
st.markdown("""
<div class="oikos-footer">
    <div class="footer-text">OikosLab · Marcelo de Salles Cunha Uchôa · UFRRJ · 2026</div>
</div>
""", unsafe_allow_html=True)
