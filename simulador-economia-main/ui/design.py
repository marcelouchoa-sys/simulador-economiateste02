# ui/design.py
"""
LBEX Design System — Apple + Power BI
Centraliza todo o CSS e componentes visuais do projeto.
Importar em todas as páginas com: from ui.design import aplicar_design
"""

import streamlit as st


# ══════════════════════════════════════════════════════════════════
# PALETA DE CORES
# Usada nos gráficos Plotly também — importe diretamente
# ══════════════════════════════════════════════════════════════════
CORES = dict(
    # Primárias
    azul   = "#0066CC",
    roxo   = "#6E3B9E",
    verde  = "#1D7A4F",
    slate  = "#3A4D6B",

    # Superfícies
    fundo       = "#FFFFFF",
    superficie  = "#F5F5F7",
    borda       = "#D2D2D7",
    borda_suave = "#E5E5EA",

    # Texto
    texto_primario   = "#1D1D1F",
    texto_secundario = "#6E6E73",
    texto_apagado    = "#AEAEB2",

    # Gráficos — base e choque
    graf_base   = "#0066CC",
    graf_choque = "#C0392B",
    graf_final  = "#1D7A4F",
    graf_bp     = "#6E3B9E",
)


# ══════════════════════════════════════════════════════════════════
# CSS GLOBAL
# ══════════════════════════════════════════════════════════════════
_CSS = """
<style>

/* ── Fonte ── */
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&display=swap');

html, body, [class*="css"], .stMarkdown, p, div, span, label,
.stSelectbox, .stRadio, .stSlider, .stNumberInput, .stTextInput,
.stMetric, .stExpander, .stTabs, button {
    font-family: 'DM Sans', -apple-system, BlinkMacSystemFont,
                 'Segoe UI', sans-serif !important;
}

/* ── Fundo ── */
.stApp { background-color: #FFFFFF; }

section[data-testid="stSidebar"] {
    background-color: #F5F5F7;
    border-right: 1px solid #D2D2D7;
}

/* ── Títulos st.title / st.header / st.subheader ── */
h1 { font-size: 1.9rem !important; font-weight: 700 !important;
     color: #1D1D1F !important; letter-spacing: -0.03em !important; }
h2 { font-size: 1.35rem !important; font-weight: 600 !important;
     color: #1D1D1F !important; letter-spacing: -0.02em !important; }
h3 { font-size: 1.1rem !important; font-weight: 600 !important;
     color: #1D1D1F !important; }

/* ── Métricas ── */
[data-testid="stMetric"] {
    background: #F5F5F7;
    border: 1px solid #E5E5EA;
    border-radius: 12px;
    padding: 14px 16px !important;
}
[data-testid="stMetricLabel"]  { color: #6E6E73 !important; font-size: 0.78rem !important; font-weight: 500 !important; text-transform: uppercase; letter-spacing: 0.04em; }
[data-testid="stMetricValue"]  { color: #1D1D1F !important; font-size: 1.6rem !important; font-weight: 600 !important; letter-spacing: -0.02em; }
[data-testid="stMetricDelta"]  { font-size: 0.8rem !important; font-weight: 500 !important; }

/* ── Tabs ── */
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

/* ── Expander ── */
[data-testid="stExpander"] {
    border: 1px solid #E5E5EA !important;
    border-radius: 12px !important;
    background: #F5F5F7 !important;
}
[data-testid="stExpander"] summary {
    font-weight: 500 !important;
    font-size: 0.88rem !important;
    color: #1D1D1F !important;
}

/* ── Selectbox / Radio / Slider ── */
[data-testid="stSelectbox"] > div,
[data-testid="stNumberInput"] > div > div {
    border-radius: 10px !important;
    border-color: #D2D2D7 !important;
    background: #F5F5F7 !important;
}
.stRadio label { font-size: 0.85rem !important; color: #1D1D1F !important; }
.stSlider [data-testid="stThumbValue"] { font-size: 0.78rem !important; }

/* ── Botão primário ── */
[data-testid="stBaseButton-primary"] button,
button[kind="primary"] {
    background: #0066CC !important;
    border: none !important;
    border-radius: 10px !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    padding: 10px 20px !important;
    transition: background 0.2s ease !important;
}
[data-testid="stBaseButton-primary"] button:hover,
button[kind="primary"]:hover {
    background: #0055AA !important;
}

/* ── Botão secundário ── */
button[kind="secondary"] {
    background: #F5F5F7 !important;
    border: 1px solid #D2D2D7 !important;
    border-radius: 10px !important;
    color: #1D1D1F !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
}

/* ── Page link ── */
div[data-testid="stPageLink"] a {
    background: #FFFFFF !important;
    border: 1px solid #D2D2D7 !important;
    border-radius: 10px !important;
    color: #1D1D1F !important;
    font-size: 0.83rem !important;
    font-weight: 500 !important;
    font-family: 'DM Sans', sans-serif !important;
    transition: background 0.2s, border-color 0.2s !important;
}
div[data-testid="stPageLink"] a:hover {
    background: #F5F5F7 !important;
    border-color: #B0B0B8 !important;
}

/* ── Info / Success / Warning / Error ── */
[data-testid="stAlert"] {
    border-radius: 12px !important;
    border-width: 1px !important;
    font-size: 0.85rem !important;
}

/* ── Dataframe / Tabela ── */
[data-testid="stDataFrame"] {
    border-radius: 12px !important;
    overflow: hidden;
    border: 1px solid #E5E5EA !important;
}

/* ── Divisor ── */
hr {
    border: none !important;
    border-top: 1px solid #E5E5EA !important;
    margin: 24px 0 !important;
}

/* ── Caption ── */
.stCaption, [data-testid="stCaptionContainer"] {
    color: #AEAEB2 !important;
    font-size: 0.75rem !important;
}

/* ── Sidebar labels ── */
section[data-testid="stSidebar"] .stMarkdown p {
    font-size: 0.82rem !important;
    color: #6E6E73 !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}

/* ── Cards LBEX ── */
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
}
.card-blue::before   { background: #0066CC; }
.card-purple::before { background: #6E3B9E; }
.card-green::before  { background: #1D7A4F; }
.card-slate::before  { background: #3A4D6B; }
.card-muted::before  { background: #B0B0B8; }
.card-muted { opacity: 0.65; }

.card-titulo {
    font-size: 0.95rem; font-weight: 600;
    color: #1D1D1F; margin-bottom: 6px; letter-spacing: -0.01em;
}
.card-desc {
    font-size: 0.82rem; color: #6E6E73;
    line-height: 1.55; margin-bottom: 14px;
}
.card-tag {
    display: inline-flex; align-items: center;
    padding: 3px 10px; border-radius: 20px;
    font-size: 0.72rem; font-weight: 500; letter-spacing: 0.01em;
}
.tag-blue   { background: #E3F0FF; color: #0055AA; }
.tag-purple { background: #F0E8FA; color: #5A2D8A; }
.tag-green  { background: #E3F5EC; color: #145E3A; }
.tag-slate  { background: #E8ECF2; color: #2C3E5A; }
.tag-muted  { background: #EBEBED; color: #6E6E73; }

/* ── Section label ── */
.section-label {
    font-size: 0.72rem; font-weight: 600;
    letter-spacing: 0.08em; text-transform: uppercase;
    color: #6E6E73; margin-bottom: 14px;
}

/* ── Page header ── */
.page-titulo {
    font-size: 1.7rem; font-weight: 700;
    color: #1D1D1F; letter-spacing: -0.03em; line-height: 1.2;
}
.page-sub {
    font-size: 0.88rem; color: #6E6E73;
    margin-top: 4px; font-weight: 400;
}

/* ── Rodapé ── */
.lbex-footer {
    font-size: 0.74rem; color: #AEAEB2;
    text-align: center; padding: 8px 0;
}

</style>
"""


