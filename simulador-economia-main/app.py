import streamlit as st
from core.parameters import DEFAULT_PARAMS

st.set_page_config(
    page_title="laboratório de economia",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- INICIALIZAÇÃO DO ESTADO GLOBAL ---
if "params" not in st.session_state:
    st.session_state.params = DEFAULT_PARAMS.copy()

if "settings" not in st.session_state:
    st.session_state.settings = {
        "nivel": "Médio",       # Básico, Médio, Avançado
        "detalhe_causal": True,
        "show_grid": True,
        "color_base": "#1565c0",  # Azul
        "color_shock": "#c62828", # Vermelho
        "color_final": "#2e7d32"  # Verde
    }

# --- CONTEÚDO DA HOME ---
st.title("laboratório de economia UFRRJ: Plataforma de estudo Econômico")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown(f"""
    ### Bem-vindo ao simulador de economia!

    Este sistema não é apenas visual; ele resolve numericamente equilíbrios de modelos
    macroeconômicos contemporâneos através de sistemas de equações interdependentes.

    #### O que você pode explorar:
    1. **Modelo IS-LM:** Equilíbrio nos mercados de bens e monetário.
    2. **Curva de Phillips:** O trade-off entre inflação e desemprego sob diferentes expectativas.
    """)

    if st.session_state.settings["nivel"] == "Avançado":
        st.info("🔬 **Modo Avançado Ativo:** O simulador exibirá as Reduções de Forma e Jacobianos das iterações numéricas.")

with col2:
    st.image("https://placehold.co/400x300/1565c0/white?text=Macro+Dynamics+AI", use_container_width=True)
    st.success("Sistema Pronto. Navegue pelas etapas no menu à esquerda.")

st.divider()
st.caption("Desenvolvido por Marcelo de Salles Cunha Uchôa.")