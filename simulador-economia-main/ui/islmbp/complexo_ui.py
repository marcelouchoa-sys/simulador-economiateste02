# ui/islmbp/complexo_ui.py
"""
Modo Complexo IS-LM-BP — painel numérico com funções integradas.
Parâmetros centrais propagam para todas as abas simultaneamente.
Expõe render() para ser chamada pela página principal.
"""

import numpy as np
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from core.parameters import DEFAULT_PARAMS
from ui.islmbp.nucleo import (
    solve_flex, solve_fixo, solve_fechada,
    curva_IS, curva_LM, curva_BP, multiplas_bp,
    consumo, investimento, balanca_comercial, fluxo_capital,
)

# Cores
COR_IS  = "#2563eb"
COR_IS1 = "#3b82f6"
COR_LM  = "#dc2626"
COR_LM1 = "#f87171"
COR_BP  = "#059669"
COR_BP1 = "#34d399"


def render() -> None:
    """Renderiza o modo complexo completo."""

    st.markdown("### 🔢 Modo Complexo — Parâmetros Numéricos")
    st.caption(
        "Altere os parâmetros abaixo e clique em **Calcular**. "
        "Todas as abas refletem os mesmos valores simultaneamente."
    )

    # ══════════════════════════════════════════════════════════
    # PAINEL DE PARÂMETROS
    # ══════════════════════════════════════════════════════════
    p, p_shock, aberta_cx, regime_cx, kf_preset, mostrar_mult_bp = _painel_parametros()

    executar = st.button("🚀 Calcular Equilíbrio", type="primary", use_container_width=False)
    st.divider()

    if not executar and "cx_resultado" not in st.session_state:
        st.info("Configure os parâmetros acima e clique em **Calcular Equilíbrio**.")
        return

    # ══════════════════════════════════════════════════════════
    # SOLVER
    # ══════════════════════════════════════════════════════════
    if executar:
        try:
            if not aberta_cx:
                eq_b = solve_fechada(p)
                eq_c = solve_fechada(p_shock)
            elif regime_cx == "flex":
                eq_b = solve_flex(p)
                eq_c = solve_flex(p_shock)
            else:
                eq_b = solve_fixo(p)
                eq_c = solve_fixo(p_shock)
            st.session_state["cx_resultado"] = (eq_b, eq_c, p, p_shock, aberta_cx, regime_cx, kf_preset, mostrar_mult_bp)
        except Exception as ex:
            st.error(f"Erro no solver: {ex}")
            st.info("Verifique os parâmetros — o sistema pode não ter solução com esses valores.")
            return

    if "cx_resultado" not in st.session_state:
        return

    eq_b, eq_c, p_, p_shock_, aberta_, regime_, kf_preset_, mostrar_mult_bp_ = st.session_state["cx_resultado"]

    # ══════════════════════════════════════════════════════════
    # MÉTRICAS PRINCIPAIS
    # ══════════════════════════════════════════════════════════
    _metricas_principais(eq_b, eq_c, aberta_)

    # ══════════════════════════════════════════════════════════
    # ABAS DE FUNÇÕES INTEGRADAS
    # ══════════════════════════════════════════════════════════
    abas = st.tabs([
        "📈 IS-LM-BP",
        "💰 Investimento",
        "🛒 Consumo",
        "💵 Demanda por Moeda",
        "🌐 Setor Externo",
        "📊 Balanço de Pagamentos",
        "🔬 Consistência",
    ])

    with abas[0]:
        _aba_islmbp(eq_b, eq_c, p_, p_shock_, aberta_, regime_, kf_preset_, mostrar_mult_bp_)

    with abas[1]:
        _aba_investimento(eq_b, eq_c, p_, p_shock_)

    with abas[2]:
        _aba_consumo(eq_b, eq_c, p_, p_shock_)

    with abas[3]:
        _aba_demanda_moeda(eq_b, eq_c, p_, p_shock_)

    with abas[4]:
        _aba_setor_externo(eq_b, eq_c, p_, p_shock_, aberta_)

    with abas[5]:
        _aba_bp(eq_b, eq_c, p_, p_shock_, aberta_)

    with abas[6]:
        _aba_consistencia(eq_b, eq_c)


