# pages/2__Escolas_Economicas.py
from pathlib import Path
import streamlit as st
from ui.design import aplicar_design, page_header
from ui.escolas.classica_ui       import render as render_classica
from ui.escolas.keynesiana_ui     import render as render_keynesiana
from ui.escolas.monetarista_ui    import render as render_monetarista
from ui.escolas.pos_keynesiana_ui import render as render_pos_keynesiana
from ui.escolas.comparativo_ui    import render as render_comparativo

BASE_DIR  = Path(__file__).parent.parent
LOGO_PATH = str(BASE_DIR / "assets" / "logo.webp")

st.set_page_config(page_title="Escolas Econômicas — LBEX", page_icon=LOGO_PATH, layout="wide")
aplicar_design()
if st.query_params.get("logged") == "1":
    st.query_params.clear()
st.page_link("app.py", label="← Voltar ao início")

page_header(
    "Escolas Econômicas",
    "Compare as grandes correntes do pensamento econômico"
)

# ── Seletor de escola ─────────────────────────────────────────────
ESCOLAS = ["Clássica", "Keynesiana", "Monetarista", "Pós-Keynesiana", "Comparativo"]

if "escola_sel"not in st.session_state:
    st.session_state.escola_sel = "Clássica"

cols = st.columns(len(ESCOLAS), gap="small")
for col, nome in zip(cols, ESCOLAS):
    with col:
        tipo = "primary"if st.session_state.escola_sel == nome else "secondary"
        if st.button(nome, use_container_width=True, type=tipo, key=f"btn_{nome}"):
            st.session_state.escola_sel = nome

escola = st.session_state.escola_sel
st.divider()

# ── Roteamento ────────────────────────────────────────────────────
ROTAS = {
    "Clássica":       render_classica,
    "Keynesiana":     render_keynesiana,
    "Monetarista":    render_monetarista,
    "Pós-Keynesiana": render_pos_keynesiana,
    "Comparativo":    render_comparativo,
}
ROTAS[escola]()