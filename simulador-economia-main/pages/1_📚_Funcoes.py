# pages/1_📚_Funcoes.py
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from core.parameters import DEFAULT_PARAMS
from models.funcoes.consumo import (
    resolver_consumo, resolver_poupanca,
    multiplicador_fiscal, multiplicador_imposto,
    calcular_ponto_equilibrio, analise_proporcional
)

st.set_page_config(layout="wide", page_title="Simulador Macro UFRRJ")

# ── 1. Estado global ──────────────────────────────────────────────
if "params" not in st.session_state:
    st.session_state.params = DEFAULT_PARAMS.copy()

novos_campos = {
    "t": 0.2, "theta": 10.0, "m": 0.1, "r": 0.05,
    "W": 1000.0, "alpha_w": 0.05
}
for chave, valor in novos_campos.items():
    if chave not in st.session_state.params:
        st.session_state.params[chave] = valor

p = st.session_state.params

# ── 2. Grid de renda ──────────────────────────────────────────────
Y_grid = np.linspace(100, 2500, 300)

# ── 3. Cabeçalho ──────────────────────────────────────────────────
st.title("📚 Funções Macroeconômicas")
st.caption("Simulador de Equilíbrio Geral e Funções de Comportamento - UFRRJ")

funcao = st.selectbox("Selecione a função para análise detalhada:", [
    "Consumo", "Poupança", "Investimento", "Demanda por Moeda",
    "Oferta de Moeda", "Demanda Agregada", "Oferta Agregada", "Produção",
    "Oferta e Demanda", "Mercado de Trabalho"
])

st.divider()

