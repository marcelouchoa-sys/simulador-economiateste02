# ui/funcoes/investimento_ui.py
"""
Aba Investimento — extraída de pages/1__Funcoes.py
Expõe render() para ser chamada pela página principal.
"""

import numpy as np
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from models.funcoes.investimento import resolver_investimento, efeito_crowding_out

# ── Grid de juros padrão (em %) ───────────────────────────────────
R_GRID = np.linspace(0, 20, 300)


def render() -> None:
    """Renderiza a aba Investimento completa."""

    st.subheader("Investimento — Decisão de Capital e Sensibilidade aos Juros")
    st.markdown(
        "Explore como as firmas decidem investir sob diferentes visões teóricas. "
        "A curva de investimento relaciona a **taxa de juros real** com o "
        "**volume de investimento agregado**."
    )

    col_eq1, col_eq2 = st.columns(2)
    with col_eq1:
        st.latex(r"I = I_0 - b \cdot r \quad \text{(Keynesiana)}")
    with col_eq2:
        st.latex(r"I = I_0 - 2b \cdot r \quad \text{(Clássica — fundos emprestáveis)}")

    st.divider()

    # ══════════════════════════════════════════════════════════════
    # CONTROLES
    # ══════════════════════════════════════════════════════════════
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Parâmetros")

        I0 = st.slider("Investimento Autônomo (I₀)", 50.0, 500.0, 200.0, 10.0,
                       help="Investimento independente dos juros — 'animal spirits'de Keynes")
        b  = st.slider("Sensibilidade aos Juros (b)", 1.0, 100.0, 50.0, 1.0,
                       help="Quanto o investimento cai para cada 1 p.p. de aumento nos juros")

        st.markdown("**Escola Econômica**")
        escola = st.radio("Visão teórica:", ["Keynesiana", "Clássica"],
                          horizontal=True,
                          help="Clássica dobra a sensibilidade b (mercado de fundos emprestáveis)")

        st.divider()
        st.markdown("**Simulação de Crowding-Out**")
        r_base   = st.slider("Juros Base (r₀ %)",   0.0, 15.0, 5.0,  0.5)
        r_choque = st.slider("Juros Choque (r₁ %)", 0.0, 20.0, 10.0, 0.5)

        # ── Indicadores ──────────────────────────────────────────
        I_base   = I0 - b * r_base   if escola == "Keynesiana"else I0 - 2*b*r_base
        I_choque = I0 - b * r_choque if escola == "Keynesiana"else I0 - 2*b*r_choque
        delta_I  = efeito_crowding_out(r_base, r_choque, b if escola == "Keynesiana"else 2*b)

        st.divider()
        st.subheader("Indicadores")
        st.metric("I ao Juros Base",   f"{max(I_base, 0):.1f}")
        st.metric("I ao Juros Choque", f"{max(I_choque, 0):.1f}",
                  delta=f"{delta_I:.1f}", delta_color="inverse")
        st.metric("Crowding-Out (ΔI)", f"{delta_I:.1f}",
                  delta_color="inverse")

    # ── Curvas ───────────────────────────────────────────────────
    I_key, eq_key = resolver_investimento(R_GRID, I0, b, "Keynesiana")
    I_cla, eq_cla = resolver_investimento(R_GRID, I0, b, "Clássica")
    I_sel, eq_sel = resolver_investimento(R_GRID, I0, b, escola)

    with col2:
        # ── Gráfico principal ─────────────────────────────────────
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=(
                f"Função Investimento ({escola})",
                "Comparação Keynesiana vs Clássica",
            ),
        )

        # Subplot 1 — curva selecionada + crowding-out
        fig.add_trace(go.Scatter(
            x=I_sel, y=R_GRID, name=f"I ({escola})",
            line=dict(color="#1565c0", width=3),
        ), row=1, col=1)

        # Pontos base e choque
        for r_val, I_val, nome, cor in [
            (r_base,   max(I_base,   0), f"r₀={r_base}%",   "#2e7d32"),
            (r_choque, max(I_choque, 0), f"r₁={r_choque}%", "#c62828"),
        ]:
            fig.add_trace(go.Scatter(
                x=[I_val], y=[r_val], mode="markers+text",
                name=nome, marker=dict(size=12, color=cor),
                text=[f"  I={I_val:.0f}"], textposition="middle right",
                textfont=dict(size=11, color=cor),
            ), row=1, col=1)
            # Tracejados
            fig.add_trace(go.Scatter(
                x=[0, I_val], y=[r_val, r_val], mode="lines",
                showlegend=False, line=dict(color=cor, width=1.2, dash="dash"),
            ), row=1, col=1)
            fig.add_trace(go.Scatter(
                x=[I_val, I_val], y=[0, r_val], mode="lines",
                showlegend=False, line=dict(color=cor, width=1.2, dash="dash"),
            ), row=1, col=1)

        # Seta do crowding-out
        if r_choque != r_base and I_choque >= 0:
            fig.add_annotation(
                x=max(I_choque, 0), y=r_choque,
                ax=max(I_base, 0),  ay=r_base,
                xref="x", yref="y", axref="x", ayref="y",
                showarrow=True, arrowhead=3, arrowwidth=2,
                arrowcolor="#FF9800", arrowsize=1.2,
            )

        # Subplot 2 — comparação escolas
        fig.add_trace(go.Scatter(
            x=I_key, y=R_GRID, name="Keynesiana",
            line=dict(color="#1565c0", width=2.5),
        ), row=1, col=2)
        fig.add_trace(go.Scatter(
            x=I_cla, y=R_GRID, name="Clássica",
            line=dict(color="#c62828", width=2.5, dash="dash"),
        ), row=1, col=2)

        # Limites dos eixos (só valores positivos de I)
        I_max = max(I0 * 1.1, 10)
        fig.update_xaxes(title_text="Investimento (I)", range=[0, I_max],
                         showgrid=True, row=1, col=1)
        fig.update_yaxes(title_text="Taxa de Juros (r %)", range=[0, 20],
                         showgrid=True, row=1, col=1)
        fig.update_xaxes(title_text="Investimento (I)", range=[0, I_max],
                         showgrid=True, row=1, col=2)
        fig.update_yaxes(title_text="Taxa de Juros (r %)", range=[0, 20],
                         showgrid=True, row=1, col=2)

        fig.update_layout(height=450, template="plotly_white",
                          legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"))
        st.plotly_chart(fig, use_container_width=True)

        # ── Gráfico de sensibilidade ──────────────────────────────
        st.subheader("Sensibilidade do Crowding-Out")
        b_range = np.linspace(1, 150, 200)
        delta_range = -b_range * (r_choque - r_base)
        if escola == "Clássica":
            delta_range *= 2

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=b_range, y=delta_range, mode="lines",
            line=dict(color="#7B1FA2", width=3), name="ΔI = −b·Δr",
        ))
        fig2.add_vline(x=b, line=dict(color="#FF9800", dash="dash", width=2),
                       annotation_text=f"b atual = {b:.0f}",
                       annotation_position="top right")
        fig2.add_hline(y=delta_I, line=dict(color="#c62828", dash="dot", width=1.5),
                       annotation_text=f"ΔI = {delta_I:.1f}",
                       annotation_position="right")
        fig2.update_layout(
            height=260, template="plotly_white",
            xaxis_title="Sensibilidade b", yaxis_title="Crowding-Out (ΔI)",
            title=f"Impacto do Crowding-Out para Δr = {r_choque - r_base:+.1f} p.p.",
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ══════════════════════════════════════════════════════════════
    # ABAS ANALÍTICAS
    # ══════════════════════════════════════════════════════════════
    st.divider()
    st.subheader("Decomposição Analítica")

    aba1, aba2, aba3, aba4 = st.tabs([
        "Função Investimento",
        "Crowding-Out",
        "Keynesiana vs Clássica",
        "Teoria Completa",
    ])

    with aba1:
        _aba_funcao(I0, b, escola, eq_sel, r_base, I_base)

    with aba2:
        _aba_crowding_out(I0, b, escola, r_base, r_choque, I_base, I_choque, delta_I)

    with aba3:
        _aba_escolas(I0, b, r_base, eq_key, eq_cla)

    with aba4:
        _aba_teoria(I0, b, escola, r_base, r_choque, delta_I)

    from ui.auth_ui import botao_salvar
    botao_salvar(
        modulo="Funcoes — Investimento",
        parametros={"I0": I0, "b": b, "escola": escola, "r_base": r_base, "r_choque": r_choque},
        resultado={"I_base": float(max(I_base,0)), "I_choque": float(max(I_choque,0)), "delta_I": float(delta_I)},
    )


# ══════════════════════════════════════════════════════════════════
# FUNÇÕES INTERNAS DE CADA ABA
# ══════════════════════════════════════════════════════════════════

def _aba_funcao(I0, b, escola, eq_sel, r_base, I_base) -> None:
    st.markdown("**Equação atual:**")
    st.latex(rf"I = {I0:.0f} - {b if escola == 'Keynesiana'else 2*b:.0f} \cdot r")
    st.markdown(f"""
**Interpretação dos parâmetros:**

- **$I_0 = {I0:.0f}$** — Investimento autônomo: o volume investido quando $r = 0$.
  Representa os *animal spirits* de Keynes — a propensão espontânea das firmas
  a investir, independente do custo do capital.
- **$b = {b:.0f}$** — Sensibilidade aos juros: para cada **1 p.p.** de aumento
  na taxa de juros, o investimento cai **{b if escola == 'Keynesiana'else 2*b:.0f} unidades**.

**Com $r = {r_base:.1f}\\%$:**
""")
    st.latex(
        rf"I = {I0:.0f} - {b if escola == 'Keynesiana'else 2*b:.0f} \times {r_base:.1f} = {max(I_base,0):.1f}"
    )
    st.markdown("""
**Por que a curva é negativamente inclinada?**

Investir tem um custo de oportunidade: a taxa de juros $r$.
- Se $r$ sobe → o custo de financiar projetos aumenta → menos projetos são viáveis → $I$ cai.
- Se $r$ cai → projetos antes inviáveis tornam-se lucrativos → $I$ sobe.

>  A inclinação da curva IS depende diretamente de $b$: quanto maior $b$,
> mais inclinada é a IS e mais eficaz é a política monetária.
""")


def _aba_crowding_out(I0, b, escola, r_base, r_choque, I_base, I_choque, delta_I) -> None:
    b_ef = b if escola == "Keynesiana"else 2 * b
    st.markdown("**Cálculo do Crowding-Out:**")
    st.latex(r"\Delta I = -b \cdot \Delta r")
    st.latex(
        rf"\Delta I = -{b_ef:.0f} \times ({r_choque:.1f} - {r_base:.1f}) = {delta_I:.1f}"
    )
    st.markdown(f"""
**O que é o Crowding-Out?**

Quando o governo aumenta os gastos ($G\\uparrow$), a curva IS desloca para a direita,
elevando a taxa de juros de equilíbrio ($r\\uparrow$). Isso **reduz o investimento privado**:

1. $G\\uparrow$ → Demanda Agregada $\\uparrow$ → IS desloca direita
2. $r\\uparrow$ (movimento ao longo da LM)
3. $I = I_0 - b \\cdot r$ → $I\\downarrow$

**Com os parâmetros atuais:**
- Juros subiram de **{r_base:.1f}%** para **{r_choque:.1f}%** (Δr = {r_choque-r_base:+.1f} p.p.)
- Investimento caiu de **{max(I_base,0):.1f}** para **{max(I_choque,0):.1f}**
- **Crowding-out = {delta_I:.1f} unidades** de investimento privado perdidas

>  O crowding-out é **parcial** em economia fechada (IS-LM) e pode ser
> **total** em economia aberta com câmbio flexível e mobilidade perfeita
> (Mundell-Fleming).
""")
    if abs(delta_I) > I0 * 0.5:
        st.warning(
            f"O crowding-out representa **{abs(delta_I)/I0*100:.0f}%** do investimento "
            "autônomo — efeito muito intenso. Considere reduzir b ou Δr."
        )


def _aba_escolas(I0, b, r_base, eq_key, eq_cla) -> None:
    I_key_val = max(I0 - b * r_base, 0)
    I_cla_val = max(I0 - 2 * b * r_base, 0)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
** Visão Keynesiana**

$I = I_0 - b \\cdot r$

- O investimento depende dos **animal spirits** (expectativas de lucro futuro)
  e do custo do capital ($r$).
- $b = {b:.0f}$: sensibilidade **moderada** aos juros.
- O investimento é **volátil** — expectativas pessimistas podem travar o
  investimento mesmo com juros baixos (armadilha da liquidez).
- Política monetária tem efeito **limitado** se $b$ for pequeno.

**Com $r = {r_base:.1f}\\%$:** $I = {I_key_val:.1f}$
""")
    with col2:
        st.markdown(f"""
** Visão Clássica (Fundos Emprestáveis)**

$I = I_0 - 2b \\cdot r$

- O investimento é determinado pelo **mercado de fundos emprestáveis**:
  $I(r) = S(r)$ no equilíbrio.
- $b$ dobrado: o investimento é **muito mais sensível** aos juros.
- Os juros equilibram poupança e investimento **automaticamente**.
- Política monetária é muito eficaz — pequenas variações de $r$ geram
  grandes mudanças em $I$.

**Com $r = {r_base:.1f}\\%$:** $I = {I_cla_val:.1f}$
""")

    st.markdown(f"""
**Diferença prática com os parâmetros atuais ($r = {r_base:.1f}\\%$):**

| | Keynesiana | Clássica | Diferença |
|---|---|---|---|
| Sensibilidade | $b = {b:.0f}$ | $b = {2*b:.0f}$ | 2× |
| Investimento | {I_key_val:.1f} | {I_cla_val:.1f} | {I_key_val - I_cla_val:.1f} |
| Impacto de Δr=1p.p. | −{b:.0f} | −{2*b:.0f} | — |

>  A diferença cresce com $r$: quanto maiores os juros, maior a divergência
> entre as escolas na previsão do nível de investimento.
""")


def _aba_teoria(I0, b, escola, r_base, r_choque, delta_I) -> None:
    st.markdown("### Teoria Completa do Investimento")

    # ── 1. O que determina o investimento ────────────────────────
    st.markdown("#### 1. O que determina o Investimento Agregado?")
    st.markdown("""
O investimento é a variável **mais volátil** da demanda agregada e o principal
canal de transmissão da política monetária para a economia real.

**Determinantes fundamentais:**

| Fator | Efeito sobre I | Canal |
|---|---|---|
| ↑ Taxa de juros ($r$) | ↓ I | Custo de financiamento sobe |
| ↑ Expectativas de lucro | ↑ I | *Animal spirits* (Keynes) |
| ↑ Produto esperado ($Y^e$) | ↑ I | Princípio do acelerador |
| ↑ Custo do capital | ↓ I | Custo de reposição sobe |
| ↑ Incerteza | ↓ I | Firmas postergam decisões irreversíveis |
""")

    st.divider()

    # ── 2. Conexão com a IS ───────────────────────────────────────
    st.markdown("#### 2. Conexão com a Curva IS")
    st.markdown(f"""
A curva IS é derivada da condição de equilíbrio no mercado de bens:
""")
    st.latex(r"Y = C + I + G = c_0 + c_1 Y - c_1 T + I_0 - b \cdot r + G")
    st.latex(r"Y^* = \underbrace{\frac{1}{1-c_1}}_{\text{multiplicador}} \cdot (c_0 - c_1 T + I_0 + G) - \underbrace{\frac{b}{1-c_1}}_{\text{inclinação IS}} \cdot r")
    st.markdown(f"""
**Implicações de $b = {b:.0f}$ com os parâmetros atuais:**
- A inclinação da IS é proporcional a $b$: quanto maior $b$, mais **horizontal** a IS.
- IS mais horizontal → política monetária mais eficaz (pequena variação de $r$
  gera grande variação de $Y$).
- IS mais vertical (b pequeno) → política monetária menos eficaz,
  política fiscal mais eficaz.
""")

    st.divider()

    # ── 3. Resumo das equações ────────────────────────────────────
    st.markdown("#### 3.  Resumo das Equações")
    st.latex(r"I = I_0 - b \cdot r \qquad \text{(Keynesiana)}")
    st.latex(r"I = I_0 - 2b \cdot r \qquad \text{(Clássica — fundos emprestáveis)}")
    st.latex(r"\Delta I = -b \cdot \Delta r \qquad \text{(Crowding-Out)}")
    st.latex(r"\frac{\partial Y^*}{\partial r} = \frac{-b}{1-c_1} \qquad \text{(inclinação da IS)}")
    st.caption("Todos os valores são calculados dinamicamente com os parâmetros dos sliders.")