# ══════════════════════════════════════════════════════════════
# PAINEL DE PARÂMETROS
# ══════════════════════════════════════════════════════════════

def _painel_parametros():
    p       = DEFAULT_PARAMS.copy()
    p_shock = DEFAULT_PARAMS.copy()

    with st.expander("⚙️ Parâmetros Base e Choque", expanded=True):
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown("**🏛️ Política Fiscal**")
            p["G"]  = st.number_input("G — Gasto do Governo",  value=float(p["G"]),  step=10., key="cx_G")
            p["T"]  = st.number_input("T — Impostos",          value=float(p["T"]),  step=10., key="cx_T")
            st.markdown("**💰 Política Monetária**")
            p["M"]  = st.number_input("M — Oferta de Moeda",   value=float(p["M"]),  step=50., key="cx_M")
            p["P"]  = st.number_input("P — Nível de Preços",   value=float(p["P"]),  step=0.1, key="cx_P")

        with col2:
            st.markdown("**📐 Parâmetros IS**")
            p["c0"] = st.number_input("c0 — Consumo Autônomo",      value=float(p["c0"]), step=10.,  key="cx_c0")
            p["c1"] = st.number_input("c1 — Propensão a Consumir",  value=float(p["c1"]), step=0.01, key="cx_c1", format="%.2f")
            p["I0"] = st.number_input("I0 — Invest. Autônomo",      value=float(p["I0"]), step=10.,  key="cx_I0")
            p["b"]  = st.number_input("b — Sensib. I a r",          value=float(p["b"]),  step=5.,   key="cx_b")

        with col3:
            st.markdown("**📐 Parâmetros LM**")
            p["k"]  = st.number_input("k — Sensib. Md a Y",  value=float(p["k"]), step=0.05, key="cx_k", format="%.2f")
            p["h"]  = st.number_input("h — Sensib. Md a r",  value=float(p["h"]), step=10.,  key="cx_h")

            st.markdown("**🌐 Economia Aberta**")
            aberta_cx = st.checkbox("Ativar economia aberta", value=False, key="cx_aberta")
            p["aberta"] = aberta_cx

            regime_cx = "flex"
            kf_preset  = "Alta"
            mostrar_mult_bp = False

            if aberta_cx:
                regime_cx = st.radio("Regime cambial:", ["flex", "fixo"],
                                     format_func=lambda x: "Flexível" if x == "flex" else "Fixo",
                                     key="cx_regime", horizontal=True)
                p["regime"] = regime_cx
                kf_preset   = st.select_slider("Mobilidade de Capital:",
                                               options=["Nula", "Baixa", "Alta", "Perfeita"],
                                               value="Alta", key="cx_kf")
                p["kf"] = {"Nula": 0., "Baixa": 10., "Alta": 700., "Perfeita": 1e7}[kf_preset]
                mostrar_mult_bp = st.checkbox("Mostrar todas as BPs no gráfico", value=False, key="cx_multbp")

                p["Y_star"] = st.number_input("Y* — Renda Externa",       value=float(p["Y_star"]), step=50., key="cx_Ys")
                p["r_star"] = st.number_input("r* — Juros Internacionais", value=float(p["r_star"]), step=0.005, key="cx_rs", format="%.4f")
                p["e"]      = st.number_input("e — Câmbio Inicial",        value=float(p["e"]),      step=0.05, key="cx_e")
                if regime_cx == "fixo":
                    p["e_fixed"] = st.number_input("e fixo (meta BC)", value=float(p.get("e_fixed", 1.)), step=0.05, key="cx_ef")

        with col4:
            st.markdown("**⚡ Choque (Cenário 2)**")
            dG = st.number_input("ΔG", value=0., step=10., key="cx_dG")
            dT = st.number_input("ΔT", value=0., step=10., key="cx_dT")
            dM = st.number_input("ΔM", value=0., step=50., key="cx_dM")

            if aberta_cx:
                dr_star = st.number_input("Δr*", value=0., step=0.005, key="cx_drs", format="%.4f")
                dY_star = st.number_input("ΔY*", value=0., step=50., key="cx_dYs")
                p["x0"] = st.number_input("x0 — Export. Autônomas", value=float(p["x0"]), step=10., key="cx_x0")
                p["x1"] = st.number_input("x1 — Sensib. X a Y*",    value=float(p["x1"]), step=0.01, key="cx_x1", format="%.3f")
                p["m0"] = st.number_input("m0 — Import. Autônomas", value=float(p["m0"]), step=10., key="cx_m0")
                p["m1"] = st.number_input("m1 — Propensão Importar", value=float(p["m1"]), step=0.01, key="cx_m1", format="%.3f")
            else:
                dr_star = dY_star = 0.

    # Montar p_shock
    p_shock = p.copy()
    p_shock["G"] += dG
    p_shock["T"] += dT
    p_shock["M"] += dM
    if aberta_cx:
        p_shock["r_star"] = p["r_star"] + dr_star
        p_shock["Y_star"] = p["Y_star"] + dY_star

    return p, p_shock, aberta_cx, regime_cx, kf_preset, mostrar_mult_bp


