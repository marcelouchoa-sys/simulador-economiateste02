# ui/funcoes/producao_ui.py
"""
Aba Produção — extraída de pages/1__Funcoes.py
Expõe render() para ser chamada pela página principal.
"""

import numpy as np
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from models.funcoes.producao import (
    resolver_producao,
    produtividade_marginal_capital,
    produtividade_marginal_trabalho,
)

K_GRID = np.linspace(10, 3000, 300)


def render() -> None:
    st.subheader("Função de Produção — Cobb-Douglas")
    st.markdown(
        "A função de produção Cobb-Douglas relaciona os **fatores de produção** "
        "(capital $K$ e trabalho $L$) ao produto $Y$, via tecnologia $A$."
    )

    col_eq1, col_eq2 = st.columns(2)
    with col_eq1:
        st.latex(r"Y = A \cdot K^\alpha \cdot L^{1-\alpha}")
    with col_eq2:
        st.latex(r"PMgK = \alpha A \left(\frac{L}{K}\right)^{1-\alpha} \qquad PMgL = (1-\alpha) A \left(\frac{K}{L}\right)^{\alpha}")

    st.divider()

    # ══════════════════════════════════════════════════════════════
    # CONTROLES
    # ══════════════════════════════════════════════════════════════
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Parâmetros")

        A     = st.slider("A — Produtividade Total dos Fatores", 0.5, 3.0, 1.0, 0.1,
                          help="Tecnologia ou eficiência — desloca toda a função para cima")
        alpha = st.slider("α — Participação do Capital", 0.1, 0.9, 0.33, 0.01,
                          help="α = participação do capital na renda. Padrão empírico ≈ 0.33")
        L     = st.slider("L — Trabalho", 10.0, 1000.0, 300.0, 10.0,
                          help="Quantidade de trabalho empregada")
        K_ref = st.slider("K — Capital de Referência", 10.0, 3000.0, 1000.0, 50.0,
                          help="Ponto específico para calcular produtividades marginais")

        st.markdown("**Escola Econômica**")
        escola = st.radio("Visão:", ["Keynesiana", "Clássica"], horizontal=True,
                          help="Clássica: pleno emprego. Keynesiana: L pode ser subempregado.")

        st.divider()
        st.markdown("**Comparação de Cenários**")
        dA  = st.slider("ΔA (choque tecnológico)", -0.5, 1.0, 0.2, 0.1)
        dL  = st.slider("ΔL (choque de trabalho)", -100.0, 200.0, 50.0, 10.0)

        # Cálculos no ponto de referência
        Y_ref,  _  = resolver_producao(np.array([K_ref]), L, A,      alpha, escola)
        Y_choque,_ = resolver_producao(np.array([K_ref]), L + dL, A + dA, alpha, escola)
        PMgK_val   = produtividade_marginal_capital(K_ref, L, A, alpha)
        PMgL_val   = produtividade_marginal_trabalho(K_ref, L, A, alpha)

        st.divider()
        st.subheader("Indicadores (K = K_ref)")
        st.metric("Y base",   f"{Y_ref[0]:.1f}")
        st.metric("Y choque", f"{Y_choque[0]:.1f}",
                  delta=f"{Y_choque[0]-Y_ref[0]:+.1f}")
        st.metric("PMgK", f"{PMgK_val:.4f}",
                  help="Taxa de retorno do capital (= taxa de juros real no equilíbrio clássico)")
        st.metric("PMgL", f"{PMgL_val:.4f}",
                  help="Salário real de equilíbrio (= w/P no equilíbrio clássico)")

    with col2:
        Y_base,   eq_b = resolver_producao(K_GRID, L,      A,      alpha, escola)
        Y_chq,    eq_c = resolver_producao(K_GRID, L + dL, A + dA, alpha, escola)

        # ── Gráfico principal ─────────────────────────────────────
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=(
                f"Função de Produção ({escola})",
                "Produtividades Marginais vs K",
            ),
        )

        # Subplot 1 — Produção vs K
        fig.add_trace(go.Scatter(
            x=K_GRID, y=Y_base, name="Y base",
            line=dict(color="#1565c0", width=3),
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=K_GRID, y=Y_chq, name=f"Y choque (ΔA={dA:+.1f}, ΔL={dL:+.0f})",
            line=dict(color="#c62828", width=2.5, dash="dash"),
        ), row=1, col=1)
        # Ponto de referência
        fig.add_trace(go.Scatter(
            x=[K_ref], y=[Y_ref[0]], mode="markers+text",
            name="K ref.", marker=dict(size=12, color="#FF9800", symbol="star"),
            text=[f"Y={Y_ref[0]:.0f}"], textposition="top right",
        ), row=1, col=1)
        # Tracejados
        fig.add_trace(go.Scatter(
            x=[0, K_ref], y=[Y_ref[0], Y_ref[0]], mode="lines",
            showlegend=False, line=dict(color="#FF9800", dash="dot", width=1.2),
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=[K_ref, K_ref], y=[0, Y_ref[0]], mode="lines",
            showlegend=False, line=dict(color="#FF9800", dash="dot", width=1.2),
        ), row=1, col=1)

        # Subplot 2 — PMgK e PMgL vs K
        PMgK_grid = np.array([produtividade_marginal_capital(k, L, A, alpha) for k in K_GRID])
        PMgL_grid = np.array([produtividade_marginal_trabalho(k, L, A, alpha) for k in K_GRID])

        fig.add_trace(go.Scatter(
            x=K_GRID, y=PMgK_grid, name="PMgK",
            line=dict(color="#2e7d32", width=2.5),
        ), row=1, col=2)
        fig.add_trace(go.Scatter(
            x=K_GRID, y=PMgL_grid, name="PMgL",
            line=dict(color="#7B1FA2", width=2.5, dash="dash"),
        ), row=1, col=2)
        fig.add_vline(x=K_ref, line=dict(color="#FF9800", dash="dot", width=1.5),
                      annotation_text=f"K={K_ref:.0f}", row=1, col=2)

        fig.update_xaxes(title_text="Capital (K)", showgrid=True, range=[0, 3000], row=1, col=1)
        fig.update_yaxes(title_text="Produto (Y)", showgrid=True, row=1, col=1)
        fig.update_xaxes(title_text="Capital (K)", showgrid=True, range=[0, 3000], row=1, col=2)
        fig.update_yaxes(title_text="Produtividade Marginal", showgrid=True, row=1, col=2)

        fig.update_layout(height=450, template="plotly_white",
                          legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"))
        st.plotly_chart(fig, use_container_width=True)

        # ── Gráfico: isoquantas ───────────────────────────────────
        st.subheader("Isoquantas — Combinações K-L que geram o mesmo Y")
        fig2 = go.Figure()
        Y_levels = [Y_ref[0] * f for f in [0.5, 0.75, 1.0, 1.25, 1.5]]
        cores_iso = ["#bbdefb", "#64b5f6", "#1565c0", "#0d47a1", "#0a2472"]
        L_range = np.linspace(10, 800, 300)

        for Y_iso, cor in zip(Y_levels, cores_iso):
            # Y = A * K^alpha * L^(1-alpha) → K = (Y / (A * L^(1-alpha)))^(1/alpha)
            K_iso = (Y_iso / (A * L_range ** (1 - alpha))) ** (1 / alpha)
            mask  = (K_iso > 0) & (K_iso < 3000)
            fig2.add_trace(go.Scatter(
                x=L_range[mask], y=K_iso[mask],
                name=f"Y = {Y_iso:.0f}",
                line=dict(color=cor, width=2),
            ))

        fig2.add_trace(go.Scatter(
            x=[L], y=[K_ref], mode="markers",
            name="Ponto atual", marker=dict(size=12, color="#FF9800", symbol="star"),
        ))
        fig2.update_layout(height=280, template="plotly_white",
                           xaxis_title="Trabalho (L)", yaxis_title="Capital (K)",
                           title="Isoquantas: mesma produção com diferentes combinações K-L",
                           xaxis=dict(range=[0, 800]), yaxis=dict(range=[0, 3000]))
        st.plotly_chart(fig2, use_container_width=True)

    # ══════════════════════════════════════════════════════════════
    # ABAS ANALÍTICAS
    # ══════════════════════════════════════════════════════════════
    st.divider()
    st.subheader("Decomposição Analítica")

    aba1, aba2, aba3, aba4 = st.tabs([
        "Cobb-Douglas",
        "Rendimentos Marginais",
        "Keynesiana vs Clássica",
        "Teoria Completa",
    ])

    with aba1:
        st.markdown("**Equação com os parâmetros atuais:**")
        st.latex(
            rf"Y = {A:.1f} \cdot K^{{{alpha:.2f}}} \cdot {L:.0f}^{{{1-alpha:.2f}}}"
        )
        st.latex(
            rf"Y(K={K_ref:.0f}) = {A:.1f} \times {K_ref:.0f}^{{{alpha:.2f}}} \times {L:.0f}^{{{1-alpha:.2f}}} = {Y_ref[0]:.1f}"
        )
        st.markdown(f"""
**Propriedades da Cobb-Douglas:**

- **Retornos constantes de escala:** se K e L dobram, Y dobra exatamente.
  $(\\lambda K)^\\alpha (\\lambda L)^{{1-\\alpha}} = \\lambda^{{\\alpha+1-\\alpha}} Y = \\lambda Y$
- **Participações constantes na renda:**
  - Capital recebe fração $\\alpha = {alpha:.2f}$ da renda total
  - Trabalho recebe fração $1-\\alpha = {1-alpha:.2f}$ da renda total
- **PMg decrescentes:** cada unidade adicional de K ou L contribui menos

**Calibração empírica:** $\\alpha \\approx 0.33$ para a maioria dos países desenvolvidos
(participação do capital na renda nacional ≈ 1/3).
""")

    with aba2:
        st.markdown("**Produtividades Marginais no ponto de referência:**")
        st.latex(
            rf"PMgK = \alpha \cdot A \cdot \left(\frac{{L}}{{K}}\right)^{{1-\alpha}} = "
            rf"{alpha:.2f} \times {A:.1f} \times \left(\frac{{{L:.0f}}}{{{K_ref:.0f}}}\right)^{{{1-alpha:.2f}}} = {PMgK_val:.4f}"
        )
        st.latex(
            rf"PMgL = (1-\alpha) \cdot A \cdot \left(\frac{{K}}{{L}}\right)^{{\alpha}} = "
            rf"{1-alpha:.2f} \times {A:.1f} \times \left(\frac{{{K_ref:.0f}}}{{{L:.0f}}}\right)^{{{alpha:.2f}}} = {PMgL_val:.4f}"
        )
        st.markdown(f"""
**Interpretação econômica:**

- **PMgK = {PMgK_val:.4f}**: cada unidade adicional de capital aumenta o produto em {PMgK_val:.4f}.
  No equilíbrio clássico, PMgK = taxa de juros real $r$ → firmas investem até PMgK = r.
- **PMgL = {PMgL_val:.4f}**: cada trabalhador adicional aumenta o produto em {PMgL_val:.4f}.
  No equilíbrio clássico, PMgL = salário real $w/P$ → firmas contratam até PMgL = w/P.

**Lei dos rendimentos decrescentes:**
- PMgK **decresce** conforme K aumenta (mais máquinas com mesmo número de trabalhadores)
- PMgL **decresce** conforme L aumenta (mais trabalhadores com mesmo capital)
""")

    with aba3:
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"""
** Visão Keynesiana**

- O trabalho empregado $L$ pode estar **abaixo do pleno emprego**.
- O produto pode ficar aquém do potencial $Y_n$ por falta de demanda.
- A função de produção dá o **máximo técnico possível** —
  mas a demanda efetiva pode impedir que esse máximo seja atingido.
- PMgL não determina salários diretamente — salários são determinados
  por contratos e poder de barganha.

**Com $L = {L:.0f}$:**
$Y = {Y_ref[0]:.1f}$ (pode estar abaixo do potencial)
""")
        with col_b:
            st.markdown(f"""
** Visão Clássica**

- $L$ está sempre no **pleno emprego** — o mercado se equilibra via salários.
- PMgL = $w/P$ determina o emprego de equilíbrio.
- PMgK = $r$ determina o investimento de equilíbrio.
- O produto é sempre igual ao potencial: $Y = Y_n$.
- Política de demanda não afeta Y no longo prazo.

**Com $L = {L:.0f}$ (pleno emprego):**
$Y_n = {Y_ref[0]:.1f}$ — produto potencial determinado pelos fatores.
""")

    with aba4:
        st.markdown("### Teoria Completa da Função de Produção")
        st.markdown("#### 1. Por que Cobb-Douglas?")
        st.markdown("""
A função Cobb-Douglas ($Y = AK^\\alpha L^{1-\\alpha}$) é a especificação mais usada
na macroeconomia porque:
1. **Calibra bem os dados**: participações de K e L na renda são relativamente
   estáveis entre países e ao longo do tempo (fato estilizado de Kaldor).
2. **Propriedades matemáticas convenientes**: derivada simples, retornos constantes
   de escala, PMg sempre positiva e decrescente.
3. **Decomposição da Produtividade Total dos Fatores (PTF)**:
""")
        st.latex(r"A = \frac{Y}{K^\alpha L^{1-\alpha}} \quad \text{(Resíduo de Solow)}")
        st.markdown("""
O parâmetro $A$ captura tudo que não é K nem L: tecnologia, qualidade institucional,
capital humano, eficiência organizacional.
""")
        st.markdown("#### 2. Crescimento Econômico")
        st.latex(r"\frac{\dot{Y}}{Y} = \frac{\dot{A}}{A} + \alpha \frac{\dot{K}}{K} + (1-\alpha)\frac{\dot{L}}{L}")
        st.markdown(f"""
Com $\\alpha = {alpha:.2f}$, um crescimento de 1% no capital gera apenas
**{alpha:.0%}** de crescimento no produto — daí a importância do crescimento da PTF ($A$)
para o desenvolvimento de longo prazo (Solow, 1956).
""")
        st.markdown("#### 3.  Resumo das Equações")
        st.latex(r"Y = A \cdot K^\alpha \cdot L^{1-\alpha}")
        st.latex(r"PMgK = \frac{\partial Y}{\partial K} = \alpha A \left(\frac{L}{K}\right)^{1-\alpha}")
        st.latex(r"PMgL = \frac{\partial Y}{\partial L} = (1-\alpha) A \left(\frac{K}{L}\right)^{\alpha}")
        st.latex(r"\text{Equilíbrio Clássico: } PMgK = r \quad PMgL = w/P")
        st.caption("Valores calculados dinamicamente com os parâmetros dos sliders.")