# ── 4. Seção: CONSUMO ─────────────────────────────────────────────
if funcao == "Consumo":
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("🛠️ Parâmetros")
        c0      = st.slider("Consumo Autônomo (c0)",            0.0,   500.0, float(p["c0"]),      10.0)
        c1      = st.slider("Propensão Marginal a Consumir (c1)", 0.01, 0.99,  float(p["c1"]),      0.01)

        st.write("**🏛️ Política Fiscal**")
        T_fixo  = st.slider("Imposto Fixo (T)",                 0.0,   500.0, float(p["T"]),       10.0)
        t_aliq  = st.slider("Alíquota sobre Renda (t)",         0.0,   0.5,   float(p["t"]),       0.05)

        st.write("**🌐 Transmissão e Riqueza**")
        W_riqueza = st.slider("Riqueza das Famílias (W)",       0.0,  5000.0, float(p["W"]),      100.0)
        alpha_w   = st.slider("Efeito Riqueza (αw)",            0.0,   0.15,  float(p["alpha_w"]), 0.01)
        theta     = st.slider("Sensibilidade a Juros (θ)",      0.0,  100.0,  float(p["theta"]),   5.0)

        p.update({
            "c0": c0, "c1": c1, "T": T_fixo, "t": t_aliq,
            "W": W_riqueza, "alpha_w": alpha_w, "theta": theta
        })

        y_star  = calcular_ponto_equilibrio(c0, c1, T_fixo, t_aliq, p["r"], theta, W_riqueza, alpha_w)
        m_fisc  = multiplicador_fiscal(c1, t=t_aliq, m=p["m"])

        st.divider()
        st.subheader("📊 Indicadores")
        st.metric("Multiplicador da Economia", f"{m_fisc:.3f}")
        if y_star and y_star > 0:
            st.metric("Renda de Equilíbrio (S=0)", f"{y_star:.2f}")

    with col2:
        C, eq_c = resolver_consumo(
            Y_grid, c0, c1, T_fixo,
            t=t_aliq, r=p["r"], theta=theta,
            W=W_riqueza, alpha_w=alpha_w
        )
        S        = resolver_poupanca(Y_grid, c0, c1, T_fixo, t=t_aliq, r=p["r"], theta=theta, W=W_riqueza, alpha_w=alpha_w)
        pmec_grid = analise_proporcional(Y_grid, C)

        # Gráfico 1 e 2: Cruzamento Keynesiano + Poupança
        fig = make_subplots(rows=1, cols=2,
                            subplot_titles=("Cruzamento Keynesiano", "Função Poupança"))

        fig.add_trace(go.Scatter(x=Y_grid, y=C,      name="Consumo",
                                 line=dict(color="#1565c0", width=3)), row=1, col=1)
        fig.add_trace(go.Scatter(x=Y_grid, y=Y_grid, name="Y = DA",
                                 line=dict(dash="dash", color="gray", width=1)), row=1, col=1)

        if y_star and y_star > 0:
            fig.add_trace(go.Scatter(
                x=[y_star], y=[y_star],
                mode="markers+text", name="Equilíbrio",
                text=[f"Y*={y_star:.0f}"], textposition="top left",
                marker=dict(color="red", size=10, symbol="diamond")
            ), row=1, col=1)

        fig.add_trace(go.Scatter(x=Y_grid, y=S, name="Poupança",
                                 line=dict(color="#2e7d32", width=3)), row=1, col=2)
        fig.add_hline(y=0, line=dict(color="black", width=1), row=1, col=2)

        fig.update_layout(height=380, template="plotly_white", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

        # Gráfico 3: Propensões
        st.subheader("📈 Dinâmica das Propensões")
        fig_p = go.Figure()
        fig_p.add_trace(go.Scatter(x=Y_grid, y=pmec_grid, name="PMeC",
                                   fill='tozeroy', line=dict(color="orange")))
        fig_p.add_hline(y=c1, line=dict(dash="dash", color="red"),
                        annotation_text=f"PMgC ({c1})")
        fig_p.update_layout(height=280, template="plotly_white",
                             xaxis_title="Renda (Y)", yaxis_title="Propensão")
        st.plotly_chart(fig_p, use_container_width=True)

    # ── 5. Abas de Análise ────────────────────────────────────────
    st.divider()
    st.subheader("🔬 Decomposição Analítica da Simulação")

    aba1, aba2, aba3, aba4 = st.tabs([
        "Interseção de Equilíbrio",
        "Mecânica da Riqueza (W)",
        "Transmissão de Juros (θ)",
        "📘 Consumo Expandido"          # ← NOVA ABA
    ])

    with aba1:
        st.write(f"""
        **O Ponto de Break-even e o Ajuste de Estoques:**
        No nível de renda $Y^* = {y_star:.2f}$, a economia atinge o equilíbrio de fluxo.
        Analiticamente, este é o ponto onde a **Poupança Agregada ($S$) é nula**.
        - **À esquerda de $Y^*$:** Há um excesso de demanda ($C > Y$). As famílias estão
          'despoupando', o que resulta em redução involuntária de estoques, sinalizando
          aumento de produção.
        - **À direita de $Y^*$:** A propensão marginal a poupar drena a demanda, gerando
          acúmulo de estoques e pressões recessivas sobre o produto real.
        """)

    with aba2:
        st.write(f"""
        **O Efeito Riqueza ($\\alpha_w W$):**
        Diferente do modelo de renda corrente, incluímos a riqueza ($W = {W_riqueza}$)
        como determinante estrutural. Este parâmetro atua como um **deslocador vertical
        (shift)** da função consumo.
        - Um choque positivo na riqueza eleva o intercepto da curva sem alterar sua inclinação.
        - Isso desloca o equilíbrio $Y^*$ para a direita através do efeito multiplicador,
          evidenciando como variações no patrimônio das famílias impactam o PIB.
        """)

    with aba3:
        st.write(f"""
        **A Sensibilidade à Taxa de Juros ($\\theta r$):**
        A variável $\\theta = {theta}$ integra o mercado de bens ao mercado monetário
        (conexão IS).
        - Sob a ótica da Síntese Neoclássica, o consumo possui um custo de oportunidade
          definido pela taxa $r = {p['r']*100:.1f}\\%$.
        - Elevações nos juros provocam uma contração de **{theta * p['r']:.2f}** unidades
          no consumo autônomo, "empurrando" a curva para baixo e reduzindo a renda de
          equilíbrio.
        """)

    # ── ABA 4: CONSUMO EXPANDIDO (NOVA) ──────────────────────────
    with aba4:
        # Valores calculados para esta aba
        mult          = 1.0 / max(1 - c1 * (1 - t_aliq), 1e-9)   # multiplicador com alíquota
        mult_simples  = 1.0 / max(1 - c1, 1e-9)                   # sem alíquota (referência)
        efeito_riqueza = alpha_w * W_riqueza
        C_expandido   = c0 + c1 * (y_star - T_fixo) + efeito_riqueza if y_star else 0
        C_simples     = c0 + c1 * (y_star - T_fixo)               if y_star else 0

        # ── Seção 1: A Fórmula ────────────────────────────────────
        st.markdown("### 1. A Fórmula Completa")
        st.latex(r"C = c_0 + c_1(Y - T) + \alpha_w W")

        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Consumo Autônomo (c₀)", f"{c0:.2f}")
            st.caption("Consumo independente da renda")
        with m2:
            st.metric("Propensão Marginal (c₁)", f"{c1:.3f}")
            st.caption("Fração da renda disponível consumida")
        with m3:
            st.metric("Efeito Riqueza (αw × W)", f"{efeito_riqueza:.2f}")
            st.caption("Contribuição da riqueza ao consumo")

        if y_star and y_star > 0:
            st.info(
                f"**Com os parâmetros atuais em Y\\* = {y_star:.1f}:** "
                f"C = {c0:.1f} + {c1:.2f}×(Y−{T_fixo:.0f}) + {alpha_w:.3f}×{W_riqueza:.0f} "
                f"= **{C_expandido:.2f}** "
                f"(vs {C_simples:.2f} sem efeito riqueza — diferença de {efeito_riqueza:.2f})"
            )

        st.divider()

        # ── Seção 2: Interpretação dos Parâmetros ─────────────────
        st.markdown("### 2. Interpretação dos Parâmetros Atuais")

        # c1
        c1_mais5 = 1.0 / max(1 - (c1 + 0.05) * (1 - t_aliq), 1e-9)
        st.markdown(f"""
**📌 Propensão Marginal a Consumir — $c_1 = {c1:.3f}$**
- A cada R\\$ 1,00 adicional de **renda disponível** $(Y - T)$, as famílias gastam
  **R\\$ {c1:.2f}** em consumo e poupam **R\\$ {1-c1:.2f}**.
- {"⚠️ **Valor alto (> 0,75):** economia com forte propensão ao consumo — multiplicador elevado e maior sensibilidade a choques." if c1 > 0.75 else "✅ **Valor moderado:** equilíbrio saudável entre consumo e poupança."}
- **Se você aumentar $c_1$ em +0,05:** o multiplicador passaria de **{mult:.3f}** para
  **{c1_mais5:.3f}** — amplificando qualquer choque de demanda em {((c1_mais5/mult)-1)*100:.1f}%.
""")

        # alpha_w e W
        st.markdown(f"""
**💰 Efeito Riqueza — $\\alpha_w = {alpha_w:.3f}$, $W = {W_riqueza:.1f}$**
- A cada R\\$ 1,00 de **riqueza acumulada** (ações, imóveis, poupança), as famílias
  consomem R\\$ {alpha_w:.3f} a mais.
- Com $W = {W_riqueza:.1f}$, o efeito riqueza total é:
""")
        st.latex(rf"\alpha_w \times W = {alpha_w:.3f} \times {W_riqueza:.1f} = {efeito_riqueza:.2f}")
        if W_riqueza == 0:
            st.warning("⚠️ **Riqueza = 0:** o efeito riqueza está desativado. "
                       "Aumente W para ver o deslocamento da curva IS.")
        else:
            st.success(f"✅ A riqueza está contribuindo com **{efeito_riqueza:.2f}** "
                       f"unidades ao consumo autônomo efetivo.")
        st.markdown(f"""
- **Se você aumentar $W$:** o consumo autônomo efetivo sobe, deslocando a curva IS
  para a **direita** → $Y^*$ aumenta via multiplicador ({mult:.3f}×ΔW×αw).
- **Se você aumentar $\\alpha_w$:** o mesmo estoque de riqueza passa a gerar mais
  consumo — efeito análogo a uma redução da propensão a poupar.
""")

        st.divider()

        # ── Seção 3: Renda vs Riqueza ──────────────────────────────
        st.markdown("### 3. 📊 Renda (Fluxo) vs Riqueza (Estoque)")

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("""
**🔄 Renda — Variável de Fluxo**
- Medida **por período** (mês, trimestre, ano)
- Exemplos: salário, lucros, aluguéis recebidos
- Na fórmula: $Y - T$ (renda disponível após impostos)
- Desaparece se não for renovada no próximo período
- Unidade: R\\$/ano
""")
        with col_b:
            st.markdown("""
**🏦 Riqueza — Variável de Estoque**
- Medida em um **ponto no tempo** (balanço patrimonial)
- Exemplos: saldo bancário, imóveis, carteira de ações
- Na fórmula: $W$ (patrimônio líquido acumulado)
- Persiste entre períodos; muda via poupança ou valorização
- Unidade: R\\$ (sem dimensão temporal)
""")

        st.markdown("""
> 💡 **Analogia didática:** A renda é como a **água que entra** numa banheira (fluxo por
> unidade de tempo). A riqueza é o **volume de água** que já está dentro dela (estoque
> num instante). Você pode ter uma banheira cheia (rico) mesmo com a torneira fechada
> (sem renda no momento) — e vice-versa: alto fluxo de renda com riqueza próxima de zero
> se toda a renda for consumida.
""")

        st.divider()

        # ── Seção 4: O Multiplicador ───────────────────────────────
        st.markdown("### 4. ⚡ O Multiplicador Keynesiano")

        st.markdown("**Fórmula geral com alíquota sobre a renda:**")
        st.latex(
            r"\text{Multiplicador} = \frac{1}{1 - c_1(1-t)} = \frac{1}{1 - "
            + f"{c1:.2f}(1-{t_aliq:.2f})"
            + r"} = "
            + f"{mult:.4f}"
        )

        st.markdown("**Fórmula simplificada (sem alíquota, referência clássica):**")
        st.latex(
            r"\frac{1}{1 - c_1} = \frac{1}{1 - "
            + f"{c1:.2f}"
            + r"} = "
            + f"{mult_simples:.4f}"
        )

        st.markdown(f"""
**Por que o multiplicador é {mult:.3f}?**

Imagine que o governo aumenta os gastos em **ΔG = 100**:

1. **1ª rodada:** Empresas recebem +100 → pagam salários → renda disponível sobe
2. **2ª rodada:** Famílias gastam $c_1(1-t) \\times 100 = {c1*(1-t_aliq)*100:.1f}$ → nova demanda
3. **3ª rodada:** Esse consumo gera mais {(c1*(1-t_aliq))**2 * 100:.1f} de renda...
4. **...convergência:** série geométrica com razão $c_1(1-t) = {c1*(1-t_aliq):.3f} < 1$
""")

        st.latex(
            r"\Delta Y^* = \frac{1}{1-c_1(1-t)} \times \Delta G = "
            + f"{mult:.3f} \\times 100 = {mult*100:.1f}"
        )

        # Tabela de rodadas
        st.markdown("**Tabela das primeiras rodadas (ΔG = 100):**")
        rodadas, delta, acumulado = [], 100.0, 0.0
        razao = c1 * (1 - t_aliq)
        for i in range(1, 9):
            acumulado += delta
            rodadas.append({
                "Rodada": i,
                "Renda Gerada (ΔY)": f"{delta:.2f}",
                "Consumo Induzido": f"{delta * razao:.2f}",
                "Poupança + Imposto": f"{delta * (1 - razao):.2f}",
                "Acumulado ΔY": f"{acumulado:.2f}"
            })
            delta *= razao

        st.dataframe(pd.DataFrame(rodadas), use_container_width=True, hide_index=True)

        st.success(
            f"💡 **Conclusão:** Com $c_1 = {c1:.2f}$ e alíquota $t = {t_aliq:.2f}$, "
            f"um aumento de 100 no consumo autônomo (ou em G) resulta em "
            f"**ΔY\\* = {mult*100:.1f}** — ou seja, **{mult:.2f}× o choque original**. "
            f"A alíquota reduz o multiplicador de {mult_simples:.3f} (sem imposto) "
            f"para {mult:.3f} (com imposto), pois parte da renda 'vaza' para o governo."
        )

        st.divider()

        # ── Seção 5: Resumo das Equações ───────────────────────────
        st.markdown("### 5. 📐 Resumo das Equações")

        st.latex(
            r"C = \underbrace{c_0}_{\text{autônomo}}"
            r"+ \underbrace{c_1(Y-T)}_{\text{renda disponível}}"
            r"+ \underbrace{\alpha_w W}_{\text{efeito riqueza}}"
        )
        st.latex(
            r"Y^* = \frac{1}{1-c_1(1-t)}"
            r"\left(c_0 - c_1 T + I_0 + G + \alpha_w W\right)"
        )
        st.latex(
            r"\frac{\partial Y^*}{\partial G} = "
            r"\frac{\partial Y^*}{\partial c_0} = "
            r"\frac{1}{1-c_1(1-t)} = "
            + f"{mult:.4f}"
        )
        st.latex(
            r"\frac{\partial Y^*}{\partial T} = "
            r"\frac{-c_1}{1-c_1(1-t)} = "
            + f"{-c1*mult:.4f}"
        )
        st.latex(
            r"\frac{\partial Y^*}{\partial W} = "
            r"\frac{\alpha_w}{1-c_1(1-t)} = "
            + f"{alpha_w*mult:.4f}"
        )

        st.caption(
            "Todas as derivadas parciais acima são calculadas dinamicamente "
            "com os valores atuais dos sliders."
        )

    st.info(f"**Equação de Consumo Atualizada:** ${eq_c}$")

# ── Seção: OFERTA E DEMANDA ───────────────────────────────────────
elif funcao == "Oferta e Demanda":

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

    # ── Controles ────────────────────────────────────────────────
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
        mostrar_tabelado = st.checkbox("Mostrar cenário com preço tabelado", value=True, key="od_show")

    # ── Cálculos ─────────────────────────────────────────────────
    # Equilíbrio: a - b*Q = c + d*Q  →  Q* = (a-c)/(b+d)
    denom = b_dem + d_ofe
    Q_eq  = max((a_dem - c_ofe) / denom, 0.0) if denom > 0 else 0.0
    P_eq  = c_ofe + d_ofe * Q_eq

    # Quantidades ao preço tabelado
    Q_dem_tab = max((a_dem - P_tabelado) / b_dem, 0.0) if b_dem > 0 else 0.0
    Q_ofe_tab = max((P_tabelado - c_ofe) / d_ofe, 0.0) if d_ofe > 0 else 0.0
    excesso   = Q_ofe_tab - Q_dem_tab   # >0 excesso de oferta; <0 escassez

    escala      = 1000          # Q em milhares no eixo
    Q_max_plot  = Q_eq * 2.2 if Q_eq > 0 else 2000.0
    Q_range     = np.linspace(0, Q_max_plot, 400)
    P_demanda   = a_dem - b_dem * Q_range
    P_oferta    = c_ofe + d_ofe * Q_range

    # ── Métricas ─────────────────────────────────────────────────
    st.markdown("### 📊 Equilíbrio de Mercado")
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Preço de Equilíbrio (P*)",    f"R$ {P_eq:.2f} mil")
    m2.metric("Quantidade de Equilíbrio (Q*)", f"{Q_eq/escala:.2f} mil")
    if mostrar_tabelado:
        m3.metric("Preço Tabelado (P̄)",      f"R$ {P_tabelado:.2f} mil")
        m4.metric("Qd ao P̄",                 f"{Q_dem_tab/escala:.2f} mil")
        m5.metric("Qs ao P̄",                 f"{Q_ofe_tab/escala:.2f} mil")
        if abs(excesso) > 10:
            tipo = "Excesso de Oferta" if excesso > 0 else "Escassez"
            st.info(f"**{tipo}:** |Qs − Qd| = {abs(excesso)/escala:.2f} mil unidades")

    # ── Gráficos ─────────────────────────────────────────────────
    n_cols  = 2 if mostrar_tabelado else 1
    titulo2 = (f"Preço Tabelado P̄={P_tabelado:.2f} → "
               f"{'Excesso de Oferta' if excesso > 0 else 'Escassez' if excesso < 0 else 'Equilíbrio'}"
               if mostrar_tabelado else "")

    fig_od = make_subplots(
        rows=1, cols=n_cols,
        subplot_titles=(
            f"Equilíbrio  (P*={P_eq:.2f}, Q*={Q_eq/escala:.0f} mil)",
            titulo2
        ) if mostrar_tabelado else (
            f"Equilíbrio  (P*={P_eq:.2f}, Q*={Q_eq/escala:.0f} mil)",
        ),
        horizontal_spacing=0.12
    )

    def _add_base(col):
        """Adiciona curvas base + ponto E + tracejados ao subplot `col`."""
        show = (col == 1)
        fig_od.add_trace(go.Scatter(
            x=Q_range / escala, y=P_demanda, name="Demanda",
            line=dict(color="#F44336", width=3), showlegend=show
        ), row=1, col=col)
        fig_od.add_trace(go.Scatter(
            x=Q_range / escala, y=P_oferta, name="Oferta",
            line=dict(color="#2196F3", width=3), showlegend=show
        ), row=1, col=col)
        fig_od.add_trace(go.Scatter(
            x=[Q_eq / escala], y=[P_eq],
            mode="markers+text", name="Equilíbrio (E)",
            marker=dict(color="#555", size=12),
            text=["E"], textposition="top right",
            textfont=dict(size=14), showlegend=show
        ), row=1, col=col)
        # tracejados P* e Q*
        for xv, yv, x0, y0 in [
            (Q_eq / escala, P_eq, 0, P_eq),
            (Q_eq / escala, P_eq, Q_eq / escala, 0)
        ]:
            fig_od.add_trace(go.Scatter(
                x=[x0, xv], y=[y0, yv],
                mode="lines", showlegend=False,
                line=dict(color="#888", width=1.2, dash="dash")
            ), row=1, col=col)

    _add_base(1)
    fig_od.update_xaxes(title_text="q (em milhares)", showgrid=True,
                        range=[0, Q_max_plot / escala], row=1, col=1)
    fig_od.update_yaxes(title_text="P (em R$ mil)", showgrid=True,
                        range=[0, a_dem * 1.1], row=1, col=1)

    if mostrar_tabelado:
        _add_base(2)

        # Linha do preço tabelado
        fig_od.add_trace(go.Scatter(
            x=[0, Q_max_plot / escala], y=[P_tabelado, P_tabelado],
            name=f"P̄ = {P_tabelado:.2f} (tabelado)",
            line=dict(color="#FF9800", width=2, dash="dot"), showlegend=True
        ), row=1, col=2)

        # Pontos Qd e Qs
        for Q_val, nome, cor in [
            (Q_dem_tab, f"Qd={Q_dem_tab/escala:.2f} mil", "#2196F3"),
            (Q_ofe_tab, f"Qs={Q_ofe_tab/escala:.2f} mil", "#F44336"),
        ]:
            fig_od.add_trace(go.Scatter(
                x=[Q_val / escala], y=[P_tabelado],
                mode="markers", name=nome,
                marker=dict(color=cor, size=11), showlegend=True
            ), row=1, col=2)
            fig_od.add_trace(go.Scatter(
                x=[Q_val / escala, Q_val / escala], y=[0, P_tabelado],
                mode="lines", showlegend=False,
                line=dict(color=cor, width=1.2, dash="dash")
            ), row=1, col=2)

        # Anotação de excesso / escassez
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
                font=dict(size=13, color=cor_a), row=1, col=2
            )

        fig_od.update_xaxes(title_text="q (em milhares)", showgrid=True,
                            range=[0, Q_max_plot / escala], row=1, col=2)
        fig_od.update_yaxes(title_text="P (em R$ mil)", showgrid=True,
                            range=[0, a_dem * 1.1], row=1, col=2)

    fig_od.update_layout(
        height=500, template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=-0.28, xanchor="center", x=0.5),
        margin=dict(t=60, b=90)
    )
    st.plotly_chart(fig_od, use_container_width=True)

    # ── Análise Narrativa ─────────────────────────────────────────
    st.divider()
    st.subheader("🔬 Decomposição Analítica")

    aba_od1, aba_od2, aba_od3, aba_od4 = st.tabs([
        "⚖️ Equilíbrio de Mercado",
        "💲 Efeito do Preço Tabelado",
        "📐 Elasticidades",
        "📘 Teoria Completa"
    ])

    with aba_od1:
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
restauradoras: se P > P*, produtores acumulam estoques e reduzem preços;
se P < P*, consumidores competem pelo bem escasso e elevam o preço.
""")

    with aba_od2:
        if not mostrar_tabelado:
            st.info("Ative 'Mostrar cenário com preço tabelado' para ver esta análise.")
        else:
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
- Com **preço mínimo (piso)** — ex: salário mínimo acima do equilíbrio — o excesso persiste
  e se manifesta como **desemprego** no mercado de trabalho.
""")
            else:
                st.markdown(f"""
**🔻 Escassez ({abs(excesso)/escala:.2f} mil unidades)**

Com P̄ = {P_tabelado:.2f} **abaixo** do equilíbrio (P* = {P_eq:.2f}):
- Consumidores demandam mais do que os produtores estão dispostos a ofertar.
- A escassez de {abs(excesso)/escala:.2f} mil unidades pressiona o preço para cima.
- Com **teto de preços** — ex: controle de aluguéis — a escassez persiste e pode
  gerar **filas, mercados paralelos e deterioração da qualidade**.
""")

    with aba_od3:
        # Elasticidades no equilíbrio (fórmula de arco no ponto)
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
                st.success(f"**Demanda elástica** (|ε| = {abs(eps_d):.2f} > 1): uma variação de 1% no preço gera {abs(eps_d):.2f}% de variação na quantidade demandada.")
            else:
                st.warning(f"**Demanda inelástica** (|ε| = {abs(eps_d):.2f} < 1): variações de preço têm impacto proporcionalmente menor na quantidade.")
        with col_eb:
            if eps_s > 1:
                st.success(f"**Oferta elástica** (ε = {eps_s:.2f} > 1): produtores respondem fortemente a variações de preço.")
            else:
                st.warning(f"**Oferta inelástica** (ε = {eps_s:.2f} < 1): produtores têm capacidade limitada de ajuste no curto prazo.")

    # ── ABA 4: TEORIA COMPLETA ────────────────────────────────────
    with aba_od4:
        st.markdown("### 📘 Teoria Completa de Oferta e Demanda")

        # ── Bloco 1: O que são as curvas ──────────────────────────
        st.markdown("#### 1. O que representam as curvas?")
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.markdown("""
**📉 Curva de Demanda — $P^D = a - b \\cdot Q$**

Representa o comportamento dos **consumidores**. Ela é **negativamente inclinada** porque:

- Quanto **maior o preço**, menor a quantidade que os consumidores desejam comprar
  (efeito substituição + efeito renda).
- O parâmetro **$a$** é o preço máximo que alguém pagaria — chamado de
  **preço de reserva do consumidor** (quando $Q = 0$).
- O parâmetro **$b$** mede a **sensibilidade da demanda ao preço**: quanto maior $b$,
  mais os consumidores reagem a variações de preço.

> 💡 **Intuição:** Se o preço do café dobrar, você compra menos café e talvez
> substitua por chá. Isso é o movimento ao longo da curva de demanda.
""")
        with col_t2:
            st.markdown("""
**📈 Curva de Oferta — $P^S = c + d \\cdot Q$**

Representa o comportamento dos **produtores**. Ela é **positivamente inclinada** porque:

- Quanto **maior o preço**, mais lucrativo produzir — produtores aumentam a quantidade
  ofertada (lei da oferta).
- O parâmetro **$c$** é o preço mínimo para que a produção seja viável —
  **custo variável médio mínimo** (quando $Q = 0$).
- O parâmetro **$d$** mede o **custo marginal crescente**: cada unidade adicional
  custa mais para produzir (rendimentos decrescentes de escala).

> 💡 **Intuição:** Se o preço do café sobe, fazendeiros plantam mais café,
> mesmo que precisem usar terras menos férteis (custo maior por unidade).
""")

        st.divider()

        # ── Bloco 2: O Equilíbrio ─────────────────────────────────
        st.markdown("#### 2. Como se forma o Equilíbrio?")
        st.markdown("""
O **equilíbrio de mercado** é o ponto onde a quantidade que os consumidores
desejam comprar é exatamente igual à quantidade que os produtores desejam vender.
Matematicamente, igualamos $P^D = P^S$:
""")
        st.latex(r"a - b \cdot Q = c + d \cdot Q")
        st.latex(r"a - c = (b + d) \cdot Q")
        st.latex(r"Q^* = \frac{a - c}{b + d} \qquad P^* = c + d \cdot Q^*")

        st.markdown(f"""
**Com os parâmetros atuais:**
- $Q^* = \\frac{{{a_dem:.2f} - {c_ofe:.2f}}}{{{b_dem:.3f} + {d_ofe:.3f}}} = {Q_eq/escala:.3f}$ mil unidades
- $P^* = {c_ofe:.2f} + {d_ofe:.3f} \\times {Q_eq:.0f} = {P_eq:.2f}$ R\\$ mil

**Por que o mercado converge para esse ponto?**

- Se $P > P^*$: produtores ofertam mais do que os consumidores demandam →
  **excesso de oferta** → estoques se acumulam → produtores reduzem o preço.
- Se $P < P^*$: consumidores demandam mais do que os produtores ofertam →
  **escassez** → consumidores competem pelo bem → preço sobe.
- Em $P^*$: nenhuma força pressiona o preço — **equilíbrio estável**.
""")

        st.divider()

        # ── Bloco 3: Deslocamentos das Curvas ─────────────────────
        st.markdown("#### 3. O que desloca as curvas? (Variáveis Exógenas)")

        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.markdown("""
**Deslocadores da Demanda** (mudam $a$ ou $b$):

| Fator | Efeito na Curva | Efeito em $Q^*$ e $P^*$ |
|---|---|---|
| ↑ Renda dos consumidores | Desloca para **direita** (↑$a$) | ↑$Q^*$, ↑$P^*$ |
| ↑ Preço de bem substituto | Desloca para **direita** (↑$a$) | ↑$Q^*$, ↑$P^*$ |
| ↑ Preço de bem complementar | Desloca para **esquerda** (↓$a$) | ↓$Q^*$, ↓$P^*$ |
| ↑ Preferências pelo bem | Desloca para **direita** (↑$a$) | ↑$Q^*$, ↑$P^*$ |
| ↑ Número de consumidores | Desloca para **direita** (↑$a$) | ↑$Q^*$, ↑$P^*$ |

> ⚠️ **Atenção:** Variação de **preço** é movimento **ao longo** da curva.
> Variação de **outra variável** é **deslocamento** da curva.
""")
        with col_d2:
            st.markdown("""
**Deslocadores da Oferta** (mudam $c$ ou $d$):

| Fator | Efeito na Curva | Efeito em $Q^*$ e $P^*$ |
|---|---|---|
| ↑ Custo dos insumos | Desloca para **esquerda** (↑$c$) | ↓$Q^*$, ↑$P^*$ |
| ↑ Tecnologia de produção | Desloca para **direita** (↓$c$) | ↑$Q^*$, ↓$P^*$ |
| ↑ Número de produtores | Desloca para **direita** (↓$c$) | ↑$Q^*$, ↓$P^*$ |
| ↑ Subsídio do governo | Desloca para **direita** (↓$c$) | ↑$Q^*$, ↓$P^*$ |
| ↑ Imposto sobre produção | Desloca para **esquerda** (↑$c$) | ↓$Q^*$, ↑$P^*$ |
""")

        st.divider()

        # ── Bloco 4: Excedentes ───────────────────────────────────
        st.markdown("#### 4. Excedente do Consumidor e do Produtor")

        # Cálculo dos excedentes (área dos triângulos)
        EC = 0.5 * (a_dem - P_eq) * Q_eq if Q_eq > 0 else 0.0
        EP = 0.5 * (P_eq - c_ofe) * Q_eq if Q_eq > 0 else 0.0
        BT = EC + EP

        col_e1, col_e2, col_e3 = st.columns(3)
        col_e1.metric("Excedente do Consumidor (EC)", f"{EC/escala:.2f}")
        col_e2.metric("Excedente do Produtor (EP)",   f"{EP/escala:.2f}")
        col_e3.metric("Benefício Total (EC + EP)",    f"{BT/escala:.2f}")

        st.markdown(f"""
**Excedente do Consumidor (EC):**
É a diferença entre o que os consumidores **estariam dispostos a pagar** e o que
**efetivamente pagam**. Geometricamente, é a área do triângulo acima de $P^*$ e
abaixo da curva de demanda:
""")
        st.latex(
            rf"EC = \frac{{1}}{{2}} \times (a - P^*) \times Q^* = "
            rf"\frac{{1}}{{2}} \times ({a_dem:.2f} - {P_eq:.2f}) \times {Q_eq:.0f} = {EC:.2f}"
        )
        st.markdown(f"""
**Excedente do Produtor (EP):**
É a diferença entre o que os produtores **recebem** e o **custo mínimo** que
aceitariam. Geometricamente, é a área do triângulo abaixo de $P^*$ e acima da
curva de oferta:
""")
        st.latex(
            rf"EP = \frac{{1}}{{2}} \times (P^* - c) \times Q^* = "
            rf"\frac{{1}}{{2}} \times ({P_eq:.2f} - {c_ofe:.2f}) \times {Q_eq:.0f} = {EP:.2f}"
        )
        st.success(
            f"🏆 **Eficiência de Mercado:** O equilíbrio competitivo maximiza o "
            f"**Benefício Total = EC + EP = {BT:.2f}**. "
            f"Qualquer intervenção (teto ou piso de preços) reduz esse total — "
            f"gerando **perda de peso morto** (deadweight loss)."
        )

        st.divider()

        # ── Bloco 5: Preço Tabelado e Perda de Peso Morto ─────────
        st.markdown("#### 5. Preço Tabelado e Perda de Peso Morto")
        if mostrar_tabelado:
            Q_transac = min(Q_dem_tab, Q_ofe_tab)   # quantidade efetivamente transacionada
            PPM = 0.5 * abs(P_tabelado - P_eq) * abs(Q_eq - Q_transac) if Q_eq > Q_transac else 0.0

            st.markdown(f"""
Com o preço tabelado em $\\bar{{P}} = {P_tabelado:.2f}$, a quantidade efetivamente
transacionada é $Q_{{transac}} = \\min(Q^D, Q^S) = {Q_transac/escala:.3f}$ mil.

A **Perda de Peso Morto (PPM)** é o benefício que deixa de ser gerado:
""")
            st.latex(
                rf"PPM \approx \frac{{1}}{{2}} \times |P^* - \bar{{P}}| \times |Q^* - Q_{{transac}}| = "
                rf"\frac{{1}}{{2}} \times {abs(P_eq - P_tabelado):.2f} \times {abs(Q_eq - Q_transac):.0f} = {PPM:.2f}"
            )
            if PPM > 0:
                st.error(
                    f"⚠️ **Ineficiência:** O preço tabelado destrói **{PPM:.2f}** unidades de "
                    f"benefício social que seriam geradas no equilíbrio competitivo. "
                    f"Isso representa a **perda de peso morto** — transações mutuamente "
                    f"benéficas que deixam de ocorrer."
                )
            else:
                st.success("✅ O preço tabelado coincide com o equilíbrio. Sem perda de eficiência.")
        else:
            st.info("Ative o preço tabelado para ver a análise de perda de peso morto.")

        st.divider()

        # ── Bloco 6: Conexão com a Macroeconomia ──────────────────
        st.markdown("#### 6. Conexão com a Macroeconomia")
        st.markdown("""
O modelo de oferta e demanda é a **microeconomia** que fundamenta os modelos
macroeconômicos do simulador:

| Mercado Micro | Equivalente Macro | Variável de Preço | Variável de Quantidade |
|---|---|---|---|
| Bem genérico | Mercado de bens (IS) | Nível de preços $P$ | Produto $Y$ |
| Trabalho | Mercado de trabalho | Salário real $w/P$ | Emprego $L$ |
| Moeda | Mercado monetário (LM) | Taxa de juros $r$ | Oferta de moeda $M$ |
| Câmbio | Balanço de pagamentos (BP) | Taxa de câmbio $e$ | Reservas internacionais |

**A curva de Demanda Agregada (DA)** é a soma de todas as demandas individuais
de bens e serviços — ela tem inclinação negativa no espaço $(Y, P)$ pelos mesmos
motivos que a demanda individual: efeito riqueza (Pigou), efeito juros (Keynes)
e efeito câmbio (Mundell-Fleming).

**A curva de Oferta Agregada (OA)** tem inclinação positiva no curto prazo
(salários rígidos) e é vertical no longo prazo (pleno emprego) — análogo à
oferta individual com custo marginal crescente.
""")
        st.latex(
            r"DA: \quad Y = \frac{1}{1-c_1(1-t)}\left(c_0 + I_0 + G - c_1 T + \frac{h}{k}M\right) - \frac{b}{k}P"
        )
        st.caption(
            "A DA é derivada do modelo IS-LM: o nível de preços P afeta a oferta real "
            "de moeda M/P, deslocando a LM e alterando o produto de equilíbrio Y."
        )

