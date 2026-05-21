# ui/funcoes/oferta_moeda_ui.py
"""
Aba Oferta de Moeda — extraída de pages/1_📚_Funcoes.py
Expõe render() para ser chamada pela página principal.
"""

import numpy as np
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from models.funcoes.oferta_moeda import resolver_oferta_moeda
from models.funcoes.demanda_moeda import resolver_demanda_moeda

R_GRID = np.linspace(0, 20, 300)


def render() -> None:
    st.subheader("🏦 Oferta de Moeda — Banco Central e Criação Monetária")
    st.markdown(
        "Explore como a oferta de moeda é determinada e como "
        "diferentes regimes monetários afetam o equilíbrio no mercado de moeda."
    )

    col_eq1, col_eq2 = st.columns(2)
    with col_eq1:
        st.latex(r"M^s/P = \bar{M}/P \quad \text{(Exógena — vertical)}")
    with col_eq2:
        st.latex(r"M^s/P = \bar{M}/P + \phi \cdot r \quad \text{(Endógena)}")

    st.divider()

    # ══════════════════════════════════════════════════════════════
    # CONTROLES
    # ══════════════════════════════════════════════════════════════
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("🛠️ Parâmetros")

        M  = st.slider("Oferta Nominal de Moeda (M)", 100.0, 3000.0, 1000.0, 50.0,
                       help="Controlada pelo Banco Central via operações de mercado aberto")
        P  = st.slider("Nível de Preços (P)", 0.5, 3.0, 1.0, 0.1,
                       help="Divide M para obter a oferta real Ms/P")

        st.markdown("**🏛️ Regime Monetário**")
        regime = st.radio("Regime:", ["Exógena", "Endógena"], horizontal=True,
                          help="Exógena: BC controla M diretamente. Endógena: M responde ao crédito.")

        st.divider()
        st.markdown("**📍 Demanda por Moeda (para comparação)**")
        k   = st.slider("k — Sensibilidade a Y", 0.1, 1.0, 0.5, 0.05)
        h   = st.slider("h — Sensibilidade a r", 10.0, 300.0, 100.0, 10.0)
        Y_ref = st.slider("Renda de Referência (Y)", 100.0, 2500.0, 1200.0, 50.0)

        MP, eq_ms = resolver_oferta_moeda(M, P, regime)

        # Equilíbrio: Md = Ms → kY - hr = M/P → r* = (kY - M/P)/h
        r_eq = (k * Y_ref - MP) / max(h, 1e-9)
        r_eq = max(0.0, min(r_eq, 20.0))

        st.divider()
        st.subheader("📊 Indicadores")
        st.metric("Oferta Real (Ms/P)", f"{MP:.1f}")
        st.metric("r* de Equilíbrio", f"{r_eq:.2f}%")
        st.metric("Md/P no equilíbrio",
                  f"{max(k*Y_ref - h*r_eq, 0):.1f}")

    with col2:
        # ── Gráfico principal ─────────────────────────────────────
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=(
                "Mercado Monetário — Oferta vs Demanda",
                "Efeito de Variações em M",
            ),
        )

        # Demanda por moeda
        Md_r, _ = resolver_demanda_moeda(
            np.full_like(R_GRID, Y_ref), R_GRID, k, h, P, "Keynesiana"
        )

        # Subplot 1 — equilíbrio
        fig.add_trace(go.Scatter(
            x=Md_r, y=R_GRID, name="Md/P",
            line=dict(color="#1565c0", width=3),
        ), row=1, col=1)

        if regime == "Exógena":
            fig.add_vline(x=MP, line=dict(color="#c62828", width=3),
                          annotation_text=f"Ms/P = {MP:.0f}",
                          annotation_position="top right", row=1, col=1)
        else:
            phi = 50.0
            Ms_end = MP + phi * R_GRID / 100
            fig.add_trace(go.Scatter(
                x=Ms_end, y=R_GRID, name="Ms/P (endógena)",
                line=dict(color="#c62828", width=3),
            ), row=1, col=1)

        # Ponto de equilíbrio
        fig.add_trace(go.Scatter(
            x=[MP], y=[r_eq], mode="markers+text",
            name="Equilíbrio", marker=dict(size=14, color="#FF9800", symbol="star"),
            text=[f" r*={r_eq:.1f}%"], textposition="top right",
        ), row=1, col=1)

        # Subplot 2 — efeito de choque monetário
        M_range  = np.linspace(200, 2500, 5)
        cores    = ["#1565c0", "#1976d2", "#42a5f5", "#90caf9", "#bbdefb"]
        for i, M_i in enumerate(M_range):
            MP_i = M_i / P
            r_eq_i = (k * Y_ref - MP_i) / max(h, 1e-9)
            fig.add_vline(x=MP_i,
                          line=dict(color=cores[i], width=1.5, dash="dot"),
                          annotation_text=f"M={M_i:.0f}",
                          annotation_position="top",
                          row=1, col=2)
            fig.add_trace(go.Scatter(
                x=[MP_i], y=[max(r_eq_i, 0)],
                mode="markers", showlegend=False,
                marker=dict(size=8, color=cores[i]),
            ), row=1, col=2)
        Md_r2, _ = resolver_demanda_moeda(
            np.full_like(R_GRID, Y_ref), R_GRID, k, h, P, "Keynesiana"
        )
        fig.add_trace(go.Scatter(
            x=Md_r2, y=R_GRID, name="Md/P (fixo)",
            line=dict(color="#2e7d32", width=2.5), showlegend=True,
        ), row=1, col=2)

        x_max = max(MP * 1.5, 100)
        fig.update_xaxes(title_text="M/P", showgrid=True, range=[0, x_max], row=1, col=1)
        fig.update_yaxes(title_text="r (%)", showgrid=True, range=[0, 20], row=1, col=1)
        fig.update_xaxes(title_text="M/P", showgrid=True, row=1, col=2)
        fig.update_yaxes(title_text="r (%)", showgrid=True, range=[0, 20], row=1, col=2)

        fig.update_layout(height=430, template="plotly_white",
                          legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"))
        st.plotly_chart(fig, use_container_width=True)

        # ── Gráfico: Ms vs M nominal ──────────────────────────────
        st.subheader("📊 Oferta Real vs Nível de Preços")
        P_range = np.linspace(0.5, 3.0, 200)
        Ms_real = M / P_range
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=P_range, y=Ms_real, name="Ms/P = M/P",
                                  line=dict(color="#c62828", width=3)))
        fig2.add_vline(x=P, line=dict(color="#FF9800", dash="dash", width=2),
                       annotation_text=f"P atual={P:.1f}")
        fig2.add_hline(y=MP, line=dict(color="#1565c0", dash="dot", width=1.5),
                       annotation_text=f"Ms/P={MP:.0f}")
        fig2.update_layout(height=250, template="plotly_white",
                           xaxis_title="Nível de Preços (P)",
                           yaxis_title="Oferta Real de Moeda (M/P)",
                           title="A inflação corrói a oferta real de moeda")
        st.plotly_chart(fig2, use_container_width=True)

    # ══════════════════════════════════════════════════════════════
    # ABAS ANALÍTICAS
    # ══════════════════════════════════════════════════════════════
    st.divider()
    st.subheader("🔬 Decomposição Analítica")

    aba1, aba2, aba3 = st.tabs([
        "🏦 Criação de Moeda",
        "⚖️ Exógena vs Endógena",
        "📘 Teoria Completa",
    ])

    with aba1:
        st.markdown(f"""
**Como o Banco Central controla M?**

O BC não imprime dinheiro diretamente — ele controla a **base monetária** ($B$)
através de três instrumentos:

| Instrumento | Mecanismo | Efeito |
|---|---|---|
| Operações de mercado aberto | Compra/venda de títulos públicos | ↑↓ Reservas bancárias |
| Taxa de redesconto | Custo do empréstimo ao BC | ↑↓ Crédito bancário |
| Compulsório | % dos depósitos retidos | ↑↓ Multiplicador bancário |

**Multiplicador bancário:**
""")
        st.latex(r"M = m \cdot B \qquad m = \frac{1}{\text{compulsório}}")
        st.markdown(f"""
**Com os parâmetros atuais:**
- Oferta nominal: $M = {M:.0f}$
- Nível de preços: $P = {P:.1f}$
- Oferta real: $M/P = {MP:.1f}$

> 💡 A oferta **nominal** $M$ é controlada pelo BC.
> A oferta **real** $M/P$ depende também dos preços —
> por isso a inflação reduz o poder de compra da moeda.
""")

    with aba2:
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"""
**🔴 Oferta Exógena (Ortodoxa)**

$M^s/P = \\bar{{M}}/P$ — linha **vertical**

- O BC determina $M$ de forma **independente** da demanda.
- Os juros se ajustam para equilibrar o mercado.
- Base da teoria convencional (IS-LM).
- BC atinge qualquer $M$ desejado instantaneamente.

> 📌 Com $M = {M:.0f}$ e $P = {P:.1f}$: $M^s/P = {MP:.1f}$
""")
        with col_b:
            st.markdown(f"""
**🔵 Oferta Endógena (Pós-Keynesiana)**

$M^s/P = \\bar{{M}}/P + \\phi \\cdot r$ — linha **positivamente inclinada**

- A moeda é criada **endogenamente** pelo sistema bancário
  em resposta à demanda por crédito.
- O BC acomoda a demanda fixando a taxa de juros ($r$),
  não a quantidade de moeda.
- Banco comercial: cria depósitos ao conceder empréstimos.
- Implica que a política monetária opera via **preço** ($r$), não **quantidade** ($M$).

> 📌 Cada 1 p.p. de $r$ aumenta $M^s/P$ em $\\phi = 50$ unidades.
""")

        st.info("""
💡 **Debate moderno:** O Banco de Inglaterra (2014) e o FMI reconheceram
que bancos comerciais criam moeda ao conceder empréstimos — validando
parcialmente a visão endógena. Na prática, o BC moderno opera fixando
a taxa de juros (overnight), não a quantidade de moeda.
""")

    with aba3:
        st.markdown("### 📘 Teoria Completa da Oferta de Moeda")
        st.markdown("#### 1. O que é Moeda?")
        st.markdown("""
Moeda é qualquer ativo aceito como meio de troca. Suas funções:
- **Meio de troca**: elimina a dupla coincidência de desejos do escambo
- **Unidade de conta**: padrão para expressar preços
- **Reserva de valor**: transfere poder de compra no tempo

**Agregados monetários no Brasil:**
| Agregado | Componentes |
|---|---|
| M0 (base) | Papel-moeda emitido |
| M1 | M0 + depósitos à vista |
| M2 | M1 + poupança + títulos privados |
| M3 | M2 + fundos de renda fixa |
| M4 | M3 + títulos públicos |
""")
        st.markdown("#### 2. Equilíbrio e Política Monetária")
        st.latex(r"M^s/P = M^d/P \;\Rightarrow\; r^* = \frac{kY - M/P}{h}")
        st.markdown(f"""
Com $Y = {Y_ref:.0f}$, $k = {k:.2f}$, $h = {h:.0f}$, $M/P = {MP:.1f}$:
""")
        st.latex(
            rf"r^* = \frac{{{k:.2f} \times {Y_ref:.0f} - {MP:.1f}}}{{{h:.0f}}} = {r_eq:.2f}\%"
        )
        st.markdown("#### 3. 📐 Resumo das Equações")
        st.latex(r"M^s/P = M/P \quad \text{(exógena)}")
        st.latex(r"M^s/P = M/P + \phi \cdot r \quad \text{(endógena, } \phi=50\text{)}")
        st.latex(r"r^* = \frac{kY - M/P}{h} \quad \text{(equilíbrio LM)}")
        st.caption("Valores calculados dinamicamente com os parâmetros dos sliders.")
