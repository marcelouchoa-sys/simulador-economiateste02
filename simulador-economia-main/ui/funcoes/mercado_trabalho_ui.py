# ui/funcoes/mercado_trabalho_ui.py
"""
Aba Mercado de Trabalho — extraída de pages/1_📚_Funcoes.py
Expõe render() para ser chamada pela página principal.
"""

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def render(p: dict | None = None) -> None:
    """Renderiza a aba Mercado de Trabalho completa.
    Aceita o dict de parâmetros global para sincronizar Y_atual e Y_pleno.
    """
    if p is None:
        p = {}
    # Garantir chaves no estado global
    if "Y_atual" not in p:
        p["Y_atual"] = 1800.0
    if "Yn" not in p:
        p["Yn"] = 1200.0

    st.subheader("👷 Mercado de Trabalho — Emprego, Salário e Desemprego")
    st.markdown(
        "Modelo de equilíbrio no mercado de trabalho com **salário mínimo (piso salarial)**, "
        "**desemprego involuntário** e integração com a **Lei de Okun** e o modelo **OA-DA**."
    )

    col_eq1, col_eq2 = st.columns(2)
    with col_eq1:
        st.latex(r"w/P^D = a - b \cdot L \quad \text{(Demanda por Trabalho — Empresas)}")
    with col_eq2:
        st.latex(r"w/P^S = c + d \cdot L \quad \text{(Oferta de Trabalho — Trabalhadores)}")

    st.divider()

    # ══════════════════════════════════════════════════════════════
    # CONTROLES
    # ══════════════════════════════════════════════════════════════
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**🏭 Demanda por Trabalho (Empresas)**")
        a_ld = st.slider("Intercepto da Demanda (a)", 2.0, 20.0, 12.0, 0.5,
                         key="mt_a",
                         help="Salário real máximo que as empresas pagariam com L=0 (PMgL máximo)")
        b_ld = st.slider("Inclinação da Demanda (b)", 0.001, 0.020, 0.006, 0.001,
                         format="%.3f", key="mt_b",
                         help="Queda do salário real para cada trabalhador adicional (PMgL decrescente)")

    with col2:
        st.markdown("**👥 Oferta de Trabalho (Trabalhadores)**")
        c_ls = st.slider("Intercepto da Oferta (c)", 0.0, 6.0, 1.0, 0.25,
                         key="mt_c",
                         help="Salário real mínimo de reserva (abaixo disso ninguém trabalha)")
        d_ls = st.slider("Inclinação da Oferta (d)", 0.001, 0.020, 0.006, 0.001,
                         format="%.3f", key="mt_d",
                         help="Aumento do salário real exigido para cada trabalhador adicional")

    with col3:
        st.markdown("**⚖️ Política Salarial e Produto**")
        w_min        = st.slider("Salário Mínimo (w̄/P)", 1.0, 18.0, 9.0, 0.25,
                                 key="mt_wmin",
                                 help="Piso salarial legal. Se acima do equilíbrio → desemprego involuntário")
        mostrar_wmin = st.checkbox("Ativar piso salarial", value=True, key="mt_show")
        st.markdown("---")
        st.markdown("**📦 Produto e Lei de Okun**")
        Y_atual   = st.number_input("Produto Atual (Y)",             value=float(p["Y_atual"]), step=50.0, key="mt_y")
        Y_pleno   = st.number_input("Produto de Pleno Emprego (Yₙ)", value=float(p["Yn"]),     step=50.0, key="mt_yn")
        p["Y_atual"] = Y_atual
        p["Yn"]      = Y_pleno
        beta_okun = st.slider("Coeficiente de Okun (β)", 0.1, 0.5, 0.3, 0.05,
                              key="mt_beta",
                              help="Variação do desemprego para cada 1% de desvio do produto")
        u_natural = st.slider("Taxa Natural de Desemprego (uₙ %)", 3.0, 8.0, 5.0, 0.5,
                              key="mt_un")

    # ══════════════════════════════════════════════════════════════
    # CÁLCULOS
    # ══════════════════════════════════════════════════════════════
    denom_mt        = b_ld + d_ls
    L_eq            = max((a_ld - c_ls) / denom_mt, 0.0) if denom_mt > 0 else 0.0
    w_eq            = c_ls + d_ls * L_eq
    L_dem_wmin      = max((a_ld - w_min) / b_ld, 0.0) if b_ld > 0 else 0.0
    L_ofe_wmin      = max((w_min - c_ls) / d_ls, 0.0) if d_ls > 0 else 0.0
    desemprego_piso = max(L_ofe_wmin - L_dem_wmin, 0.0)
    gap_produto     = Y_atual - Y_pleno
    gap_pct         = (gap_produto / Y_pleno) * 100 if Y_pleno > 0 else 0.0
    u_ciclico       = -beta_okun * gap_pct
    u_efetivo       = u_natural + u_ciclico

    escala_L   = 1000
    L_max_plot = L_eq * 2.2 if L_eq > 0 else 2000
    L_range    = np.linspace(0, L_max_plot, 400)
    wP_demanda = a_ld - b_ld * L_range
    wP_oferta  = c_ls + d_ls * L_range

    # ══════════════════════════════════════════════════════════════
    # MÉTRICAS
    # ══════════════════════════════════════════════════════════════
    st.markdown("### 📊 Indicadores do Mercado de Trabalho")
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Salário Real de Equilíbrio (w*/P)", f"{w_eq:.2f}")
    m2.metric("Emprego de Equilíbrio (L*)",        f"{L_eq/escala_L:.2f} mil")
    if mostrar_wmin:
        m3.metric("Desemprego pelo Piso (LS−LD)",  f"{desemprego_piso/escala_L:.2f} mil")
    m4.metric("Desemprego Cíclico (Okun)",         f"{u_ciclico:+.2f} p.p.")
    m5.metric("Taxa de Desemprego Efetiva",        f"{u_efetivo:.2f}%")

    if mostrar_wmin and desemprego_piso > 10:
        st.error(
            f"⚠️ **Desemprego Involuntário:** Com salário mínimo w̄/P = {w_min:.2f} "
            f"(acima do equilíbrio w* = {w_eq:.2f}), há **{desemprego_piso/escala_L:.2f} mil** "
            "trabalhadores desempregados involuntariamente."
        )
    elif mostrar_wmin and w_min <= w_eq:
        st.success(
            f"✅ O salário mínimo ({w_min:.2f}) está **abaixo do equilíbrio** ({w_eq:.2f}). "
            "O piso não é restritivo — não gera desemprego involuntário."
        )

    # ══════════════════════════════════════════════════════════════
    # GRÁFICOS — Oferta, Demanda e Piso Salarial
    # ══════════════════════════════════════════════════════════════
    n_cols_mt  = 2 if mostrar_wmin else 1
    titulo_mt2 = (
        f"Piso Salarial w̄/P={w_min:.2f} → "
        f"{'Desemprego Involuntário' if desemprego_piso > 10 else 'Sem Distorção'}"
        if mostrar_wmin else ""
    )

    fig_mt = make_subplots(
        rows=1, cols=n_cols_mt,
        subplot_titles=(
            f"Equilíbrio  (w*/P={w_eq:.2f}, L*={L_eq/escala_L:.0f} mil)", titulo_mt2
        ) if mostrar_wmin else (
            f"Equilíbrio  (w*/P={w_eq:.2f}, L*={L_eq/escala_L:.0f} mil)",
        ),
        horizontal_spacing=0.12,
    )

    def _add_base_mt(col: int) -> None:
        show = (col == 1)
        fig_mt.add_trace(go.Scatter(
            x=L_range / escala_L, y=wP_demanda,
            name="Demanda por Trabalho (Lᴰ)",
            line=dict(color="#F44336", width=3), showlegend=show,
        ), row=1, col=col)
        fig_mt.add_trace(go.Scatter(
            x=L_range / escala_L, y=wP_oferta,
            name="Oferta de Trabalho (Lˢ)",
            line=dict(color="#2196F3", width=3), showlegend=show,
        ), row=1, col=col)
        fig_mt.add_trace(go.Scatter(
            x=[L_eq / escala_L], y=[w_eq],
            mode="markers+text", name="Equilíbrio (E*)",
            marker=dict(color="#333", size=12),
            text=["E*"], textposition="top right",
            textfont=dict(size=14), showlegend=show,
        ), row=1, col=col)
        for x0, y0, xv, yv in [
            (0, w_eq, L_eq / escala_L, w_eq),
            (L_eq / escala_L, 0, L_eq / escala_L, w_eq),
        ]:
            fig_mt.add_trace(go.Scatter(
                x=[x0, xv], y=[y0, yv], mode="lines", showlegend=False,
                line=dict(color="#888", width=1.2, dash="dash"),
            ), row=1, col=col)

    _add_base_mt(1)
    fig_mt.update_xaxes(title_text="L — Trabalho (em milhares)", showgrid=True,
                        range=[0, L_max_plot / escala_L], row=1, col=1)
    fig_mt.update_yaxes(title_text="w/P — Salário Real", showgrid=True,
                        range=[0, a_ld * 1.1], row=1, col=1)

    if mostrar_wmin:
        _add_base_mt(2)
        fig_mt.add_trace(go.Scatter(
            x=[0, L_max_plot / escala_L], y=[w_min, w_min],
            name=f"Salário Mínimo w̄/P = {w_min:.2f}",
            line=dict(color="#FF9800", width=2.5, dash="dot"), showlegend=True,
        ), row=1, col=2)
        for L_val, nome, cor in [
            (L_dem_wmin, f"Lᴰ = {L_dem_wmin/escala_L:.2f} mil (empregados)", "#F44336"),
            (L_ofe_wmin, f"Lˢ = {L_ofe_wmin/escala_L:.2f} mil (ofertantes)", "#2196F3"),
        ]:
            fig_mt.add_trace(go.Scatter(
                x=[L_val / escala_L], y=[w_min], mode="markers",
                name=nome, marker=dict(color=cor, size=11), showlegend=True,
            ), row=1, col=2)
            fig_mt.add_trace(go.Scatter(
                x=[L_val / escala_L, L_val / escala_L], y=[0, w_min],
                mode="lines", showlegend=False,
                line=dict(color=cor, width=1.2, dash="dash"),
            ), row=1, col=2)
        if desemprego_piso > 10:
            L_min_a = L_dem_wmin / escala_L
            L_max_a = L_ofe_wmin / escala_L
            y_ann   = w_min + 0.5
            fig_mt.add_shape(type="line",
                x0=L_min_a, x1=L_max_a, y0=y_ann, y1=y_ann,
                line=dict(color="#B71C1C", width=1.5), row=1, col=2)
            for xv in [L_min_a, L_max_a]:
                fig_mt.add_shape(type="line",
                    x0=xv, x1=xv, y0=w_min, y1=y_ann,
                    line=dict(color="#B71C1C", width=1.2, dash="dot"), row=1, col=2)
            fig_mt.add_annotation(
                x=(L_min_a + L_max_a) / 2, y=y_ann + 0.35,
                text=f"<b>Desemprego Involuntário<br>{desemprego_piso/escala_L:.2f} mil</b>",
                showarrow=False, font=dict(size=12, color="#B71C1C"), row=1, col=2,
            )
        fig_mt.update_xaxes(title_text="L — Trabalho (em milhares)", showgrid=True,
                            range=[0, L_max_plot / escala_L], row=1, col=2)
        fig_mt.update_yaxes(title_text="w/P — Salário Real", showgrid=True,
                            range=[0, a_ld * 1.1], row=1, col=2)

    fig_mt.update_layout(
        height=500, template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=-0.30, xanchor="center", x=0.5),
        margin=dict(t=60, b=100),
    )
    st.plotly_chart(fig_mt, use_container_width=True)

    # ══════════════════════════════════════════════════════════════
    # GRÁFICO — Lei de Okun
    # ══════════════════════════════════════════════════════════════
    st.divider()
    st.subheader("📉 Lei de Okun — Produto e Desemprego Cíclico")

    col_ok1, col_ok2 = st.columns([2, 1])
    with col_ok1:
        Y_range_ok  = np.linspace(Y_pleno * 0.7, Y_pleno * 1.15, 300)
        u_okun_line = u_natural - beta_okun * ((Y_range_ok - Y_pleno) / Y_pleno * 100)
        fig_ok = go.Figure()
        fig_ok.add_trace(go.Scatter(
            x=Y_range_ok, y=u_okun_line,
            name="Curva de Okun", line=dict(color="#7B1FA2", width=3),
        ))
        fig_ok.add_trace(go.Scatter(
            x=[Y_atual], y=[u_efetivo],
            mode="markers+text", name=f"Situação Atual (u={u_efetivo:.2f}%)",
            marker=dict(color="#E53935", size=13),
            text=[f"u={u_efetivo:.1f}%"], textposition="top right",
            textfont=dict(size=13),
        ))
        fig_ok.add_vline(x=Y_pleno, line=dict(color="green", dash="dash", width=2),
                         annotation_text=f"Yₙ={Y_pleno:.0f}", annotation_position="top right")
        fig_ok.add_hline(y=u_natural, line=dict(color="gray", dash="dot", width=1.5),
                         annotation_text=f"uₙ={u_natural:.1f}%", annotation_position="right")
        fig_ok.update_layout(
            height=340, template="plotly_white",
            xaxis_title="Produto (Y)", yaxis_title="Taxa de Desemprego (%)",
            title="Lei de Okun: Δu = −β × (ΔY/Yₙ)",
        )
        st.plotly_chart(fig_ok, use_container_width=True)

    with col_ok2:
        st.markdown("### 🔢 Decomposição do Desemprego")
        st.metric("Taxa Natural (uₙ)",       f"{u_natural:.1f}%")
        st.metric("Componente Cíclico",      f"{u_ciclico:+.2f} p.p.",
                  delta="Recessão" if u_ciclico > 0 else "Expansão",
                  delta_color="inverse")
        st.metric("Taxa Efetiva (u)",        f"{u_efetivo:.2f}%")
        st.metric("Hiato do Produto (Y−Yₙ)", f"{gap_produto:+.0f}",
                  delta=f"{gap_pct:+.1f}%", delta_color="normal")
        if gap_pct < -2:   st.error("🔴 **Recessão profunda**")
        elif gap_pct < 0:  st.warning("🟡 **Hiato negativo**")
        elif gap_pct > 2:  st.info("🔵 **Sobreaquecimento**")
        else:              st.success("🟢 **Próximo ao pleno emprego**")

    # ══════════════════════════════════════════════════════════════
    # ABAS ANALÍTICAS
    # ══════════════════════════════════════════════════════════════
    st.divider()
    st.subheader("🔬 Decomposição Analítica")

    aba1, aba2, aba3, aba4, aba5 = st.tabs([
        "⚖️ Equilíbrio do Mercado de Trabalho",
        "🚫 Desemprego Involuntário (Piso Salarial)",
        "📉 Lei de Okun e Desemprego Cíclico",
        "🔗 Integração OA-DA",
        "📘 Fundamentos Teóricos",
    ])

    with aba1:
        _aba_equilibrio(a_ld, b_ld, c_ls, d_ls, L_eq, w_eq, escala_L)

    with aba2:
        _aba_piso_salarial(a_ld, b_ld, c_ls, d_ls, w_min, w_eq,
                           L_eq, L_dem_wmin, L_ofe_wmin, desemprego_piso, escala_L)

    with aba3:
        _aba_okun(beta_okun, Y_atual, Y_pleno, gap_pct, u_ciclico, u_efetivo, u_natural)

    with aba4:
        _aba_integracao_oa_da(Y_atual, Y_pleno, gap_pct, u_ciclico, u_efetivo, u_natural, beta_okun)

    with aba5:
        _aba_fundamentos(a_ld, b_ld, c_ls, d_ls, L_eq, w_eq,
                         w_min, L_dem_wmin, L_ofe_wmin, desemprego_piso,
                         beta_okun, Y_atual, Y_pleno, gap_pct, u_ciclico,
                         u_efetivo, u_natural, escala_L)