# ── Seção: MERCADO DE TRABALHO ────────────────────────────────────
elif funcao == "Mercado de Trabalho":

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

    # ── Controles ────────────────────────────────────────────────
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
        w_min = st.slider("Salário Mínimo (w̄/P)", 1.0, 18.0, 9.0, 0.25,
                          key="mt_wmin",
                          help="Piso salarial legal. Se acima do equilíbrio → desemprego involuntário")
        mostrar_wmin = st.checkbox("Ativar piso salarial", value=True, key="mt_show")

        st.markdown("---")
        st.markdown("**📦 Produto e Lei de Okun**")
        Y_atual   = st.number_input("Produto Atual (Y)",             value=1800.0, step=50.0, key="mt_y")
        Y_pleno   = st.number_input("Produto de Pleno Emprego (Yₙ)", value=2000.0, step=50.0, key="mt_yn")
        beta_okun = st.slider("Coeficiente de Okun (β)", 0.1, 0.5, 0.3, 0.05,
                              key="mt_beta",
                              help="Variação do desemprego para cada 1% de desvio do produto")
        u_natural = st.slider("Taxa Natural de Desemprego (uₙ %)", 3.0, 8.0, 5.0, 0.5,
                              key="mt_un")

    # ── Cálculos de Equilíbrio ────────────────────────────────────
    denom_mt = b_ld + d_ls
    L_eq     = max((a_ld - c_ls) / denom_mt, 0.0) if denom_mt > 0 else 0.0
    w_eq     = c_ls + d_ls * L_eq

    # Quantidades ao salário mínimo
    L_dem_wmin      = max((a_ld - w_min) / b_ld, 0.0) if b_ld > 0 else 0.0
    L_ofe_wmin      = max((w_min - c_ls) / d_ls, 0.0) if d_ls > 0 else 0.0
    desemprego_piso = max(L_ofe_wmin - L_dem_wmin, 0.0)

    # Lei de Okun
    gap_produto  = Y_atual - Y_pleno
    gap_pct      = (gap_produto / Y_pleno) * 100 if Y_pleno > 0 else 0.0
    u_ciclico    = -beta_okun * gap_pct
    u_efetivo    = u_natural + u_ciclico

    escala_L   = 1000
    L_max_plot = L_eq * 2.2 if L_eq > 0 else 2000
    L_range    = np.linspace(0, L_max_plot, 400)
    wP_demanda = a_ld - b_ld * L_range
    wP_oferta  = c_ls + d_ls * L_range

    # ── Métricas ─────────────────────────────────────────────────
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
            f"trabalhadores desempregados involuntariamente."
        )
    elif mostrar_wmin and w_min <= w_eq:
        st.success(
            f"✅ O salário mínimo ({w_min:.2f}) está **abaixo do equilíbrio** ({w_eq:.2f}). "
            f"O piso não é restritivo — não gera desemprego involuntário."
        )

    # ── Gráficos ─────────────────────────────────────────────────
    n_cols_mt  = 2 if mostrar_wmin else 1
    titulo_mt2 = (
        f"Piso Salarial w̄/P={w_min:.2f} → "
        f"{'Desemprego Involuntário' if desemprego_piso > 10 else 'Sem Distorção'}"
        if mostrar_wmin else ""
    )

    fig_mt = make_subplots(
        rows=1, cols=n_cols_mt,
        subplot_titles=(
            f"Equilíbrio  (w*/P={w_eq:.2f}, L*={L_eq/escala_L:.0f} mil)",
            titulo_mt2
        ) if mostrar_wmin else (
            f"Equilíbrio  (w*/P={w_eq:.2f}, L*={L_eq/escala_L:.0f} mil)",
        ),
        horizontal_spacing=0.12
    )

    def _add_base_mt(col):
        show = (col == 1)
        fig_mt.add_trace(go.Scatter(
            x=L_range / escala_L, y=wP_demanda, name="Demanda por Trabalho (Lᴰ)",
            line=dict(color="#F44336", width=3), showlegend=show
        ), row=1, col=col)
        fig_mt.add_trace(go.Scatter(
            x=L_range / escala_L, y=wP_oferta, name="Oferta de Trabalho (Lˢ)",
            line=dict(color="#2196F3", width=3), showlegend=show
        ), row=1, col=col)
        fig_mt.add_trace(go.Scatter(
            x=[L_eq / escala_L], y=[w_eq],
            mode="markers+text", name="Equilíbrio (E*)",
            marker=dict(color="#333", size=12),
            text=["E*"], textposition="top right",
            textfont=dict(size=14), showlegend=show
        ), row=1, col=col)
        for x0, y0, xv, yv in [
            (0, w_eq, L_eq / escala_L, w_eq),
            (L_eq / escala_L, 0, L_eq / escala_L, w_eq)
        ]:
            fig_mt.add_trace(go.Scatter(
                x=[x0, xv], y=[y0, yv], mode="lines", showlegend=False,
                line=dict(color="#888", width=1.2, dash="dash")
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
            line=dict(color="#FF9800", width=2.5, dash="dot"), showlegend=True
        ), row=1, col=2)

        for L_val, nome, cor, sym in [
            (L_dem_wmin, f"Lᴰ = {L_dem_wmin/escala_L:.2f} mil (empregados)", "#F44336", "circle"),
            (L_ofe_wmin, f"Lˢ = {L_ofe_wmin/escala_L:.2f} mil (ofertantes)", "#2196F3", "circle"),
        ]:
            fig_mt.add_trace(go.Scatter(
                x=[L_val / escala_L], y=[w_min],
                mode="markers", name=nome,
                marker=dict(color=cor, size=11, symbol=sym), showlegend=True
            ), row=1, col=2)
            fig_mt.add_trace(go.Scatter(
                x=[L_val / escala_L, L_val / escala_L], y=[0, w_min],
                mode="lines", showlegend=False,
                line=dict(color=cor, width=1.2, dash="dash")
            ), row=1, col=2)

        if desemprego_piso > 10:
            L_min_a = L_dem_wmin / escala_L
            L_max_a = L_ofe_wmin / escala_L
            L_mid_a = (L_min_a + L_max_a) / 2
            y_ann   = w_min + 0.5
            cor_a   = "#B71C1C"

            fig_mt.add_shape(type="line",
                x0=L_min_a, x1=L_max_a, y0=y_ann, y1=y_ann,
                line=dict(color=cor_a, width=1.5), row=1, col=2)
            for xv in [L_min_a, L_max_a]:
                fig_mt.add_shape(type="line",
                    x0=xv, x1=xv, y0=w_min, y1=y_ann,
                    line=dict(color=cor_a, width=1.2, dash="dot"), row=1, col=2)
            fig_mt.add_annotation(
                x=L_mid_a, y=y_ann + 0.35,
                text=f"<b>Desemprego Involuntário<br>{desemprego_piso/escala_L:.2f} mil</b>",
                showarrow=False, font=dict(size=12, color=cor_a), row=1, col=2
            )

        fig_mt.update_xaxes(title_text="L — Trabalho (em milhares)", showgrid=True,
                            range=[0, L_max_plot / escala_L], row=1, col=2)
        fig_mt.update_yaxes(title_text="w/P — Salário Real", showgrid=True,
                            range=[0, a_ld * 1.1], row=1, col=2)

    fig_mt.update_layout(
        height=500, template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=-0.30, xanchor="center", x=0.5),
        margin=dict(t=60, b=100)
    )
    st.plotly_chart(fig_mt, use_container_width=True)

    # ── Gráfico 3: Lei de Okun ────────────────────────────────────
    st.divider()
    st.subheader("📉 Lei de Okun — Produto e Desemprego Cíclico")

    col_ok1, col_ok2 = st.columns([2, 1])

    with col_ok1:
        Y_range_ok  = np.linspace(Y_pleno * 0.7, Y_pleno * 1.15, 300)
        u_okun_line = u_natural - beta_okun * ((Y_range_ok - Y_pleno) / Y_pleno * 100)

        fig_ok = go.Figure()
        fig_ok.add_trace(go.Scatter(
            x=Y_range_ok, y=u_okun_line, name="Curva de Okun",
            line=dict(color="#7B1FA2", width=3)
        ))
        fig_ok.add_trace(go.Scatter(
            x=[Y_atual], y=[u_efetivo],
            mode="markers+text", name=f"Situação Atual (u={u_efetivo:.2f}%)",
            marker=dict(color="#E53935", size=13),
            text=[f"u={u_efetivo:.1f}%"], textposition="top right",
            textfont=dict(size=13)
        ))
        fig_ok.add_vline(x=Y_pleno, line=dict(color="green", dash="dash", width=2),
                         annotation_text=f"Yₙ={Y_pleno:.0f}", annotation_position="top right")
        fig_ok.add_hline(y=u_natural, line=dict(color="gray", dash="dot", width=1.5),
                         annotation_text=f"uₙ={u_natural:.1f}%", annotation_position="right")

        fig_ok.update_layout(
            height=340, template="plotly_white",
            xaxis_title="Produto (Y)", yaxis_title="Taxa de Desemprego (%)",
            title="Lei de Okun: Δu = −β × (ΔY/Yₙ)"
        )
        st.plotly_chart(fig_ok, use_container_width=True)

    with col_ok2:
        st.markdown("### 🔢 Decomposição do Desemprego")
        st.metric("Taxa Natural (uₙ)",        f"{u_natural:.1f}%")
        st.metric("Componente Cíclico",       f"{u_ciclico:+.2f} p.p.",
                  delta=f"{'Recessão' if u_ciclico > 0 else 'Expansão'}",
                  delta_color="inverse")
        st.metric("Taxa Efetiva (u)",         f"{u_efetivo:.2f}%")
        st.metric("Hiato do Produto (Y−Yₙ)",  f"{gap_produto:+.0f}",
                  delta=f"{gap_pct:+.1f}%", delta_color="normal")

        if gap_pct < -2:
            st.error("🔴 **Recessão profunda** — desemprego cíclico elevado")
        elif gap_pct < 0:
            st.warning("🟡 **Hiato negativo** — economia abaixo do pleno emprego")
        elif gap_pct > 2:
            st.info("🔵 **Sobreaquecimento** — pressão inflacionária")
        else:
            st.success("🟢 **Próximo ao pleno emprego**")

    # ── Abas Analíticas ───────────────────────────────────────────
    st.divider()
    st.subheader("🔬 Decomposição Analítica")

    aba_mt1, aba_mt2, aba_mt3, aba_mt4, aba_mt5 = st.tabs([
        "⚖️ Equilíbrio do Mercado de Trabalho",
        "🚫 Desemprego Involuntário (Piso Salarial)",
        "📉 Lei de Okun e Desemprego Cíclico",
        "🔗 Integração OA-DA",
        "📘 Fundamentos Teóricos"
    ])

    with aba_mt1:
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
O salário real $w^*/P = {w_eq:.2f}$ iguala o **Produto Marginal do Trabalho (PMgL)** ao
**salário de reserva** dos trabalhadores.