# ══════════════════════════════════════════════════════════════
# MÉTRICAS PRINCIPAIS
# ══════════════════════════════════════════════════════════════

def _metricas_principais(eq_b, eq_c, aberta):
    st.markdown("### 📊 Resultados do Equilíbrio")
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Produto (Y*)",     f"{eq_b['Y']:.2f}",            f"{eq_c['Y']-eq_b['Y']:+.2f}")
    m2.metric("Juros (r*)",       f"{eq_b['r']*100:.3f}%",       f"{(eq_c['r']-eq_b['r'])*100:+.3f}pp")
    m3.metric("Consumo (C)",      f"{eq_b['C']:.2f}",            f"{eq_c['C']-eq_b['C']:+.2f}")
    m4.metric("Investimento (I)", f"{eq_b['I']:.2f}",            f"{eq_c['I']-eq_b['I']:+.2f}")
    if aberta:
        m5.metric("Câmbio (e*)",  f"{eq_b['e']:.4f}",            f"{eq_c['e']-eq_b['e']:+.4f}")
    else:
        m5.metric("NX",           "N/A (fechada)", "")

    # Tabela completa
    with st.expander("📋 Tabela completa de resultados", expanded=False):
        linhas = [
            ("Y — Produto",              eq_b["Y"],        eq_c["Y"]),
            ("r — Taxa de Juros (%)",    eq_b["r"]*100,    eq_c["r"]*100),
            ("C — Consumo",              eq_b["C"],        eq_c["C"]),
            ("I — Investimento",         eq_b["I"],        eq_c["I"]),
        ]
        if aberta:
            linhas += [
                ("e — Câmbio",           eq_b["e"],        eq_c["e"]),
                ("NX — Export. Líquidas", eq_b["NX"],      eq_c["NX"]),
                ("CF — Fluxo de Capital", eq_b["CF"],      eq_c["CF"]),
                ("BP — Bal. Pagamentos",  eq_b["BP"],      eq_c["BP"]),
            ]
        md = "| Variável | Base | Choque | Δ |\n|---|---|---|---|\n"
        for nome, vb, vc in linhas:
            md += f"| **{nome}** | {vb:.3f} | {vc:.3f} | **{vc-vb:+.3f}** |\n"
        st.markdown(md)


# ══════════════════════════════════════════════════════════════
# ABA IS-LM-BP
# ══════════════════════════════════════════════════════════════

