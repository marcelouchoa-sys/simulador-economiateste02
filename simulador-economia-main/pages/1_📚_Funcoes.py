# pages/1__Funcoes.py
from pathlib import Path
import streamlit as st
from ui.design import aplicar_design, page_header
from core.parameters import DEFAULT_PARAMS
from ui.funcoes.consumo_ui          import render as render_consumo
from ui.funcoes.investimento_ui     import render as render_investimento
from ui.funcoes.demanda_moeda_ui    import render as render_demanda_moeda
from ui.funcoes.oferta_moeda_ui     import render as render_oferta_moeda
from ui.funcoes.demanda_agregada_ui import render as render_demanda_agregada
from ui.funcoes.oferta_agregada_ui  import render as render_oferta_agregada
from ui.funcoes.producao_ui         import render as render_producao
from ui.funcoes.oferta_demanda_ui   import render as render_oferta_demanda
from ui.funcoes.mercado_trabalho_ui import render as render_mercado_trabalho

BASE_DIR  = Path(__file__).parent.parent
LOGO_PATH = str(BASE_DIR / "assets" / "logo.webp")

st.set_page_config(layout="wide", page_title="Funções Econômicas — LBEX", page_icon=LOGO_PATH)
aplicar_design()
st.page_link("app.py", label="← Voltar ao início")

# ── Estado global ─────────────────────────────────────────────────
if "params"not in st.session_state:
    st.session_state.params = DEFAULT_PARAMS.copy()
for chave, valor in {"t": 0.2, "theta": 10.0, "m": 0.1,
                     "r": 0.05, "W": 1000.0, "alpha_w": 0.05}.items():
    if chave not in st.session_state.params:
        st.session_state.params[chave] = valor
p = st.session_state.params

# ── Cabeçalho ─────────────────────────────────────────────────────
page_header(
    "Funções Econômicas",
    "Analise individualmente as funções macroeconômicas fundamentais"
)

funcao = st.selectbox("Selecione a função:", [
    "Consumo",
    "Investimento",
    "Demanda por Moeda",
    "Oferta de Moeda",
    "Demanda Agregada",
    "Oferta Agregada",
    "Produção",
    "Oferta e Demanda",
    "Mercado de Trabalho",
], label_visibility="collapsed")

st.divider()

# ── Roteamento ────────────────────────────────────────────────────
ROTAS = {
    "Consumo":           lambda: render_consumo(p),
    "Investimento":      render_investimento,
    "Demanda por Moeda": render_demanda_moeda,
    "Oferta de Moeda":   render_oferta_moeda,
    "Demanda Agregada":  render_demanda_agregada,
    "Oferta Agregada":   render_oferta_agregada,
    "Produção":          render_producao,
    "Oferta e Demanda":  render_oferta_demanda,
    "Mercado de Trabalho": lambda: render_mercado_trabalho(p),
}
ROTAS[funcao]()