# app.py
"""
LBEX — Laboratório Brasileiro de Economia Experimental
"""

from pathlib import Path
import streamlit as st
from core.parameters import DEFAULT_PARAMS

# Configuração da página (removido o ícone da logo para evitar erros se o arquivo não existir)
st.set_page_config(
    page_title="LBEX — Laboratório de Economia",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Estado global ─────────────────────────────────────────────────
if "params" not in st.session_state:
    st.session_state.params = DEFAULT_PARAMS.copy()

if "settings" not in st.session_state:
    st.session_state.settings = {
        "nivel": "Médio",
        "mobilidade_capital": "Alta",
        "detalhe_causal": True,
        "show_grid": True,
        "color_base":  "#0066CC",
        "color_shock": "#C0392B",
        "color_final": "#1D7A4F",
    }

# ══════════════════════════════════════════════════════════════════
# DESIGN SYSTEM — Apple + Power BI
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<style>

/* ── Fonte ── */
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"], .stMarkdown, .stText, p, div, span {
    font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

/* ── Fundo da página ── */
.stApp {
    background-color: #FFFFFF;
}
section[data-testid="stSidebar"] {
    background-color: #F5F5F7;
    border-right: 1px solid #D2D2D7;
}

/* ── Card base ── */
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

/* Linha colorida no topo */
.lbex-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 4px;
    border-radius: 18px 18px 0 0;
}
.card-blue::before   { background: #0066CC; }
.card-purple::before { background: #6E3B9E; }
.card-green::before  { background: #1D7A4F; }
.card-slate::before  { background: #3A4D6B; }
.card-muted::before  { background: #B0B0B8; }

/* Título */
.card-titulo {
    font-size: 1rem;
    font-weight: 600;
    color: #1D1D1F;
    margin-bottom: 8px;
    letter-spacing: -0.01em;
}

/* Descrição */
.card-desc {
    font-size: 0.83rem;
    color: #6E6E73;
    line-height: 1.55;
    margin-bottom: 14px;
}

/* Tag de status */
.card-tag {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 0.01em;
}
.tag-blue   { background: #E3F0FF; color: #0055AA; }
.tag-purple { background: #F0E8FA; color: #5A2D8A; }
.tag-green  { background: #E3F5EC; color: #145E3A; }
.tag-slate  { background: #E8ECF2; color: #2C3E5A; }
.tag-muted  { background: #EBEBED; color: #6E6E73; }

/* Cards futuros mais apagados */
.card-muted {
    opacity: 0.65;
}
.card-muted .card-titulo { color: #3A3A3C; }

/* ── Seção de título ── */
.section-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #6E6E73;
    margin-bottom: 14px;
    margin-top: 8px;
}

/* ── Divisor fino ── */
.lbex-divider {
    border: none;
    border-top: 1px solid #E5E5EA;
    margin: 28px 0;
}

/* ── Header ── */
.lbex-header-titulo {
    font-size: 2.1rem;
    font-weight: 700;
    color: #1D1D1F;
    letter-spacing: -0.03em;
    line-height: 1.15;
}
.lbex-header-sub {
    font-size: 0.9rem;
    font-weight: 400;
    color: #6E6E73;
    margin-top: 4px;
    letter-spacing: 0.01em;
}

/* ── Rodapé ── */
.lbex-footer {
    font-size: 0.75rem;
    color: #AEAEB2;
    text-align: center;
    padding: 12px 0 4px 0;
    letter-spacing: 0.01em;
}

/* ── Botões de link — Ajustados com Efeito Sombra Idêntico ao Card ── */
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
}

div[data-testid="stPageLink"] a, 
div[data-testid="stPageLink"] a * {
    color: #1a1a1c !important;             
}

div[data-testid="stPageLink"] a:hover {
    background-color: #F5F5F7 !important;  
    border-color: #D2D2D7 !important;      
    box-shadow: 0 8px 28px rgba(0,0,0,0.11) !important; 
    transform: translateY(-2px) !important; 
}

div[data-testid="stPageLink"] a:hover, 
div[data-testid="stPageLink"] a:hover * {
    color: #1a1a1c !important;            
}

</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════
# Removidas as colunas e a imagem da logo. Agora o texto ocupa o topo completo de forma limpa.
st.markdown("""
<div style="padding-top: 14px;">
    <div class="lbex-header-titulo">Laboratório de Economia</div>
    <div class="lbex-header-sub">
        LBEX — Laboratório Brasileiro de Economia Experimental &nbsp;·&nbsp; UFRRJ
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="lbex-divider">', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# MÓDULOS DISPONÍVEIS
# ══════════════════════════════════════════════════════════════════
st.markdown('<div class="section-label">Módulos disponíveis</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4, gap="medium")

with col1:
    st.markdown("""
<div class="lbex-card card-blue">
    <div class="card-titulo">Funções Econômicas</div>
    <div class="card-desc">
        Analise individualmente as funções macroeconômicas fundamentais.
        Consumo, investimento, oferta agregada, mercado de trabalho e mais.
    </div>
    <span class="card-tag tag-blue">Disponível</span>
</div>
""", unsafe_allow_html=True)
    st.page_link("pages/1_📚_Funcoes.py", label="Acessar módulo", use_container_width=True)

with col2:
    st.markdown("""
<div class="lbex-card card-purple">
    <div class="card-titulo">Escolas Econômicas</div>
    <div class="card-desc">
        Compare as grandes correntes do pensamento econômico.
        Clássica, Keynesiana, Monetarista e Pós-Keynesiana com análise comparativa.
    </div>
    <span class="card-tag tag-purple">Disponível</span>
</div>
""", unsafe_allow_html=True)
    st.page_link("pages/2_🏛️_Escolas_Economicas.py", label="Acessar módulo", use_container_width=True)

with col3:
    st.markdown("""
<div class="lbex-card card-green">
    <div class="card-titulo">Economia Aberta</div>
    <div class="card-desc">
        Modelo IS-LM-BP (Mundell-Fleming). Câmbio fixo e flexível,
        graus de mobilidade de capital e eficácia das políticas econômicas.
    </div>
    <span class="card-tag tag-green">Disponível</span>
</div>
""", unsafe_allow_html=True)
    st.page_link("pages/3_🌍_Economia_Aberta.py", label="Acessar módulo", use_container_width=True)

with col4:
    st.markdown("""
<div class="lbex-card card-slate">
    <div class="card-titulo">Laboratório</div>
    <div class="card-desc">
        Construa e analise economias completas. Monte modelos,
        aplique políticas e visualize resultados integrados em tempo real.
    </div>
    <span class="card-tag tag-slate">Em construção</span>
</div>
""", unsafe_allow_html=True)
    st.page_link("pages/4_🧪_Laboratorio.py", label="Acessar módulo", use_container_width=True)

# ══════════════════════════════════════════════════════════════════
# PRÓXIMAS BANCADAS
# ══════════════════════════════════════════════════════════════════
st.markdown('<hr class="lbex-divider">', unsafe_allow_html=True)
st.markdown('<div class="section-label">Próximas bancadas</div>', unsafe_allow_html=True)

col5, col6, col7, col8 = st.columns(4, gap="medium")

CARDS_FUTUROS = [
    ("Séries Temporais",
     "Evolução de variáveis macroeconômicas período a período. "
     "Simulação dinâmica com choques e políticas sequenciais."),
    ("Cenários Econômicos",
     "Economias pré-calibradas: Brasil, Argentina, países em guerra, "
     "economias em desenvolvimento. Análise comparativa."),
    ("Construtor de Economias",
     "Monte funções econômicas customizadas. Defina estrutura produtiva, "
     "setor externo, políticas e distribuição de renda."),
    ("Microeconomia",
     "Teoria do consumidor, teoria da firma e estruturas de mercado. "
     "Integração entre micro e macroeconomia."),
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

# ══════════════════════════════════════════════════════════════════
# RODAPÉ
# ══════════════════════════════════════════════════════════════════
st.markdown('<hr class="lbex-divider">', unsafe_allow_html=True)
st.markdown("""
<div class="lbex-footer">
    Marcelo de Salles Cunha Uchôa &nbsp;·&nbsp; LBEX / UFRRJ &nbsp;·&nbsp;
    Projeto de graduação em desenvolvimento contínuo
</div>
""", unsafe_allow_html=True)