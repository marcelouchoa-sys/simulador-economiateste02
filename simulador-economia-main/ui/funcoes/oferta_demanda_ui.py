# ui/funcoes/oferta_demanda_ui.py
"""
Aba Oferta e Demanda — extraída de pages/1_📚_Funcoes.py
Expõe render() para ser chamada pela página principal.
"""

import numpy as np
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def render() -> None:
    """Renderiza a aba Oferta e Demanda completa."""

    st.subheader("📈 Oferta e Demanda — Equilíbrio de Mercado")
    st.markdown(
        "Explore o equilíbrio de mercado, **excesso de oferta** e **escassez** "
        "com curvas lineares interativas. As curvas são definidas por:"
    )
    col_eq1, col_eq2 = st.columns(2)
    with col_eq1:
        st.latex(r"P^D = a - b \cdot Q \quad \text{(Demanda)}")
    with col_eq2:
        st.latex(r"P^S = c + d \cdot Q \quad \text{(Oferta)}")

    st.divider()

    # ══════════════════════════════════════════════════════════════
    # CONTROLES
    # ══════════════════════════════════════════════════════════════
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**📉 Curva de Demanda**")
        a_dem = st.slider("Intercepto da Demanda (a)", 2.0, 12.0, 7.0, 0.25,
                          key="od_a", help="Preço máximo que os consumidores pagariam (Q=0)")
        b_dem = st.slider("Inclinação da Demanda (b)", 0.001, 0.010, 0.004, 0.001,
                          format="%.3f", key="od_b",
                          help="Quanto P cai para cada unidade adicional de Q")

    with col2:
        st.markdown("**📈 Curva de Oferta**")
        c_ofe = st.slider("Intercepto da Oferta (c)", 0.0, 4.0, 1.0, 0.25,
                          key="od_c", help="Preço mínimo para os produtores ofertarem (Q=0)")
        d_ofe = st.slider("Inclinação da Oferta (d)", 0.001, 0.010, 0.004, 0.001,
                          format="%.3f", key="od_d",
                          help="Quanto P sobe para cada unidade adicional de Q")

    with col3:
        st.markdown("**💲 Preço Tabelado**")
        P_tabelado = st.slider("Preço Tabelado (P̄)", 1.0, 10.0, 6.0, 0.25,
                               key="od_ptab",
                               help="Acima do equilíbrio → excesso de oferta; abaixo → escassez")
        mostrar_tabelado = st.checkbox("Mostrar cenário com preço tabelado",
                                       value=True, key="od_show")

    # ══════════════════════════════════════════════════════════════
    # CÁLCULOS
    # ══════════════════════════════════════════════════════════════
    denom     = b_dem + d_ofe
    Q_eq      = max((a_dem - c_ofe) / denom, 0.0) if denom > 0 else 0.0
    P_eq      = c_ofe + d_ofe * Q_eq
    Q_dem_tab = max((a_dem - P_tabelado) / b_dem, 0.0) if b_dem > 0 else 0.0
    Q_ofe_tab = max((P_tabelado - c_ofe) / d_ofe, 0.0) if d_ofe > 0 else 0.0
    excesso   = Q_ofe_tab - Q_dem_tab   # >0 excesso de oferta; <0 escassez

    escala     = 1000
    Q_max_plot = Q_eq * 2.2 if Q_eq > 0 else 2000.0
    Q_range    = np.linspace(0, Q_max_plot, 400)
    P_demanda  = a_dem - b_dem * Q_range
    P_oferta   = c_ofe + d_ofe * Q_range

    # ══════════════════════════════════════════════════════════════
    # MÉTRICAS
    # ══════════════════════════════════════════════════════════════
    st.markdown("### 📊 Equilíbrio de Mercado")
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Preço de Equilíbrio (P*)",     f"R$ {P_eq:.2f} mil")
    m2.metric("Quantidade de Equilíbrio (Q*)", f"{Q_eq/escala:.2f} mil")
    if mostrar_tabelado:
        m3.metric("Preço Tabelado (P̄)",       f"R$ {P_tabelado:.2f} mil")
        m4.metric("Qd ao P̄",                  f"{Q_dem_tab/escala:.2f} mil")
        m5.metric("Qs ao P̄",                  f"{Q_ofe_tab/escala:.2f} mil")
        if abs(excesso) > 10:
            tipo = "Excesso de Oferta" if excesso > 0 else "Escassez"
            st.info(f"**{tipo}:** |Qs − Qd| = {abs(excesso)/escala:.2f} mil unidades")

    # ══════════════════════════════════════════════════════════════
    # GRÁFICOS
    # ══════════════════════════════════════════════════════════════
    n_cols  = 2 if mostrar_tabelado else 1
    titulo2 = (
        f"Preço Tabelado P̄={P_tabelado:.2f} → "
        f"{'Excesso de Oferta' if excesso > 0 else 'Escassez' if excesso < 0 else 'Equilíbrio'}"
        if mostrar_tabelado else ""
    )

    fig_od = make_subplots(
        rows=1, cols=n_cols,
        subplot_titles=(
            f"Equilíbrio  (P*={P_eq:.2f}, Q*={Q_eq/escala:.0f} mil)", titulo2
        ) if mostrar_tabelado else (
            f"Equilíbrio  (P*={P_eq:.2f}, Q*={Q_eq/escala:.0f} mil)",
        ),
        horizontal_spacing=0.12,
    )

    def _add_base(col: int) -> None:
        show = (col == 1)
        fig_od.add_trace(go.Scatter(
            x=Q_range / escala, y=P_demanda, name="Demanda",
            line=dict(color="#F44336", width=3), showlegend=show,
        ), row=1, col=col)
        fig_od.add_trace(go.Scatter(
            x=Q_range / escala, y=P_oferta, name="Oferta",
            line=dict(color="#2196F3", width=3), showlegend=show,
        ), row=1, col=col)
        fig_od.add_trace(go.Scatter(
            x=[Q_eq / escala], y=[P_eq], mode="markers+text",
            name="Equilíbrio (E)", marker=dict(color="#555", size=12),
            text=["E"], textposition="top right", textfont=dict(size=14),
            showlegend=show,
        ), row=1, col=col)
        # Tracejados até os eixos
        for xv, yv, x0, y0 in [
            (Q_eq / escala, P_eq, 0, P_eq),
            (Q_eq / escala, P_eq, Q_eq / escala, 0),
        ]:
            fig_od.add_trace(go.Scatter(
                x=[x0, xv], y=[y0, yv], mode="lines", showlegend=False,
                line=dict(color="#888", width=1.2, dash="dash"),
            ), row=1, col=col)

    _add_base(1)
    fig_od.update_xaxes(title_text="q (em milhares)", showgrid=True,
                        range=[0, Q_max_plot / escala], row=1, col=1)
    fig_od.update_yaxes(title_text="P (em R$ mil)", showgrid=True,
                        range=[0, a_dem * 1.1], row=1, col=1)

    if mostrar_tabelado:
        _add_base(2)

        fig_od.add_trace(go.Scatter(
            x=[0, Q_max_plot / escala], y=[P_tabelado, P_tabelado],
            name=f"P̄ = {P_tabelado:.2f} (tabelado)",
            line=dict(color="#FF9800", width=2, dash="dot"), showlegend=True,
        ), row=1, col=2)

        for Q_val, nome, cor in [
            (Q_dem_tab, f"Qd={Q_dem_tab/escala:.2f} mil", "#2196F3"),
            (Q_ofe_tab, f"Qs={Q_ofe_tab/escala:.2f} mil", "#F44336"),
        ]:
            fig_od.add_trace(go.Scatter(
                x=[Q_val / escala], y=[P_tabelado], mode="markers",
                name=nome, marker=dict(color=cor, size=11), showlegend=True,
            ), row=1, col=2)
            fig_od.add_trace(go.Scatter(
                x=[Q_val / escala, Q_val / escala], y=[0, P_tabelado],
                mode="lines", showlegend=False,
                line=dict(color=cor, width=1.2, dash="dash"),
            ), row=1, col=2)

        if abs(excesso) > 10:
            Q_min_a = min(Q_dem_tab, Q_ofe_tab) / escala
            Q_max_a = max(Q_dem_tab, Q_ofe_tab) / escala
            Q_mid_a = (Q_min_a + Q_max_a) / 2
            label   = "Excesso" if excesso > 0 else "Escassez"
            cor_a   = "#E65100" if excesso > 0 else "#1565C0"
            y_ann   = P_tabelado + (0.45 if excesso > 0 else -0.65)

            fig_od.add_shape(type="line",
                x0=Q_min_a, x1=Q_max_a, y0=y_ann, y1=y_ann,
                line=dict(color=cor_a, width=1.5), row=1, col=2)
            for xv in [Q_min_a, Q_max_a]:
                fig_od.add_shape(type="line",
                    x0=xv, x1=xv, y0=P_tabelado, y1=y_ann,
                    line=dict(color=cor_a, width=1.2, dash="dot"), row=1, col=2)
            fig_od.add_annotation(
                x=Q_mid_a, y=y_ann + (0.28 if excesso > 0 else -0.28),
                text=f"<b>{label}</b>", showarrow=False,
                font=dict(size=13, color=cor_a), row=1, col=2,
            )

        fig_od.update_xaxes(title_text="q (em milhares)", showgrid=True,
                            range=[0, Q_max_plot / escala], row=1, col=2)
        fig_od.update_yaxes(title_text="P (em R$ mil)", showgrid=True,
                            range=[0, a_dem * 1.1], row=1, col=2)

    fig_od.update_layout(
        height=500, template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=-0.28, xanchor="center", x=0.5),
        margin=dict(t=60, b=90),
    )
    st.plotly_chart(fig_od, use_container_width=True)

    # ══════════════════════════════════════════════════════════════
    # ABAS ANALÍTICAS
    # ══════════════════════════════════════════════════════════════
    st.divider()
    st.subheader("🔬 Decomposição Analítica")

    aba1, aba2, aba3, aba4 = st.tabs([
        "⚖️ Equilíbrio de Mercado",
        "💲 Efeito do Preço Tabelado",
        "📐 Elasticidades",
        "📘 Teoria Completa",
    ])

    with aba1:
        _aba_equilibrio(a_dem, b_dem, c_ofe, d_ofe, Q_eq, P_eq, escala)

    with aba2:
        _aba_preco_tabelado(
            mostrar_tabelado, a_dem, b_dem, c_ofe, d_ofe,
            P_tabelado, P_eq, Q_dem_tab, Q_ofe_tab, excesso, escala,
        )

    with aba3:
        _aba_elasticidades(b_dem, d_ofe, P_eq, Q_eq)

    with aba4:
        _aba_teoria_completa(
            a_dem, b_dem, c_ofe, d_ofe, P_eq, Q_eq,
            mostrar_tabelado, P_tabelado, Q_dem_tab, Q_ofe_tab,
            Q_ofe_tab - Q_dem_tab, escala,
        )


