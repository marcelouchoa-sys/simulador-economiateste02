# pages/3_🌍_Economia_Aberta.py
import streamlit as st
from ui.design import aplicar_design, page_header
from ui.islmbp.didatico_ui import render as render_didatico
from ui.islmbp.complexo_ui import render as render_complexo

st.set_page_config(page_title="Economia Aberta — LBEX", page_icon="🌍", layout="wide")
aplicar_design()

from core.parameters import DEFAULT_PARAMS
if "params" not in st.session_state:
    st.session_state.params = DEFAULT_PARAMS.copy()
if "settings" not in st.session_state:
    st.session_state.settings = {"mobilidade_capital": "Alta"}

page_header(
    "Economia Aberta",
    "Modelo IS-LM-BP (Mundell-Fleming) — câmbio fixo e flexível"
)

modo = st.radio(
    "Modo:",
    ["Modo Didático", "Modo Complexo"],
    horizontal=True,
    key="modo_islmbp",
    label_visibility="collapsed",
)
st.divider()

if "Didático" in modo:
    render_didatico()
else:
    render_complexo()