# ui/escolas/classica_ui.py
"""
Escola Clássica — Oferta determina o produto
Expõe render() para ser chamada pela página principal.
"""

import numpy as np
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def render() -> None:
    st.subheader("Escola Clássica — Oferta Determina o Produto")

    with st.expander("Fundamentos da Escola Clássica", expanded=False):
        st.markdown("""
| Princípio | Descrição |
|---|---|
| **Lei de Say** | "A oferta cria sua própria demanda" — produção gera renda que financia o consumo |
| **Preços Flexíveis** | Preços e salários se ajustam livremente, eliminando desequilíbrios |
| **Pleno Emprego** | A economia tende naturalmente ao pleno emprego no longo prazo |
| **Neutralidade da Moeda** | Variações em M afetam apenas P, não o produto real Y |
| **Dicotomia Clássica** | Variáveis reais e nominais são determinadas separadamente |
| **Ajuste Automático** | Não há necessidade de intervenção governamental |
""")

    # ══════════════════════════════════════════════════════════════
    # CONTROLES
    # ══════════════════════════════════════════════════════════════
    st.markdown("### Parâmetros")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Lado da Oferta**")
        produtividade = st.slider("Produtividade Total (A)", 0.5, 2.0, 1.0, 0.05,
                                  key="cl_A")
        tecnologia    = st.slider("Tecnologia (θ)", 0.5, 2.0, 1.0, 0.05,
                                  key="cl_theta")
        trabalho      = st.slider("Força de Trabalho (L̄)", 50.0, 200.0, 100.0, 5.0,
                                  key="cl_L")

    with col2:
        st.markdown("**Lado Monetário**")
        oferta_monetaria = st.slider("Oferta Monetária (M)", 50.0, 300.0, 100.0, 10.0,
                                     key="cl_M")
        velocidade       = st.slider("Velocidade da Moeda (V)", 0.5, 3.0, 1.0, 0.1,
                                     key="cl_V")

    with col3:
        st.markdown("**Fatores de Produção**")
        salario_nominal = st.slider("Salário Nominal (W)", 0.5, 3.0, 1.0, 0.1,
                                    key="cl_W")
        capital         = st.slider("Estoque de Capital (K)", 50.0, 200.0, 100.0, 10.0,
                                    key="cl_K")

    # ══════════════════════════════════════════════════════════════
    # CÁLCULOS
    # ══════════════════════════════════════════════════════════════
    alpha = 0.35
    Y_potencial      = produtividade * tecnologia * (capital ** alpha) * (trabalho ** (1 - alpha))
    P_equilibrio     = (oferta_monetaria * velocidade) / Y_potencial
    salario_real_eq  = (1 - alpha) * produtividade * tecnologia * (capital / trabalho) ** alpha
    salario_real_atual = salario_nominal / P_equilibrio
    desvio_w = ((salario_real_atual - salario_real_eq) / salario_real_eq) * 100

    P_range  = np.linspace(0.1, P_equilibrio * 3, 300)
    DA       = (oferta_monetaria * velocidade) / P_range
    L_range  = np.linspace(10, trabalho * 1.8, 300)
    demanda_trabalho = (1 - alpha) * produtividade * tecnologia * (capital / L_range) ** alpha

    # ══════════════════════════════════════════════════════════════
    # MÉTRICAS
    # ══════════════════════════════════════════════════════════════
    st.markdown("### Equilíbrio Macroeconômico Clássico")
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Produto Potencial (Y*)",    f"{Y_potencial:.1f}")
    m2.metric("Nível de Preços (P*)",      f"{P_equilibrio:.3f}")
    m3.metric("Salário Real Eq. (w*)",     f"{salario_real_eq:.3f}")
    m4.metric("Salário Real Atual (w)",    f"{salario_real_atual:.3f}")
    m5.metric("Desvio Salarial",           f"{desvio_w:+.1f}%",
              delta_color="inverse"if abs(desvio_w) > 5 else "off")

    # ══════════════════════════════════════════════════════════════
    # GRÁFICOS
    # ══════════════════════════════════════════════════════════════
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=(
            "Oferta e Demanda Agregada — Visão Clássica",
            "Mercado de Trabalho Clássico",
        ),
        horizontal_spacing=0.12,
    )

    # ── Subplot 1: OA vertical + DA hipérbole ────────────────────
    fig.add_trace(go.Scatter(
        x=DA, y=P_range, mode="lines", name="DA (MV/P)",
        line=dict(color="#2196F3", width=2.5),
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=[Y_potencial, Y_potencial], y=[0, P_equilibrio * 2.5],
        mode="lines", name="OA Longo Prazo (vertical)",
        line=dict(color="#F44336", width=3),
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=[0, Y_potencial], y=[P_equilibrio, P_equilibrio],
        mode="lines", name=f"P* = {P_equilibrio:.3f}",
        line=dict(color="#4CAF50", width=1.5, dash="dash"),
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=[Y_potencial], y=[P_equilibrio],
        mode="markers+text", name="Equilíbrio E*",
        marker=dict(color="#FF9800", size=12),
        text=["E*"], textposition="top right",
        textfont=dict(size=13, color="#FF9800"),
    ), row=1, col=1)
    fig.add_annotation(
        x=Y_potencial * 1.05, y=P_equilibrio * 2.0,
        text="OA vertical: Y* independe de P<br>(neutralidade da moeda)",
        showarrow=True, arrowhead=2, ax=60, ay=-30,
        font=dict(size=11, color="#F44336"),
        bgcolor="rgba(244,67,54,0.08)", bordercolor="#F44336",
        row=1, col=1,
    )

    fig.update_xaxes(title_text="Produto (Y)", row=1, col=1, showgrid=True)
    fig.update_yaxes(title_text="Nível de Preços (P)", row=1, col=1, showgrid=True,
                     range=[0, P_equilibrio * 2.8])

    # ── Subplot 2: Mercado de Trabalho ───────────────────────────
    fig.add_trace(go.Scatter(
        x=L_range, y=demanda_trabalho,
        mode="lines", name="Demanda por Trabalho (PMgL)",
        line=dict(color="#9C27B0", width=2.5),
    ), row=1, col=2)
    fig.add_trace(go.Scatter(
        x=[trabalho, trabalho], y=[0, salario_real_eq * 2.5],
        mode="lines", name="Oferta de Trabalho (vertical)",
        line=dict(color="#FF5722", width=3),
    ), row=1, col=2)
    fig.add_trace(go.Scatter(
        x=[10, trabalho * 1.8], y=[salario_real_atual, salario_real_atual],
        mode="lines", name=f"w atual = {salario_real_atual:.3f}",
        line=dict(color="#607D8B", width=1.5, dash="dot"),
    ), row=1, col=2)
    fig.add_trace(go.Scatter(
        x=[10, trabalho * 1.8], y=[salario_real_eq, salario_real_eq],
        mode="lines", name=f"w* = {salario_real_eq:.3f}",
        line=dict(color="#4CAF50", width=1.5, dash="dash"),
    ), row=1, col=2)
    fig.add_trace(go.Scatter(
        x=[trabalho], y=[salario_real_eq],
        mode="markers+text", name="Equilíbrio Trabalho",
        marker=dict(color="#FF9800", size=12),
        text=["E*"], textposition="top right",
        textfont=dict(size=13, color="#FF9800"),
        showlegend=False,
    ), row=1, col=2)

    if abs(desvio_w) > 2:
        fig.add_annotation(
            x=trabalho * 0.85,
            y=(salario_real_atual + salario_real_eq) / 2,
            ax=trabalho * 0.85,
            ay=salario_real_eq if salario_real_atual > salario_real_eq else salario_real_atual,
            xref="x2", yref="y2", axref="x2", ayref="y2",
            text="ajuste automático",
            showarrow=True, arrowhead=3, arrowcolor="#FF9800",
            font=dict(size=10, color="#FF9800"),
        )

    fig.update_xaxes(title_text="Trabalho (L)", row=1, col=2, showgrid=True)
    fig.update_yaxes(title_text="Salário Real (w = W/P)", row=1, col=2, showgrid=True)

    fig.update_layout(
        height=520, template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
        margin=dict(t=60, b=80),
    )
    st.plotly_chart(fig, use_container_width=True)

    # ══════════════════════════════════════════════════════════════
    # ANÁLISE NARRATIVA
    # ══════════════════════════════════════════════════════════════
    st.markdown("### Análise Completa da Situação Econômica")

    # Narrativa Função de Produção
    narrativa_producao = (
        f"Com produtividade A = {produtividade:.2f}, tecnologia θ = {tecnologia:.2f}, "
        f"capital K = {capital:.0f} e força de trabalho L̄ = {trabalho:.0f}, "
        f"a função Cobb-Douglas Y* = A·θ·K^α·L̄^(1-α) resulta em **Y* = {Y_potencial:.1f}**. "
        f"Um aumento de 10% em A elevaria Y* para "
        f"≈ {produtividade*1.1*tecnologia*(capital**alpha)*(trabalho**(1-alpha)):.1f} "
        f"— sem alterar P* se M e V forem constantes."
    )

    # Narrativa Monetária
    MV = oferta_monetaria * velocidade
    narrativa_monetaria = (
        f"Com M = {oferta_monetaria:.0f} e V = {velocidade:.1f}, temos MV = {MV:.1f}. "
        f"Pela TQM: P* = MV/Y* = {MV:.1f}/{Y_potencial:.1f} = **{P_equilibrio:.3f}**. "
        f"Se M dobrasse para {oferta_monetaria*2:.0f}, P* subiria para "
        f"{(oferta_monetaria*2*velocidade)/Y_potencial:.3f} — exatamente o dobro — "
        f"enquanto Y* permaneceria em {Y_potencial:.1f}. **Neutralidade da moeda.**"
    )

    # Narrativa Mercado de Trabalho
    if abs(desvio_w) < 2:
        narrativa_trabalho = (
            f"O mercado de trabalho está em equilíbrio pleno: w = {salario_real_atual:.3f} "
            f"≈ w* = {salario_real_eq:.3f} (desvio de apenas {desvio_w:+.1f}%). "
            f"Sem pressão sobre preços ou salários nominais."
        )
        cor_trabalho = ""
    elif desvio_w > 0:
        cor_trabalho = ""
        narrativa_trabalho = (
            f"O salário real (w = {salario_real_atual:.3f}) está **{desvio_w:.1f}% acima** "
            f"do equilíbrio (w* = {salario_real_eq:.3f}). Há excesso de oferta de trabalho. "
            f"O ajuste automático pressiona W para baixo ou P para cima até restaurar w*. "
            f"Y* = {Y_potencial:.1f} permanece inalterado durante o ajuste."
        )
    else:
        cor_trabalho = ""
        narrativa_trabalho = (
            f"O salário real (w = {salario_real_atual:.3f}) está **{abs(desvio_w):.1f}% abaixo** "
            f"do equilíbrio (w* = {salario_real_eq:.3f}). Excesso de demanda por trabalho. "
            f"O ajuste eleva W nominalmente ou reduz P, restaurando w* sem alterar Y* = {Y_potencial:.1f}."
        )

    _card(" 1. Produto Potencial e Função de Produção", narrativa_producao, "blue")
    _card(" 2. Nível de Preços e Neutralidade da Moeda", narrativa_monetaria, "blue")
    _card(f"{cor_trabalho} 3. Mercado de Trabalho e Ajuste Automático",
          narrativa_trabalho, "green"if abs(desvio_w) < 2 else "orange")
    _card(
        " 4. Conclusão — Dicotomia Clássica",
        f"A economia opera em dois planos independentes: o **setor real** "
        f"(Y* = {Y_potencial:.1f}, w* = {salario_real_eq:.3f}) é determinado por fatores de produção; "
        f"o **setor nominal** (P* = {P_equilibrio:.3f}) é determinado por M e V. "
        f"Políticas de demanda são incapazes de alterar Y* — apenas deslocam P*. "
        f"Crescimento real exige ganhos de produtividade, capital ou trabalho.",
        "orange",
    )

    # ══════════════════════════════════════════════════════════════
    # ABAS ANALÍTICAS
    # ══════════════════════════════════════════════════════════════
    st.divider()
    st.subheader("Aprofundamento Teórico")
    aba1, aba2, aba3 = st.tabs([
        "Função de Produção",
        "Teoria Quantitativa",
        "Dicotomia Clássica",
    ])

    with aba1:
        st.latex(r"Y^* = A \cdot \theta \cdot K^\alpha \cdot \bar{L}^{1-\alpha}")
        st.latex(
            rf"Y^* = {produtividade:.2f} \times {tecnologia:.2f} \times "
            rf"{capital:.0f}^{{{alpha}}} \times {trabalho:.0f}^{{{1-alpha:.2f}}} = {Y_potencial:.2f}"
        )
        st.markdown(f"""
- **Participação do Capital (α = {alpha}):** cada 1% de aumento em K eleva Y em {alpha*100:.0f}%.
- **Participação do Trabalho (1-α = {1-alpha:.2f}):** cada 1% de aumento em L eleva Y em {(1-alpha)*100:.0f}%.
- **PTF (A × θ):** qualquer melhoria tecnológica desloca toda a função para cima.
""")

    with aba2:
        st.latex(r"MV = PY \;\Rightarrow\; P^* = \frac{MV}{Y^*}")
        st.latex(
            rf"P^* = \frac{{{oferta_monetaria:.0f} \times {velocidade:.1f}}}{{{Y_potencial:.1f}}} = {P_equilibrio:.3f}"
        )
        st.markdown("""
**Implicações:**
- Duplicar M → duplicar P, sem efeito sobre Y (neutralidade).
- V constante é a hipótese central — criticada por Keynes e pós-Keynesianos.
- Política monetária é apenas um termostato de inflação, não de crescimento.
""")

    with aba3:
        st.markdown("""
**A Dicotomia Clássica separa o mundo em dois blocos:**

| Bloco Real | Bloco Nominal |
|---|---|
| Y*, L*, K*, w* | P*, W, M |
| Determinado por tecnologia e fatores | Determinado pela oferta de moeda |
| Invariante a choques nominais | Proporcional a variações em M |

**Por que é controversa?**
- No curto prazo, rigidezes de preço e salário conectam os dois blocos.
- Keynes argumentou que a demanda efetiva determina Y no curto prazo.
- A síntese neoclássica (IS-LM) reconhece a dicotomia apenas no longo prazo.
""")


# ── Helper de cards ───────────────────────────────────────────────
def _card(titulo: str, conteudo: str, cor: str = "blue") -> None:
    """Renderiza um card com bordas coloridas usando componentes nativos."""
    icone_cor = {
        "blue":   "",
        "green":  "",
        "orange": "",
        "red":    "",
        "purple": "",
    }.get(cor, "")
    fn_map = {
        "green":  st.success,
        "red":    st.error,
        "orange": st.warning,
        "blue":   st.info,
        "purple": st.info,
    }
    fn = fn_map.get(cor, st.info)
    msg = "**" + icone_cor + " " + titulo + "**\n\n" + conteudo
    fn(msg)