def _aba_islmbp(eq_b, eq_c, p, p_shock, aberta, regime, kf_preset, mostrar_mult_bp):
    st.markdown("#### 📈 Gráfico IS-LM-BP — Base vs. Choque")

    # Range dinâmico centrado no equilíbrio real
    Y_center = (eq_b["Y"] + eq_c["Y"]) / 2
    r_center = (eq_b["r"] + eq_c["r"]) / 2
    Y_span   = max(abs(eq_c["Y"] - eq_b["Y"]) * 2, 600)
    r_span   = max(abs(eq_c["r"] - eq_b["r"]) * 4, 0.3)

    Y_lo = max(100, Y_center - Y_span)
    Y_hi = Y_center + Y_span
    r_min = r_center - r_span
    r_max = r_center + r_span

    Y_grid = np.linspace(Y_lo, Y_hi, 500)

    fig = go.Figure()

    # IS e LM base e choque
    for r_c, nm, cor, dsh in [
        (curva_IS(Y_grid, eq_b["e"], p, aberta),        "IS base",   COR_IS,  "solid"),
        (curva_IS(Y_grid, eq_c["e"], p_shock, aberta),  "IS choque", COR_IS1, "dash"),
        (curva_LM(Y_grid, p["M"],    p),                "LM base",   COR_LM,  "solid"),
        (curva_LM(Y_grid, p_shock["M"], p_shock),       "LM choque", COR_LM1, "dash"),
    ]:
        mask = (r_c > r_min) & (r_c < r_max)
        fig.add_trace(go.Scatter(
            x=Y_grid[mask], y=r_c[mask], name=nm,
            line=dict(color=cor, width=2.5, dash=dsh),
        ))

    # BP(s)
    if aberta:
        if mostrar_mult_bp:
            # Mostrar todas as 4 BPs
            Y_anchor = eq_b["Y"]
            r_anchor = eq_b["r"]
            bps = multiplas_bp(Y_grid, Y_anchor, r_anchor)
            cores_bp = {
                "Nula (vertical)":   "#065f46",
                "Baixa (íngreme)":   "#059669",
                "Alta (suave)":      "#10b981",
                "Perfeita (horiz.)": "#34d399",
            }
            for label, r_bp in bps.items():
                if r_bp is None:
                    # Vertical
                    fig.add_vline(x=Y_anchor,
                                  line=dict(color=cores_bp[label], width=2, dash="dash"),
                                  annotation_text=label, annotation_position="top")
                else:
                    mask = (r_bp > r_min) & (r_bp < r_max)
                    fig.add_trace(go.Scatter(
                        x=Y_grid[mask], y=r_bp[mask], name=f"BP — {label}",
                        line=dict(color=cores_bp[label], width=2, dash="dot"),
                    ))
        else:
            # Só a BP do preset selecionado — ancorada no equilíbrio real
            for r_bp, nm, cor, dsh in [
                (curva_BP(Y_grid, eq_b["e"], p,      Y_anchor=eq_b["Y"], r_anchor=eq_b["r"]), f"BP base ({kf_preset})",   COR_BP,  "solid"),
                (curva_BP(Y_grid, eq_c["e"], p_shock, Y_anchor=eq_c["Y"], r_anchor=eq_c["r"]), f"BP choque ({kf_preset})", COR_BP1, "dash"),
            ]:
                mask = (r_bp > r_min) & (r_bp < r_max)
                fig.add_trace(go.Scatter(
                    x=Y_grid[mask], y=r_bp[mask], name=nm,
                    line=dict(color=cor, width=2.5, dash=dsh),
                ))

    # Pontos de equilíbrio
    fig.add_trace(go.Scatter(
        x=[eq_b["Y"], eq_c["Y"]], y=[eq_b["r"], eq_c["r"]],
        mode="markers+text",
        marker=dict(size=14, color=[COR_IS, COR_LM], symbol="star",
                    line=dict(width=1, color="white")),
        text=["E₀", "E₁"], textposition="top right",
        textfont=dict(size=14), name="Equilíbrios",
    ))

    # Seta A→C
    fig.add_annotation(
        ax=eq_b["Y"], ay=eq_b["r"], x=eq_c["Y"], y=eq_c["r"],
        xref="x", yref="y", axref="x", ayref="y",
        showarrow=True, arrowhead=3, arrowwidth=2.5, arrowcolor="#0f172a",
    )

    fig.update_layout(
        title="IS-LM-BP: Base vs. Choque",
        xaxis_title="Produto (Y)", yaxis_title="Taxa de Juros (r)",
        xaxis=dict(range=[Y_lo, Y_hi]),
        yaxis=dict(range=[r_min, r_max]),
        template="plotly_white", height=520,
        legend=dict(x=0.01, y=0.99),
    )
    st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════