- **PMgL decrescente** (inclinação negativa de $L^D$): cada trabalhador adicional
  contribui menos ao produto — reflexo da lei dos rendimentos decrescentes.
- **Oferta crescente** (inclinação positiva de $L^S$): trabalhadores exigem salários
  maiores para abrir mão do lazer adicional — custo de oportunidade crescente.
""")

    with aba_mt2:
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
3. **Resultado:** {desemprego_piso/escala_L:.2f} mil trabalhadores **querem trabalhar ao salário vigente
   mas não encontram emprego** — definição clássica de desemprego involuntário (Keynes).

> 💡 Este é o argumento neoclássico contra o salário mínimo. A resposta keynesiana
> é que, com demanda agregada insuficiente, o problema não é o salário — é o nível de Y.
""")
        else:
            st.success(
                f"O piso salarial ({w_min:.2f}) está abaixo do equilíbrio ({w_eq:.2f}). "
                "Não é restritivo — o mercado opera livremente no equilíbrio walrasiano."
            )

    with aba_mt3:
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
> Para economias emergentes, $\\beta$ tende a ser menor (mercados de trabalho menos
> flexíveis, maior informalidade).
""")

    with aba_mt4:
        st.markdown("""
### Integração com o Modelo OA-DA

O mercado de trabalho é o **elo de transmissão** entre o produto agregado ($Y$)
e a inflação ($\\pi$) no modelo OA-DA:
""")
        st.latex(r"Y \xrightarrow{\text{Okun}} u \xrightarrow{\text{Phillips}} \pi \xrightarrow{\text{Fisher}} r \xrightarrow{\text{IS}} Y")

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
- 🟠 **Involuntário (Keynes):** Piso salarial acima do equilíbrio — modelo acima

**Política econômica:**
- Para reduzir o desemprego **cíclico**: política fiscal expansionista ($\\uparrow G$)
  ou monetária ($\\uparrow M$) → $\\uparrow Y$ → $\\downarrow u$
- Para reduzir o desemprego **estrutural/friccional**: políticas de oferta
  (educação, retreinamento, mobilidade laboral)
- Para eliminar o desemprego **involuntário**: debate entre neoclássicos
  (flexibilizar salários) e keynesianos (estimular demanda agregada)
""")

        st.latex(
            r"\underbrace{u_{\text{efetivo}}}_{" + f"{u_efetivo:.2f}\\%" + r"} = "
            r"\underbrace{u_n}_{" + f"{u_natural:.1f}\\%" + r"} + "
            r"\underbrace{\Delta u_{\text{cíclico}}}_{" + f"{u_ciclico:+.2f}" + r"\text{ p.p.}}"
        )

    # ── ABA 5: FUNDAMENTOS TEÓRICOS ──────────────────────────────
    with aba_mt5:
        st.markdown("### 📘 Fundamentos Teóricos do Mercado de Trabalho")

        # ── Bloco 1: O que é o Mercado de Trabalho ────────────────
        st.markdown("#### 1. O Mercado de Trabalho como Mercado de Oferta e Demanda")
        st.markdown("""
O mercado de trabalho funciona como qualquer outro mercado competitivo, mas com
uma diferença fundamental: o **"bem" transacionado é o tempo e esforço humano**.

- O **"preço"** não é em R\\$, mas em **salário real** $w/P$ — o poder de compra
  do salário nominal $w$ deflacionado pelo nível de preços $P$.
- A **"quantidade"** não é em unidades, mas em **horas de trabalho** ou
  **número de trabalhadores** $L$.

Por isso, os eixos do gráfico são:
- **Eixo Y:** Salário Real $(w/P)$ — análogo ao preço $P$ no mercado de bens
- **Eixo X:** Quantidade de Trabalho $(L)$ — análogo à quantidade $Q$
""")

        col_f1, col_f2 = st.columns(2)
        with col_f1:
            st.markdown(f"""
**📉 Demanda por Trabalho — $L^D = \\frac{{a - w/P}}{{b}}$**

Representa as **empresas** decidindo quantos trabalhadores contratar.

**Fundamento microeconômico:** A empresa maximiza lucro contratando até o ponto
onde o **Produto Marginal do Trabalho (PMgL)** iguala o salário real:

$$PMgL = \\frac{{w}}{{P}}$$

- **PMgL decrescente** (lei dos rendimentos decrescentes): o $n$-ésimo trabalhador
  produz menos que o $(n-1)$-ésimo, pois divide capital fixo com mais pessoas.
- Por isso, a empresa só contrata mais se o salário **cair** — curva negativamente
  inclinada com intercepto $a = {a_ld:.2f}$ (PMgL máximo) e inclinação $b = {b_ld:.3f}$.

> 💡 **Exemplo:** Uma fábrica com 10 máquinas. O 1º trabalhador opera todas as
> máquinas e produz muito. O 11º trabalhador não tem máquina disponível e produz
> pouco. O PMgL caiu — a empresa só o contrata se o salário for baixo.
""")
        with col_f2:
            st.markdown(f"""
**📈 Oferta de Trabalho — $L^S = \\frac{{w/P - c}}{{d}}$**

Representa os **trabalhadores** decidindo quantas horas trabalhar.

**Fundamento microeconômico:** O trabalhador maximiza utilidade escolhendo entre
**consumo** (requer renda → trabalho) e **lazer** (requer tempo → não trabalho).

- **Custo de oportunidade do lazer crescente**: cada hora adicional de trabalho
  sacrifica lazer cada vez mais valioso — curva positivamente inclinada.
- O intercepto $c = {c_ls:.2f}$ é o **salário de reserva**: abaixo disso, o trabalhador
  prefere o lazer a trabalhar.
- A inclinação $d = {d_ls:.3f}$ mede quanto o salário precisa subir para atrair
  cada trabalhador adicional ao mercado.

> 💡 **Exemplo:** Com salário baixo, só quem precisa muito trabalha. Com salário
> alto, até quem preferia estudar ou cuidar da família entra no mercado de trabalho.
""")

        st.divider()

        # ── Bloco 2: Salário Real vs Nominal ──────────────────────
        st.markdown("#### 2. Por que usamos Salário Real e não Nominal?")
        st.markdown("""
Esta é uma distinção **fundamental** em macroeconomia:
""")
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.markdown("""
**💵 Salário Nominal ($w$)**
- O valor em reais que aparece no contracheque
- Exemplo: R\\$ 2.000/mês
- Pode subir sem que o trabalhador fique mais rico
- Relevante para contratos e obrigações nominais
- **Ilusão monetária:** confundir aumento nominal com aumento real
""")
        with col_r2:
            st.markdown("""
**🛒 Salário Real ($w/P$)**
- O poder de compra do salário — quantos bens ele compra
- Exemplo: se $w = 2.000$ e $P = 1.0$, então $w/P = 2.000$ bens
- Se $P$ dobra e $w$ dobra, o salário real não mudou
- **É o que realmente importa** para decisões de trabalho e consumo
- Usado em todos os modelos de equilíbrio geral
""")
        st.markdown("""
> 💡 **Analogia:** Imagine que seu salário sobe 10% mas a inflação é 15%.
> Nominalmente você ganhou mais, mas **realmente** você perdeu poder de compra.
> O mercado de trabalho responde ao salário **real**, não ao nominal.
> Por isso, políticas que aumentam salários nominais sem aumentar produtividade
> podem gerar inflação sem reduzir o desemprego real.
""")
        st.latex(r"\text{Salário Real} = \frac{w}{P} \qquad \Rightarrow \qquad \frac{\Delta(w/P)}{w/P} = \frac{\Delta w}{w} - \frac{\Delta P}{P} = \text{crescimento nominal} - \pi")

        st.divider()

        # ── Bloco 3: Tipos de Desemprego ──────────────────────────
        st.markdown("#### 3. Taxonomia Completa do Desemprego")

        dados_desemp = {
            "Tipo": ["Friccional", "Estrutural", "Cíclico (Keynesiano)", "Involuntário (Keynes)", "Sazonal"],
            "Causa": [
                "Tempo de busca entre empregos",
                "Incompatibilidade de habilidades com vagas disponíveis",
                "Insuficiência de Demanda Agregada (Y < Yₙ)",
                "Salário acima do equilíbrio (piso salarial)",
                "Variações sazonais na demanda por trabalho"
            ],
            "Componente": ["uₙ", "uₙ", "Δu via Okun", "LS − LD", "uₙ (parcial)"],
            "Política Adequada": [
                "Agências de emprego, informação de mercado",
                "Educação, retreinamento, mobilidade",
                "Política fiscal/monetária expansionista",
                "Debate: flexibilizar salários vs. estimular DA",
                "Seguro-desemprego, programas temporários"
            ]
        }
        st.dataframe(pd.DataFrame(dados_desemp), use_container_width=True, hide_index=True)

        st.markdown(f"""
**Com os parâmetros atuais, a decomposição é:**
""")
        st.latex(
            r"u_{\text{total}} = \underbrace{u_n}_{\text{friccional + estrutural}}"
            r"+ \underbrace{\Delta u_{\text{cíclico}}}_{\text{via Okun}}"
            r"+ \underbrace{(L^S - L^D)/\bar{L}}_{\text{involuntário (piso)}}"
        )
        st.latex(
            rf"u_{{total}} = {u_natural:.1f}\% + ({u_ciclico:+.2f}\text{{ p.p.}}) = {u_efetivo:.2f}\%"
        )

        st.divider()

        # ── Bloco 4: Debate Neoclássico vs Keynesiano ─────────────
        st.markdown("#### 4. O Grande Debate: Neoclássicos vs. Keynesianos")

        col_nc, col_kn = st.columns(2)
        with col_nc:
            st.markdown("""
**🏛️ Visão Neoclássica**

- O mercado de trabalho se equilibra **automaticamente** via ajuste de salários.
- O desemprego é **voluntário**: quem está desempregado escolhe não trabalhar
  ao salário de mercado (prefere lazer ou busca melhor oferta).
- O desemprego involuntário só existe se houver **rigidez salarial** (salário
  mínimo, sindicatos, contratos de longo prazo).
- **Política:** remover rigidezes, flexibilizar o mercado de trabalho.
- **Implicação:** a curva de oferta agregada de longo prazo é **vertical** em $Y_n$.

> 📌 Representantes: Pigou, Lucas, Prescott (RBC)
""")
        with col_kn:
            st.markdown("""
**🔵 Visão Keynesiana**

- Os salários são **rígidos para baixo** (trabalhadores resistem a cortes nominais).
- O desemprego pode ser **involuntário**: trabalhadores querem trabalhar ao salário
  vigente mas não encontram emprego — o problema é a **demanda insuficiente**.
- Mesmo sem piso salarial, a economia pode ficar presa em equilíbrio com desemprego.
- **Política:** estimular a Demanda Agregada ($\\uparrow G$, $\\uparrow M$) para
  elevar $Y$ e reduzir $u$ via Lei de Okun.
- **Implicação:** a curva de oferta agregada de curto prazo é **positivamente inclinada**.

> 📌 Representantes: Keynes, Hicks, Samuelson, Mankiw (NK)
""")

        st.info("""
💡 **Síntese Moderna (Nova Síntese Neoclássica):** Os modelos atuais combinam
rigidez nominal de curto prazo (Keynesiano) com equilíbrio de longo prazo
(Neoclássico). No curto prazo, choques de demanda afetam $Y$ e $u$; no longo
prazo, a economia retorna a $Y_n$ e $u_n$ via ajuste de preços e salários.
""")

        st.divider()

        # ── Bloco 5: A Lei de Okun em Detalhe ─────────────────────
        st.markdown("#### 5. A Lei de Okun — Origem e Interpretação")
        st.markdown(f"""
A **Lei de Okun** (Arthur Okun, 1962) é uma relação **empírica** — não derivada
de teoria, mas observada nos dados — entre crescimento do produto e variação do
desemprego:
""")
        st.latex(r"\Delta u = -\beta \cdot \left(\frac{Y - Y_n}{Y_n}\right) \times 100")
        st.markdown(f"""
**Por que $\\beta < 1$?** (e não $\\beta = 1$)

Quando o produto cresce 1%, o desemprego não cai 1% porque:

1. **Horas trabalhadas:** Empresas primeiro aumentam horas dos empregados atuais
   antes de contratar novos.
2. **Trabalhadores desalentados:** Quando a economia melhora, pessoas que haviam
   desistido de procurar emprego voltam ao mercado (aumentam $L^S$), amortecendo
   a queda do desemprego.
3. **Produtividade:** Parte do crescimento vem de ganhos de produtividade, não
   de mais emprego.

**Calibração:**
- EUA (Okun, 1962): $\\beta \\approx 0.3$
- Brasil (estimativas recentes): $\\beta \\approx 0.15$ a $0.25$ (mercado menos flexível)
- Parâmetro atual no simulador: $\\beta = {beta_okun:.2f}$

**Interpretação com os valores atuais:**
- Hiato do produto: $Y - Y_n = {gap_produto:+.0f}$ ({gap_pct:+.1f}%)
- Variação do desemprego: $\\Delta u = -{beta_okun:.2f} \\times ({gap_pct:+.1f}) = {u_ciclico:+.2f}$ p.p.
- Taxa efetiva: $u = {u_natural:.1f}\\% + ({u_ciclico:+.2f}) = {u_efetivo:.2f}\\%$
""")

        st.divider()

        # ── Bloco 6: Resumo das Equações ──────────────────────────
        st.markdown("#### 6. 📐 Resumo das Equações do Módulo")

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
            "Todas as equações acima são calculadas dinamicamente com os parâmetros "
            "dos sliders. Altere os valores e observe como os resultados mudam em tempo real."
        )