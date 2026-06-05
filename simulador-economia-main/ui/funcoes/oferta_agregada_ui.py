# ui/funcoes/oferta_agregada_ui.py
"""
Aba Oferta Agregada — extraída de pages/1__Funcoes.py
Expõe render() para ser chamada pela página principal.
"""

import numpy as np
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from models.funcoes.oferta_agregada import resolver_oa_curto, resolver_oa_longo, hiato_produto

Y_GRID = np.linspace(200, 2500, 300)
P_GRID = np.linspace(0.2, 3.5, 300)


def render() -> None:
    st.subheader("Oferta Agregada — Curto e Longo Prazo")
    st.markdown(
        "A Oferta Agregada mostra a relação entre o nível de preços $P$ e o produto $Y$ "
        "que as firmas estão dispostas a ofertar. "
        "No **curto prazo** (salários rígidos), ela é positivamente inclinada. "
        "No **longo prazo** (pleno emprego), ela é vertical."
    )

    col_eq1, col_eq2 = st.columns(2)
    with col_eq1:
        st.latex(r"P = P^e + \frac{1}{\alpha}(Y - Y_n) \quad \text{(OA Curto Prazo)}")
    with col_eq2:
        st.latex(r"Y = Y_n \quad \text{(OA Longo Prazo — vertical)}")

    st.divider()

    # ══════════════════════════════════════════════════════════════
    # CONTROLES
    # ══════════════════════════════════════════════════════════════
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Parâmetros")

        Pe    = st.slider("Expectativa de Preços (Pᵉ)", 0.5, 3.0, 1.0, 0.1,
                          help="Nível de preços esperado pelos trabalhadores ao negociar salários")
        Yn    = st.slider("Produto Potencial (Yₙ)", 500.0, 2000.0, 1200.0, 50.0,
                          help="Produto de pleno emprego — posição da OA de longo prazo")
        alpha = st.slider("α — Sensibilidade da OA", 10.0, 500.0, 100.0, 10.0,
                          help="Quanto Y precisa variar para mover P em 1 unidade. α grande → OA mais plana")

        st.divider()
        st.markdown("**Choque de Oferta**")
        dPe   = st.slider("ΔPᵉ (choque de expectativas)", -0.5, 1.0, 0.0, 0.1,
                          help="Choque de expectativas inflacionárias")
        dYn   = st.slider("ΔYₙ (choque de produtividade)", -200.0, 200.0, 0.0, 20.0,
                          help="Mudança no produto potencial via tecnologia ou capital")

        st.divider()
        st.markdown("**Produto Atual**")
        Y_atual = st.slider("Y atual", 500.0, 2000.0, 1100.0, 50.0)

        # Cálculos
        P_oa_base,   _ = resolver_oa_curto(np.array([Y_atual]), Pe,      Yn,       alpha)
        P_oa_choque, _ = resolver_oa_curto(np.array([Y_atual]), Pe+dPe,  Yn+dYn,   alpha)
        hiato_base     = hiato_produto(Y_atual, Yn)
        hiato_choque   = hiato_produto(Y_atual, Yn + dYn)

        st.divider()
        st.subheader("Indicadores")
        st.metric("Hiato do Produto (Y−Yₙ)", f"{hiato_base:+.0f}",
                  delta="Inflacionário"if hiato_base > 0 else "Recessivo",
                  delta_color="inverse"if hiato_base > 0 else "normal")
        st.metric("P na OA base (Y atual)",   f"{P_oa_base[0]:.3f}")
        st.metric("P na OA choque",           f"{P_oa_choque[0]:.3f}",
                  delta=f"{P_oa_choque[0]-P_oa_base[0]:+.3f}")

    with col2:
        # Curvas
        P_base,   _ = resolver_oa_curto(Y_GRID, Pe,       Yn,       alpha)
        P_choque, _ = resolver_oa_curto(Y_GRID, Pe + dPe, Yn + dYn, alpha)

        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=(
                "OA Curto Prazo vs Longo Prazo",
                "Efeito de Choques de Oferta",
            ),
        )

        # Subplot 1 — base + longo prazo
        fig.add_trace(go.Scatter(
            x=Y_GRID, y=P_base, name="OA Curto Prazo",
            line=dict(color="#1565c0", width=3),
        ), row=1, col=1)
        # OA Longo Prazo (linha vertical)
        fig.add_vline(x=Yn, line=dict(color="#2e7d32", width=2.5, dash="dash"),
                      annotation_text=f"OA LP: Yₙ={Yn:.0f}",
                      annotation_position="top", row=1, col=1)
        # Ponto atual
        fig.add_trace(go.Scatter(
            x=[Y_atual], y=[P_oa_base[0]],
            mode="markers+text", name="Situação atual",
            marker=dict(size=13, color="#FF9800", symbol="star"),
            text=[f"Y={Y_atual:.0f}<br> P={P_oa_base[0]:.2f}"],
            textposition="top right",
        ), row=1, col=1)
        # Linha Pe
        fig.add_hline(y=Pe, line=dict(color="#7B1FA2", dash="dot", width=1.5),
                      annotation_text=f"Pᵉ={Pe:.1f}", row=1, col=1)

        # Subplot 2 — base vs choque
        fig.add_trace(go.Scatter(
            x=Y_GRID, y=P_base, name="OA Base",
            line=dict(color="#1565c0", width=3),
        ), row=1, col=2)
        fig.add_trace(go.Scatter(
            x=Y_GRID, y=P_choque, name="OA Choque",
            line=dict(color="#c62828", width=3, dash="dash"),
        ), row=1, col=2)
        fig.add_vline(x=Yn,       line=dict(color="#2e7d32", width=1.5, dash="dash"),
                      annotation_text=f"Yₙ={Yn:.0f}", row=1, col=2)
        fig.add_vline(x=Yn+dYn,   line=dict(color="#c62828", width=1.5, dash="dash"),
                      annotation_text=f"Yₙ'={Yn+dYn:.0f}", row=1, col=2)

        # Seta de deslocamento
        P_mid = (P_base[len(P_base)//2] + P_choque[len(P_choque)//2]) / 2
        if abs(dPe) > 0 or abs(dYn) > 0:
            fig.add_annotation(
                x=Y_GRID[len(Y_GRID)//2], y=P_choque[len(P_choque)//2],
                ax=Y_GRID[len(Y_GRID)//2], ay=P_base[len(P_base)//2],
                xref="x2", yref="y2", axref="x2", ayref="y2",
                showarrow=True, arrowhead=3, arrowwidth=2,
                arrowcolor="#c62828",
            )

        for col in [1, 2]:
            fig.update_xaxes(title_text="Produto (Y)", showgrid=True,
                             range=[200, 2500], row=1, col=col)
            fig.update_yaxes(title_text="Nível de Preços (P)", showgrid=True,
                             range=[0.2, 3.5], row=1, col=col)

        fig.update_layout(height=450, template="plotly_white",
                          legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"))
        st.plotly_chart(fig, use_container_width=True)

        # ── Gráfico: α e inclinação da OA ────────────────────────
        st.subheader("Sensibilidade α e Inclinação da OA")
        alpha_range = np.linspace(10, 500, 200)
        inclinacao  = 1 / alpha_range  # dP/dY = 1/alpha

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=alpha_range, y=inclinacao,
                                  line=dict(color="#1565c0", width=3), name="dP/dY = 1/α"))
        fig2.add_vline(x=alpha, line=dict(color="#FF9800", dash="dash", width=2),
                       annotation_text=f"α atual={alpha:.0f}")
        fig2.update_layout(height=250, template="plotly_white",
                           xaxis_title="α (sensibilidade)",
                           yaxis_title="Inclinação da OA (dP/dY)",
                           title="α grande → OA mais plana → mais próxima do keynesiano")
        st.plotly_chart(fig2, use_container_width=True)

    # ══════════════════════════════════════════════════════════════
    # ABAS ANALÍTICAS
    # ══════════════════════════════════════════════════════════════
    st.divider()
    st.subheader("Decomposição Analítica")

    aba1, aba2, aba3 = st.tabs([
        "Curto vs Longo Prazo",
        "Choques de Oferta",
        "Teoria Completa",
    ])

    with aba1:
        st.markdown("**OA de Curto Prazo:**")
        st.latex(rf"P = {Pe:.2f} + \frac{{Y - {Yn:.0f}}}{{{alpha:.0f}}}")
        st.markdown(f"""
**Interpretação:**
- $P^e = {Pe:.2f}$: preço esperado ao negociar contratos salariais.
- $Y_n = {Yn:.0f}$: produto potencial (pleno emprego).
- $\\alpha = {alpha:.0f}$: quanto Y precisa desviar de Yₙ para mover P em 1 unidade.

**Por que a OA CP tem inclinação positiva?**
Quando $P > P^e$: firmas percebem que seus preços subiram mais do que os custos
(salários fixos em contrato) → lucro marginal aumenta → produzem mais.
É o mecanismo de **surpresa de preços** (Lucas).

**Situação atual:**
- Hiato = $Y - Y_n = {Y_atual:.0f} - {Yn:.0f}$ = **{hiato_base:+.0f}**
- P na OA = $P^e + hiato/\\alpha = {Pe:.2f} + {hiato_base/alpha:.3f}$ = **{P_oa_base[0]:.3f}**
- {"Economia **acima do potencial** → pressão inflacionária"if hiato_base > 0 else "Economia **abaixo do potencial** → pressão deflacionária"if hiato_base < 0 else "Economia **no potencial**"}
""")
        st.markdown("**OA de Longo Prazo:**")
        st.latex(rf"Y = Y_n = {Yn:.0f}")
        st.markdown("""
No longo prazo, expectativas se ajustam ($P^e = P$) e salários se flexibilizam.
O produto retorna ao potencial independente do nível de preços.
A OA LP é **vertical** — política de demanda não afeta Y no longo prazo.
""")

    with aba2:
        st.markdown(f"""
**Tipos de Choques de Oferta:**

| Choque | Efeito na OA | Exemplo |
|---|---|---|
| ↑ Pᵉ (expectativas inflacionárias) | Desloca para **cima/esquerda** | Sindicatos pedem reajustes maiores |
| ↓ Pᵉ (ancoragem) | Desloca para **baixo/direita** | Credibilidade do BC |
| ↑ Yₙ (produtividade) | Desloca LP para **direita** | Inovação tecnológica, capital humano |
| ↓ Yₙ (destruição de capital) | Desloca LP para **esquerda** | Guerra, desastre natural |
| ↑ Custo de insumos | Desloca CP para **cima/esquerda** | Choque do petróleo |

**Com os choques atuais:**
- ΔPᵉ = {dPe:+.1f}: OA desloca {"para cima (inflação maior)"if dPe > 0 else "para baixo (desinflação)"if dPe < 0 else "sem efeito"}
- ΔYₙ = {dYn:+.0f}: produto potencial {"aumenta"if dYn > 0 else "cai"if dYn < 0 else "inalterado"}
- Efeito em P (em Y={Y_atual:.0f}): {P_oa_base[0]:.3f} → **{P_oa_choque[0]:.3f}** (Δ = {P_oa_choque[0]-P_oa_base[0]:+.3f})

>  **Estagflação**: choque negativo de oferta (OA sobe) com DA inalterada →
> P↑ e Y↓ simultaneamente — o pior dos mundos para a política econômica.
""")

    with aba3:
        st.markdown("### Teoria Completa da Oferta Agregada")
        st.markdown("#### 1. Por que existem duas OAs?")
        st.markdown("""
**A distinção curto/longo prazo** é central na macroeconomia moderna:

- **Curto prazo**: salários e preços são **rígidos** (contratos, menu costs).
  Firmas respondem a variações de demanda ajustando **quantidade** mais que preços.
- **Longo prazo**: todos os preços se ajustam. A economia converge para $Y_n$.

A velocidade de convergência depende da **credibilidade do BC**, da
**flexibilidade do mercado de trabalho** e das **expectativas** dos agentes.
""")
        st.markdown("#### 2. A Curva de Phillips e a OA")
        st.latex(r"\pi = \pi^e + \frac{1}{\alpha}(Y - Y_n)")
        st.markdown("""
A OA de curto prazo é equivalente à **Curva de Phillips aumentada por expectativas**:
inflação acima da esperada quando Y > Yₙ (hiato positivo).
""")
        st.markdown("#### 3.  Resumo das Equações")
        st.latex(r"P = P^e + \frac{1}{\alpha}(Y - Y_n) \quad \text{(OA CP)}")
        st.latex(r"Y = Y_n \quad \text{(OA LP)}")
        st.latex(r"\text{Hiato} = Y - Y_n \quad \Rightarrow \quad P = P^e + \frac{\text{Hiato}}{\alpha}")
        st.caption("Valores calculados dinamicamente com os parâmetros dos sliders.")

    from ui.auth_ui import botao_salvar
    botao_salvar(
        modulo="Funcoes — Oferta Agregada",
        parametros={"Pe": Pe, "Yn": Yn, "alpha": alpha, "Y_atual": Y_atual},
        resultado={"hiato": float(hiato_base), "P_oa": float(P_oa_base[0])},
    )