# ABA INVESTIMENTO
# ══════════════════════════════════════════════════════════════

def _aba_investimento(eq_b, eq_c, p, p_shock):
    st.markdown("#### 💰 Função Investimento — I = I₀ − b·r")
    st.latex(r"I = I_0 - b \cdot r")

    r_range = np.linspace(0, 0.25, 300)
    I_base   = p["I0"]      - p["b"]      * r_range
    I_choque = p_shock["I0"] - p_shock["b"] * r_range

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=I_base,   y=r_range * 100, name="I base",   line=dict(color=COR_IS,  width=2.5)))
    fig.add_trace(go.Scatter(x=I_choque, y=r_range * 100, name="I choque", line=dict(color=COR_IS1, width=2.5, dash="dash")))

    # Pontos de equilíbrio
    for eq, nm, cor in [(eq_b, "E₀", COR_IS), (eq_c, "E₁", COR_LM)]:
        fig.add_trace(go.Scatter(
            x=[eq["I"]], y=[eq["r"] * 100],
            mode="markers+text", name=nm,
            marker=dict(size=12, color=cor, symbol="star"),
            text=[f" I={eq['I']:.1f}"], textposition="middle right",
        ))

    fig.update_layout(
        xaxis_title="Investimento (I)", yaxis_title="Taxa de Juros (r %)",
        template="plotly_white", height=380,
    )
    st.plotly_chart(fig, use_container_width=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("I base",           f"{eq_b['I']:.2f}")
    c2.metric("I choque",         f"{eq_c['I']:.2f}", f"{eq_c['I']-eq_b['I']:+.2f}")
    c3.metric("Crowding-out (ΔI)", f"{eq_c['I']-eq_b['I']:+.2f}",
              delta_color="inverse" if eq_c["I"] < eq_b["I"] else "normal")

    if eq_c["I"] < eq_b["I"]:
        st.warning(f"⚠️ **Crowding-out:** a política elevou os juros de {eq_b['r']*100:.2f}% para {eq_c['r']*100:.2f}%, "
                   f"reduzindo o investimento privado em {eq_b['I']-eq_c['I']:.2f}.")


# ══════════════════════════════════════════════════════════════
# ABA CONSUMO
# ══════════════════════════════════════════════════════════════

def _aba_consumo(eq_b, eq_c, p, p_shock):
    st.markdown("#### 🛒 Função Consumo — C = c₀ + c₁(Y − T)")
    st.latex(r"C = c_0 + c_1(Y - T)")

    Y_range  = np.linspace(200, 2500, 300)
    C_base   = consumo(p["c0"],      p["c1"],      Y_range, p["T"])
    C_choque = consumo(p_shock["c0"], p_shock["c1"], Y_range, p_shock["T"])

    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=("Função Consumo", "Cruzamento Keynesiano"))

    fig.add_trace(go.Scatter(x=Y_range, y=C_base,   name="C base",   line=dict(color=COR_IS,  width=2.5)), row=1, col=1)
    fig.add_trace(go.Scatter(x=Y_range, y=C_choque, name="C choque", line=dict(color=COR_IS1, width=2.5, dash="dash")), row=1, col=1)

    fig.add_trace(go.Scatter(x=Y_range, y=Y_range,  name="Y = DA (45°)", line=dict(color="gray", width=1.5, dash="dot")), row=1, col=2)
    fig.add_trace(go.Scatter(x=Y_range, y=C_base + p["I0"] + p["G"],   name="DA base",   line=dict(color=COR_IS,  width=2.5)), row=1, col=2)
    fig.add_trace(go.Scatter(x=Y_range, y=C_choque + p_shock["I0"] + p_shock["G"], name="DA choque", line=dict(color=COR_IS1, width=2.5, dash="dash")), row=1, col=2)

    for eq, nm, cor in [(eq_b, "Y₀", COR_IS), (eq_c, "Y₁", COR_LM)]:
        fig.add_trace(go.Scatter(x=[eq["Y"]], y=[eq["Y"]],
                                  mode="markers+text", name=nm,
                                  marker=dict(size=11, color=cor, symbol="star"),
                                  text=[f" {nm}"], textposition="top right"), row=1, col=2)

    fig.update_layout(template="plotly_white", height=380)
    fig.update_xaxes(title_text="Y", row=1, col=1)
    fig.update_yaxes(title_text="C", row=1, col=1)
    fig.update_xaxes(title_text="Y", row=1, col=2)
    fig.update_yaxes(title_text="DA", row=1, col=2)
    st.plotly_chart(fig, use_container_width=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("C base",   f"{eq_b['C']:.2f}")
    c2.metric("C choque", f"{eq_c['C']:.2f}", f"{eq_c['C']-eq_b['C']:+.2f}")
    mult_teorico = 1.0 / max(1 - p["c1"], 1e-9)
    c3.metric("Multiplicador k", f"{mult_teorico:.3f}×")


# ══════════════════════════════════════════════════════════════
# ABA DEMANDA POR MOEDA
# ══════════════════════════════════════════════════════════════

def _aba_demanda_moeda(eq_b, eq_c, p, p_shock):
    st.markdown("#### 💵 Demanda por Moeda e Curva LM")
    st.latex(r"M^d/P = kY - hr \qquad r_{LM} = \frac{kY - M/P}{h}")

    Y_range = np.linspace(200, 2500, 300)
    r_LM_b  = (p["k"]      * Y_range - p["M"]      / p["P"])      / p["h"]
    r_LM_c  = (p_shock["k"] * Y_range - p_shock["M"] / p_shock["P"]) / p_shock["h"]

    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=("Curva LM", "Md vs Juros (Y fixo)"))

    fig.add_trace(go.Scatter(x=Y_range, y=r_LM_b  * 100, name="LM base",   line=dict(color=COR_LM,  width=2.5)), row=1, col=1)
    fig.add_trace(go.Scatter(x=Y_range, y=r_LM_c  * 100, name="LM choque", line=dict(color=COR_LM1, width=2.5, dash="dash")), row=1, col=1)

    for eq, nm, cor in [(eq_b, "E₀", COR_IS), (eq_c, "E₁", COR_LM)]:
        fig.add_trace(go.Scatter(x=[eq["Y"]], y=[eq["r"] * 100],
                                  mode="markers+text", name=nm,
                                  marker=dict(size=11, color=cor, symbol="star"),
                                  text=[f" {nm}"], textposition="top right"), row=1, col=1)

    # Md vs r para Y fixo em Y base
    r_range = np.linspace(0, 0.2, 300)
    Md_b = p["k"] * eq_b["Y"] - p["h"] * r_range
    Md_c = p_shock["k"] * eq_c["Y"] - p_shock["h"] * r_range
    Ms_b = p["M"] / p["P"]
    Ms_c = p_shock["M"] / p_shock["P"]

    fig.add_trace(go.Scatter(x=Md_b, y=r_range * 100, name="Md base",   line=dict(color=COR_LM,  width=2.5)), row=1, col=2)
    fig.add_trace(go.Scatter(x=Md_c, y=r_range * 100, name="Md choque", line=dict(color=COR_LM1, width=2.5, dash="dash")), row=1, col=2)
    fig.add_vline(x=Ms_b, line=dict(color=COR_IS,  width=2, dash="dot"), annotation_text=f"Ms/P={Ms_b:.0f}", row=1, col=2)
    fig.add_vline(x=Ms_c, line=dict(color=COR_IS1, width=2, dash="dot"), annotation_text=f"Ms'/P={Ms_c:.0f}", row=1, col=2)

    fig.update_layout(template="plotly_white", height=380)
    fig.update_xaxes(title_text="Y", row=1, col=1)
    fig.update_yaxes(title_text="r (%)", row=1, col=1)
    fig.update_xaxes(title_text="Md/P", row=1, col=2)
    fig.update_yaxes(title_text="r (%)", row=1, col=2)
    st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════
