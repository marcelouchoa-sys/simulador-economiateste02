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
    "Oferta de Moeda", "Demanda Agregada", "Oferta Agregada", "Produção"
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