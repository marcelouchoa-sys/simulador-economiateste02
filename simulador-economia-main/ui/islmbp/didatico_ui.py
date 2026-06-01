# ui/islmbp/didatico_ui.py
"""
Modo Didático IS-LM-BP — controles inline (sem sidebar).
Expõe render() para ser chamada pela página principal.
"""

import streamlit as st
from ui.islmbp.grafico import grafico_etapa, grafico_multiplas_bp
from ui.islmbp.textos  import texto_etapa, conclusao_etapa


def render() -> None:
    """Renderiza o modo didático completo com controles inline."""

    # ══════════════════════════════════════════════════════════
    # PAINEL DE CONFIGURAÇÃO — inline, acima do gráfico
    # ══════════════════════════════════════════════════════════
    with st.expander("Configurar Simulação", expanded=not st.session_state.get("did_ok", False)):

        c1, c2, c3, c4, c5 = st.columns([1, 1, 1, 1, 1])

        with c1:
            st.markdown("** Economia**")
            tipo_eco = st.radio("Tipo:", ["Fechada", "Aberta"],
                                key="did_eco", label_visibility="collapsed")

        with c2:
            st.markdown("** Regime**")
            if tipo_eco == "Aberta":
                regime = st.radio("Regime:", ["Flexível", "Fixo"],
                                  key="did_reg", label_visibility="collapsed")
            else:
                st.caption("N/A (economia fechada)")
                regime = "Flexível"

        with c3:
            st.markdown("** Política**")
            politica = st.radio("Política:", ["Fiscal", "Monetária"],
                                key="did_pol", label_visibility="collapsed")

        with c4:
            st.markdown("** Direção**")
            direcao = st.radio("Direção:", ["Expansionista", "Contracionista"],
                               key="did_dir", label_visibility="collapsed")

        with c5:
            st.markdown("** Mobilidade de Capital**")
            if tipo_eco == "Aberta":
                mob_opts    = ["Nula", "Baixa", "Alta", "Perfeita"]
                default_mob = st.session_state.get("settings", {}).get("mobilidade_capital", "Alta")
                if default_mob not in mob_opts:
                    default_mob = "Alta"
                sel_mob = st.radio("Mobilidade:", mob_opts,
                                   index=mob_opts.index(default_mob),
                                   key="did_mob", label_visibility="collapsed")
                if "settings"not in st.session_state:
                    st.session_state["settings"] = {}
                st.session_state["settings"]["mobilidade_capital"] = sel_mob
            else:
                st.caption("N/A (economia fechada)")
                sel_mob = "Alta"

        st.markdown("")
        _, btn_col, _ = st.columns([2, 1, 2])
        with btn_col:
            executar = st.button("▶ Simular", type="primary",
                                 use_container_width=True, key="did_executar")

    if executar:
        st.session_state["did_ok"]  = True
        st.session_state["did_cfg"] = (tipo_eco, regime, politica, direcao, sel_mob)
        st.session_state["etapa"]   = 0

    if not st.session_state.get("did_ok"):
        _tela_boas_vindas()
        return

    tipo_eco_s, regime_s, politica_s, direcao_s, mob_s = st.session_state["did_cfg"]

    # ── Resumo da configuração ativa ──────────────────────────
    eco_str = f"{tipo_eco_s}"
    if tipo_eco_s == "Aberta":
        eco_str += f" · {regime_s} · Mobilidade {mob_s}"
    st.caption(
        f"Configuração ativa: **{eco_str}** | "
        f"Política **{politica_s} {direcao_s}**"
    )

    # ── Navegação entre etapas ────────────────────────────────
    _nav_etapas()
    etapa = st.session_state.get("etapa", 0)
    _barra_progresso(etapa)
    st.divider()

    # ── Layout principal: gráfico | explicação ────────────────
    col_graf, col_exp = st.columns([3, 2], gap="large")

    with col_graf:
        fig = grafico_etapa(politica_s, direcao_s, tipo_eco_s, regime_s, mob_s, etapa)
        st.plotly_chart(fig, use_container_width=True)

        # Legenda de pontos
        if etapa >= 1:
            lc1, lc2, lc3 = st.columns(3)
            lc1.info(" **A** — Equilíbrio inicial")
            if etapa >= 1: lc2.warning(" **B** — Desequilíbrio transitório")
            if etapa >= 2: lc3.success(" **C** — Novo equilíbrio")

        # Comparativo das 4 BPs (apenas economia aberta)
        if tipo_eco_s == "Aberta":
            with st.expander("Ver comparação de todos os graus de mobilidade", expanded=False):
                fig_bp = grafico_multiplas_bp(politica_s, direcao_s, tipo_eco_s, regime_s)
                st.plotly_chart(fig_bp, use_container_width=True)
                st.caption(
                    "As 4 configurações possíveis da curva BP para o mesmo equilíbrio A. "
                    "A inclinação da BP determina a eficácia das políticas em economia aberta."
                )

    with col_exp:
        _painel_explicativo(politica_s, direcao_s, tipo_eco_s, regime_s, mob_s, etapa)


# ══════════════════════════════════════════════════════════════
# COMPONENTES DE INTERFACE
# ══════════════════════════════════════════════════════════════