# ══════════════════════════════════════════════════════════════════
# FUNÇÕES INTERNAS DE CADA ABA
# ══════════════════════════════════════════════════════════════════

def _aba_equilibrio(a_ld, b_ld, c_ls, d_ls, L_eq, w_eq, escala_L) -> None:
    st.markdown("**Cálculo analítico do equilíbrio:**")
    st.latex(
        rf"L^D = L^S \;\Rightarrow\; {a_ld:.2f} - {b_ld:.3f}L = {c_ls:.2f} + {d_ls:.3f}L"
    )
    st.latex(
        rf"L^* = \frac{{{a_ld:.2f} - {c_ls:.2f}}}{{{b_ld:.3f} + {d_ls:.3f}}} = {L_eq/escala_L:.3f} \text{{ mil trabalhadores}}"
    )
    st.latex(
        rf"\frac{{w^*}}{{P}} = {c_ls:.2f} + {d_ls:.3f} \times {L_eq:.0f} = {w_eq:.2f}"
    )
    st.markdown(f"""
No equilíbrio walrasiano, **toda a oferta de trabalho é absorvida** pela demanda das empresas.
O salário real $w^*/P = {w_eq:.2f}$ iguala o **Produto Marginal do Trabalho (PMgL)**
ao **salário de reserva** dos trabalhadores.

- **PMgL decrescente** (inclinação negativa de $L^D$): cada trabalhador adicional contribui
  menos ao produto — reflexo da lei dos rendimentos decrescentes.
- **Oferta crescente** (inclinação positiva de $L^S$): trabalhadores exigem salários maiores
  para abrir mão do lazer adicional — custo de oportunidade crescente.
""")