# ══════════════════════════════════════════════════════════════════
# FUNÇÕES INTERNAS DE CADA ABA
# ══════════════════════════════════════════════════════════════════

def _aba_equilibrio(
    a_dem, b_dem, c_ofe, d_ofe, Q_eq, P_eq, escala
) -> None:
    st.markdown("**Cálculo analítico do equilíbrio:**")
    st.latex(
        rf"P^D = P^S \;\Rightarrow\; {a_dem:.2f} - {b_dem:.3f}Q = {c_ofe:.2f} + {d_ofe:.3f}Q"
    )
    st.latex(
        rf"Q^* = \frac{{{a_dem:.2f} - {c_ofe:.2f}}}{{{b_dem:.3f} + {d_ofe:.3f}}} = {Q_eq/escala:.3f} \text{{ mil}}"
    )
    st.latex(
        rf"P^* = {c_ofe:.2f} + {d_ofe:.3f} \times {Q_eq:.0f} = {P_eq:.2f} \text{{ R\$ mil}}"
    )
    st.markdown(f"""
No equilíbrio, **toda a produção é vendida** e **toda a demanda é atendida**.
Não há pressão para que o preço suba ou caia. Qualquer desvio de P* gera forças
restauradoras:
- Se **P > P***: produtores acumulam estoques → reduzem preços.
- Se **P < P***: consumidores competem pelo bem escasso → elevam o preço.
""")