# ABA SETOR EXTERNO
# ══════════════════════════════════════════════════════════════

def _aba_setor_externo(eq_b, eq_c, p, p_shock, aberta):
    st.markdown("#### 🌐 Setor Externo — NX, CF e Câmbio")

    if not aberta:
        st.info("Ative a economia aberta para ver o setor externo.")
        return

    st.latex(r"NX = X(e, Y^*) - M(e, Y) \qquad CF = k_f(r - r^*)")

    # NX vs câmbio
    e_range = np.linspace(0.3, 3.0, 300)
    NX_e_b  = [balanca_comercial(p["x0"], p["x1"], p["Y_star"], p["m0"], p["m1"], eq_b["Y"], e) for e in e_range]
    NX_e_c  = [balanca_comercial(p_shock["x0"], p_shock["x1"], p_shock["Y_star"], p_shock["m0"], p_shock["m1"], eq_c["Y"], e) for e in e_range]

    # CF vs r
    r_range = np.linspace(-0.05, 0.25, 300)
    CF_r_b  = [fluxo_capital(p["kf"],       r, p["r_star"])       for r in r_range]
    CF_r_c  = [fluxo_capital(p_shock["kf"], r, p_shock["r_star"]) for r in r_range]

    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=("Balança Comercial vs Câmbio", "Fluxo de Capital vs Juros"))

    fig.add_trace(go.Scatter(x=e_range, y=NX_e_b, name="NX base",   line=dict(color=COR_BP,  width=2.5)), row=1, col=1)
    fig.add_trace(go.Scatter(x=e_range, y=NX_e_c, name="NX choque", line=dict(color=COR_BP1, width=2.5, dash="dash")), row=1, col=1)
    fig.add_hline(y=0, line=dict(color="gray", width=1), row=1, col=1)
    for eq, nm, cor in [(eq_b, "e₀", COR_IS), (eq_c, "e₁", COR_LM)]:
        fig.add_vline(x=eq["e"], line=dict(color=cor, width=1.5, dash="dot"),
                      annotation_text=f"{nm}={eq['e']:.3f}", row=1, col=1)

    fig.add_trace(go.Scatter(x=np.array(CF_r_b), y=r_range * 100, name="CF base",   line=dict(color=COR_BP,  width=2.5)), row=1, col=2)
    fig.add_trace(go.Scatter(x=np.array(CF_r_c), y=r_range * 100, name="CF choque", line=dict(color=COR_BP1, width=2.5, dash="dash")), row=1, col=2)
    fig.add_hline(y=p["r_star"] * 100, line=dict(color="gray", width=1, dash="dot"),
                  annotation_text=f"r*={p['r_star']*100:.1f}%", row=1, col=2)

    fig.update_layout(template="plotly_white", height=380)
    fig.update_xaxes(title_text="Câmbio (e)", row=1, col=1)
    fig.update_yaxes(title_text="NX", row=1, col=1)
    fig.update_xaxes(title_text="CF (Fluxo de Capital)", row=1, col=2)
    fig.update_yaxes(title_text="r (%)", row=1, col=2)
    st.plotly_chart(fig, use_container_width=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("NX base",  f"{eq_b['NX']:.2f}")
    c2.metric("NX choque", f"{eq_c['NX']:.2f}", f"{eq_c['NX']-eq_b['NX']:+.2f}")
    c3.metric("CF base",  f"{eq_b['CF']:.2f}")
    c4.metric("CF choque", f"{eq_c['CF']:.2f}", f"{eq_c['CF']-eq_b['CF']:+.2f}")


# ══════════════════════════════════════════════════════════════
# ABA BALANÇO DE PAGAMENTOS
# ══════════════════════════════════════════════════════════════

def _aba_bp(eq_b, eq_c, p, p_shock, aberta):
    st.markdown("#### 📊 Balanço de Pagamentos — NX + CF = 0")

    if not aberta:
        st.info("Ative a economia aberta para ver o Balanço de Pagamentos.")
        return

    st.latex(r"BP = NX + CF = 0 \quad \text{(equilíbrio externo)}")

    Y_grid  = np.linspace(200, 2500, 300)
    BP_base = [balanca_comercial(p["x0"], p["x1"], p["Y_star"], p["m0"], p["m1"], Y, eq_b["e"])
               + fluxo_capital(p["kf"], eq_b["r"], p["r_star"]) for Y in Y_grid]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=Y_grid, y=BP_base, name="BP base", line=dict(color=COR_BP, width=2.5)))
    fig.add_hline(y=0, line=dict(color="black", width=1.5))
    fig.add_vline(x=eq_b["Y"], line=dict(color=COR_IS, width=1.5, dash="dash"),
                  annotation_text=f"Y₀={eq_b['Y']:.0f}")
    fig.add_vline(x=eq_c["Y"], line=dict(color=COR_LM, width=1.5, dash="dash"),
                  annotation_text=f"Y₁={eq_c['Y']:.0f}")

    # Decomposição: NX e CF separados
    NX_grid = [balanca_comercial(p["x0"], p["x1"], p["Y_star"], p["m0"], p["m1"], Y, eq_b["e"]) for Y in Y_grid]
    CF_val  = fluxo_capital(p["kf"], eq_b["r"], p["r_star"])
    fig.add_trace(go.Scatter(x=Y_grid, y=NX_grid, name="NX (comércio)",
                             line=dict(color="#0891b2", width=2, dash="dot")))
    fig.add_hline(y=CF_val, line=dict(color="#7c3aed", width=2, dash="dot"),
                  annotation_text=f"CF={CF_val:.1f}")

    fig.update_layout(
        title="Balanço de Pagamentos: NX + CF",
        xaxis_title="Produto (Y)", yaxis_title="BP",
        template="plotly_white", height=380,
    )
    st.plotly_chart(fig, use_container_width=True)

    bp_b = eq_b["NX"] + eq_b["CF"]
    bp_c = eq_c["NX"] + eq_c["CF"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("BP base",   f"{bp_b:.4f}", delta="≈ 0 ✅" if abs(bp_b) < 0.1 else "⚠️ Desequilíbrio")
    c2.metric("BP choque", f"{bp_c:.4f}", delta="≈ 0 ✅" if abs(bp_c) < 0.1 else "⚠️ Desequilíbrio")
    c3.metric("NX choque", f"{eq_c['NX']:.2f}", f"{eq_c['NX']-eq_b['NX']:+.2f}")
    c4.metric("CF choque", f"{eq_c['CF']:.2f}", f"{eq_c['CF']-eq_b['CF']:+.2f}")


# ══════════════════════════════════════════════════════════════
# ABA CONSISTÊNCIA
# ══════════════════════════════════════════════════════════════

def _aba_consistencia(eq_b, eq_c):
    st.markdown("#### 🔬 Verificação de Consistência do Solver")
    st.caption("Resíduos das equações de equilíbrio — valores próximos de 0 indicam solução correta.")

    for label, eq, sufixo in [("Base (E₀)", eq_b, "b"), ("Choque (E₁)", eq_c, "c")]:
        st.markdown(f"**{label}:**")
        for nome, res in [("IS", eq["IS_res"]), ("LM", eq["LM_res"]), ("BP", eq["BP_res"])]:
            ok  = abs(res) < 0.01
            ico = "✅" if ok else "⚠️"
            st.markdown(f"{ico} **{nome}** resíduo = `{res:.8f}`")
        st.markdown("")