def _aba_piso_salarial(
    a_ld, b_ld, c_ls, d_ls, w_min, w_eq,
    L_eq, L_dem_wmin, L_ofe_wmin, desemprego_piso, escala_L,
) -> None:
    st.markdown("**Efeito do piso salarial sobre o emprego:**")
    st.latex(
        rf"L^D(\bar{{w}}/P) = \frac{{{a_ld:.2f} - {w_min:.2f}}}{{{b_ld:.3f}}} = {L_dem_wmin/escala_L:.3f} \text{{ mil}}"
    )
    st.latex(
        rf"L^S(\bar{{w}}/P) = \frac{{{w_min:.2f} - {c_ls:.2f}}}{{{d_ls:.3f}}} = {L_ofe_wmin/escala_L:.3f} \text{{ mil}}"
    )
    st.latex(
        rf"\text{{Desemprego}} = L^S - L^D = {L_ofe_wmin/escala_L:.3f} - {L_dem_wmin/escala_L:.3f} = {desemprego_piso/escala_L:.3f} \text{{ mil}}"
    )
    if w_min > w_eq:
        st.markdown(f"""
**Por que o piso salarial gera desemprego?**

Com $\\bar{{w}}/P = {w_min:.2f} > w^*/P = {w_eq:.2f}$:

1. **Empresas** reduzem contratações: o custo do trabalho supera o PMgL para os
   trabalhadores marginais → $L^D$ cai de {L_eq/escala_L:.2f} para {L_dem_wmin/escala_L:.2f} mil.
2. **Trabalhadores** aumentam a oferta: o salário mais alto atrai mais pessoas ao
   mercado → $L^S$ sobe de {L_eq/escala_L:.2f} para {L_ofe_wmin/escala_L:.2f} mil.
3. **Resultado:** {desemprego_piso/escala_L:.2f} mil trabalhadores **querem trabalhar ao salário
   vigente mas não encontram emprego** — definição clássica de desemprego involuntário (Keynes).

> 💡 Este é o argumento neoclássico contra o salário mínimo. A resposta keynesiana
> é que, com demanda agregada insuficiente, o problema não é o salário — é o nível de Y.
""")
    else:
        st.success(
            f"O piso salarial ({w_min:.2f}) está abaixo do equilíbrio ({w_eq:.2f}). "
            "Não é restritivo — o mercado opera livremente no equilíbrio walrasiano."
        )


