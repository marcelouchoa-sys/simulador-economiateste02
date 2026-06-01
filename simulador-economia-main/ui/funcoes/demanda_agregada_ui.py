# ui/funcoes/demanda_agregada_ui.py
"""
Aba Demanda Agregada — extraída de pages/1__Funcoes.py
Expõe render() para ser chamada pela página principal.
"""

import numpy as np
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from models.funcoes.demanda_agregada import resolver_da

P_GRID = np.linspace(0.2, 3.5, 300)


def render() -> None:
    st.subheader("Demanda Agregada — O Locus IS-LM")
    st.markdown(
        "A curva DA é derivada analiticamente do modelo IS-LM. "
        "Para cada nível de preços $P$, ela mostra o produto $Y$ que equilibra "
        "simultaneamente os mercados de **bens** e **moeda**."
    )

    col_eq1, _ = st.columns([3, 1])
    with col_eq1:
        st.latex(
            r"Y^{DA} = \frac{\text{mult} \cdot A + \text{mult} \cdot b \cdot M/(h \cdot P)}"
            r"{1 + \text{mult} \cdot b \cdot k/h}"
            r"\qquad \text{mult} = \frac{1}{1-c_1},\; A = c_0 - c_1 T + I_0 + G"
        )

    st.divider()

    # ══════════════════════════════════════════════════════════════
    # CONTROLES
    # ══════════════════════════════════════════════════════════════
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Parâmetros")

        st.markdown("**Demanda Privada**")
        c0 = st.slider("c₀ — Consumo Autônomo",    50.0,  300.0, 100.0, 10.0)
        c1 = st.slider("c₁ — Propensão a Consumir", 0.5,   0.95,  0.75,  0.01)
        I0 = st.slider("I₀ — Invest. Autônomo",    50.0,  400.0, 200.0, 10.0)
        b  = st.slider("b — Sensib. I a r",         10.0, 150.0,  50.0,  5.0)

        st.markdown("**Política Fiscal**")
        G  = st.slider("G — Gastos do Governo",  100.0, 800.0, 300.0, 10.0)
        T  = st.slider("T — Impostos",            50.0, 500.0, 200.0, 10.0)

        st.markdown("**Política Monetária**")
        M  = st.slider("M — Oferta de Moeda",   200.0, 2000.0, 1000.0, 50.0)
        k  = st.slider("k — Sensib. Md a Y",      0.1,   1.0,    0.5,  0.05)
        h  = st.slider("h — Sensib. Md a r",     10.0, 300.0,  100.0, 10.0)

        st.divider()
        st.markdown("**Choque para Comparação**")
        dG = st.slider("ΔG (choque fiscal)",    -200.0, 200.0, 100.0, 10.0)
        dM = st.slider("ΔM (choque monetário)", -500.0, 500.0, 200.0, 50.0)

        # ── Cálculos no nível de preços P=1 ──────────────────────
        mult = 1.0 / max(1 - c1, 1e-9)
        A    = c0 - c1 * T + I0 + G
        denom = 1.0 + mult * b * k / max(h, 1e-9)
        Y_P1  = (mult * A + mult * b * M / (h * 1.0)) / denom
        Y_P1_choque = resolver_da(
            np.array([1.0]), c0, c1, T, I0, b, G + dG, k, h, M + dM
        )[0]

        st.divider()
        st.subheader("Indicadores (P = 1)")
        st.metric("Y* base",   f"{Y_P1:.1f}")
        st.metric("Y* choque", f"{Y_P1_choque:.1f}",
                  delta=f"{Y_P1_choque - Y_P1:+.1f}")
        st.metric("Multiplicador IS-LM", f"{mult/denom:.3f}")

    with col2:
        Y_da_base   = resolver_da(P_GRID, c0, c1, T, I0, b, G,      k, h, M)
        Y_da_choque = resolver_da(P_GRID, c0, c1, T, I0, b, G + dG, k, h, M + dM)

        # ── Gráfico principal ─────────────────────────────────────
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=(
                "Curva DA — Base vs Choque",
                "Decomposição do Deslocamento",
            ),
        )

        # DA base e choque
        fig.add_trace(go.Scatter(
            x=Y_da_base, y=P_GRID, name="DA Base",
            line=dict(color="#1565c0", width=3),
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=Y_da_choque, y=P_GRID, name="DA Choque",
            line=dict(color="#c62828", width=3, dash="dash"),
        ), row=1, col=1)

        # Seta de deslocamento em P=1
        fig.add_annotation(
            x=Y_P1_choque, y=1.0, ax=Y_P1, ay=1.0,
            xref="x", yref="y", axref="x", ayref="y",
            showarrow=True, arrowhead=3, arrowwidth=2.5,
            arrowcolor="#FF9800", arrowsize=1.2,
        )
        fig.add_annotation(
            x=(Y_P1 + Y_P1_choque) / 2, y=1.05,
            text=f"ΔY = {Y_P1_choque - Y_P1:+.0f}",
            showarrow=False, font=dict(size=12, color="#FF9800"),
            row=1, col=1,
        )

        # Subplot 2 — decomposição por fonte do choque
        Y_so_fiscal  = resolver_da(P_GRID, c0, c1, T, I0, b, G + dG, k, h, M)
        Y_so_monet   = resolver_da(P_GRID, c0, c1, T, I0, b, G,      k, h, M + dM)

        fig.add_trace(go.Scatter(
            x=Y_da_base, y=P_GRID, name="Base",
            line=dict(color="#1565c0", width=2),
        ), row=1, col=2)
        fig.add_trace(go.Scatter(
            x=Y_so_fiscal, y=P_GRID, name=f"Só ΔG={dG:+.0f}",
            line=dict(color="#2e7d32", width=2, dash="dot"),
        ), row=1, col=2)
        fig.add_trace(go.Scatter(
            x=Y_so_monet, y=P_GRID, name=f"Só ΔM={dM:+.0f}",
            line=dict(color="#7B1FA2", width=2, dash="dot"),
        ), row=1, col=2)
        fig.add_trace(go.Scatter(
            x=Y_da_choque, y=P_GRID, name="ΔG + ΔM",
            line=dict(color="#c62828", width=2, dash="dash"),
        ), row=1, col=2)

        Y_max = max(Y_da_choque.max(), Y_da_base.max()) * 1.1
        for col in [1, 2]:
            fig.update_xaxes(title_text="Produto (Y)", showgrid=True,
                             range=[0, Y_max], row=1, col=col)
            fig.update_yaxes(title_text="Nível de Preços (P)", showgrid=True,
                             range=[0.2, 3.5], row=1, col=col)

        fig.update_layout(height=450, template="plotly_white",
                          legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"))
        st.plotly_chart(fig, use_container_width=True)

        # ── Gráfico: sensibilidade do multiplicador ───────────────
        st.subheader("Multiplicador IS-LM vs Multiplicador Keynesiano Simples")
        c1_range = np.linspace(0.5, 0.95, 200)
        mult_simples = 1 / (1 - c1_range)
        mult_islm    = mult_simples / (1 + mult_simples * b * k / h)

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=c1_range, y=mult_simples, name="Mult. Keynesiano simples",
                                  line=dict(color="#c62828", width=2.5, dash="dash")))
        fig2.add_trace(go.Scatter(x=c1_range, y=mult_islm, name="Mult. IS-LM (com efeito monetário)",
                                  line=dict(color="#1565c0", width=2.5)))
        fig2.add_vline(x=c1, line=dict(color="#FF9800", dash="dot", width=2),
                       annotation_text=f"c₁={c1:.2f}")
        fig2.update_layout(height=260, template="plotly_white",
                           xaxis_title="Propensão a Consumir (c₁)",
                           yaxis_title="Multiplicador",
                           title="O efeito monetário reduz o multiplicador keynesiano")
        st.plotly_chart(fig2, use_container_width=True)

    # ══════════════════════════════════════════════════════════════
    # ABAS ANALÍTICAS
    # ══════════════════════════════════════════════════════════════
    st.divider()
    st.subheader("Decomposição Analítica")

    aba1, aba2, aba3 = st.tabs([
        "Derivação da DA",
        "Deslocadores da DA",
        "Teoria Completa",
    ])

    with aba1:
        st.markdown("**Derivação analítica do sistema IS-LM:**")
        st.markdown("**IS:** equilíbrio no mercado de bens")
        st.latex(r"Y = \frac{1}{1-c_1}(c_0 - c_1 T + I_0 + G) - \frac{b}{1-c_1} r")
        st.markdown("**LM:** equilíbrio no mercado monetário")
        st.latex(r"r = \frac{kY - M/P}{h}")
        st.markdown("**Substituindo LM na IS:**")
        st.latex(
            r"Y^{DA} = \frac{\text{mult} \cdot A + \text{mult} \cdot b \cdot M/(hP)}"
            r"{1 + \text{mult} \cdot b \cdot k/h}"
        )
        st.markdown(f"""
**Com os parâmetros atuais (P = 1):**
- Multiplicador simples: mult = $1/(1-{c1:.2f})$ = **{mult:.3f}**
- $A = {c0:.0f} - {c1:.2f}\\times{T:.0f} + {I0:.0f} + {G:.0f}$ = **{A:.1f}**
- Denominador IS-LM = $1 + {mult:.3f}\\times{b:.0f}\\times{k:.2f}/{h:.0f}$ = **{denom:.3f}**
- **$Y^* = {Y_P1:.1f}$**

>  O denominador IS-LM é sempre **maior que 1** — o multiplicador IS-LM
> é sempre **menor** que o multiplicador keynesiano simples,
> porque o aumento de Y eleva a demanda por moeda e os juros,
> o que reduz o investimento (crowding-out parcial).
""")

    with aba2:
        st.markdown("""
**O que desloca a DA?**

| Variável | Direção | Efeito sobre DA | Mecanismo |
|---|---|---|---|
| ↑ G (fiscal expansionista) | Direita | ↑ Y para todo P | IS desloca direita via mult. |
| ↑ T (fiscal contracionista) | Esquerda | ↓ Y para todo P | Reduz consumo disponível |
| ↑ M (monetária expansionista) | Direita | ↑ Y para todo P | LM desloca direita, r↓, I↑ |
| ↑ c₁ | Direita | ↑ Y para todo P | Mult. maior amplifica tudo |
| ↑ I₀ (animal spirits) | Direita | ↑ Y para todo P | Demanda privada autônoma |
| ↑ P | Movimento ao longo | ↓ Y | M/P↓ → LM sobe → r↑ → I↓ |

>  Variação de **P** é movimento **ao longo** da DA.
> Variação de **G, M, T, c₁, I₀** é **deslocamento** da DA.
""")
        Y_P1_fiscal = resolver_da(np.array([1.0]), c0, c1, T, I0, b, G+dG, k, h, M)[0]
        Y_P1_monet  = resolver_da(np.array([1.0]), c0, c1, T, I0, b, G,    k, h, M+dM)[0]
        st.markdown(f"""
**Com os choques atuais (em P=1):**
- Só ΔG = {dG:+.0f}: ΔY = **{Y_P1_fiscal - Y_P1:+.1f}**
  (multiplicador IS-LM = {(Y_P1_fiscal-Y_P1)/abs(dG) if dG!=0 else 0:.3f}×ΔG)
- Só ΔM = {dM:+.0f}: ΔY = **{Y_P1_monet - Y_P1:+.1f}**
- ΔG + ΔM: ΔY = **{Y_P1_choque - Y_P1:+.1f}**
""")

    with aba3:
        st.markdown("### Teoria Completa da Demanda Agregada")
        st.markdown("""
#### Por que a DA tem inclinação negativa?

Existem três mecanismos que fazem Y cair quando P sobe:

1. **Efeito Keynes (juros):** P↑ → M/P↓ → LM sobe → r↑ → I↓ → Y↓
2. **Efeito Pigou (riqueza real):** P↑ → riqueza real cai → C↓ → Y↓
3. **Efeito Mundell-Fleming (câmbio):** P↑ → exportações menos competitivas → NX↓ → Y↓

O canal dominante no modelo IS-LM é o **Efeito Keynes**.
""")
        st.latex(
            r"\frac{\partial Y}{\partial P} = "
            r"-\frac{\text{mult} \cdot b \cdot M}{h \cdot P^2 \cdot (1 + \text{mult} \cdot b \cdot k/h)}"
            r"< 0"
        )
        st.markdown("####  Resumo das Equações")
        st.latex(
            r"Y^{DA} = \frac{\text{mult} \cdot A + \text{mult} \cdot b \cdot M/(hP)}"
            r"{1 + \text{mult} \cdot b \cdot k/h}"
        )
        st.latex(r"\text{mult} = \frac{1}{1-c_1} \qquad A = c_0 - c_1 T + I_0 + G")
        st.latex(
            r"\frac{\partial Y}{\partial G} = \frac{\text{mult}}{1 + \text{mult} \cdot bk/h}"
            r" < \frac{1}{1-c_1} \quad \text{(mult. IS-LM < mult. keynesiano)}"
        )
        st.caption("Valores calculados dinamicamente com os parâmetros dos sliders.")
