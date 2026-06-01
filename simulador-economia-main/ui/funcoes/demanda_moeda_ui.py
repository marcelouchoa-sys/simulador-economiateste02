# ui/funcoes/demanda_moeda_ui.py
"""
Aba Demanda por Moeda — extraída de pages/1__Funcoes.py
Expõe render() para ser chamada pela página principal.
"""

import numpy as np
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from models.funcoes.demanda_moeda import resolver_demanda_moeda, resolver_lm

Y_GRID = np.linspace(100, 2500, 300)
R_GRID = np.linspace(0, 20, 300)


def render() -> None:
    st.subheader("Demanda por Moeda — Preferência pela Liquidez")
    st.markdown(
        "Explore os motivos pelos quais os agentes demandam moeda e como "
        "isso determina a curva LM e a taxa de juros de equilíbrio."
    )

    col_eq1, col_eq2 = st.columns(2)
    with col_eq1:
        st.latex(r"M^d/P = kY - hr \quad \text{(Keynesiana)}")
    with col_eq2:
        st.latex(r"M^d/P = \frac{1}{V} \cdot Y \quad \text{(TQM Clássica)}")

    st.divider()

    # ══════════════════════════════════════════════════════════════
    # CONTROLES
    # ══════════════════════════════════════════════════════════════
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Parâmetros")

        k = st.slider("Sensibilidade a Y (k)", 0.1, 1.0, 0.5, 0.05,
                      help="Quanto a demanda por moeda sobe para cada unidade de Y")
        h = st.slider("Sensibilidade a r (h)", 10.0, 300.0, 100.0, 10.0,
                      help="Quanto a demanda por moeda cai para cada 1 p.p. de juros")
        P = st.slider("Nível de Preços (P)", 0.5, 3.0, 1.0, 0.1)
        M = st.slider("Oferta de Moeda (M)", 100.0, 2000.0, 1000.0, 50.0)

        st.markdown("** Escola Econômica**")
        escola = st.radio("Visão teórica:", ["Keynesiana", "Clássica"], horizontal=True)

        st.divider()
        st.markdown("** Ponto de Análise**")
        Y_ref = st.slider("Renda de Referência (Y)", 100.0, 2500.0, 1200.0, 50.0)
        r_ref = st.slider("Juros de Referência (r %)", 0.0, 20.0, 5.0, 0.5)

        Md_ref, eq_md = resolver_demanda_moeda(
            np.array([Y_ref]), np.array([r_ref]), k, h, P, escola
        )
        r_lm_ref = resolver_lm(np.array([Y_ref]), k, h, M, P)[0]

        st.divider()
        st.subheader("Indicadores")
        st.metric("Md/P no ponto", f"{max(Md_ref[0], 0):.1f}")
        st.metric("Ms/P (oferta real)", f"{M/P:.1f}")
        st.metric("r LM em Y ref.", f"{r_lm_ref:.2f}%",
                  delta=f"{'excesso Md'if Md_ref[0] > M/P else 'excesso Ms'}",
                  delta_color="inverse"if Md_ref[0] > M/P else "normal")

    with col2:
        # ── Gráficos ──────────────────────────────────────────────
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=(
                "Demanda por Moeda vs Juros (Y fixo)",
                "Curva LM — Equilíbrio Monetário",
            ),
        )

        # Subplot 1 — Md vs r para Y fixo
        Md_r, _ = resolver_demanda_moeda(
            np.full_like(R_GRID, Y_ref), R_GRID, k, h, P, escola
        )
        fig.add_trace(go.Scatter(
            x=Md_r, y=R_GRID, name=f"Md/P ({escola})",
            line=dict(color="#1565c0", width=3),
        ), row=1, col=1)
        # Linha vertical Ms/P
        fig.add_vline(x=M/P, line=dict(color="#c62828", dash="dash", width=2),
                      annotation_text=f"Ms/P={M/P:.0f}", row=1, col=1)
        # Ponto de referência
        fig.add_trace(go.Scatter(
            x=[max(Md_ref[0], 0)], y=[r_ref],
            mode="markers", name="Ponto ref.",
            marker=dict(size=12, color="#FF9800"),
        ), row=1, col=1)

        # Subplot 2 — Curva LM
        r_lm = resolver_lm(Y_GRID, k, h, M, P)
        mask = (r_lm >= 0) & (r_lm <= 20)
        fig.add_trace(go.Scatter(
            x=Y_GRID[mask], y=r_lm[mask], name="LM",
            line=dict(color="#2e7d32", width=3),
        ), row=1, col=2)
        fig.add_trace(go.Scatter(
            x=[Y_ref], y=[r_lm_ref], mode="markers+text",
            name=f"Equilíbrio LM", marker=dict(size=12, color="#FF9800"),
            text=[f"r={r_lm_ref:.1f}%"], textposition="top right",
        ), row=1, col=2)

        fig.update_xaxes(title_text="Md/P", showgrid=True, row=1, col=1)
        fig.update_yaxes(title_text="Taxa de Juros (r %)", showgrid=True,
                         range=[0, 20], row=1, col=1)
        fig.update_xaxes(title_text="Produto (Y)", showgrid=True, row=1, col=2)
        fig.update_yaxes(title_text="Taxa de Juros (r %)", showgrid=True,
                         range=[0, 20], row=1, col=2)

        fig.update_layout(height=430, template="plotly_white",
                          legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"))
        st.plotly_chart(fig, use_container_width=True)

        # ── Gráfico: Md vs Y para r fixo ──────────────────────────
        st.subheader("Demanda por Moeda vs Renda (r fixo)")
        Md_y, _ = resolver_demanda_moeda(Y_GRID, np.full_like(Y_GRID, r_ref), k, h, P, escola)
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=Y_GRID, y=Md_y, name="Md/P",
                                  line=dict(color="#1565c0", width=3)))
        fig2.add_hline(y=M/P, line=dict(color="#c62828", dash="dash", width=2),
                       annotation_text=f"Ms/P = {M/P:.0f}")
        fig2.update_layout(height=260, template="plotly_white",
                           xaxis_title="Produto (Y)", yaxis_title="Md/P",
                           title=f"Demanda por Moeda para r = {r_ref:.1f}%")
        st.plotly_chart(fig2, use_container_width=True)

    # ══════════════════════════════════════════════════════════════
    # ABAS ANALÍTICAS
    # ══════════════════════════════════════════════════════════════
    st.divider()
    st.subheader("Decomposição Analítica")

    aba1, aba2, aba3, aba4 = st.tabs([
        "Preferência pela Liquidez",
        "Curva LM",
        "Keynesiana vs Clássica",
        "Teoria Completa",
    ])

    with aba1:
        st.markdown("**Os três motivos para demandar moeda (Keynes):**")
        st.markdown(f"""
| Motivo | Determinante | Parcela em Md |
|---|---|---|
|  **Transação** | Renda (Y) | $k \\cdot Y = {k:.2f} \\times {Y_ref:.0f} = {k*Y_ref:.1f}$ |
|  **Precaução** | Renda (Y) | incluído em k |
|  **Especulação** | Juros (r) | $-h \\cdot r = -{h:.0f} \\times {r_ref:.1f} = {-h*r_ref:.1f}$ |

**Fórmula completa:**
""")
        st.latex(rf"M^d/P = {k:.2f} \times {Y_ref:.0f} - {h:.0f} \times {r_ref:.1f} = {max(Md_ref[0],0):.1f}")
        st.markdown(f"""
- **$k = {k:.2f}$**: cada unidade de renda gera {k:.2f} de demanda por moeda
  (motivo transação + precaução).
- **$h = {h:.0f}$**: cada 1 p.p. de juros reduz a demanda por moeda em {h:.0f}
  (motivo especulação — custo de oportunidade de reter moeda).

>  Quando $r$ é muito baixo (armadilha da liquidez), $h \\to \\infty$:
> a demanda por moeda é infinitamente elástica — a LM fica horizontal.
""")

    with aba2:
        st.markdown("**Derivação da Curva LM:**")
        st.latex(r"\frac{M}{P} = kY - hr \;\Rightarrow\; r = \frac{kY - M/P}{h}")
        st.latex(
            rf"r = \frac{{{k:.2f} \times Y - {M/P:.1f}}}{{{h:.0f}}} = {k/h:.4f} \cdot Y - {M/(P*h):.4f}"
        )
        st.markdown(f"""
**Inclinação da LM:** $\\frac{{k}}{{h}} = \\frac{{{k:.2f}}}{{{h:.0f}}} = {k/h:.4f}$

- LM **mais íngreme** (k↑ ou h↓): política monetária menos eficaz,
  fiscal mais eficaz.
- LM **mais plana** (k↓ ou h↑): política monetária mais eficaz.
- LM **horizontal** ($h \\to \\infty$): armadilha da liquidez —
  política monetária completamente ineficaz.
- LM **vertical** ($h = 0$): TQM clássica —
  política fiscal completamente ineficaz (crowding-out total).

**Em $Y = {Y_ref:.0f}$:** $r^* = {r_lm_ref:.2f}\\%$
""")

    with aba3:
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"""
** Preferência pela Liquidez (Keynes)**

$M^d/P = kY - hr$

- Três motivos: transação, precaução e **especulação**.
- O motivo especulação ($-hr$) é a inovação keynesiana:
  agentes preferem liquidez quando esperam queda nos preços
  dos títulos (alta nos juros).
- A demanda por moeda é **instável** — pode mudar com as expectativas.
- Implica LM **positivamente inclinada**.
""")
        with col_b:
            st.markdown(f"""
** Teoria Quantitativa da Moeda (Clássica)**

$MV = PY \;\Rightarrow\; M^d/P = \\frac{{1}}{{V}} Y$

- Apenas um motivo: **transação**.
- Velocidade $V$ é **constante** — sem motivo especulação.
- A demanda por moeda é **estável** e proporcional à renda.
- Implica LM **vertical** — política fiscal ineficaz.
- $V$ implícito = {k*2:.2f} (o dobro de k).
""")

    with aba4:
        st.markdown("### Teoria Completa da Demanda por Moeda")
        st.markdown("#### 1. Por que as pessoas demandam moeda?")
        st.markdown("""
A moeda não rende juros diretamente — então por que mantê-la?
Porque ela oferece **liquidez**: a capacidade de realizar transações
imediatamente, sem custo de conversão.

O custo de manter moeda é o **juro não recebido** $r$ — o custo de
oportunidade de não aplicar em títulos.
""")
        st.latex(r"M^d/P = \underbrace{kY}_{\text{transação + precaução}} - \underbrace{hr}_{\text{especulação}}")

        st.markdown("#### 2. Equilíbrio no Mercado Monetário")
        st.latex(r"M^s/P = M^d/P \;\Rightarrow\; \frac{M}{P} = kY - hr")
        st.latex(r"r^* = \frac{kY - M/P}{h}")
        st.markdown("""
O equilíbrio determina a taxa de juros que iguala oferta e demanda por moeda.
Uma expansão monetária ($M\\uparrow$) desloca a LM para baixo/direita,
reduzindo $r^*$ e estimulando o investimento.
""")
        st.markdown("#### 3.  Resumo das Equações")
        st.latex(r"M^d/P = kY - hr \quad \text{(Keynesiana)}")
        st.latex(r"M^d/P = \frac{1}{V} Y \quad \text{(TQM)}")
        st.latex(r"r_{LM} = \frac{k}{h} Y - \frac{M}{hP} \quad \text{(Curva LM)}")
        st.caption("Valores calculados dinamicamente com os parâmetros dos sliders.")
