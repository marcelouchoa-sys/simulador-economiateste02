# app.py
from pathlib import Path
import streamlit as st
from core.parameters import DEFAULT_PARAMS

# Caminho absoluto — funciona independente de onde o streamlit run é chamado
BASE_DIR  = Path(__file__).parent
LOGO_PATH = BASE_DIR / "assets" / "logo.webp"

st.set_page_config(
    page_title="LBEX — Laboratório Brasileiro de Economia Experimental",
    page_icon=str(LOGO_PATH),
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Estado global ─────────────────────────────────────────────────
if "params" not in st.session_state:
    st.session_state.params = DEFAULT_PARAMS.copy()

if "settings" not in st.session_state:
    st.session_state.settings = {
        "nivel": "Médio",
        "detalhe_causal": True,
        "show_grid": True,
        "color_base":  "#1565c0",
        "color_shock": "#c62828",
        "color_final": "#2e7d32",
    }

# ══════════════════════════════════════════════════════════════════
# HEADER — Logo + Título
# ══════════════════════════════════════════════════════════════════
col_logo, col_titulo = st.columns([1, 3])

with col_logo:
    st.image(str(LOGO_PATH), use_container_width=True)



# ══════════════════════════════════════════════════════════════════
# CORPO — Apresentação + Status
# ══════════════════════════════════════════════════════════════════
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### Bem-vindo à plataforma!")
    st.markdown("""
Este sistema resolve numericamente equilíbrios de modelos macroeconômicos
contemporâneos através de sistemas de equações interdependentes.

#### O que você pode explorar:

| Módulo | Descrição |
|---|---|
| 📚 **Funções Econômicas** | Consumo, Investimento, Oferta & Demanda, Mercado de Trabalho |
| 🏛️ **Escolas Econômicas** | Comparação entre abordagens Keynesiana, Clássica e Novo-Keynesiana |
| 🌍 **Economia Aberta** | Modelo IS-LM-BP (Mundell-Fleming) com regimes cambiais |
""")

    if st.session_state.settings["nivel"] == "Avançado":
        st.info(
            "🔬 **Modo Avançado Ativo:** O simulador exibirá as Reduções de Forma "
            "e Jacobianos das iterações numéricas."
        )

with col2:
    st.success("✅ Sistema pronto. Navegue pelas páginas no menu à esquerda.")
    st.markdown("**Módulos disponíveis:**")
    st.markdown("""
- 📚 Funções Econômicas
- 🏛️ Escolas Econômicas  
- 🌍 Economia Aberta (IS-LM-BP)
""")

st.divider()
st.caption("Desenvolvido por Marcelo de Salles Cunha Uchôa — LBEX / UFRRJ")