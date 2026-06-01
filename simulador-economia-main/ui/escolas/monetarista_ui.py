# ui/escolas/monetarista_ui.py
"""
Escola Monetarista — Regras vs. Discrição, expectativas adaptativas
Expõe render() para ser chamada pela página principal.
"""

import numpy as np
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ui.escolas.classica_ui import _card


def render() -> None:
    st.subheader("🔴 Escola Monetarista — Regras, Expectativas e Taxa Natural")

    with st.expander("📖 Fundamentos da Escola Monetarista", expanded=False):
        st.markdown("""
| Princípio | Descrição |
|---|---|
| **Neutralidade de Longo Prazo** | Surpresas monetárias afetam Y temporariamente; no LP, voltamos a Yₙ |
| **Expectativas Adaptativas** | Agentes revisam expectativas com base em erros passados |
| **Taxa Natural de Desemprego** | Existe um uₙ de equilíbrio — qualquer tentativa de manter u < uₙ gera inflação crescente |
| **Regra de Friedman** | BC deve seguir regra fixa de crescimento de M (ex: 3-5% a.a.) |
| **Defasagens Longas** | Política monetária age com defasagens longas e variáveis — ativa é desestabilizadora |
| **Crowding-Out** | Política fiscal é ineficaz no LP (crowding-out do investimento privado) |
""")

    # ══════════════════════════════════════════════════════════════
    # CONTROLES
    # ══════════════════════════════════════════════════════════════
    st.markdown("### ⚙️ Parâmetros")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**🏦 Política Monetária**")
        M_crescimento = st.slider("Crescimento de M (%/ano)", 0.0, 30.0, 5.0, 0.5, key="mn_dM",
                                  help="Regra de Friedman: manter crescimento fixo de M")
        pi_esperada   = st.slider("Inflação Esperada (πᵉ %)", 0.0, 20.0, 3.0, 0.5, key="mn_pie")

    with col2:
        st.markdown("**📊 Estrutura**")
        u_natural = st.slider("Taxa Natural de Desemprego (uₙ %)", 2.0, 10.0, 5.0, 0.5, key="mn_un")
        Yn        = st.slider("Produto Potencial (Yₙ)", 500.0, 2000.0, 1200.0, 50.0, key="mn_Yn")
        beta      = st.slider("β — Sensib. Phillips a u", 0.5, 3.0, 1.5, 0.1, key="mn_beta")

    with col3:
        st.markdown("**🔄 Expectativas**")
        lambda_adapt = st.slider("λ — Velocidade de Adaptação", 0.1, 1.0, 0.5, 0.05, key="mn_lambda",
                                 help="λ=1: expectativas se ajustam totalmente em 1 período")
        u_atual   = st.slider("Desemprego Atual (u %)", 1.0, 15.0, 4.0, 0.5, key="mn_u")
        periodos  = st.slider("Períodos de Simulação", 5, 20, 10, 1, key="mn_T")

    # ══════════════════════════════════════════════════════════════
    # CÁLCULOS
    # ══════════════════════════════════════════════════════════════
    # Curva de Phillips acelerada: π = πᵉ - β*(u - uₙ)
    u_range = np.linspace(0.5, 15.0, 300)
    pi_CP   = pi_esperada - beta * (u_range - u_natural)  # CP de curto prazo

    # Simulação dinâmica: tentativa de manter u < uₙ
    u_sim  = [u_atual]
    pi_sim = [pi_esperada - beta * (u_atual - u_natural)]
    pie_sim = [pi_esperada]

    for t in range(periodos - 1):
        pi_t  = pie_sim[-1] - beta * (u_sim[-1] - u_natural)
        pie_novo = pie_sim[-1] + lambda_adapt * (pi_t - pie_sim[-1])
        # Com política mantendo u < uₙ: u permanece fixo, mas πᵉ acelera
        u_sim.append(u_atual)
        pi_sim.append(pie_novo - beta * (u_atual - u_natural))
        pie_sim.append(pie_novo)

    # Inflação de longo prazo se u for mantido artificialmente baixo
    pi_lp = pi_esperada + (u_natural - u_atual) * beta / (1 - lambda_adapt + 1e-9) if lambda_adapt < 1 else 99.9

    # Curva de Phillips de LP (vertical em uₙ)
    pi_range_lp = np.linspace(-5, 25, 100)

    # ══════════════════════════════════════════════════════════════
    # MÉTRICAS
    # ══════════════════════════════════════════════════════════════
    st.markdown("### 📊 Indicadores Monetaristas")
    pi_atual = pi_esperada - beta * (u_atual - u_natural)
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Inflação Atual (π)",         f"{pi_atual:.2f}%")
    m2.metric("Inflação Esperada (πᵉ)",     f"{pi_esperada:.2f}%")
    m3.metric("Desvio de u vs uₙ",          f"{u_atual - u_natural:+.1f}pp")
    m4.metric("π de Longo Prazo (se u fixo)", f"{min(pi_lp, 99.9):.1f}%")
    m5.metric("Crescimento M (regra)",       f"{M_crescimento:.1f}%/ano")

    if u_atual < u_natural:
        st.warning(
            f"⚠️ **Armadilha de Friedman:** manter u = {u_atual:.1f}% < uₙ = {u_natural:.1f}% "
            f"requer inflação crescente. No longo prazo, u retorna a uₙ com inflação mais alta."
        )

    # ══════════════════════════════════════════════════════════════
    # GRÁFICOS
    # ══════════════════════════════════════════════════════════════
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=(
            "Curva de Phillips — Curto vs Longo Prazo",
            "Dinâmica Inflacionária (Expectativas Adaptativas)",
        ),
        horizontal_spacing=0.12,
    )

    # ── Subplot 1: Phillips CP e LP ──────────────────────────────
    fig.add_trace(go.Scatter(
        x=u_range, y=pi_CP, mode="lines",
        name=f"Phillips CP (πᵉ={pi_esperada:.1f}%)",
        line=dict(color="#2196F3", width=2.5),
    ), row=1, col=1)

    # LP vertical em uₙ
    fig.add_trace(go.Scatter(
        x=[u_natural, u_natural], y=[-5, 25],
        mode="lines", name=f"Phillips LP (vertical em uₙ={u_natural:.1f}%)",
        line=dict(color="#F44336", width=2.5),
    ), row=1, col=1)

    # Ponto atual
    fig.add_trace(go.Scatter(
        x=[u_atual], y=[pi_atual],
        mode="markers+text", name="Situação Atual",
        marker=dict(size=13, color="#FF9800", symbol="star"),
        text=[f" π={pi_atual:.1f}%"], textposition="top right",
    ), row=1, col=1)

    # Seta de retorno ao LP
    if abs(u_atual - u_natural) > 0.5:
        fig.add_annotation(
            x=u_natural, y=pi_atual,
            ax=u_atual, ay=pi_atual,
            xref="x", yref="y", axref="x", ayref="y",
            showarrow=True, arrowhead=3, arrowwidth=2,
            arrowcolor="#4CAF50",
            text="ajuste LP",
            font=dict(size=10, color="#4CAF50"),
        )

    fig.update_xaxes(title_text="Desemprego (u %)", row=1, col=1,
                     range=[0, 15], showgrid=True)
    fig.update_yaxes(title_text="Inflação (π %)", row=1, col=1,
                     range=[-5, 25], showgrid=True)

    # ── Subplot 2: Dinâmica inflacionária ────────────────────────
    t_range = list(range(periodos))
    fig.add_trace(go.Scatter(
        x=t_range, y=pi_sim, mode="lines+markers",
        name="Inflação realizada (π)",
        line=dict(color="#E91E63", width=2.5),
        marker=dict(size=7),
    ), row=1, col=2)
    fig.add_trace(go.Scatter(
        x=t_range, y=pie_sim, mode="lines+markers",
        name="Inflação esperada (πᵉ)",
        line=dict(color="#9C27B0", width=2, dash="dash"),
        marker=dict(size=6),
    ), row=1, col=2)
    fig.add_hline(y=M_crescimento, line=dict(color="#4CAF50", dash="dot", width=1.5),
                  annotation_text=f"Regra de Friedman: ΔM={M_crescimento:.0f}%",
                  annotation_position="right", row=1, col=2)

    fig.update_xaxes(title_text="Período", row=1, col=2, showgrid=True)
    fig.update_yaxes(title_text="Inflação (%)", row=1, col=2, showgrid=True)

    fig.update_layout(
        height=490, template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
        margin=dict(t=60, b=80),
    )
    st.plotly_chart(fig, use_container_width=True)

    # ══════════════════════════════════════════════════════════════
    # ANÁLISE NARRATIVA
    # ══════════════════════════════════════════════════════════════
    st.markdown("### 📝 Análise Monetarista")

    _card(
        "📉 1. A Curva de Phillips Acelerada",
        f"No curto prazo, com πᵉ = {pi_esperada:.1f}%, manter u = {u_atual:.1f}% gera π = {pi_atual:.1f}%. "
        f"Mas as expectativas se adaptam (λ = {lambda_adapt:.2f}): πᵉ sobe para acomodar a inflação realizada. "
        f"Para manter u abaixo de uₙ = {u_natural:.1f}%, é preciso sempre surpreender os agentes com mais inflação — "
        f"gerando inflação crescente (aceleração). No longo prazo, u retorna a uₙ independentemente de π.",
        "red",
    )
    _card(
        "🏦 2. A Regra de Friedman",
        f"Friedman propôs que o BC adote uma regra fixa de crescimento monetário "
        f"(ex: ΔM = {M_crescimento:.1f}%/ano), em vez de política discricionária. "
        f"Razões: (1) defasagens longas e variáveis tornam a política ativa desestabilizadora; "
        f"(2) expectativas racionais eliminam os benefícios das surpresas; "
        f"(3) regras geram credibilidade e ancoram expectativas inflacionárias.",
        "blue",
    )
    _card(
        "🔄 3. Expectativas Adaptativas",
        f"Com λ = {lambda_adapt:.2f}, os agentes revisam πᵉ corrigindo {lambda_adapt*100:.0f}% "
        f"do erro do período anterior. "
        f"Se π > πᵉ consistentemente, πᵉ converge gradualmente para π. "
        f"Isso implica que políticas sistemáticas perdem eficácia ao longo do tempo — "
        f"os agentes aprendem e antecipam as ações do BC.",
        "orange",
    )

    # ══════════════════════════════════════════════════════════════
    # ABAS ANALÍTICAS
    # ══════════════════════════════════════════════════════════════
    st.divider()
    st.subheader("🔬 Aprofundamento Teórico")
    aba1, aba2 = st.tabs(["📐 Curva de Phillips Acelerada", "📘 Debate Regras vs. Discrição"])

    with aba1:
        st.latex(r"\pi = \pi^e - \beta(u - u_n)")
        st.latex(r"\pi^e_{t+1} = \pi^e_t + \lambda(\pi_t - \pi^e_t)")
        st.markdown(f"""
**No longo prazo** (quando $\\pi = \\pi^e$):
""")
        st.latex(r"\pi = \pi^e \;\Rightarrow\; 0 = -\beta(u - u_n) \;\Rightarrow\; u = u_n")
        st.markdown(f"""
A Curva de Phillips de LP é **vertical** em $u_n = {u_natural:.1f}\\%$.
Não existe trade-off permanente entre inflação e desemprego.
""")

    with aba2:
        st.markdown("""
**Argumentos pró-regras (Friedman/Monetaristas):**
- Defasagens: efeitos da política chegam com 6-18 meses de atraso.
- Inconsistência temporal: governo tem incentivo a sempre "enganar" os agentes.
- Credibilidade: regras ancoram expectativas e reduzem custos de desinflação.

**Argumentos pró-discrição (Keynesianos):**
- Choques inesperados exigem respostas flexíveis.
- Regras rígidas podem amplificar crises.
- Bancos centrais modernos usam "discrição restrita" (inflation targeting).

**Síntese atual — Inflation Targeting:**
Metas de inflação com flexibilidade operacional. O BC tem discrição nos meios,
mas é vinculado pela meta — híbrido entre regra e discrição.
""")