def _aba_preco_tabelado(
    mostrar_tabelado, a_dem, b_dem, c_ofe, d_ofe,
    P_tabelado, P_eq, Q_dem_tab, Q_ofe_tab, excesso, escala,
) -> None:
    if not mostrar_tabelado:
        st.info("Ative 'Mostrar cenário com preço tabelado' para ver esta análise.")
        return

    st.latex(
        rf"Q_d(\bar{{P}}) = \frac{{{a_dem:.2f} - {P_tabelado:.2f}}}{{{b_dem:.3f}}} = {Q_dem_tab/escala:.3f} \text{{ mil}}"
    )
    st.latex(
        rf"Q_s(\bar{{P}}) = \frac{{{P_tabelado:.2f} - {c_ofe:.2f}}}{{{d_ofe:.3f}}} = {Q_ofe_tab/escala:.3f} \text{{ mil}}"
    )

    if abs(excesso) < 10:
        st.success(f"O preço tabelado P̄ = {P_tabelado:.2f} coincide com P* = {P_eq:.2f}. Sem distorção.")
    elif excesso > 0:
        st.markdown(f"""
**📦 Excesso de Oferta ({abs(excesso)/escala:.2f} mil unidades)**

Com P̄ = {P_tabelado:.2f} **acima** do equilíbrio (P* = {P_eq:.2f}):
- Produtores querem vender mais do que os consumidores desejam comprar.
- O excesso de {abs(excesso)/escala:.2f} mil unidades pressiona o preço para baixo.
- Com **preço mínimo (piso)** — ex: salário mínimo — o excesso persiste como **desemprego**.
""")
    else:
        st.markdown(f"""
**🔻 Escassez ({abs(excesso)/escala:.2f} mil unidades)**

Com P̄ = {P_tabelado:.2f} **abaixo** do equilíbrio (P* = {P_eq:.2f}):
- Consumidores demandam mais do que os produtores estão dispostos a ofertar.
- A escassez pressiona o preço para cima.
- Com **teto de preços** — ex: controle de aluguéis — a escassez persiste e gera
  **filas, mercados paralelos e deterioração da qualidade**.
""")