def _aba_okun(beta_okun, Y_atual, Y_pleno, gap_pct, u_ciclico, u_efetivo, u_natural) -> None:
    st.markdown("**A Lei de Okun — formulação empírica:**")
    st.latex(r"\Delta u = -\beta \cdot \frac{Y - Y_n}{Y_n} \times 100")
    st.latex(
        rf"\Delta u = -{beta_okun:.2f} \times \frac{{{Y_atual:.0f} - {Y_pleno:.0f}}}{{{Y_pleno:.0f}}} \times 100 = {u_ciclico:+.2f} \text{{ p.p.}}"
    )
    st.latex(
        rf"u = u_n + \Delta u = {u_natural:.1f}\% + ({u_ciclico:+.2f}) = {u_efetivo:.2f}\%"
    )
    st.markdown(f"""
**Interpretação com os parâmetros atuais:**

- O produto atual ($Y = {Y_atual:.0f}$) está **{abs(gap_pct):.1f}%
  {'abaixo' if gap_pct < 0 else 'acima'}** do produto de pleno emprego ($Y_n = {Y_pleno:.0f}$).
- Pelo coeficiente de Okun $\\beta = {beta_okun:.2f}$, isso implica um desemprego cíclico
  de **{u_ciclico:+.2f} p.p.** em relação à taxa natural.
- A taxa efetiva de desemprego é **{u_efetivo:.2f}%**
  ({'acima' if u_efetivo > u_natural else 'abaixo'} da taxa natural de {u_natural:.1f}%).

> 📌 **Calibração histórica:** Okun estimou $\\beta \\approx 0.3$ para os EUA.
> Para economias emergentes, $\\beta$ tende a ser menor (mercados menos flexíveis,
> maior informalidade). Para o Brasil: $\\beta \\approx 0.15$ a $0.25$.
""")


