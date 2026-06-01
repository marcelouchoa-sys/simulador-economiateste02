# ui/escolas/pos_keynesiana_ui.py
"""
Escola Pós-Keynesiana — Kalecki, Minsky, endogeneidade da moeda
Expõe render() para ser chamada pela página principal.
"""

import numpy as np
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ui.escolas.classica_ui import _card


def render() -> None:
    st.subheader("Escola Pós-Keynesiana — Demanda, Distribuição e Instabilidade")

    with st.expander("Fundamentos da Escola Pós-Keynesiana", expanded=False):
        st.markdown("""
| Princípio | Descrição |
|---|---|
| **Demanda Efetiva (Kalecki)** | Lucros são determinados pelos gastos dos capitalistas — investimento financia a si mesmo |
| **Moeda Endógena** | Bancos criam moeda ao conceder crédito; BC acomoda a demanda fixando r |
| **Preços por Markup** | Firmas formam preços adicionando margem sobre custos (não pela interação O-D) |
| **Princípio da Demanda Efetiva** | No longo prazo também — sem tendência ao pleno emprego |
| **Instabilidade de Minsky** | Períodos de estabilidade geram fragilidade financeira crescente |
| **Conflito Distributivo** | Inflação resulta de disputa por participação na renda entre salários e lucros |
""")

    # ══════════════════════════════════════════════════════════════
    # CONTROLES
    # ══════════════════════════════════════════════════════════════
    st.markdown("### Parâmetros — Modelo Kaleckiano")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("** Distribuição de Renda**")
        participacao_salarios = st.slider("Participação dos Salários (ω = W/Y)", 0.3, 0.8, 0.6, 0.01,
                                          key="pk_omega",
                                          help="Fração da renda que vai para salários (1-ω = participação dos lucros)")
        markup = st.slider("Markup das Firmas (m)", 1.0, 2.5, 1.4, 0.05, key="pk_markup",
                           help="Preço = (1+m) × Custo. Markup determina a participação dos lucros")

    with col2:
        st.markdown("** Decisões de Gasto**")
        inv_capitalistas = st.slider("Investimento dos Capitalistas (I)", 50.0, 500.0, 200.0, 10.0,
                                     key="pk_I",
                                     help="Kalecki: lucros = investimento + consumo dos capitalistas")
        consumo_capitalistas = st.slider("Consumo dos Capitalistas (Cc)", 20.0, 200.0, 80.0, 5.0,
                                         key="pk_Cc")
        prop_consumo_salarios = st.slider("Propensão a Consumir dos Trabalhadores (cw)", 0.7, 1.0, 0.95, 0.01,
                                          key="pk_cw")

    with col3:
        st.markdown("** Fragilidade Financeira (Minsky)**")
        divida_pib = st.slider("Dívida/PIB (%)", 0.0, 200.0, 60.0, 5.0, key="pk_debt")
        taxa_juros = st.slider("Taxa de Juros (r %)", 0.0, 20.0, 5.0, 0.5, key="pk_r")
        crescimento = st.slider("Crescimento do PIB (%)", -5.0, 10.0, 3.0, 0.5, key="pk_g")

    # ══════════════════════════════════════════════════════════════
    # CÁLCULOS KALECKIANOS
    # ══════════════════════════════════════════════════════════════
    # Identidade de Kalecki: Lucros = Investimento + Consumo dos Capitalistas + Déficit Público
    # (simplificado: sem governo)
    lucros_kalecki = inv_capitalistas + consumo_capitalistas

    # Participação dos lucros implícita pelo markup
    participacao_lucros = 1.0 - participacao_salarios
    participacao_lucros_markup = (markup - 1.0) / markup

    # Produto de equilíbrio kaleckiano
    # Y = (I + Cc) / (1 - cw*(1-π_L))  onde π_L = participação dos lucros
    # Trabalhadores: salário = ω*Y, consomem cw*ω*Y
    # Capitalistas: lucros = (1-ω)*Y, mas gastos = I + Cc (autônomos)
    denom_kal = 1.0 - prop_consumo_salarios * participacao_salarios
    Y_kalecki = (inv_capitalistas + consumo_capitalistas) / max(denom_kal, 1e-9)

    # Lucros realizados
    lucros_realizados = participacao_lucros * Y_kalecki

    # Paradoxo da Parcimônia: se cw cai, Y cai mas lucros ficam iguais
    # (demonstração: L = I + Cc sempre, independente de cw)

    # ── Fragilidade Minsky ────────────────────────────────────────
    # Serviço da dívida como % do PIB
    servico_divida = divida_pib * taxa_juros / 100
    # Capacidade de pagamento: crescimento do PIB
    folga_financeira = crescimento - taxa_juros
    # Classificação Minsky
    if divida_pib < 40 and folga_financeira > 2:
        regime_minsky = "hedge"
        desc_minsky   = "Hedge — unidades conseguem pagar juros e principal com renda corrente"
        cor_minsky    = "green"
    elif divida_pib < 80 or folga_financeira > 0:
        regime_minsky = "especulativo"
        desc_minsky   = "Especulativo — unidades pagam juros mas precisam rolar o principal"
        cor_minsky    = "orange"
    else:
        regime_minsky = "ponzi"
        desc_minsky   = "Ponzi — unidades precisam de nova dívida para pagar até os juros"
        cor_minsky    = "red"

    # ── Inflação de conflito ──────────────────────────────────────
    # π = f(markup, salários alvo)
    # Simplificado: π = max(0, markup_pressao + salario_pressao)
    markup_pressao  = (markup - 1.4) * 5.0   # desvio do markup "normal"
    salario_pressao = (participacao_salarios - 0.6) * 10.0

    # Curvas de markup e salário alvo
    omega_range = np.linspace(0.3, 0.9, 300)
    # Markup implica: π_L = (m-1)/m → ω = 1 - π_L
    omega_markup_line = np.full_like(omega_range, 1.0 - (markup - 1.0) / markup)
    # Salário alvo: trabalhadores buscam participação ω_alvo
    omega_salario_alvo = participacao_salarios
    # Inflação = positivo se ω alvo dos trabalhadores > ω compatível com markup
    inflacao_conflito = max(0.0, (omega_salario_alvo - (1.0 - participacao_lucros_markup)) * 15.0)

    # ══════════════════════════════════════════════════════════════
    # MÉTRICAS
    # ══════════════════════════════════════════════════════════════
    st.markdown("### Indicadores Pós-Keynesianos")
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Produto (Y) — Kalecki",         f"{Y_kalecki:.1f}")
    m2.metric("Lucros Realizados",              f"{lucros_realizados:.1f}")
    m3.metric("Lucros pela Identidade Kalecki", f"{lucros_kalecki:.1f}")
    m4.metric("Inflação de Conflito Estimada",  f"{inflacao_conflito:.1f}%")
    m5.metric("Regime Minsky",                  regime_minsky.capitalize(),
              delta=desc_minsky[:30] + "...",
              delta_color="normal"if regime_minsky == "hedge"else "inverse")

    if lucros_realizados > 0:
        diferenca_lucros = abs(lucros_realizados - lucros_kalecki) / lucros_kalecki * 100
        if diferenca_lucros > 5:
            st.warning(
                f" **Inconsistência Kaleckiana:** lucros realizados ({lucros_realizados:.1f}) "
                f"diferem da identidade I+Cc ({lucros_kalecki:.1f}) em {diferenca_lucros:.1f}%. "
                f"Isso ocorre porque ω e Y são endógenos — ajuste os parâmetros."
            )

    # ══════════════════════════════════════════════════════════════
    # GRÁFICOS
    # ══════════════════════════════════════════════════════════════
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=(
            "Determinação do Produto — Kalecki",
            "Inflação de Conflito Distributivo",
        ),
        horizontal_spacing=0.12,
    )

    # ── Subplot 1: Kalecki — gasto autônomo determina lucros ─────
    # Eixo X: Investimento, Eixo Y: Lucros
    I_range = np.linspace(0, 500, 300)
    lucros_I = I_range + consumo_capitalistas   # identidade de Kalecki

    fig.add_trace(go.Scatter(
        x=I_range, y=lucros_I, mode="lines",
        name="Lucros = I + Cc (Kalecki)",
        line=dict(color="#9C27B0", width=2.5),
    ), row=1, col=1)
    # Linha 45° (lucros = investimento se Cc=0)
    fig.add_trace(go.Scatter(
        x=I_range, y=I_range, mode="lines",
        name="Lucros = I (Cc=0)",
        line=dict(color="#607D8B", width=1.5, dash="dot"),
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=[inv_capitalistas], y=[lucros_kalecki],
        mode="markers+text", name="Ponto Atual",
        marker=dict(size=13, color="#FF9800", symbol="star"),
        text=[f"L={lucros_kalecki:.0f}"], textposition="top right",
    ), row=1, col=1)
    fig.add_annotation(
        x=inv_capitalistas * 0.5, y=lucros_kalecki * 0.7,
        text=f"Cc = {consumo_capitalistas:.0f}<br>(deslocamento vertical)",
        showarrow=True, arrowhead=2,
        font=dict(size=10, color="#9C27B0"),
        row=1, col=1,
    )

    fig.update_xaxes(title_text="Investimento dos Capitalistas (I)", row=1, col=1, showgrid=True)
    fig.update_yaxes(title_text="Lucros Agregados (L)", row=1, col=1, showgrid=True)

    # ── Subplot 2: Inflação de conflito ──────────────────────────
    # Curva de markup: participação compatível com o markup atual
    omega_compat = 1.0 - participacao_lucros_markup
    fig.add_hline(y=omega_compat,
                  line=dict(color="#F44336", width=2.5),
                  annotation_text=f"ω compatível com markup={markup:.2f}: {omega_compat:.2f}",
                  annotation_position="right", row=1, col=2)
    # Salário alvo dos trabalhadores
    fig.add_hline(y=participacao_salarios,
                  line=dict(color="#2196F3", width=2.5, dash="dash"),
                  annotation_text=f"ω alvo dos trabalhadores: {participacao_salarios:.2f}",
                  annotation_position="right", row=1, col=2)

    # Área de conflito
    if participacao_salarios > omega_compat:
        fig.add_hrect(y0=omega_compat, y1=participacao_salarios,
                      fillcolor="rgba(244,67,54,0.12)", layer="below", line_width=0,
                      row=1, col=2)
        fig.add_annotation(
            x=0.5, y=(omega_compat + participacao_salarios) / 2,
            xref="x2 domain", yref="y2",
            text=f"Zona de conflito<br>π ≈ {inflacao_conflito:.1f}%",
            showarrow=False, font=dict(size=11, color="#F44336"),
        )

    # Eixo X: período de tempo (dinâmica)
    t_range = np.arange(10)
    omega_dinamic = omega_compat + (participacao_salarios - omega_compat) * np.exp(-0.3 * t_range)
    fig.add_trace(go.Scatter(
        x=t_range, y=omega_dinamic, mode="lines+markers",
        name="Trajetória de ω no tempo",
        line=dict(color="#4CAF50", width=2),
    ), row=1, col=2)

    fig.update_xaxes(title_text="Período", row=1, col=2, showgrid=True)
    fig.update_yaxes(title_text="Participação dos Salários (ω)", row=1, col=2,
                     showgrid=True, range=[0.2, 0.95])

    fig.update_layout(
        height=490, template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
        margin=dict(t=60, b=80),
    )
    st.plotly_chart(fig, use_container_width=True)

    # ══════════════════════════════════════════════════════════════
    # ANÁLISE NARRATIVA
    # ══════════════════════════════════════════════════════════════
    st.markdown("### Análise Pós-Keynesiana")

    _card(
        " 1. Identidade de Kalecki — Os Capitalistas Ganham o que Gastam",
        f"**Lucros = Investimento + Consumo dos Capitalistas** = {inv_capitalistas:.0f} + {consumo_capitalistas:.0f} = **{lucros_kalecki:.0f}**. "
        f"Esta é uma identidade contábil, não uma teoria comportamental. "
        f"Os capitalistas, ao gastarem em investimento e consumo, criam a renda que retorna como lucros. "
        f"Os trabalhadores, ao consumirem quase toda sua renda (cw = {prop_consumo_salarios:.2f}), "
        f"não determinam os lucros — apenas amplificam o produto via multiplicador. "
        f"**Paradoxo da Parcimônia Kaleckiano:** se os trabalhadores pouparem mais (↓cw), "
        f"Y cai mas os lucros permanecem os mesmos (= I + Cc).",
        "purple",
    )
    _card(
        " 2. Moeda Endógena — Bancos Criam Moeda",
        f"Na visão pós-keynesiana, o Banco Central não controla M diretamente. "
        f"Quando uma firma pede um empréstimo, o banco cria um depósito — 'moeda do nada'. "
        f"O BC acomoda essa demanda por crédito fixando a taxa de juros (r = {taxa_juros:.1f}%). "
        f"Implicação: a curva LM é endógena (horizontal na taxa de juros fixada pelo BC), "
        f"não positivamente inclinada como no IS-LM convencional.",
        "blue",
    )
    _card(
        f" 3. Regime Minsky — {regime_minsky.capitalize()}",
        f"{desc_minsky}. "
        f"Com Dívida/PIB = {divida_pib:.0f}%, juros de {taxa_juros:.1f}% e crescimento de {crescimento:.1f}%, "
        f"o serviço da dívida consome {servico_divida:.1f}% do PIB e a folga financeira é de "
        f"{folga_financeira:+.1f}pp. "
        f"**Hipótese de Instabilidade de Minsky:** em períodos de estabilidade, firmas assumem "
        f"mais risco (hedge → especulativo → Ponzi), tornando o sistema financeiro progressivamente mais frágil.",
        cor_minsky,
    )
    _card(
        " 4. Inflação de Conflito Distributivo",
        f"Com markup m = {markup:.2f}, a participação dos lucros compatível é "
        f"π_L = (m-1)/m = {participacao_lucros_markup:.2f}, "
        f"implicando ω compatível = {omega_compat:.2f}. "
        f"Os trabalhadores buscam ω = {participacao_salarios:.2f}. "
        f"{'Há conflito: trabalhadores exigem mais do que o markup permite → inflação estimada de ' + str(inflacao_conflito.__format__('.1f')) + '%.'if inflacao_conflito > 0.5 else 'Não há conflito: ω alvo dos trabalhadores é compatível com o markup — inflação baixa.'} "
        f"Nesta visão, inflação não é excesso de demanda — é resultado de disputas distributivas.",
        "orange"if inflacao_conflito > 0.5 else "green",
    )

    # ══════════════════════════════════════════════════════════════
    # ABAS ANALÍTICAS
    # ══════════════════════════════════════════════════════════════
    st.divider()
    st.subheader("Aprofundamento Teórico")
    aba1, aba2, aba3 = st.tabs([
        "Kalecki — Determinação dos Lucros",
        "Minsky — Hipótese de Instabilidade",
        "Pós-Keynesiana vs Keynesiana Ortodoxa",
    ])

    with aba1:
        st.markdown("**Identidade de Kalecki:**")
        st.latex(r"L = I + C_c + D_g - NX")
        st.markdown("(simplificado, sem governo e economia fechada:)")
        st.latex(r"L = I + C_c")
        st.latex(
            rf"L = {inv_capitalistas:.0f} + {consumo_capitalistas:.0f} = {lucros_kalecki:.0f}"
        )
        st.markdown(f"""
**Determinação do produto:**
""")
        st.latex(r"Y = \frac{I + C_c}{1 - c_w \cdot \omega}")
        st.latex(
            rf"Y = \frac{{{inv_capitalistas:.0f} + {consumo_capitalistas:.0f}}}"
            rf"{{1 - {prop_consumo_salarios:.2f} \times {participacao_salarios:.2f}}} = {Y_kalecki:.1f}"
        )
        st.markdown("""
**Paradoxo da Parcimônia (versão kaleckiana):**
Se trabalhadores pouparem mais (↓cw): Y cai, mas L = I + Cc permanece igual.
Os capitalistas não ficam mais ricos — apenas os trabalhadores ficam mais pobres.
""")

    with aba2:
        st.markdown("""
**Os três regimes de Minsky:**

| Regime | Condição | Característica |
|---|---|---|
| **Hedge** | Receita > Juros + Principal | Fluxo de caixa cobre todas obrigações |
| **Especulativo** | Receita > Juros, mas < Juros + Principal | Precisa rolar a dívida continuamente |
| **Ponzi** | Receita < Juros | Precisa de nova dívida para pagar até os juros |

**A Hipótese de Instabilidade Financeira:**
> "A estabilidade é desestabilizadora"

Em períodos de bonança: firmas hedge tornam-se especulativas, especulativas tornam-se Ponzi.
O sistema acumula fragilidade até a crise de Minsky — momento de venda de ativos em pânico.
""")
        if regime_minsky == "ponzi":
            st.error(f"Regime Ponzi detectado: Dívida/PIB = {divida_pib:.0f}%, r = {taxa_juros:.1f}%, g = {crescimento:.1f}%")

    with aba3:
        st.markdown("""
| Dimensão | Keynesiana Ortodoxa (IS-LM) | Pós-Keynesiana |
|---|---|---|
| **Moeda** | Exógena (BC controla M) | Endógena (criada por bancos) |
| **LM** | Positivamente inclinada | Horizontal (r fixado pelo BC) |
| **Preços** | Determinados por O-D | Markup sobre custos |
| **Inflação** | Excesso de demanda | Conflito distributivo |
| **LP** | Tende ao pleno emprego | Sem tendência ao pleno emprego |
| **Instabilidade** | Exógena (choques) | Endógena (fragilidade financeira) |
| **Política** | Fiscal + Monetária | Fiscal permanente + regulação financeira |
""")