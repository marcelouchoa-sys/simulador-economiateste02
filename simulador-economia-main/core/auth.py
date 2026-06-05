# core/auth.py
"""
Autenticação OikosLab via Supabase.
Funções de login, cadastro, logout e gerenciamento de sessão.
"""

import streamlit as st
from supabase import create_client, Client


# ══════════════════════════════════════════════════════════════════
# CONEXÃO COM SUPABASE
# ══════════════════════════════════════════════════════════════════

def _get_client() -> Client:
    """
    Retorna o cliente Supabase.
    Lê as credenciais do st.secrets (Streamlit Cloud)
    ou das variáveis de ambiente locais.
    """
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
    except Exception:
        import os
        from dotenv import load_dotenv
        load_dotenv()
        url = os.getenv("SUPABASE_URL", "")
        key = os.getenv("SUPABASE_KEY", "")

    if not url or not key:
        raise ValueError("Credenciais do Supabase não encontradas.")

    return create_client(url, key)


# ══════════════════════════════════════════════════════════════════
# ESTADO DA SESSÃO
# ══════════════════════════════════════════════════════════════════

def init_auth_state() -> None:
    """Inicializa as chaves de autenticação no session_state."""
    if "user" not in st.session_state:
        st.session_state.user = None
    if "auth_token" not in st.session_state:
        st.session_state.auth_token = None


def is_logged_in() -> bool:
    """Retorna True se há usuário logado."""
    return st.session_state.get("user") is not None


def get_user() -> dict | None:
    """Retorna os dados do usuário logado ou None."""
    return st.session_state.get("user")


def get_user_id() -> str | None:
    """Retorna o ID do usuário logado ou None."""
    user = get_user()
    return user["id"] if user else None


def get_user_email() -> str | None:
    """Retorna o email do usuário logado ou None."""
    user = get_user()
    return user.get("email") if user else None


def get_user_nome() -> str:
    """Retorna o nome do usuário logado ou 'Usuário'."""
    user = get_user()
    if not user:
        return "Usuário"
    return user.get("nome") or user.get("email", "Usuário").split("@")[0]


# ══════════════════════════════════════════════════════════════════
# AUTENTICAÇÃO
# ══════════════════════════════════════════════════════════════════

def cadastrar(email: str, senha: str, nome: str) -> tuple[bool, str]:
    """
    Cadastra um novo usuário.
    Retorna (sucesso, mensagem).
    """
    try:
        client = _get_client()
        resp = client.auth.sign_up({
            "email": email,
            "password": senha,
            "options": {"data": {"nome": nome}},
        })

        if resp.user:
            # Criar perfil na tabela profiles
            try:
                client.table("profiles").insert({
                    "id":   resp.user.id,
                    "nome": nome,
                }).execute()
            except Exception:
                pass  # Perfil será criado no próximo login

            return True, "Conta criada com sucesso! Verifique seu email para confirmar."
        return False, "Erro ao criar conta. Tente novamente."

    except Exception as e:
        msg = str(e)
        if "already registered" in msg:
            return False, "Este email já está cadastrado."
        if "Password should be" in msg:
            return False, "A senha deve ter pelo menos 6 caracteres."
        return False, f"Erro: {msg}"


def login(email: str, senha: str) -> tuple[bool, str]:
    """
    Faz login com email e senha.
    Retorna (sucesso, mensagem).
    """
    try:
        client = _get_client()
        resp = client.auth.sign_in_with_password({
            "email": email,
            "password": senha,
        })

        if resp.user:
            # Buscar nome do perfil
            try:
                perfil = client.table("profiles").select("nome").eq(
                    "id", resp.user.id
                ).single().execute()
                nome = perfil.data.get("nome", "") if perfil.data else ""
            except Exception:
                nome = ""

            st.session_state.user = {
                "id":    resp.user.id,
                "email": resp.user.email,
                "nome":  nome or resp.user.email.split("@")[0],
            }
            st.session_state["auth_token"] = resp.session.access_token
            st.session_state["auth_refresh"] = resp.session.refresh_token
            return True, "Login realizado com sucesso!"

        return False, "Email ou senha incorretos."

    except Exception as e:
        msg = str(e)
        if "Invalid login" in msg or "invalid_credentials" in msg:
            return False, "Email ou senha incorretos."
        if "Email not confirmed" in msg:
            return False, "Confirme seu email antes de fazer login."
        return False, f"Erro ao fazer login: {msg}"