def _aba_integracao_oa_da(
    Y_atual, Y_pleno, gap_pct, u_ciclico, u_efetivo, u_natural, beta_okun,
) -> None:
    st.markdown("""
### Integração com o Modelo OA-DA

O mercado de trabalho é o **elo de transmissão** entre o produto agregado ($Y$)
e a inflação ($\\pi$) no modelo OA-DA:
""")
    st.latex(r"Y \xrightarrow{\text{Okun}} u \xrightarrow{\text{Phillips}} \pi \xrightarrow{\text{Fisher}} r \xrightarrow{\text{IS}} Y")

    gap_produto = Y_atual - Y_pleno
    st.markdown(f"""
**Cadeia causal com os valores atuais:**

| Variável | Valor | Interpretação |
|---|---|---|
| Produto Atual ($Y$) | {Y_atual:.0f} | Demanda Agregada realizada |
| Produto Potencial ($Y_n$) | {Y_pleno:.0f} | Oferta Agregada de longo prazo |
| Hiato do Produto | {gap_pct:+.1f}% | {'Recessivo' if gap_pct < 0 else 'Inflacionário'} |
| Desemprego Cíclico | {u_ciclico:+.2f} p.p. | Via Lei de Okun |
| Taxa de Desemprego Efetiva | {u_efetivo:.2f}% | $u_n$ + componente cíclico |

**Tipos de desemprego no modelo:**
- 🔵 **Friccional:** Tempo de busca entre empregos — componente de $u_n$
- 🟡 **Estrutural:** Incompatibilidade de habilidades — componente de $u_n$
- 🔴 **Cíclico:** Insuficiência de demanda agregada — $\\Delta u$ via Okun
- 🟠 **Involuntário (Keynes):** Piso salarial acima do equilíbrio

**Política econômica:**
- Para reduzir o desemprego **cíclico**: política fiscal expansionista ($\\uparrow G$)
  ou monetária ($\\uparrow M$) → $\\uparrow Y$ → $\\downarrow u$
- Para reduzir o desemprego **estrutural/friccional**: políticas de oferta
  (educação, retreinamento, mobilidade laboral)
""")
    st.latex(
        r"\underbrace{u_{\text{efetivo}}}_{" + f"{u_efetivo:.2f}\\%" + r"} = "
        r"\underbrace{u_n}_{" + f"{u_natural:.1f}\\%" + r"} + "
        r"\underbrace{\Delta u_{\text{cíclico}}}_{" + f"{u_ciclico:+.2f}" + r"\text{ p.p.}}"
    )