def _aba_elasticidades(b_dem, d_ofe, P_eq, Q_eq) -> None:
    eps_d = -(1 / b_dem) * (P_eq / Q_eq) if Q_eq > 0 else 0
    eps_s =  (1 / d_ofe) * (P_eq / Q_eq) if Q_eq > 0 else 0

    st.markdown("**Elasticidade-preço da Demanda no equilíbrio:**")
    st.latex(
        rf"\varepsilon_d = \frac{{dQ^D}}{{dP}} \cdot \frac{{P^*}}{{Q^*}} "
        rf"= \frac{{-1}}{{{b_dem:.3f}}} \cdot \frac{{{P_eq:.2f}}}{{{Q_eq:.0f}}} = {eps_d:.3f}"
    )
    st.markdown("**Elasticidade-preço da Oferta no equilíbrio:**")
    st.latex(
        rf"\varepsilon_s = \frac{{dQ^S}}{{dP}} \cdot \frac{{P^*}}{{Q^*}} "
        rf"= \frac{{1}}{{{d_ofe:.3f}}} \cdot \frac{{{P_eq:.2f}}}{{{Q_eq:.0f}}} = {eps_s:.3f}"
    )

    col_ea, col_eb = st.columns(2)
    with col_ea:
        if abs(eps_d) > 1:
            st.success(f"**Demanda elástica** (|ε| = {abs(eps_d):.2f} > 1): "
                       f"1% no preço gera {abs(eps_d):.2f}% na quantidade demandada.")
        else:
            st.warning(f"**Demanda inelástica** (|ε| = {abs(eps_d):.2f} < 1): "
                       "variações de preço têm impacto proporcionalmente menor.")
    with col_eb:
        if eps_s > 1:
            st.success(f"**Oferta elástica** (ε = {eps_s:.2f} > 1): "
                       "produtores respondem fortemente a variações de preço.")
        else:
            st.warning(f"**Oferta inelástica** (ε = {eps_s:.2f} < 1): "
                       "capacidade limitada de ajuste no curto prazo.")


