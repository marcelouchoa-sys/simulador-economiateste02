# pages/4__Laboratorio.py
from pathlib import Path
import streamlit as st
from ui.design import aplicar_design, page_header, section_label, divider

BASE_DIR  = Path(__file__).parent.parent
LOGO_PATH = str(BASE_DIR / "assets" / "logo.webp")

st.set_page_config(page_title="Laboratório — LBEX", page_icon=LOGO_PATH, layout="wide")
aplicar_design()
from core.auth import require_login, restore_session
restore_session()
if st.query_params.get("logged") == "1":
    st.query_params.clear()
if not require_login():
    st.stop()
st.page_link("app.py", label="← Voltar ao início")

page_header(
    "Laboratório",
    "Construa e analise economias completas"
)

divider()

# ── Bancadas disponíveis (em breve) ───────────────────────────────
section_label("Bancadas em desenvolvimento")

BANCADAS = [
    ("Simulador de Economia Completa",
     "Monte uma economia do zero: defina estrutura produtiva, políticas, "
     "setor externo e escola econômica. Analise equilíbrios e choques.",
     "slate"),
    ("Análise de Séries Temporais",
     "Evolução de variáveis macroeconômicas período a período. "
     "Choques sequenciais e trajetória de ajuste.",
     "muted"),
    ("Cenários Pré-calibrados",
     "Economias reais parametrizadas: Brasil, Argentina, países em guerra, "
     "economias em desenvolvimento.",
     "muted"),
    ("Construtor de Funções",
     "Defina suas próprias equações econômicas e analise o comportamento "
     "do modelo resultante.",
     "muted"),
]

cols = st.columns(4, gap="medium")
for col, (titulo, desc, cor) in zip(cols, BANCADAS):
    with col:
        st.markdown(f"""
<div class="lbex-card card-{cor}">
    <div class="card-titulo">{titulo}</div>
    <div class="card-desc">{desc}</div>
    <span class="card-tag tag-{cor}">{"Em desenvolvimento"if cor == "slate"else "Em breve"}</span>
</div>
""", unsafe_allow_html=True)

divider()
st.markdown("""
<div style="text-align:center; padding: 40px 0;">
    <div style="font-size:1rem; font-weight:600; color:#1D1D1F; margin-bottom:8px;">
        Laboratório em construção
    </div>
    <div style="font-size:0.85rem; color:#6E6E73; max-width:480px; margin:0 auto; line-height:1.6;">
        Este módulo será desenvolvido progressivamente durante a graduação.
        As bancadas disponíveis acima serão ativadas conforme o projeto avança.
    </div>
</div>
""", unsafe_allow_html=True)