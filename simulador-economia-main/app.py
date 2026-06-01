# app.py
from pathlib import Path
import streamlit as st
from core.parameters import DEFAULT_PARAMS

BASE_DIR  = Path(__file__).parent
LOGO_PATH = BASE_DIR / "assets" / "logo.webp"

st.set_page_config(
    page_title="LBEX — Laboratorio de Economia",
    page_icon=str(LOGO_PATH),
    layout="wide",
    initial_sidebar_state="expanded",
)

if "params" not in st.session_state:
    st.session_state.params = DEFAULT_PARAMS.copy()

if "settings" not in st.session_state:
    st.session_state.settings = {
        "nivel": "Medio",
        "mobilidade_capital": "Alta",
        "detalhe_causal": True,
        "show_grid": True,
        "color_base":  "#0066CC",
        "color_shock": "#C0392B",
        "color_final": "#1D7A4F",
    }

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"], .stMarkdown, p, div, span {
    font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

.stApp { background-color: #FFFFFF; }

section[data-testid="stSidebar"] {
    background-color: #F5F5F7;
    border-right: 1px solid #D2D2D7;
}

.lbex-card {
    background: #F5F5F7;
    border: 1px solid #D2D2D7;
    border-radius: 18px;
    padding: 26px 24px 20px 24px;
    margin-bottom: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    transition: box-shadow 0.25s ease, transform 0.25s ease;
    position: relative;
    overflow: hidden;
    height: 100%;
}
.lbex-card:hover {
    box-shadow: 0 8px 28px rgba(0,0,0,0.11);
    transform: translateY(-2px);
}
.lbex-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 4px;
    border-radius: 18px 18px 0 0;
}
.lbex-card.card-blue::before   { background: #0066CC; }
.lbex-card.card-purple::before { background: #6E3B9E; }
.lbex-card.card-green::before  { background: #1D7A4F; }
.lbex-card.card-slate::before  { background: #3A4D6B; }
.lbex-card.card-muted::before  { background: #B0B0B8; }
.lbex-card.card-muted          { opacity: 0.65; }

.card-titulo { font-size: 1rem; font-weight: 600; color: #1D1D1F; margin-bottom: 8px; letter-spacing: -0.01em; }
.card-desc   { font-size: 0.83rem; color: #6E6E73; line-height: 1.55; margin-bottom: 14px; }
.card-tag    { display: inline-flex; align-items: center; padding: 3px 10px; border-radius: 20px; font-size: 0.72rem; font-weight: 500; }

.tag-blue   { background: #E3F0FF; color: #0055AA; }
.tag-purple { background: #F0E8FA; color: #5A2D8A; }
.tag-green  { background: #E3F5EC; color: #145E3A; }
.tag-slate  { background: #E8ECF2; color: #2C3E5A; }
.tag-muted  { background: #EBEBED; color: #6E6E73; }

.section-label {
    font-size: 0.72rem; font-weight: 600;
    letter-spacing: 0.08em; text-transform: uppercase;
    color: #6E6E73; margin-bottom: 14px; margin-top: 8px;
}
.lbex-divider { border: none; border-top: 1px solid #E5E5EA; margin: 28px 0; }
.lbex-header-titulo { font-size: 2.1rem; font-weight: 700; color: #1D1D1F; letter-spacing: -0.03em; line-height: 1.15; }
.lbex-header-sub    { font-size: 0.9rem; font-weight: 400; color: #6E6E73; margin-top: 4px; }
.lbex-footer        { font-size: 0.75rem; color: #AEAEB2; text-align: center; padding: 12px 0 4px 0; }

div[data-testid="stPageLink"] a {
    background-color: #F5F5F7 !important;
    border: 1px solid #D2D2D7 !important;
    border-radius: 12px !important;
    font-size: 0.83rem !important;
    font-weight: 600 !important;
    font-family: 'DM Sans', sans-serif !important;
    padding: 10px 16px !important;
    text-decoration: none !important;
    display: flex !important;
    justify-content: center !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    transition: box-shadow 0.25s ease, transform 0.25s ease !important;
    color: #1a1a1c !important;
}
div[data-testid="stPageLink"] a:hover {
    box-shadow: 0 8px 28px rgba(0,0,0,0.11) !important;
    transform: translateY(-2px) !important;
}
section[data-testid="stSidebar"] { display: none !important; }
[data-testid="collapsedControl"]  { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────
st.markdown("""
<div style="padding-top: 14px;">
    <div class="lbex-header-titulo">Laboratorio de Economia</div>
    <div class="lbex-header-sub">
        LBEX — Laboratorio Brasileiro de Economia Experimental &nbsp;·&nbsp; UFRRJ
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="lbex-divider">', unsafe_allow_html=True)

# ── Modulos disponiveis ───────────────────────────────────────────
st.markdown('<div class="section-label">Modulos disponiveis</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4, gap="medium")

with col1:
    st.markdown("""
<div class="lbex-card card-blue">
    <div class="card-titulo">Funcoes Economicas</div>
    <div class="card-desc">Analise individualmente as funcoes macroeconomicas fundamentais.
    Consumo, investimento, oferta agregada, mercado de trabalho e mais.</div>
    <span class="card-tag tag-blue">Disponivel</span>
</div>
""", unsafe_allow_html=True)
    st.page_link("pages/1_\U0001f4da_Funcoes.py", label="Acessar modulo", use_container_width=True)

with col2:
    st.markdown("""
<div class="lbex-card card-purple">
    <div class="card-titulo">Escolas Economicas</div>
    <div class="card-desc">Compare as grandes correntes do pensamento economico.
    Classica, Keynesiana, Monetarista e Pos-Keynesiana com analise comparativa.</div>
    <span class="card-tag tag-purple">Disponivel</span>
</div>
""", unsafe_allow_html=True)
    st.page_link("pages/2_\U0001f3db\ufe0f_Escolas_Economicas.py", label="Acessar modulo", use_container_width=True)

with col3:
    st.markdown("""
<div class="lbex-card card-green">
    <div class="card-titulo">Economia Aberta</div>
    <div class="card-desc">Modelo IS-LM-BP (Mundell-Fleming). Cambio fixo e flexivel,
    graus de mobilidade de capital e eficacia das politicas economicas.</div>
    <span class="card-tag tag-green">Disponivel</span>
</div>
""", unsafe_allow_html=True)
    st.page_link("pages/3_\U0001f30d_Economia_Aberta.py", label="Acessar modulo", use_container_width=True)

with col4:
    st.markdown("""
<div class="lbex-card card-slate">
    <div class="card-titulo">Laboratorio</div>
    <div class="card-desc">Construa e analise economias completas. Monte modelos,
    aplique politicas e visualize resultados integrados em tempo real.</div>
    <span class="card-tag tag-slate">Em construcao</span>
</div>
""", unsafe_allow_html=True)
    st.page_link("pages/4_\U0001f9ea_Laboratorio.py", label="Acessar modulo", use_container_width=True)

# ── Proximas bancadas ─────────────────────────────────────────────
st.markdown('<hr class="lbex-divider">', unsafe_allow_html=True)
st.markdown('<div class="section-label">Proximas bancadas</div>', unsafe_allow_html=True)

col5, col6, col7, col8 = st.columns(4, gap="medium")

CARDS_FUTUROS = [
    ("Series Temporais",
     "Evolucao de variaveis macroeconomicas periodo a periodo. "
     "Simulacao dinamica com choques e politicas sequenciais."),
    ("Cenarios Economicos",
     "Economias pre-calibradas: Brasil, Argentina, paises em guerra, "
     "economias em desenvolvimento. Analise comparativa."),
    ("Construtor de Economias",
     "Monte funcoes economicas customizadas. Defina estrutura produtiva, "
     "setor externo, politicas e distribuicao de renda."),
    ("Microeconomia",
     "Teoria do consumidor, teoria da firma e estruturas de mercado. "
     "Integracao entre micro e macroeconomia."),
]

for col, (titulo, desc) in zip([col5, col6, col7, col8], CARDS_FUTUROS):
    with col:
        st.markdown(f"""
<div class="lbex-card card-muted">
    <div class="card-titulo">{titulo}</div>
    <div class="card-desc">{desc}</div>
    <span class="card-tag tag-muted">Em breve</span>
</div>
""", unsafe_allow_html=True)

# ── Rodape ────────────────────────────────────────────────────────
st.markdown('<hr class="lbex-divider">', unsafe_allow_html=True)
st.markdown("""
<div class="lbex-footer">
    Marcelo de Salles Cunha Uchoa &nbsp;·&nbsp; LBEX / UFRRJ &nbsp;·&nbsp;
    Projeto de graduacao em desenvolvimento continuo
</div>
""", unsafe_allow_html=True)