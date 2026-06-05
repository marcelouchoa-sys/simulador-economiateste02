# ui/auth_ui.py
"""
Interface de autenticação do OikosLab.
Modal de login/cadastro e painel do usuário logado.
"""

import streamlit as st
from core.auth import (
    init_auth_state, is_logged_in, get_user_nome, get_user_email,
    login, cadastrar, logout, listar_simulacoes, listar_historico,
    deletar_simulacao,
)


# ══════════════════════════════════════════════════════════════════
# CSS DA AUTH UI
# ══════════════════════════════════════════════════════════════════

AUTH_CSS = """
<style>
/* Modal de auth */
.auth-container {
    max-width: 440px;
    margin: 0 auto;
    padding: 40px 36px;
    background: #FFFFFF;
    border: 1px solid #E5E5EA;
    border-radius: 20px;
    box-shadow: 0 8px 40px rgba(0,0,0,0.10);
}
.auth-titulo {
    font-size: 1.5rem;
    font-weight: 700;
    color: #1D1D1F;
    margin-bottom: 6px;
    letter-spacing: -0.02em;
}
.auth-sub {
    font-size: 0.88rem;
    color: #6E6E73;
    margin-bottom: 28px;
}
.auth-divider {
    text-align: center;
    color: #AEAEB2;
    font-size: 0.8rem;
    margin: 16px 0;
    position: relative;
}
.auth-divider::before, .auth-divider::after {
    content: '';
    position: absolute;
    top: 50%;
    width: 42%;
    height: 1px;
    background: #E5E5EA;
}
.auth-divider::before { left: 0; }
.auth-divider::after  { right: 0; }

/* Painel do usuário */
.user-panel {
    background: #F5F5F7;
    border: 1px solid #E5E5EA;
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 20px;
}
.user-avatar {
    width: 48px; height: 48px;
    border-radius: 50%;
    background: linear-gradient(135deg, #0066CC, #6E3B9E);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    font-weight: 700;
    color: white;
    margin-bottom: 12px;
}
.user-nome  { font-size: 1rem; font-weight: 600; color: #1D1D1F; }
.user-email { font-size: 0.8rem; color: #6E6E73; margin-top: 2px; }

/* Card de simulação salva */
.sim-card {
    background: #FFFFFF;
    border: 1px solid #E5E5EA;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 10px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.sim-titulo  { font-size: 0.9rem; font-weight: 600; color: #1D1D1F; }
.sim-modulo  { font-size: 0.75rem; color: #6E6E73; margin-top: 2px; }
.sim-data    { font-size: 0.72rem; color: #AEAEB2; }
</style>
"""


# ══════════════════════════════════════════════════════════════════
# MODAL DE LOGIN / CADASTRO
# ══════════════════════════════════════════════════════════════════

def render_auth_modal() -> None:
    """
    Renderiza o modal de login/cadastro.
    Chamado quando o usuário clica em 'Entrar' no header.
    """
    st.markdown(AUTH_CSS, unsafe_allow_html=True)

    init_auth_state()

    if is_logged_in():
        render_user_panel()
        return

    # Tabs de login e cadastro
    tab_login, tab_cadastro = st.tabs(["Entrar", "Criar conta"])

    with tab_login:
        _render_login()

    with tab_cadastro:
        _render_cadastro()


def _render_login() -> None:
    st.markdown("""
<div style="padding: 8px 0 20px 0;">
    <div class="auth-titulo">Bem-vindo de volta</div>
    <div class="auth-sub">Entre com sua conta OikosLab</div>
</div>
""", unsafe_allow_html=True)

    email = st.text_input("Email", placeholder="seu@email.com", key="login_email")
    senha = st.text_input("Senha", type="password", placeholder="Sua senha", key="login_senha")

    st.markdown("")
    if st.button("Entrar", type="primary", use_container_width=True, key="btn_login"):
        if not email or not senha:
            st.error("Preencha email e senha.")
        else:
            with st.spinner("Entrando..."):
                ok, msg = login(email, senha)
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)


def _render_cadastro() -> None:
    st.markdown("""
<div style="padding: 8px 0 20px 0;">
    <div class="auth-titulo">Criar conta</div>
    <div class="auth-sub">Comece a usar o OikosLab gratuitamente</div>
</div>
""", unsafe_allow_html=True)

    nome  = st.text_input("Nome", placeholder="Seu nome", key="cad_nome")
    email = st.text_input("Email", placeholder="seu@email.com", key="cad_email")
    senha = st.text_input("Senha", type="password",
                          placeholder="Minimo 6 caracteres", key="cad_senha")
    senha2 = st.text_input("Confirmar senha", type="password",
                            placeholder="Repita a senha", key="cad_senha2")

    st.markdown("")
    if st.button("Criar conta", type="primary", use_container_width=True, key="btn_cadastro"):
        if not nome or not email or not senha:
            st.error("Preencha todos os campos.")
        elif senha != senha2:
            st.error("As senhas nao conferem.")
        elif len(senha) < 6:
            st.error("A senha deve ter pelo menos 6 caracteres.")
        else:
            with st.spinner("Criando conta..."):
                ok, msg = cadastrar(email, senha, nome)
            if ok:
                st.success(msg)
            else:
                st.error(msg)


