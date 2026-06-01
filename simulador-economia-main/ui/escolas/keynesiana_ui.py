# ui/escolas/keynesiana_ui.py
"""
Escola Keynesiana — Demanda efetiva determina o produto
Expõe render() para ser chamada pela página principal.
"""

import numpy as np
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ui.escolas.classica_ui import _card


def render() -> None:
    st.subheader("Escola Keynesiana — Demanda Efetiva Determina o Produto")

    with st.expander("Fundamentos da Escola Keynesiana", expanded=False):
        st.markdown("""
| Princípio | Descrição |
|---|---|
| **Demanda Efetiva** | É a demanda agregada que determina o nível de produto e emprego |
| **Rigidez de Preços/Salários** | Preços e salários são rígidos no curto prazo (especialmente para baixo) |
| **Desemprego Involuntário** | A economia pode se equilibrar abaixo do pleno emprego |
| **Multiplicador** | Variações em G ou I têm efeito amplificado sobre Y |
| **Armadilha da Liquidez** | Em crises, política monetária pode ser ineficaz |
| **Papel do Estado** | Política fiscal ativa é necessária para estabilizar a economia |
""")

    # ══════════════════════════════════════════════════════════════
    # CONTROLES
    # ══════════════════════════════════════════════════════════════
    st.markdown("### Parâmetros")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("** Política Fiscal**")
        G  = st.slider("Gasto do Governo (G)",    0.0, 100.0, 30.0, 1.0, key="kn_G")
        T  = st.slider("Impostos (T)",             0.0,  80.0, 20.0, 1.0, key="kn_T")
        TR = st.slider("Transferências (TR)",      0.0,  50.0, 10.0, 1.0, key="kn_TR")

    with col2:
        st.markdown("** Setor Privado**")
        C0  = st.slider("Consumo Autônomo (C₀)",            0.0,  80.0, 20.0, 1.0,  key="kn_C0")
        mpc = st.slider("Propensão Marginal a Consumir (c)", 0.50, 0.95, 0.75, 0.01, key="kn_mpc")
        I0  = st.slider("Investimento Autônomo (I₀)",       0.0,  80.0, 25.0, 1.0,  key="kn_I0")

    with col3:
        st.markdown("** Juros e Referências**")
        taxa_juros = st.slider("Taxa de Juros (r)", 0.0, 0.20, 0.05, 0.005,
                               format="%.3f", key="kn_r")
        b_inv      = st.slider("Sensibilidade Inv. a r (b)", 0.0, 200.0, 50.0, 5.0, key="kn_b")
        Y_pleno    = st.slider("Produto Potencial (Ȳ)", 100.0, 400.0, 250.0, 10.0, key="kn_Yp")

    # ══════════════════════════════════════════════════════════════
    # CÁLCULOS
    # ══════════════════════════════════════════════════════════════
    I_eq        = I0 - b_inv * taxa_juros
    numerador   = C0 + I_eq + G - mpc * (T - TR)
    multiplicador = 1.0 / (1.0 - mpc)
    Y_eq        = numerador * multiplicador
    C_eq        = C0 + mpc * (Y_eq - T + TR)
    hiato       = Y_eq - Y_pleno
    hiato_pct   = (hiato / Y_pleno) * 100

    u_natural   = 0.05
    lambda_okun = 0.5
    u_eq        = max(0.0, u_natural - lambda_okun * (hiato / Y_pleno))

    mult_G  = multiplicador
    mult_T  = -mpc * multiplicador
    mult_TR =  mpc * multiplicador

    Y_range = np.linspace(0, Y_pleno * 1.6, 300)
    DA_line = C0 + I_eq + G - mpc * (T - TR) + mpc * Y_range
    linha_45 = Y_range

    # OA-DA: P range e curvas
    P_base    = 1.0
    P_range_k = np.linspace(0.2, 3.0, 300)
    DA_k      = Y_eq * (P_base / P_range_k)
    phi       = Y_pleno * 0.8
    OA_k      = np.maximum(Y_pleno + phi * (P_range_k - P_base), 0)

    # Interseção correta OA-DA
    # DA_k = OA_k → Y_eq*(P0/P) = Y_pleno + phi*(P - P0)
    # Resolve numericamente
    idx_intersec = np.argmin(np.abs(DA_k - OA_k))
    P_eq_k = P_range_k[idx_intersec]
    Y_eq_k = float(DA_k[idx_intersec])

    # ══════════════════════════════════════════════════════════════
    # MÉTRICAS
    # ══════════════════════════════════════════════════════════════
    st.markdown("### Equilíbrio Keynesiano")
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Produto de Equilíbrio (Y*)", f"{Y_eq:.1f}")
    m2.metric("Produto Potencial (Ȳ)",      f"{Y_pleno:.1f}")
    m3.metric("Hiato do Produto",           f"{hiato:+.1f}",
              delta_color="normal"if hiato >= 0 else "inverse")
    m4.metric("Multiplicador Keynesiano",   f"{multiplicador:.2f}×")
    m5.metric("Desemprego Estimado",        f"{u_eq*100:.1f}%",
              delta=f"{(u_eq - u_natural)*100:+.1f}pp vs natural",
              delta_color="inverse")

    # ══════════════════════════════════════════════════════════════
    # GRÁFICOS
    # ══════════════════════════════════════════════════════════════
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=(
            "Diagrama de Cruz Keynesiana (DA × 45°)",
            "Oferta e Demanda Agregada — Curto Prazo",
        ),
        horizontal_spacing=0.12,
    )

    # ── Subplot 1: Cruz Keynesiana ───────────────────────────────
    fig.add_trace(go.Scatter(
        x=Y_range, y=linha_45, mode="lines", name="Y = DA (45°)",
        line=dict(color="#607D8B", width=1.5, dash="dot"),
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=Y_range, y=DA_line, mode="lines", name=f"DA (c={mpc:.2f})",
        line=dict(color="#2196F3", width=2.5),
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=[Y_pleno, Y_pleno], y=[0, Y_pleno * 1.1],
        mode="lines", name=f"Pleno Emprego (Ȳ={Y_pleno:.0f})",
        line=dict(color="#4CAF50", width=2, dash="dash"),
    ), row=1, col=1)
    DA_at_eq = C0 + I_eq + G - mpc * (T - TR) + mpc * Y_eq
    fig.add_trace(go.Scatter(
        x=[Y_eq], y=[DA_at_eq], mode="markers+text",
        name=f"Equilíbrio Y*={Y_eq:.1f}",
        marker=dict(color="#FF9800", size=12),
        text=["E*"], textposition="top right",
        textfont=dict(size=13, color="#FF9800"),
    ), row=1, col=1)

    if hiato < -1:
        fig.add_vrect(x0=Y_eq, x1=Y_pleno,
                      fillcolor="rgba(244,67,54,0.08)", layer="below", line_width=0,
                      annotation_text="Hiato Recessivo",
                      annotation_font_color="#F44336", row=1, col=1)
    elif hiato > 1:
        fig.add_vrect(x0=Y_pleno, x1=Y_eq,
                      fillcolor="rgba(255,152,0,0.08)", layer="below", line_width=0,
                      annotation_text="Hiato Inflacionário",
                      annotation_font_color="#FF9800", row=1, col=1)

    fig.update_xaxes(title_text="Produto (Y)", row=1, col=1, showgrid=True,
                     range=[0, Y_pleno * 1.5])
    fig.update_yaxes(title_text="Demanda Agregada (DA)", row=1, col=1, showgrid=True,
                     range=[0, Y_pleno * 1.5])

    # ── Subplot 2: OA-DA correto ─────────────────────────────────
    fig.add_trace(go.Scatter(
        x=DA_k, y=P_range_k, mode="lines", name="DA (Keynesiana)",
        line=dict(color="#2196F3", width=2.5),
    ), row=1, col=2)
    fig.add_trace(go.Scatter(
        x=OA_k, y=P_range_k, mode="lines", name="OA Curto Prazo (inclinada)",
        line=dict(color="#E91E63", width=2.5),
    ), row=1, col=2)
    fig.add_trace(go.Scatter(
        x=[Y_pleno, Y_pleno], y=[0.2, 3.0],
        mode="lines", name="OA Longo Prazo (Ȳ)",
        line=dict(color="#4CAF50", width=2, dash="dash"),
    ), row=1, col=2)
    # Ponto de equilíbrio OA-DA corrigido
    fig.add_trace(go.Scatter(
        x=[Y_eq_k], y=[P_eq_k], mode="markers+text",
        name="Equilíbrio OA-DA",
        marker=dict(color="#FF9800", size=12),
        text=["E*"], textposition="top right",
        textfont=dict(size=13, color="#FF9800"),
    ), row=1, col=2)

    if Y_eq < Y_pleno - 1:
        fig.add_vrect(x0=Y_eq, x1=Y_pleno,
                      fillcolor="rgba(244,67,54,0.06)", layer="below", line_width=0,
                      annotation_text=f"Desemprego: u={u_eq*100:.1f}%",
                      annotation_font_color="#F44336", row=1, col=2)

    fig.update_xaxes(title_text="Produto (Y)", row=1, col=2, showgrid=True,
                     range=[0, Y_pleno * 1.6])
    fig.update_yaxes(title_text="Nível de Preços (P)", row=1, col=2, showgrid=True,
                     range=[0.2, 3.0])

    fig.update_layout(
        height=520, template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=-0.28, xanchor="center", x=0.5),
        margin=dict(t=60, b=90),
    )
    st.plotly_chart(fig, use_container_width=True)

    # ══════════════════════════════════════════════════════════════
    # ANÁLISE NARRATIVA
    # ══════════════════════════════════════════════════════════════
    st.markdown("### Análise Completa da Situação Econômica")

    narrativa_demanda = (
        f"C₀ = {C0:.1f}, c = {mpc:.2f} → cada R$ 1 de renda disponível: "
        f"R$ {mpc:.2f} consumidos, R$ {1-mpc:.2f} poupados. "
        f"Investimento: I = {I0:.1f} − {b_inv:.0f}×{taxa_juros:.3f} = **{I_eq:.1f}**. "
        f"Com G = {G:.1f}, T = {T:.1f}, TR = {TR:.1f}: renda disponível líquida pública = {T-TR:.1f}."
    )

    narrativa_multiplicador = (
        f"Demanda autônoma: A = {C0:.1f} + {I_eq:.1f} + {G:.1f} − {mpc:.2f}×{T-TR:.1f} = **{numerador:.1f}**. "
        f"Multiplicador: k = 1/(1−{mpc:.2f}) = **{multiplicador:.2f}×**. "
        f"Produto de equilíbrio: Y* = {numerador:.1f} × {multiplicador:.2f} = **{Y_eq:.1f}**."
    )

    if abs(hiato) < 5:
        cor_hiato = ""
        narrativa_hiato = (
            f"Y* = {Y_eq:.1f} ≈ Ȳ = {Y_pleno:.1f} (hiato = {hiato:+.1f}, {hiato_pct:+.1f}%). "
            f"Economia próxima ao pleno emprego. Desemprego estimado: {u_eq*100:.1f}% "
            f"(natural: {u_natural*100:.0f}%)."
        )
        politica_rec = "Nenhuma intervenção fiscal urgente necessária."
        cor_politica = "green"
    elif hiato < -5:
        cor_hiato = ""
        G_nec = abs(hiato) / mult_G
        T_nec = abs(hiato) / abs(mult_T)
        narrativa_hiato = (
            f"**Recessão:** Y* = {Y_eq:.1f} está **{abs(hiato):.1f} abaixo** de Ȳ = {Y_pleno:.1f} "
            f"({hiato_pct:.1f}%). Desemprego estimado: **{u_eq*100:.1f}%** "
            f"({(u_eq-u_natural)*100:.1f}pp acima do natural). "
            f"Salários rígidos para baixo — ajuste automático não ocorre."
        )
        politica_rec = (
            f"Para fechar o hiato de {abs(hiato):.1f}: "
            f"**ΔG ≈ +{G_nec:.1f}** (mult. = {mult_G:.2f}×) "
            f"OU **ΔT ≈ −{T_nec:.1f}** (mult. = {abs(mult_T):.2f}×). "
            f"Aumento de G é mais eficaz que corte de T."
        )
        cor_politica = "red"
    else:
        cor_hiato = ""
        G_corte = hiato / mult_G
        narrativa_hiato = (
            f"**Superaquecimento:** Y* = {Y_eq:.1f} supera Ȳ = {Y_pleno:.1f} em +{hiato:.1f} "
            f"({hiato_pct:+.1f}%). Pressões inflacionárias. "
            f"Desemprego ({u_eq*100:.1f}%) abaixo do natural — risco de espiral salário-preço."
        )
        politica_rec = (
            f"Contração fiscal recomendada: **ΔG ≈ −{G_corte:.1f}** "
            f"ou aumento equivalente de impostos."
        )
        cor_politica = "orange"

    _card(" 1. Composição da Demanda Agregada",   narrativa_demanda,      "blue")
    _card(" 2. Multiplicador Keynesiano e Equilíbrio", narrativa_multiplicador, "purple")
    _card(f"{cor_hiato} 3. Hiato do Produto e Desemprego", narrativa_hiato,  "green"if abs(hiato) < 5 else "red"if hiato < -5 else "orange")
    _card(" 4. Recomendação de Política Econômica",
          f"{politica_rec}<br><br>"
          f"Multiplicadores: ΔG → <b>{mult_G:.2f}×</b> | "
          f"ΔT → <b>{mult_T:.2f}×</b> | ΔTR → <b>{mult_TR:.2f}×</b>",
          cor_politica)

    # ══════════════════════════════════════════════════════════════
    # ABAS ANALÍTICAS
    # ══════════════════════════════════════════════════════════════
    st.divider()
    st.subheader("Aprofundamento Teórico")
    aba1, aba2, aba3 = st.tabs([
        "Cruz Keynesiana",
        "Multiplicador",
        "Rigidez de Preços",
    ])

    with aba1:
        st.latex(r"Y^* = \frac{C_0 + I_0 - b \cdot r + G - c(T - TR)}{1 - c}")
        st.latex(
            rf"Y^* = \frac{{{C0:.1f} + {I_eq:.1f} + {G:.1f} - {mpc:.2f} \times {T-TR:.1f}}}"
            rf"{{1 - {mpc:.2f}}} = {Y_eq:.1f}"
        )

    with aba2:
        st.latex(r"k = \frac{1}{1-c} = \frac{1}{1-" + f"{mpc:.2f}" + r"} = " + f"{multiplicador:.4f}")
        st.markdown(f"""
**Rodadas do multiplicador (ΔG = 100):**

| Rodada | ΔRenda | Consumo Induzido | Acumulado |
|---|---|---|---|
| 1 | 100.00 | {mpc*100:.2f} | 100.00 |
| 2 | {mpc*100:.2f} | {mpc**2*100:.2f} | {100+mpc*100:.2f} |
| 3 | {mpc**2*100:.2f} | {mpc**3*100:.2f} | {100+mpc*100+mpc**2*100:.2f} |
| ∞ | ... | ... | **{multiplicador*100:.1f}** |
""")

    with aba3:
        st.markdown("""
**Por que preços e salários são rígidos para baixo?**

1. **Contratos de trabalho:** salários são fixados por períodos de 1-3 anos.
2. **Menu costs:** custos de alterar preços (cardápios, catálogos, sistemas).
3. **Salário-eficiência:** cortar salários reduz produtividade — firmas resistem.
4. **Ilusão monetária:** trabalhadores resistem a cortes nominais mesmo com deflação.
5. **Poder de barganha sindical:** pisos salariais institucionalizados.

>  Consequência: quando a demanda cai, a economia não volta automaticamente ao
> pleno emprego — fica presa num equilíbrio com desemprego involuntário.
""")