def _aba_teoria_completa(
    a_dem, b_dem, c_ofe, d_ofe, P_eq, Q_eq,
    mostrar_tabelado, P_tabelado, Q_dem_tab, Q_ofe_tab,
    excesso, escala,
) -> None:
    st.markdown("### 📘 Teoria Completa de Oferta e Demanda")

    # ── 1. O que são as curvas ────────────────────────────────────
    st.markdown("#### 1. O que representam as curvas?")
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.markdown(f"""
**📉 Curva de Demanda — $P^D = a - b \\cdot Q$**

Representa o comportamento dos **consumidores**. É **negativamente inclinada** porque:
- Quanto maior o preço, menor a quantidade demandada (efeito substituição + renda).
- **$a = {a_dem:.2f}$**: preço de reserva do consumidor (preço máximo, quando $Q=0$).
- **$b = {b_dem:.3f}$**: sensibilidade da demanda ao preço.

> 💡 Se o preço do café dobrar, você compra menos e substitui por chá.
""")
    with col_t2:
        st.markdown(f"""
**📈 Curva de Oferta — $P^S = c + d \\cdot Q$**

Representa o comportamento dos **produtores**. É **positivamente inclinada** porque:
- Quanto maior o preço, mais lucrativo produzir → mais quantidade ofertada.
- **$c = {c_ofe:.2f}$**: custo variável médio mínimo (preço mínimo viável, quando $Q=0$).
- **$d = {d_ofe:.3f}$**: custo marginal crescente (rendimentos decrescentes de escala).

> 💡 Se o preço do café sobe, fazendeiros plantam mais mesmo em terras menos férteis.
""")

    st.divider()

    # ── 2. O Equilíbrio ───────────────────────────────────────────
    st.markdown("#### 2. Como se forma o Equilíbrio?")
    st.latex(r"a - b \cdot Q = c + d \cdot Q")
    st.latex(r"Q^* = \frac{a - c}{b + d} \qquad P^* = c + d \cdot Q^*")
    st.markdown(f"""
**Com os parâmetros atuais:**
- $Q^* = {Q_eq/escala:.3f}$ mil unidades
- $P^* = {P_eq:.2f}$ R\\$ mil

**Por que o mercado converge para esse ponto?**
- Se $P > P^*$: excesso de oferta → estoques acumulam → preço cai.
- Se $P < P^*$: escassez → consumidores competem → preço sobe.
- Em $P^*$: nenhuma força desequilibrante — **equilíbrio estável**.
""")

    st.divider()

    # ── 3. Deslocadores ──────────────────────────────────────────
    st.markdown("#### 3. O que desloca as curvas?")
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.markdown("""
**Deslocadores da Demanda** (mudam $a$):

| Fator | Efeito | $Q^*$ e $P^*$ |
|---|---|---|
| ↑ Renda dos consumidores | Desloca ➡️ | ↑↑ |
| ↑ Preço de bem substituto | Desloca ➡️ | ↑↑ |
| ↑ Preço de bem complementar | Desloca ⬅️ | ↓↓ |
| ↑ Preferências pelo bem | Desloca ➡️ | ↑↑ |

> ⚠️ Variação de **preço** = movimento **ao longo** da curva.
> Variação de **outra variável** = **deslocamento** da curva.
""")
    with col_d2:
        st.markdown("""
**Deslocadores da Oferta** (mudam $c$):

| Fator | Efeito | $Q^*$ e $P^*$ |
|---|---|---|
| ↑ Custo dos insumos | Desloca ⬅️ | ↓Q, ↑P |
| ↑ Tecnologia | Desloca ➡️ | ↑Q, ↓P |
| ↑ Número de produtores | Desloca ➡️ | ↑Q, ↓P |
| ↑ Subsídio do governo | Desloca ➡️ | ↑Q, ↓P |
| ↑ Imposto sobre produção | Desloca ⬅️ | ↓Q, ↑P |
""")

    st.divider()

    # ── 4. Excedentes ────────────────────────────────────────────
    st.markdown("#### 4. Excedente do Consumidor e do Produtor")

    EC = 0.5 * (a_dem - P_eq) * Q_eq if Q_eq > 0 else 0.0
    EP = 0.5 * (P_eq - c_ofe) * Q_eq if Q_eq > 0 else 0.0
    BT = EC + EP

    col_e1, col_e2, col_e3 = st.columns(3)
    col_e1.metric("Excedente do Consumidor (EC)", f"{EC/escala:.2f}")
    col_e2.metric("Excedente do Produtor (EP)",   f"{EP/escala:.2f}")
    col_e3.metric("Benefício Total (EC + EP)",    f"{BT/escala:.2f}")

    st.latex(
        rf"EC = \frac{{1}}{{2}} \times ({a_dem:.2f} - {P_eq:.2f}) \times {Q_eq:.0f} = {EC:.2f}"
    )
    st.latex(
        rf"EP = \frac{{1}}{{2}} \times ({P_eq:.2f} - {c_ofe:.2f}) \times {Q_eq:.0f} = {EP:.2f}"
    )
    st.success(
        f"🏆 **Eficiência de Mercado:** O equilíbrio competitivo maximiza o "
        f"Benefício Total = EC + EP = **{BT:.2f}**. "
        "Qualquer intervenção (teto ou piso) reduz esse total — gerando **perda de peso morto**."
    )

    st.divider()

    # ── 5. Perda de Peso Morto ────────────────────────────────────
    st.markdown("#### 5. Preço Tabelado e Perda de Peso Morto")
    if mostrar_tabelado:
        Q_transac = min(Q_dem_tab, Q_ofe_tab)
        PPM = (0.5 * abs(P_tabelado - P_eq) * abs(Q_eq - Q_transac)
               if Q_eq > Q_transac else 0.0)

        st.markdown(f"""
Com o preço tabelado em $\\bar{{P}} = {P_tabelado:.2f}$, a quantidade efetivamente
transacionada é $Q_{{transac}} = \\min(Q^D, Q^S) = {Q_transac/escala:.3f}$ mil.
""")
        st.latex(
            rf"PPM \approx \frac{{1}}{{2}} \times |{P_eq:.2f} - {P_tabelado:.2f}| "
            rf"\times |{Q_eq:.0f} - {Q_transac:.0f}| = {PPM:.2f}"
        )
        if PPM > 0:
            st.error(
                f"⚠️ **Ineficiência:** O preço tabelado destrói **{PPM:.2f}** unidades de "
                "benefício social — transações mutuamente benéficas que deixam de ocorrer "
                "(**perda de peso morto**)."
            )
        else:
            st.success("✅ O preço tabelado coincide com o equilíbrio. Sem perda de eficiência.")
    else:
        st.info("Ative o preço tabelado para ver a análise de perda de peso morto.")

    st.divider()

    # ── 6. Conexão com a Macroeconomia ────────────────────────────
    st.markdown("#### 6. Conexão com a Macroeconomia")
    st.markdown("""
O modelo de oferta e demanda é a **microeconomia** que fundamenta os modelos
macroeconômicos do simulador:

| Mercado Micro | Equivalente Macro | Preço | Quantidade |
|---|---|---|---|
| Bem genérico | Mercado de bens (IS) | Nível de preços $P$ | Produto $Y$ |
| Trabalho | Mercado de trabalho | Salário real $w/P$ | Emprego $L$ |
| Moeda | Mercado monetário (LM) | Taxa de juros $r$ | Oferta de moeda $M$ |
| Câmbio | Balanço de pagamentos (BP) | Taxa de câmbio $e$ | Reservas internacionais |
""")
    st.latex(
        r"DA: \quad Y = \frac{1}{1-c_1(1-t)}\left(c_0 + I_0 + G - c_1 T + \frac{h}{k}M\right) - \frac{b}{k}P"
    )
    st.caption(
        "A DA é derivada do modelo IS-LM: o nível de preços P afeta a oferta real "
        "de moeda M/P, deslocando a LM e alterando o produto de equilíbrio Y."
    )