def _aba_fundamentos(
    a_ld, b_ld, c_ls, d_ls, L_eq, w_eq,
    w_min, L_dem_wmin, L_ofe_wmin, desemprego_piso,
    beta_okun, Y_atual, Y_pleno, gap_pct, u_ciclico,
    u_efetivo, u_natural, escala_L,
) -> None:
    st.markdown("### 📘 Fundamentos Teóricos do Mercado de Trabalho")

    # ── 1. Curvas ─────────────────────────────────────────────────
    st.markdown("#### 1. O Mercado de Trabalho como Mercado de Oferta e Demanda")
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        st.markdown(f"""
**📉 Demanda por Trabalho — $L^D = \\frac{{a - w/P}}{{b}}$**

Representa as **empresas** decidindo quantos trabalhadores contratar.
A empresa maximiza lucro contratando até onde $PMgL = w/P$:

- **PMgL decrescente**: o $n$-ésimo trabalhador produz menos que o anterior
  (rendimentos decrescentes).
- Intercepto $a = {a_ld:.2f}$: PMgL máximo (com $L=0$).
- Inclinação $b = {b_ld:.3f}$: velocidade de queda do PMgL.

> 💡 Uma fábrica com 10 máquinas: o 11º trabalhador não tem máquina disponível
> e produz pouco — só vale contratar se o salário for baixo.
""")
    with col_f2:
        st.markdown(f"""
**📈 Oferta de Trabalho — $L^S = \\frac{{w/P - c}}{{d}}$**

Representa os **trabalhadores** decidindo quanto trabalhar.
Cada trabalhador escolhe entre **consumo** (requer trabalho) e **lazer**.

- **Custo de oportunidade crescente**: cada hora adicional sacrifica lazer
  cada vez mais valioso.
- Salário de reserva $c = {c_ls:.2f}$: abaixo disso, ninguém trabalha.
- Inclinação $d = {d_ls:.3f}$: quanto o salário precisa subir para atrair
  mais trabalhadores.

> 💡 Com salário baixo, só quem precisa muito trabalha. Com salário alto,
> até quem preferia estudar entra no mercado.
""")

    st.divider()

    # ── 2. Salário Real vs Nominal ────────────────────────────────
    st.markdown("#### 2. Por que usamos Salário Real e não Nominal?")
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.markdown("""
**💵 Salário Nominal ($w$)**
- Valor em reais no contracheque
- Pode subir sem que o trabalhador fique mais rico
- Relevante para contratos e obrigações nominais
- **Ilusão monetária:** confundir aumento nominal com real
""")
    with col_r2:
        st.markdown("""
**🛒 Salário Real ($w/P$)**
- Poder de compra do salário — quantos bens ele compra
- **É o que realmente importa** para decisões de trabalho e consumo
- Se $P$ dobra e $w$ dobra, o salário real não mudou
- Usado em todos os modelos de equilíbrio geral
""")
    st.latex(
        r"\text{Salário Real} = \frac{w}{P} \qquad \Rightarrow \qquad "
        r"\frac{\Delta(w/P)}{w/P} = \frac{\Delta w}{w} - \frac{\Delta P}{P} = "
        r"\text{crescimento nominal} - \pi"
    )

    st.divider()

    # ── 3. Tipos de Desemprego ────────────────────────────────────
    st.markdown("#### 3. Taxonomia Completa do Desemprego")
    dados_desemp = {
        "Tipo": ["Friccional", "Estrutural", "Cíclico (Keynesiano)", "Involuntário (Keynes)", "Sazonal"],
        "Causa": [
            "Tempo de busca entre empregos",
            "Incompatibilidade de habilidades com vagas disponíveis",
            "Insuficiência de Demanda Agregada (Y < Yₙ)",
            "Salário acima do equilíbrio (piso salarial)",
            "Variações sazonais na demanda por trabalho",
        ],
        "Componente": ["uₙ", "uₙ", "Δu via Okun", "LS − LD", "uₙ (parcial)"],
        "Política Adequada": [
            "Agências de emprego, informação de mercado",
            "Educação, retreinamento, mobilidade",
            "Política fiscal/monetária expansionista",
            "Debate: flexibilizar salários vs. estimular DA",
            "Seguro-desemprego, programas temporários",
        ],
    }
    st.dataframe(pd.DataFrame(dados_desemp), use_container_width=True, hide_index=True)

    st.latex(
        r"u_{\text{total}} = \underbrace{u_n}_{\text{friccional + estrutural}}"
        r"+ \underbrace{\Delta u_{\text{cíclico}}}_{\text{via Okun}}"
        r"+ \underbrace{(L^S - L^D)/\bar{L}}_{\text{involuntário (piso)}}"
    )

    st.divider()

    # ── 4. Debate Neoclássico vs Keynesiano ───────────────────────
    st.markdown("#### 4. O Grande Debate: Neoclássicos vs. Keynesianos")
    col_nc, col_kn = st.columns(2)
    with col_nc:
        st.markdown("""
**🏛️ Visão Neoclássica**
- O mercado se equilibra **automaticamente** via ajuste de salários.
- Desemprego é **voluntário** — quem está desempregado escolhe não trabalhar
  ao salário de mercado.
- Desemprego involuntário só existe com **rigidez salarial**.
- **Política:** remover rigidezes, flexibilizar o mercado.
- Curva OA de longo prazo é **vertical** em $Y_n$.

> 📌 Representantes: Pigou, Lucas, Prescott (RBC)
""")
    with col_kn:
        st.markdown("""
**🔵 Visão Keynesiana**
- Salários são **rígidos para baixo** (trabalhadores resistem a cortes nominais).
- Desemprego pode ser **involuntário** — o problema é a **demanda insuficiente**.
- Mesmo sem piso salarial, a economia pode ficar com desemprego.
- **Política:** estimular DA ($\\uparrow G$, $\\uparrow M$) → $\\uparrow Y$ → $\\downarrow u$.
- Curva OA de curto prazo é **positivamente inclinada**.

> 📌 Representantes: Keynes, Hicks, Samuelson, Mankiw (NK)
""")
    st.info("""
💡 **Síntese Moderna:** Os modelos atuais combinam rigidez nominal de curto prazo
(Keynesiano) com equilíbrio de longo prazo (Neoclássico). No curto prazo, choques de
demanda afetam $Y$ e $u$; no longo prazo, a economia retorna a $Y_n$ e $u_n$.
""")

    st.divider()

    # ── 5. Resumo das Equações ────────────────────────────────────
    st.markdown("#### 5. 📐 Resumo das Equações do Módulo")
    st.markdown("**Equilíbrio Walrasiano:**")
    st.latex(r"L^* = \frac{a - c}{b + d} \qquad \frac{w^*}{P} = c + d \cdot L^*")
    st.markdown("**Desemprego pelo Piso Salarial:**")
    st.latex(
        r"L^D(\bar{w}/P) = \frac{a - \bar{w}/P}{b} \qquad "
        r"L^S(\bar{w}/P) = \frac{\bar{w}/P - c}{d} \qquad "
        r"U_{inv} = \max(L^S - L^D,\; 0)"
    )
    st.markdown("**Lei de Okun:**")
    st.latex(
        r"\Delta u = -\beta \cdot \frac{Y - Y_n}{Y_n} \times 100 \qquad "
        r"u = u_n + \Delta u"
    )
    st.markdown("**Cadeia de Transmissão Completa:**")
    st.latex(
        r"\uparrow G \;\xrightarrow{\times \frac{1}{1-c_1(1-t)}}\; \uparrow Y "
        r"\;\xrightarrow{\text{Okun}}\; \downarrow u "
        r"\;\xrightarrow{\text{Phillips}}\; \downarrow \pi "
        r"\;\xrightarrow{\text{Fisher}}\; \downarrow r "
        r"\;\xrightarrow{\text{IS}}\; \uparrow Y \;\text{(2ª rodada)}"
    )
    st.caption(
        "Todas as equações são calculadas dinamicamente com os parâmetros dos sliders."
    )