def logout() -> None:
    """Faz logout do usuário."""
    try:
        client = _get_client()
        client.auth.sign_out()
    except Exception:
        pass
    st.session_state.user              = None
    st.session_state.auth_token        = None
    st.session_state["auth_refresh"]   = None


def restore_session() -> None:
    """Tenta restaurar a sessão salva ao recarregar a página."""
    if is_logged_in():
        return
    token = st.session_state.get("auth_token")
    refresh = st.session_state.get("auth_refresh")
    if not token or not refresh:
        return
    try:
        client = _get_client()
        resp = client.auth.set_session(token, refresh)
        if resp.user:
            try:
                perfil = client.table("profiles").select("nome").eq(
                    "id", resp.user.id
                ).single().execute()
                nome = perfil.data.get("nome", "") if perfil.data else ""
            except Exception:
                nome = ""
            st.session_state.user = {
                "id":    resp.user.id,
                "email": resp.user.email,
                "nome":  nome or resp.user.email.split("@")[0],
            }
    except Exception:
        pass


def require_login(modulo: str = "") -> bool:
    """
    Verifica se o usuário está logado.
    Se não estiver, mostra mensagem e botão de login.
    Retorna True se logado, False se não.
    """
    restore_session()
    if is_logged_in():
        return True
    st.markdown("""
<div style="text-align:center; padding: 80px 0;">
    <div style="font-size:1.3rem; font-weight:700; color:#1D1D1F; margin-bottom:8px;">
        Acesso restrito
    </div>
    <div style="font-size:0.9rem; color:#6E6E73; margin-bottom:24px;">
        Faca login para acessar este modulo e salvar suas simulacoes.
    </div>
</div>
""", unsafe_allow_html=True)
    _, col2, _ = st.columns([2, 1, 2])
    with col2:
        st.page_link("pages/5_Login.py", label="Fazer login", use_container_width=True)
    return False


# ══════════════════════════════════════════════════════════════════
# SIMULAÇÕES SALVAS
# ══════════════════════════════════════════════════════════════════

def salvar_simulacao(titulo: str, modulo: str, parametros: dict, resultado: dict) -> tuple[bool, str]:
    """Salva uma simulação no banco de dados."""
    if not is_logged_in():
        return False, "Faça login para salvar simulações."
    try:
        client = _get_client()
        client.table("simulacoes").insert({
            "user_id":    get_user_id(),
            "titulo":     titulo,
            "modulo":     modulo,
            "parametros": parametros,
            "resultado":  resultado,
        }).execute()
        return True, "Simulação salva com sucesso!"
    except Exception as e:
        return False, f"Erro ao salvar: {e}"


def listar_simulacoes() -> list:
    """Retorna as simulações salvas do usuário logado."""
    if not is_logged_in():
        return []
    try:
        client = _get_client()
        resp = client.table("simulacoes").select("*").eq(
            "user_id", get_user_id()
        ).order("created_at", desc=True).execute()
        return resp.data or []
    except Exception:
        return []


def deletar_simulacao(simulacao_id: str) -> tuple[bool, str]:
    """Deleta uma simulação salva."""
    if not is_logged_in():
        return False, "Não autorizado."
    try:
        client = _get_client()
        client.table("simulacoes").delete().eq("id", simulacao_id).execute()
        return True, "Simulação removida."
    except Exception as e:
        return False, f"Erro: {e}"


# ══════════════════════════════════════════════════════════════════
# HISTÓRICO
# ══════════════════════════════════════════════════════════════════

def registrar_acesso(modulo: str, acao: str = "") -> None:
    """Registra um acesso no histórico do usuário."""
    if not is_logged_in():
        return
    try:
        client = _get_client()
        client.table("historico").insert({
            "user_id": get_user_id(),
            "modulo":  modulo,
            "acao":    acao,
        }).execute()
    except Exception:
        pass


def listar_historico(limite: int = 20) -> list:
    """Retorna o histórico de acesso do usuário."""
    if not is_logged_in():
        return []
    try:
        client = _get_client()
        resp = client.table("historico").select("*").eq(
            "user_id", get_user_id()
        ).order("created_at", desc=True).limit(limite).execute()
        return resp.data or []
    except Exception:
        return []