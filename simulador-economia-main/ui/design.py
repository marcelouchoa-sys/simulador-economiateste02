# ui/design.py
"""
LBEX Design System — Apple + Power BI
Centraliza todo o CSS e componentes visuais do projeto.
Importar em todas as páginas com: from ui.design import aplicar_design
"""

import streamlit as st

CORES = dict(
    azul   = "#0066CC",
    roxo   = "#6E3B9E",
    verde  = "#1D7A4F",
    slate  = "#3A4D6B",
    fundo       = "#FFFFFF",
    superficie  = "#F5F5F7",
    borda       = "#D2D2D7",
    borda_suave = "#E5E5EA",
    texto_primario   = "#1D1D1F",
    texto_secundario = "#6E6E73",
    texto_apagado    = "#AEAEB2",
    graf_base   = "#0066CC",
    graf_choque = "#C0392B",
    graf_final  = "#1D7A4F",
    graf_bp     = "#6E3B9E",
)

_CSS = """
<style>

@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&display=swap');

html, body, [class*="css"], .stMarkdown, p, div, span, label,
.stSelectbox, .stRadio, .stSlider, .stNumberInput, .stTextInput,
.stMetric, .stTabs, button {
    font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
}

.stApp { background-color: #FFFFFF; }

section[data-testid="stSidebar"] {
    background-color: #F5F5F7;
    border-right: 1px solid #D2D2D7;
}

h1 { font-size: 1.9rem !important; font-weight: 700 !important; color: #1D1D1F !important; letter-spacing: -0.03em !important; }
h2 { font-size: 1.35rem !important; font-weight: 600 !important; color: #1D1D1F !important; letter-spacing: -0.02em !important; }
h3 { font-size: 1.1rem !important; font-weight: 600 !important; color: #1D1D1F !important; }

[data-testid="stMetric"] {
    background: #F5F5F7;
    border: 1px solid #E5E5EA;
    border-radius: 12px;
    padding: 14px 16px !important;
}
[data-testid="stMetricLabel"] { color: #6E6E73 !important; font-size: 0.78rem !important; font-weight: 500 !important; text-transform: uppercase; letter-spacing: 0.04em; }
[data-testid="stMetricValue"] { color: #1D1D1F !important; font-size: 1.6rem !important; font-weight: 600 !important; letter-spacing: -0.02em; }
[data-testid="stMetricDelta"] { font-size: 0.8rem !important; font-weight: 500 !important; }

[data-testid="stTabs"] button {
    font-size: 0.83rem !important;
    font-weight: 500 !important;
    color: #6E6E73 !important;
    border-radius: 8px 8px 0 0 !important;
    padding: 8px 16px !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: #1D1D1F !important;
    font-weight: 600 !important;
    border-bottom: 2px solid #0066CC !important;
}

/* Expander — apenas borda e fundo, sem tocar no summary para nao quebrar icone */
details[data-testid="stExpander"] {
    border: 1px solid #E5E5EA !important;
    border-radius: 12px !important;
    background: #F5F5F7 !important;
    overflow: hidden !important;
}

[data-testid="stSelectbox"] > div,
[data-testid="stNumberInput"] > div > div {
    border-radius: 10px !important;
    border-color: #D2D2D7 !important;
    background: #F5F5F7 !important;
}
.stRadio label { font-size: 0.85rem !important; color: #1D1D1F !important; }

button[kind="primary"] {
    background: #0066CC !important;
    border: none !important;
    border-radius: 10px !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
}
button[kind="primary"]:hover { background: #0055AA !important; }

button[kind="secondary"] {
    background: #F5F5F7 !important;
    border: 1px solid #D2D2D7 !important;
    border-radius: 10px !important;
    color: #1D1D1F !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
}

div[data-testid="stPageLink"] a {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 100% !important;
    padding: 10px 20px !important;
    background: #FFFFFF !important;
    border: 1px solid #D2D2D7 !important;
    border-radius: 10px !important;
    color: #1D1D1F !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    text-decoration: none !important;
    transition: background 0.2s ease, border-color 0.2s ease !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06) !important;
}
div[data-testid="stPageLink"] a:hover {
    background: #F5F5F7 !important;
    border-color: #0066CC !important;
    color: #0066CC !important;
}

[data-testid="stAlert"] {
    border-radius: 12px !important;
    border-width: 1px !important;
    font-size: 0.85rem !important;
}

[data-testid="stDataFrame"] {
    border-radius: 12px !important;
    overflow: hidden;
    border: 1px solid #E5E5EA !important;
}

hr {
    border: none !important;
    border-top: 1px solid #E5E5EA !important;
    margin: 24px 0 !important;
}

.stCaption, [data-testid="stCaptionContainer"] {
    color: #AEAEB2 !important;
    font-size: 0.75rem !important;
}

section[data-testid="stSidebar"] [data-testid="stSidebarNavItems"] a {
    color: #1D1D1F !important;
    font-size: 0.88rem !important;
    font-weight: 400 !important;
    border-radius: 8px !important;
    padding: 6px 12px !important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarNavItems"] a:hover {
    background: #E8E8ED !important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarNavItems"] a[aria-current="page"] {
    background: #E3F0FF !important;
    color: #0066CC !important;
    font-weight: 500 !important;
}

/* Cards LBEX — escopo restrito para nao vazar em outros elementos */
.lbex-card {
    background: #F5F5F7;
    border: 1px solid #D2D2D7;
    border-radius: 18px;
    padding: 24px 22px 18px 22px;
    margin-bottom: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    transition: box-shadow 0.25s ease, transform 0.25s ease;
    position: relative;
    overflow: hidden;
}
.lbex-card:hover {
    box-shadow: 0 8px 24px rgba(0,0,0,0.10);
    transform: translateY(-2px);
}
.lbex-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 4px;
    border-radius: 18px 18px 0 0;
    background: transparent;
}
.lbex-card.card-blue::before   { background: #0066CC; }
.lbex-card.card-purple::before { background: #6E3B9E; }
.lbex-card.card-green::before  { background: #1D7A4F; }
.lbex-card.card-slate::before  { background: #3A4D6B; }
.lbex-card.card-muted::before  { background: #B0B0B8; }
.lbex-card.card-muted          { opacity: 0.65; }

.card-titulo { font-size: 0.95rem; font-weight: 600; color: #1D1D1F; margin-bottom: 6px; letter-spacing: -0.01em; }
.card-desc   { font-size: 0.82rem; color: #6E6E73; line-height: 1.55; margin-bottom: 14px; }
.card-tag    { display: inline-flex; align-items: center; padding: 3px 10px; border-radius: 20px; font-size: 0.72rem; font-weight: 500; }

.tag-blue   { background: #E3F0FF; color: #0055AA; }
.tag-purple { background: #F0E8FA; color: #5A2D8A; }
.tag-green  { background: #E3F5EC; color: #145E3A; }
.tag-slate  { background: #E8ECF2; color: #2C3E5A; }
.tag-muted  { background: #EBEBED; color: #6E6E73; }

.section-label {
    font-size: 0.72rem; font-weight: 600;
    letter-spacing: 0.08em; text-transform: uppercase;
    color: #6E6E73; margin-bottom: 14px;
}

.page-titulo { font-size: 1.7rem; font-weight: 700; color: #1D1D1F; letter-spacing: -0.03em; line-height: 1.2; }
.page-sub    { font-size: 0.88rem; color: #6E6E73; margin-top: 4px; font-weight: 400; }
.lbex-footer { font-size: 0.74rem; color: #AEAEB2; text-align: center; padding: 8px 0; }

details summary svg,
details summary span[data-testid="stExpanderToggleIcon"] {
    display: none !important;
}

section[data-testid="stSidebar"] { display: none !important; }
[data-testid="collapsedControl"]  { display: none !important; }

</style>
"""


def aplicar_design() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)


def page_header(titulo: str, subtitulo: str = "") -> None:
    sub = f"<div class='page-sub'>{subtitulo}</div>" if subtitulo else ""
    st.markdown(f"""
<div style="padding: 4px 0 16px 0;">
    <div class="page-titulo">{titulo}</div>
    {sub}
</div>
""", unsafe_allow_html=True)


def section_label(texto: str) -> None:
    st.markdown(f'<div class="section-label">{texto}</div>', unsafe_allow_html=True)


def divider() -> None:
    st.markdown('<hr>', unsafe_allow_html=True)


def card(titulo: str, desc: str, tag: str, cor: str = "blue") -> None:
    st.markdown(f"""
<div class="lbex-card card-{cor}">
    <div class="card-titulo">{titulo}</div>
    <div class="card-desc">{desc}</div>
    <span class="card-tag tag-{cor}">{tag}</span>
</div>
""", unsafe_allow_html=True)