# pages/1_📚_Funcoes.py
import streamlit as st

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

st.set_page_config(layout="wide", page_title="Simulador Macro UFRRJ")

# ── Estado global ─────────────────────────────────────────────────
if "params" not in st.session_state:
    st.session_state.params = DEFAULT_PARAMS.copy()

for chave, valor in {
    "t": 0.2, "theta": 10.0, "m": 0.1,
    "r": 0.05, "W": 1000.0, "alpha_w": 0.05,
}.items():
    if chave not in st.session_state.params:
        st.session_state.params[chave] = valor

p = st.session_state.params

# ── Cabeçalho ─────────────────────────────────────────────────────
st.title("📚 Funções Econômicas")
st.caption("Simulador de Equilíbrio Geral e Funções de Comportamento - UFRRJ")

funcao = st.selectbox("Selecione a função para análise detalhada:", [
    "Consumo",
    "Investimento",
    "Demanda por Moeda",
    "Oferta de Moeda",
    "Demanda Agregada",
    "Oferta Agregada",
    "Produção",
    "Oferta e Demanda",
    "Mercado de Trabalho",
])

st.divider()

# ── Roteamento ────────────────────────────────────────────────────
if funcao == "Consumo":
    render_consumo(p)

elif funcao == "Investimento":
    render_investimento()

elif funcao == "Demanda por Moeda":
    render_demanda_moeda()

elif funcao == "Oferta de Moeda":
    render_oferta_moeda()

elif funcao == "Demanda Agregada":
    render_demanda_agregada()

elif funcao == "Oferta Agregada":
    render_oferta_agregada()

elif funcao == "Produção":
    render_producao()

elif funcao == "Oferta e Demanda":
    render_oferta_demanda()

elif funcao == "Mercado de Trabalho":
    render_mercado_trabalho()