def _tela_boas_vindas() -> None:
    st.markdown("### Como usar o Modo Didático")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("**1⃣ Configure** acima:\n- Tipo de economia\n- Política e direção\n- Mobilidade de capital")
    with col2:
        st.info("**2⃣ Simule** clicando em **▶ Simular**")
    with col3:
        st.info("**3⃣ Navegue** pelas etapas A → B → C\ne leia as explicações")

    st.markdown("---")
    st.markdown("####  O que você vai ver")
    st.markdown("""
| Etapa | O que acontece |
|---|---|
| **A — Equilíbrio Inicial** | IS₀, LM₀ e BP se cruzam no ponto A. Economia em equilíbrio. |
| **B — Choque de Curto Prazo** | A política desloca IS ou LM. Economia move-se para B. |
| **C — Novo Equilíbrio** | Ajustes cambiais e de capital levam ao novo equilíbrio C. |
""")


def _nav_etapas() -> None:
    col1, col2, col3, _ = st.columns([1, 1, 1, 3])
    with col1:
        if st.button("◀ Anterior", use_container_width=True, key="did_prev"):
            st.session_state["etapa"] = max(0, st.session_state.get("etapa", 0) - 1)
    with col2:
        if st.button("Próximo ▶", use_container_width=True, key="did_next"):
            st.session_state["etapa"] = min(2, st.session_state.get("etapa", 0) + 1)
    with col3:
        etapa_sel = st.selectbox(
            "Etapa:", [0, 1, 2],
            index=st.session_state.get("etapa", 0),
            format_func=lambda x: ["A — Inicial", "B — Choque", "C — Equilíbrio"][x],
            label_visibility="collapsed",
            key="did_etapa_sel",
        )
        st.session_state["etapa"] = etapa_sel


def _barra_progresso(etapa: int) -> None:
    ETAPAS = [
        ("A — Equilíbrio Inicial",    "etapa-blue"),
        ("B — Choque de Curto Prazo", "etapa-orange"),
        ("C — Novo Equilíbrio",       "etapa-green"),
    ]
    cols = st.columns(3)
    for i, (col, (lbl, cor_cls)) in enumerate(zip(cols, ETAPAS)):
        ativo  = (i == etapa)
        bullet = "●"if ativo else "○"
        bold   = "**"if ativo else ""
        with col:
            st.markdown(
                f'<div class="etapa-card {cor_cls if ativo else ""}" '
                f'style="opacity:{"1"if i <= etapa else "0.35"}; padding:8px 12px;">'
                f'{bold}{bullet} {lbl}{bold}</div>',
                unsafe_allow_html=True,
            )


def _painel_explicativo(politica, direcao, tipo_eco, regime, mob_s, etapa) -> None:
    txt = texto_etapa(politica, direcao, tipo_eco, regime, mob_s, etapa)

    COR_BORDA = {"blue": "#2563eb", "orange": "#d97706", "green": "#059669"}
    COR_TXT_L = {"blue": "#1e3a5f", "orange": "#7c3a00", "green": "#064e3b"}
    COR_TXT_D = {"blue": "#93c5fd", "orange": "#fcd34d", "green": "#6ee7b7"}
    BG_LIGHT  = {"blue": "#eef2ff", "orange": "#fef9ee", "green": "#f0fdf4"}
    BG_DARK   = {
        "blue":   "rgba(37,99,235,0.12)",
        "orange": "rgba(217,119,6,0.12)",
        "green":  "rgba(5,150,105,0.12)",
    }

    cor = txt["cor"]
    cid = f"ep-{cor}"
    st.markdown(
        f"<style>"
        f"#{cid}{{background:{BG_LIGHT[cor]};border-left:4px solid {COR_BORDA[cor]};"
        f"border-radius:8px;padding:14px 16px;font-family:'Segoe UI',sans-serif;}}"
        f"#{cid} .ep-titulo{{color:{COR_TXT_L[cor]};font-weight:700;font-size:1.05rem;}}"
        f"@media(prefers-color-scheme:dark){{"
        f"#{cid}{{background:{BG_DARK[cor]};}}"
        f"#{cid} .ep-titulo{{color:{COR_TXT_D[cor]};}}}}"
        f"</style>"
        f'<div id="{cid}"><span class="ep-titulo">{txt["titulo"]}</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown("")

    for subtitulo, conteudo in txt["blocos"]:
        with st.expander(f"{subtitulo}", expanded=True):
            st.markdown(conteudo)

    if etapa == 2:
        _painel_conclusao(politica, direcao, tipo_eco, regime, mob_s)


def _painel_conclusao(politica, direcao, tipo_eco, regime, mob_s) -> None:
    conc = conclusao_etapa(politica, direcao, tipo_eco, regime, mob_s)
    st.markdown("---")

    fn_map = {
        "eficaz":   st.success,
        "parcial":  st.warning,
        "ineficaz": st.error,
    }
    fn = fn_map.get(conc["veredicto"], st.info)
    fn(f"**{conc['emoji']} Conclusão — {conc['titulo']}**")

    with st.expander("Por que a política foi (in)eficaz?", expanded=True):
        st.markdown(conc["razao"])
    with st.expander("Canal econômico dominante", expanded=True):
        st.markdown(conc["canal"])
    with st.expander("E se fosse diferente? (Contrafactual)", expanded=False):
        st.markdown(conc["contrafactual"])

    fn(f" {conc['licao']}")