import streamlit as st
from ui.design import aplicar_design
from ui.auth_ui import render_auth_modal

st.set_page_config(page_title="Entrar — OikosLab", layout="centered")
aplicar_design()
render_auth_modal()