# ══════════════════════════════════════════════════════════════════
# PAINEL DO USUÁRIO LOGADO
# ══════════════════════════════════════════════════════════════════

def render_user_panel() -> None:
    """Painel completo do usuário logado — perfil, simulações e histórico."""
    st.markdown(AUTH_CSS, unsafe_allow_html=True)

    nome  = get_user_nome()
    email = get_user_email() or ""
    inicial = nome[0].upper() if nome else "U"

    # Avatar + info
    st.markdown(f"""
<div class="user-panel">
    <div class="user-avatar">{inicial}</div>
    <div class="user-nome">{nome}</div>
    <div class="user-email">{email}</div>
</div>
""", unsafe_allow_html=True)

    if st.button("Sair da conta", use_container_width=True, key="btn_logout"):
        logout()
        st.rerun()

    st.divider()

    # Abas do painel
    aba1, aba2 = st.tabs(["Simulacoes salvas", "Historico"])

    with aba1:
        _render_simulacoes()

    with aba2:
        _render_historico()


def _render_simulacoes() -> None:
    sims = listar_simulacoes()

    if not sims:
        st.caption("Nenhuma simulacao salva ainda.")
        st.info("Use o botao 'Salvar simulacao' dentro de qualquer modulo para salvar aqui.")
        return

    st.caption(f"{len(sims)} simulacao(oes) salva(s)")

    for sim in sims:
        col1, col2 = st.columns([4, 1])
        with col1:
            data = sim.get("created_at", "")[:10] if sim.get("created_at") else ""
            st.markdown(f"""
<div class="sim-card">
    <div>
        <div class="sim-titulo">{sim.get('titulo', 'Sem titulo')}</div>
        <div class="sim-modulo">{sim.get('modulo', '')}</div>
    </div>
    <div class="sim-data">{data}</div>
</div>
""", unsafe_allow_html=True)
        with col2:
            if st.button("Remover", key=f"del_{sim['id']}", use_container_width=True):
                ok, msg = deletar_simulacao(sim["id"])
                if ok:
                    st.rerun()
                else:
                    st.error(msg)


def _render_historico() -> None:
    hist = listar_historico()

    if not hist:
        st.caption("Nenhum acesso registrado ainda.")
        return

    st.caption(f"Ultimos {len(hist)} acessos")

    for h in hist:
        data = h.get("created_at", "")[:16].replace("T", " ") if h.get("created_at") else ""
        modulo = h.get("modulo", "")
        acao   = h.get("acao", "")
        st.markdown(
            f"**{modulo}** {('— ' + acao) if acao else ''} "
            f"<span style='color:#AEAEB2; font-size:0.78rem'>{data}</span>",
            unsafe_allow_html=True,
        )


# ══════════════════════════════════════════════════════════════════
# WIDGET DO HEADER — botão Entrar / nome do usuário
# ══════════════════════════════════════════════════════════════════

def render_header_auth() -> None:
    """
    Renderiza o botão de auth no header.
    Quando logado: mostra nome + botão de painel.
    Quando deslogado: mostra botão 'Entrar'.
    """
    init_auth_state()

    if is_logged_in():
        nome    = get_user_nome()
        inicial = nome[0].upper()
        # Botão com inicial do nome
        if st.button(
            f"{inicial}  {nome}",
            key="header_user_btn",
            help="Ver painel da conta",
        ):
            st.session_state["mostrar_auth"] = True
    else:
        if st.button("Entrar", key="header_login_btn", type="primary"):
            st.session_state["mostrar_auth"] = True


def botao_salvar(modulo: str, parametros: dict, resultado: dict = {}) -> None:
    from core.auth import is_logged_in, salvar_simulacao
    st.divider()
    if not is_logged_in():
        st.caption("Faca login para salvar esta simulacao.")
        return
    col1, col2 = st.columns([2, 1])
    with col1:
        titulo = st.text_input(
            "Nome da simulacao",
            placeholder=f"Ex: {modulo} — cenario base",
            key=f"titulo_sim_{modulo}",
            label_visibility="collapsed",
        )
    with col2:
        if st.button("Salvar simulacao", key=f"salvar_{modulo}", use_container_width=True):
            if not titulo:
                st.warning("Digite um nome para a simulacao.")
            else:
                ok, msg = salvar_simulacao(titulo, modulo, parametros, resultado)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)