def aplicar_design() -> None:
    """
    Aplica o design system LBEX na página atual.
    Chamar no topo de cada página, após set_page_config.

    Uso:
        from ui.design import aplicar_design
        aplicar_design()
    """
    st.markdown(_CSS, unsafe_allow_html=True)


def page_header(titulo: str, subtitulo: str = "") -> None:
    """
    Renderiza o cabeçalho padrão de uma página interna.

    Uso:
        page_header("Funções Econômicas", "Analise as funções macroeconômicas fundamentais")
    """
    st.markdown(f"""
<div style="padding: 4px 0 16px 0;">
    <div class="page-titulo">{titulo}</div>
    {"<div class='page-sub'>" + subtitulo + "</div>" if subtitulo else ""}
</div>
""", unsafe_allow_html=True)


def section_label(texto: str) -> None:
    """Label de seção em uppercase — igual ao padrão Apple."""
    st.markdown(f'<div class="section-label">{texto}</div>', unsafe_allow_html=True)


def divider() -> None:
    """Divisor fino padrão do design system."""
    st.markdown('<hr>', unsafe_allow_html=True)


def card(titulo: str, desc: str, tag: str, cor: str = "blue") -> None:
    """
    Renderiza um card LBEX.

    Parâmetros:
        titulo : título do card
        desc   : descrição curta
        tag    : texto da tag (ex: "Disponível", "Em breve")
        cor    : "blue" | "purple" | "green" | "slate" | "muted"
    """
    st.markdown(f"""
<div class="lbex-card card-{cor}">
    <div class="card-titulo">{titulo}</div>
    <div class="card-desc">{desc}</div>
    <span class="card-tag tag-{cor}">{tag}</span>
</div>
""", unsafe_allow_html=True)