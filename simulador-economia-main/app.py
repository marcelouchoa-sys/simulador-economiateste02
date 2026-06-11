# app.py — OikosLab Landing Page
from pathlib import Path
import streamlit as st
from core.parameters import DEFAULT_PARAMS
from core.auth import init_auth_state
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
    page_title="OikosLab — Laboratório de Economia",
    page_icon=str(LOGO_PATH),
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "params" not in st.session_state:
    st.session_state.params = DEFAULT_PARAMS.copy()
if "settings" not in st.session_state:
    st.session_state.settings = {
        "nivel": "Medio",
        "mobilidade_capital": "Alta",
        "color_base":  "#0066CC",
        "color_shock": "#C0392B",
        "color_final": "#1D7A4F",
    }

init_auth_state()
from core.auth import restore_session
restore_session()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&display=swap');

* { font-family: 'DM Sans', -apple-system, sans-serif !important; }

/* ── Reset e fundo ── */
.stApp { background: #FFFFFF; }
#MainMenu, footer, header { visibility: hidden; }
section[data-testid="stSidebar"]  { display: none !important; }
[data-testid="collapsedControl"]   { display: none !important; }

/* ── Header fixo ── */
.oikos-header {
    position: fixed;
    top: 0; left: 0; right: 0;
    z-index: 9999;
    background: rgba(255,255,255,0.92);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-bottom: 1px solid #E5E5EA;
    padding: 0 48px;
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.oikos-header-logo {
    font-size: 1.2rem;
    font-weight: 700;
    color: #1D1D1F;
    letter-spacing: -0.02em;
    text-decoration: none;
    display: flex;
    align-items: center;
    gap: 10px;
}
.oikos-header-logo img {
    height: 32px;
    width: auto;
}
.oikos-nav {
    display: flex;
    align-items: center;
    gap: 32px;
}
.oikos-nav a {
    font-size: 0.88rem;
    font-weight: 500;
    color: #1D1D1F;
    text-decoration: none;
    transition: color 0.2s;
}
.oikos-nav a:hover { color: #0066CC; }
.oikos-nav-btn {
    background: #0066CC;
    color: #FFFFFF !important;
    padding: 8px 20px;
    border-radius: 10px;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    transition: background 0.2s !important;
}
.oikos-nav-btn:hover { background: #0055AA !important; }

/* ── Espaço abaixo do header fixo ── */
.header-spacer { height: 80px; }

/* ── Hero ── */
.hero {
    padding: 100px 48px 80px 48px;
    text-align: center;
    background: linear-gradient(180deg, #F5F5F7 0%, #FFFFFF 100%);
}
.hero-tag {
    display: inline-block;
    background: #E3F0FF;
    color: #0055AA;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    padding: 4px 14px;
    border-radius: 20px;
    margin-bottom: 24px;
}
.hero-titulo {
    font-size: 3.2rem;
    font-weight: 700;
    color: #1D1D1F;
    letter-spacing: -0.04em;
    line-height: 1.1;
    margin-bottom: 20px;
    max-width: 700px;
    margin-left: auto;
    margin-right: auto;
}
.hero-titulo span {
    background: linear-gradient(90deg, #0066CC, #6E3B9E);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-sub {
    font-size: 1.1rem;
    color: #6E6E73;
    max-width: 520px;
    margin: 0 auto 36px auto;
    line-height: 1.6;
    font-weight: 400;
}
.hero-btns {
    display: flex;
    gap: 14px;
    justify-content: center;
    flex-wrap: wrap;
}
.btn-primary {
    background: #0066CC;
    color: #FFFFFF;
    padding: 14px 28px;
    border-radius: 12px;
    font-size: 0.95rem;
    font-weight: 600;
    text-decoration: none;
    transition: background 0.2s, transform 0.2s;
    display: inline-block;
}
.btn-primary:hover {
    background: #0055AA;
    transform: translateY(-1px);
    color: #FFFFFF;
}
.btn-secondary {
    background: #F5F5F7;
    color: #1D1D1F;
    padding: 14px 28px;
    border-radius: 12px;
    font-size: 0.95rem;
    font-weight: 500;
    text-decoration: none;
    border: 1px solid #D2D2D7;
    transition: background 0.2s, transform 0.2s;
    display: inline-block;
}
.btn-secondary:hover {
    background: #E8E8ED;
    transform: translateY(-1px);
    color: #1D1D1F;
}

/* ── Seções ── */
.section {
    padding: 80px 48px;
}
.section-alt { background: #F5F5F7; }
.section-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #6E6E73;
    margin-bottom: 10px;
}
.section-titulo {
    font-size: 2rem;
    font-weight: 700;
    color: #1D1D1F;
    letter-spacing: -0.03em;
    margin-bottom: 12px;
}
.section-sub {
    font-size: 1rem;
    color: #6E6E73;
    max-width: 560px;
    line-height: 1.6;
    margin-bottom: 48px;
}

/* ── Cards dos módulos ── */
.modulos-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 20px;
    margin-top: 40px;
}
.modulo-card {
    background: #FFFFFF;
    border: 1px solid #D2D2D7;
    border-radius: 18px;
    padding: 28px 24px 22px 24px;
    position: relative;
    overflow: hidden;
    transition: box-shadow 0.25s, transform 0.25s;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.modulo-card:hover {
    box-shadow: 0 8px 28px rgba(0,0,0,0.10);
    transform: translateY(-2px);
}
.modulo-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 4px;
    border-radius: 18px 18px 0 0;
}
.mc-blue::before   { background: #0066CC; }
.mc-purple::before { background: #6E3B9E; }
.mc-green::before  { background: #1D7A4F; }
.mc-slate::before  { background: #3A4D6B; }
.mc-muted::before  { background: #B0B0B8; }
.mc-muted          { opacity: 0.6; }

.modulo-titulo { font-size: 1rem; font-weight: 600; color: #1D1D1F; margin-bottom: 8px; letter-spacing: -0.01em; }
.modulo-desc   { font-size: 0.83rem; color: #6E6E73; line-height: 1.55; margin-bottom: 16px; }
.modulo-tag    { display: inline-flex; padding: 3px 10px; border-radius: 20px; font-size: 0.72rem; font-weight: 500; }

.tag-blue   { background: #E3F0FF; color: #0055AA; }
.tag-purple { background: #F0E8FA; color: #5A2D8A; }
.tag-green  { background: #E3F5EC; color: #145E3A; }
.tag-slate  { background: #E8ECF2; color: #2C3E5A; }
.tag-muted  { background: #EBEBED; color: #6E6E73; }

.modulo-btn {
    display: block;
    margin-top: 16px;
    text-align: center;
    padding: 9px 16px;
    background: #F5F5F7;
    border: 1px solid #D2D2D7;
    border-radius: 10px;
    font-size: 0.83rem;
    font-weight: 500;
    color: #1D1D1F;
    text-decoration: none;
    transition: background 0.2s, border-color 0.2s;
}
.modulo-btn:hover {
    background: #E8E8ED;
    border-color: #0066CC;
    color: #0066CC;
}

/* ── Sobre ── */
.sobre-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 60px;
    align-items: center;
}
.sobre-texto p {
    font-size: 0.95rem;
    color: #3A3A3C;
    line-height: 1.75;
    margin-bottom: 16px;
}
.sobre-stats {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
}
.stat-card {
    background: #FFFFFF;
    border: 1px solid #E5E5EA;
    border-radius: 14px;
    padding: 24px;
    text-align: center;
}
.stat-num  { font-size: 2rem; font-weight: 700; color: #0066CC; letter-spacing: -0.03em; }
.stat-desc { font-size: 0.8rem; color: #6E6E73; margin-top: 4px; }

/* ── Sobre mim ── */
.sobreMim-card {
    background: #FFFFFF;
    border: 1px solid #D2D2D7;
    border-radius: 20px;
    padding: 40px;
    max-width: 700px;
    margin: 40px auto 0 auto;
    text-align: center;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}
.sobreMim-avatar {
    width: 80px; height: 80px;
    border-radius: 50%;
    background: linear-gradient(135deg, #0066CC, #6E3B9E);
    margin: 0 auto 20px auto;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2rem;
    color: white;
    font-weight: 700;
}
.sobreMim-nome { font-size: 1.3rem; font-weight: 700; color: #1D1D1F; margin-bottom: 6px; }
.sobreMim-cargo { font-size: 0.88rem; color: #6E6E73; margin-bottom: 20px; }
.sobreMim-bio { font-size: 0.92rem; color: #3A3A3C; line-height: 1.7; }

/* ── Contato ── */
.contato-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
    max-width: 700px;
    margin: 40px auto 0 auto;
}
.contato-card {
    background: #FFFFFF;
    border: 1px solid #E5E5EA;
    border-radius: 14px;
    padding: 28px 20px;
    text-align: center;
    transition: box-shadow 0.2s, transform 0.2s;
}
.contato-card:hover {
    box-shadow: 0 6px 20px rgba(0,0,0,0.08);
    transform: translateY(-2px);
}
.contato-tipo  { font-size: 0.72rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; color: #6E6E73; margin-bottom: 8px; }
.contato-valor { font-size: 0.9rem; font-weight: 500; color: #0066CC; }

/* ── Footer ── */
.oikos-footer {
    background: #F5F5F7;
    border-top: 1px solid #E5E5EA;
    padding: 32px 48px;
    text-align: center;
}
.footer-logo { font-size: 1.1rem; font-weight: 700; color: #1D1D1F; margin-bottom: 8px; }
.footer-sub  { font-size: 0.78rem; color: #AEAEB2; }

/* ── Divisor ── */
.divider { border: none; border-top: 1px solid #E5E5EA; margin: 0; }

/* ── Próximas bancadas ── */
.futuras-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-top: 32px;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# HEADER FIXO
# ══════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="oikos-header">
    <a class="oikos-header-logo" href="#inicio">
        <img src="data:image/webp;base64,{_logo_base64()}" alt="OikosLab"/>
        OikosLab
    </a>
    <nav class="oikos-nav">
        <a href="#modulos">Simuladores</a>
        <a href="#sobre">Sobre o OikosLab</a>
        <a href="#sobreMim">Sobre mim</a>
        <a href="#contato">Contato</a>
        <a href="/Login" class="oikos-nav-btn">Entrar</a>
    </nav>
</div>
<div class="header-spacer"></div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="position:fixed; top:12px; right:60px; z-index:9999;">
    <a href="https://oikoslab-platform.vercel.app" target="_blank"
       style="background:#0066CC; color:white; padding:8px 18px;
              border-radius:10px; font-size:0.85rem; font-weight:600;
              text-decoration:none; font-family:'DM Sans',sans-serif;">
        Acessar Plataforma
    </a>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# HERO
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<div id="inicio" class="hero">
    <div class="hero-tag">Laboratório de Economia Experimental</div>
    <div class="hero-titulo">
        Explore, simule e analise<br>
        <span>economias completas</span>
    </div>
    <div class="hero-sub">
        OikosLab é uma plataforma de simulação macroeconômica desenvolvida na UFRRJ.
        Do modelo IS-LM-BP às escolas do pensamento econômico — tudo em um lugar.
    </div>
    <div class="hero-btns">
        <a href="#modulos" class="btn-primary">Explorar simuladores</a>
        <a href="#sobre" class="btn-secondary">Saiba mais</a>
    </div>
</div>
<hr class="divider">
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# MÓDULOS
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<div id="modulos" class="section">
    <div class="section-label">Módulos disponíveis</div>
    <div class="section-titulo">Escolha uma área para explorar</div>
    <div class="section-sub">
        Cada módulo é uma bancada independente do laboratório.
        Analise funções, compare escolas ou simule economias abertas.
    </div>
    <div class="modulos-grid">
        <div class="modulo-card mc-blue">
            <div class="modulo-titulo">Funções Econômicas</div>
            <div class="modulo-desc">Analise individualmente as funções macroeconômicas fundamentais. Consumo, investimento, oferta agregada e mais.</div>
            <span class="modulo-tag tag-blue">Disponível</span>
            <a href="/Funcoes" class="modulo-btn">Acessar módulo</a>
        </div>
        <div class="modulo-card mc-purple">
            <div class="modulo-titulo">Escolas Econômicas</div>
            <div class="modulo-desc">Compare as grandes correntes do pensamento econômico. Clássica, Keynesiana, Monetarista e Pós-Keynesiana.</div>
            <span class="modulo-tag tag-purple">Disponível</span>
            <a href="/Escolas_Economicas" class="modulo-btn">Acessar módulo</a>
        </div>
        <div class="modulo-card mc-green">
            <div class="modulo-titulo">Economia Aberta</div>
            <div class="modulo-desc">Modelo IS-LM-BP (Mundell-Fleming). Câmbio fixo e flexível, graus de mobilidade de capital.</div>
            <span class="modulo-tag tag-green">Disponível</span>
            <a href="/Economia_Aberta" class="modulo-btn">Acessar módulo</a>
        </div>
        <div class="modulo-card mc-slate">
            <div class="modulo-titulo">Laboratório</div>
            <div class="modulo-desc">Construa e analise economias completas. Monte modelos, aplique políticas e visualize resultados.</div>
            <span class="modulo-tag tag-slate">Em construção</span>
            <a href="/Laboratorio" class="modulo-btn">Acessar módulo</a>
        </div>
    </div>
</div>
<hr class="divider">
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# SOBRE O OIKOSLAB
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<div id="sobre" class="section section-alt">
    <div class="section-label">Sobre o OikosLab</div>
    <div class="section-titulo">Um laboratório construído para crescer</div>
    <div class="sobre-grid">
        <div class="sobre-texto">
            <p>
                OikosLab é um projeto de graduação desenvolvido na Universidade Federal
                Rural do Rio de Janeiro (UFRRJ), com o objetivo de criar uma plataforma
                completa de simulação e análise econômica.
            </p>
            <p>
                O nome vem do grego <em>οἶκος</em> (oikos), que significa "casa" ou
                "gestão da casa" — raiz etimológica da palavra "economia".
            </p>
            <p>
                O projeto será desenvolvido ao longo de toda a graduação, crescendo
                junto com o conhecimento econômico do autor. Cada semestre novos
                modelos, ferramentas e análises são adicionados.
            </p>
        </div>
        <div class="sobre-stats">
            <div class="stat-card">
                <div class="stat-num">4</div>
                <div class="stat-desc">Módulos disponíveis</div>
            </div>
            <div class="stat-card">
                <div class="stat-num">9</div>
                <div class="stat-desc">Funções econômicas</div>
            </div>
            <div class="stat-card">
                <div class="stat-num">4</div>
                <div class="stat-desc">Escolas de pensamento</div>
            </div>
            <div class="stat-card">
                <div class="stat-num">∞</div>
                <div class="stat-desc">Em construção contínua</div>
            </div>
        </div>
    </div>
</div>
<hr class="divider">
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# SOBRE MIM
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<div id="sobreMim" class="section">
    <div class="section-label">Sobre mim</div>
    <div class="section-titulo">Quem está por trás do OikosLab</div>
    <div class="sobreMim-card">
        <div class="sobreMim-avatar">M</div>
        <div class="sobreMim-nome">Marcelo de Salles Cunha Uchôa</div>
        <div class="sobreMim-cargo">Estudante de Economia — UFRRJ</div>
        <div class="sobreMim-bio">
            Em breve — texto sobre trajetória, interesses e motivações para criar o OikosLab.
        </div>
    </div>
</div>
<hr class="divider">
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# CONTATO
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<div id="contato" class="section section-alt">
    <div class="section-label">Contato</div>
    <div class="section-titulo">Fale comigo</div>
    <div class="contato-grid">
        <div class="contato-card">
            <div class="contato-tipo">Email</div>
            <div class="contato-valor">Em breve</div>
        </div>
        <div class="contato-card">
            <div class="contato-tipo">LinkedIn</div>
            <div class="contato-valor">Em breve</div>
        </div>
        <div class="contato-card">
            <div class="contato-tipo">GitHub</div>
            <div class="contato-valor">Em breve</div>
        </div>
    </div>
</div>
<hr class="divider">
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<div class="oikos-footer">
    <div class="footer-logo">OikosLab</div>
    <div class="footer-sub">
        Marcelo de Salles Cunha Uchôa &nbsp;·&nbsp; UFRRJ &nbsp;·&nbsp;
        Projeto de graduação em desenvolvimento contínuo
    </div>
</div>
""", unsafe_allow_html=True)