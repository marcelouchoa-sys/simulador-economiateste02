"""
Página: Escolas Econômicas
Visão Clássica vs Keynesiana — com rigor analítico e visualização pedagógica
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─────────────────────────────────────────────
# CONFIGURAÇÃO DA PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Escolas Econômicas",
    page_icon="🏛️",
    layout="wide"
)

st.title("🏛️ Escolas Econômicas")
st.markdown("Compare as visões **Clássica** e **Keynesiana** sobre o funcionamento da macroeconomia.")

# ─────────────────────────────────────────────
# SELETOR DE ESCOLA
# ─────────────────────────────────────────────
col_btn1, col_btn2, col_spacer = st.columns([1, 1, 4])

if "escola" not in st.session_state:
    st.session_state.escola = "Clássica"

with col_btn1:
    if st.button("🏺 Visão Clássica", use_container_width=True,
                 type="primary" if st.session_state.escola == "Clássica" else "secondary"):
        st.session_state.escola = "Clássica"

with col_btn2:
    if st.button("📊 Visão Keynesiana", use_container_width=True,
                 type="primary" if st.session_state.escola == "Keynesiana" else "secondary"):
        st.session_state.escola = "Keynesiana"

escola = st.session_state.escola

st.divider()

# ═══════════════════════════════════════════════════════════════
# ██████████████████  VISÃO CLÁSSICA  ██████████████████████████
# ═══════════════════════════════════════════════════════════════
if escola == "Clássica":

    st.subheader("🏺 Escola Clássica — Oferta Determina o Produto")

    with st.expander("📖 Fundamentos da Escola Clássica", expanded=False):
        st.markdown("""
        | Princípio | Descrição |
        |-----------|-----------|
        | **Lei de Say** | "A oferta cria sua própria demanda" — produção gera renda que financia o consumo |
        | **Preços Flexíveis** | Preços e salários se ajustam livremente, eliminando desequilíbrios |
        | **Pleno Emprego** | A economia tende naturalmente ao pleno emprego no longo prazo |
        | **Neutralidade da Moeda** | Variações em M afetam apenas o nível de preços (P), não o produto real (Y) |
        | **Dicotomia Clássica** | Variáveis reais e nominais são determinadas separadamente |
        | **Ajuste Automático** | Não há necessidade de intervenção governamental |
        """)

    # ── PAINEL DE CONTROLES ──────────────────────────────────────
    st.markdown("### ⚙️ Parâmetros")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**🏭 Lado da Oferta**")
        produtividade = st.slider("Produtividade Total (A)", 0.5, 2.0, 1.0, 0.05,
                                  help="Fator de produtividade total — desloca OA para direita")
        tecnologia    = st.slider("Tecnologia (θ)", 0.5, 2.0, 1.0, 0.05,
                                  help="Nível tecnológico — amplifica o produto potencial")
        trabalho      = st.slider("Força de Trabalho (L̄)", 50.0, 200.0, 100.0, 5.0,
                                  help="Oferta de trabalho no pleno emprego")

    with col2:
        st.markdown("**💰 Lado Monetário**")
        oferta_monetaria = st.slider("Oferta Monetária (M)", 50.0, 300.0, 100.0, 10.0,
                                     help="Quantidade de moeda — afeta apenas P (neutralidade)")
        velocidade       = st.slider("Velocidade da Moeda (V)", 0.5, 3.0, 1.0, 0.1,
                                     help="Velocidade de circulação da moeda (Teoria Quantitativa: MV = PY)")

    with col3:
        st.markdown("**👷 Mercado de Trabalho**")
        salario_nominal = st.slider("Salário Nominal (W)", 0.5, 3.0, 1.0, 0.1,
                                    help="Salário nominal — com preços flexíveis, salário real se ajusta")
        capital         = st.slider("Estoque de Capital (K)", 50.0, 200.0, 100.0, 10.0,
                                    help="Capital disponível na economia")

    # ── CÁLCULOS CLÁSSICOS ───────────────────────────────────────
    # Função de produção: Y* = A * θ * K^α * L̄^(1-α)
    alpha = 0.35  # participação do capital
    Y_potencial = produtividade * tecnologia * (capital ** alpha) * (trabalho ** (1 - alpha))

    # Teoria Quantitativa da Moeda: MV = PY → P* = MV / Y*
    P_equilibrio = (oferta_monetaria * velocidade) / Y_potencial

    # Salário real de equilíbrio: w* = (1-α) * A * θ * (K/L̄)^α
    salario_real_eq = (1 - alpha) * produtividade * tecnologia * (capital / trabalho) ** alpha
    salario_real_atual = salario_nominal / P_equilibrio

    # Demanda Agregada: DA = MV / P  (hipérbole)
    P_range = np.linspace(0.1, P_equilibrio * 3, 300)
    DA = (oferta_monetaria * velocidade) / P_range

    # ── MÉTRICAS ─────────────────────────────────────────────────
    st.markdown("### 📊 Equilíbrio Macroeconômico Clássico")
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Produto Potencial (Y*)", f"{Y_potencial:.1f}")
    m2.metric("Nível de Preços (P*)", f"{P_equilibrio:.3f}")
    m3.metric("Salário Real Eq. (w*)", f"{salario_real_eq:.3f}")
    m4.metric("Salário Real Atual (w)", f"{salario_real_atual:.3f}")
    desvio_w = ((salario_real_atual - salario_real_eq) / salario_real_eq) * 100
    m5.metric("Desvio Salarial", f"{desvio_w:+.1f}%",
              delta_color="inverse" if abs(desvio_w) > 5 else "off")

    # ── GRÁFICOS ─────────────────────────────────────────────────
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=(
            "Oferta e Demanda Agregada — Visão Clássica",
            "Mercado de Trabalho Clássico"
        ),
        horizontal_spacing=0.12
    )

    # ── Gráfico 1: OA vertical + DA hipérbole ──
    # DA (hipérbole)
    fig.add_trace(go.Scatter(
        x=DA, y=P_range,
        mode="lines", name="DA (MV/P)",
        line=dict(color="#2196F3", width=2.5),
    ), row=1, col=1)

    # OA vertical (longo prazo)
    fig.add_trace(go.Scatter(
        x=[Y_potencial, Y_potencial],
        y=[0, P_equilibrio * 2.5],
        mode="lines", name="OA (Longo Prazo — vertical)",
        line=dict(color="#F44336", width=3, dash="solid"),
    ), row=1, col=1)

    # Linha tracejada no pleno emprego
    fig.add_trace(go.Scatter(
        x=[0, Y_potencial],
        y=[P_equilibrio, P_equilibrio],
        mode="lines", name=f"P* = {P_equilibrio:.3f}",
        line=dict(color="#4CAF50", width=1.5, dash="dash"),
        showlegend=True
    ), row=1, col=1)

    # Ponto de equilíbrio
    fig.add_trace(go.Scatter(
        x=[Y_potencial], y=[P_equilibrio],
        mode="markers+text",
        name="Equilíbrio E*",
        marker=dict(color="#FF9800", size=12, symbol="circle"),
        text=["E*"], textposition="top right",
        textfont=dict(size=13, color="#FF9800")
    ), row=1, col=1)

    # Anotação: neutralidade da moeda
    fig.add_annotation(
        x=Y_potencial * 1.05, y=P_equilibrio * 2.0,
        text="OA vertical:<br>Y* independe de P<br>(neutralidade da moeda)",
        showarrow=True, arrowhead=2,
        ax=60, ay=-30,
        font=dict(size=11, color="#F44336"),
        bgcolor="rgba(244,67,54,0.1)",
        bordercolor="#F44336",
        row=1, col=1
    )

    fig.update_xaxes(title_text="Produto (Y) →", row=1, col=1, showgrid=True, gridcolor="#eee")
    fig.update_yaxes(title_text="Nível de Preços (P) →", row=1, col=1, showgrid=True, gridcolor="#eee",
                     range=[0, P_equilibrio * 2.8])

    # ── Gráfico 2: Mercado de Trabalho ──
    L_range = np.linspace(10, trabalho * 1.8, 300)

    # Demanda por trabalho: w = PMgL = (1-α)*A*θ*(K/L)^α
    demanda_trabalho = (1 - alpha) * produtividade * tecnologia * (capital / L_range) ** alpha

    # Oferta de trabalho: vertical no pleno emprego (clássico)
    fig.add_trace(go.Scatter(
        x=L_range, y=demanda_trabalho,
        mode="lines", name="Demanda por Trabalho (PMgL)",
        line=dict(color="#9C27B0", width=2.5),
    ), row=1, col=2)

    fig.add_trace(go.Scatter(
        x=[trabalho, trabalho],
        y=[0, salario_real_eq * 2.5],
        mode="lines", name="Oferta de Trabalho (vertical)",
        line=dict(color="#FF5722", width=3),
    ), row=1, col=2)

    # Salário real atual
    fig.add_trace(go.Scatter(
        x=[10, trabalho * 1.8],
        y=[salario_real_atual, salario_real_atual],
        mode="lines", name=f"w atual = {salario_real_atual:.3f}",
        line=dict(color="#607D8B", width=1.5, dash="dot"),
    ), row=1, col=2)

    # Salário real de equilíbrio
    fig.add_trace(go.Scatter(
        x=[10, trabalho * 1.8],
        y=[salario_real_eq, salario_real_eq],
        mode="lines", name=f"w* = {salario_real_eq:.3f}",
        line=dict(color="#4CAF50", width=1.5, dash="dash"),
    ), row=1, col=2)

    # Ponto de equilíbrio no mercado de trabalho
    fig.add_trace(go.Scatter(
        x=[trabalho], y=[salario_real_eq],
        mode="markers+text",
        name="Equilíbrio Trabalho",
        marker=dict(color="#FF9800", size=12),
        text=["E*"], textposition="top right",
        textfont=dict(size=13, color="#FF9800"),
        showlegend=False
    ), row=1, col=2)

    # Seta de ajuste se salário desviado
    if abs(desvio_w) > 2:
        fig.add_annotation(
            x=trabalho * 0.85,
            y=(salario_real_atual + salario_real_eq) / 2,
            ax=trabalho * 0.85,
            ay=salario_real_eq if salario_real_atual > salario_real_eq else salario_real_atual,
            xref="x2", yref="y2", axref="x2", ayref="y2",
            text="ajuste<br>automático",
            showarrow=True, arrowhead=3, arrowcolor="#FF9800",
            font=dict(size=10, color="#FF9800"),
        )

    fig.update_xaxes(title_text="Trabalho (L) →", row=1, col=2, showgrid=True, gridcolor="#eee")
    fig.update_yaxes(title_text="Salário Real (w = W/P) →", row=1, col=2, showgrid=True, gridcolor="#eee")

    fig.update_layout(
        height=520,
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
        margin=dict(t=60, b=80)
    )

    st.plotly_chart(fig, use_container_width=True, config={"staticPlot": True})

    # ── EXPLICAÇÃO NARRATIVA COMPLETA ────────────────────────────
    st.markdown("### 📝 Análise Completa da Situação Econômica")

    # Diagnóstico do mercado de trabalho
    if abs(desvio_w) < 2:
        status_trabalho = "em pleno equilíbrio"
        cor_trabalho = "✅"
        narrativa_trabalho = (
            f"O mercado de trabalho encontra-se em equilíbrio pleno: o salário real vigente "
            f"(w = {salario_real_atual:.3f}) coincide com o salário real de equilíbrio "
            f"(w* = {salario_real_eq:.3f}), com desvio de apenas {desvio_w:+.1f}%. "
            f"Não há pressão sobre preços nem sobre salários nominais."
        )
    elif desvio_w > 0:
        cor_trabalho = "⚠️"
        narrativa_trabalho = (
            f"O salário real atual (w = {salario_real_atual:.3f}) está **{desvio_w:.1f}% acima** "
            f"do equilíbrio (w* = {salario_real_eq:.3f}). Na visão clássica, isso gera excesso de oferta "
            f"de trabalho: trabalhadores oferecem mais horas do que as empresas demandam ao salário vigente. "
            f"O mecanismo de ajuste automático pressiona o salário nominal (W) para baixo ou, "
            f"alternativamente, o nível de preços (P) sobe até que w = W/P retorne a w*. "
            f"O produto real Y* = {Y_potencial:.1f} permanece inalterado durante todo o ajuste."
        )
    else:
        cor_trabalho = "⚠️"
        narrativa_trabalho = (
            f"O salário real atual (w = {salario_real_atual:.3f}) está **{abs(desvio_w):.1f}% abaixo** "
            f"do equilíbrio (w* = {salario_real_eq:.3f}). Isso indica excesso de demanda por trabalho: "
            f"as empresas querem contratar mais do que a oferta disponível ao salário vigente. "
            f"O ajuste clássico eleva W nominalmente ou reduz P, restaurando w* sem alterar Y* = {Y_potencial:.1f}."
        )

    # Diagnóstico monetário
    MV = oferta_monetaria * velocidade
    narrativa_monetaria = (
        f"A oferta monetária é M = {oferta_monetaria:.0f} com velocidade V = {velocidade:.1f}, "
        f"gerando MV = {MV:.1f}. Pela Teoria Quantitativa (MV = PY), com produto fixo em "
        f"Y* = {Y_potencial:.1f}, o nível de preços de equilíbrio é P* = MV/Y* = **{P_equilibrio:.3f}**. "
        f"Se a oferta monetária fosse duplicada para M = {oferta_monetaria*2:.0f}, "
        f"o nível de preços subiria para P* = {(oferta_monetaria*2*velocidade)/Y_potencial:.3f} "
        f"— exatamente o dobro — enquanto Y* permaneceria em {Y_potencial:.1f}. "
        f"Isso ilustra a **neutralidade da moeda**: variações em M afetam apenas variáveis nominais."
    )

    # Diagnóstico da função de produção
    narrativa_producao = (
        f"O produto potencial é determinado exclusivamente pelos fatores reais de produção. "
        f"Com produtividade A = {produtividade:.2f}, tecnologia θ = {tecnologia:.2f}, "
        f"capital K = {capital:.0f} e força de trabalho L̄ = {trabalho:.0f}, "
        f"a função de produção Y* = A·θ·K^α·L̄^(1-α) resulta em **Y* = {Y_potencial:.1f}**. "
        f"A participação do capital é α = {alpha} e do trabalho é (1-α) = {1-alpha:.2f}. "
        f"Um aumento de 10% na produtividade (A → {produtividade*1.1:.2f}) elevaria Y* para "
        f"aproximadamente {produtividade*1.1 * tecnologia * (capital**alpha) * (trabalho**(1-alpha)):.1f}, "
        f"deslocando a OA vertical para a direita sem alterar P* (se M e V forem constantes)."
    )

    # Exibição em cards
    CARD_STYLE = "background:#1e1e2e;color:#e0e0e0;border-radius:8px;padding:18px;margin-bottom:14px;border-left:5px solid {color};"
    TITLE_STYLE = "color:{color};font-weight:700;font-size:1.05em;margin-bottom:8px;"

    with st.container():
        st.markdown(f"""
        <div style="{CARD_STYLE.format(color='#F44336')}">
        <div style="{TITLE_STYLE.format(color='#F44336')}">🏭 1. Produto Potencial e Função de Produção</div>
        {narrativa_producao}
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="{CARD_STYLE.format(color='#2196F3')}">
        <div style="{TITLE_STYLE.format(color='#64B5F6')}">💰 2. Nível de Preços e Neutralidade da Moeda</div>
        {narrativa_monetaria}
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="{CARD_STYLE.format(color='#4CAF50')}">
        <div style="{TITLE_STYLE.format(color='#81C784')}">{ cor_trabalho} 3. Mercado de Trabalho e Ajuste Automático</div>
        {narrativa_trabalho}
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background:#2a2200;color:#e0e0e0;border-radius:8px;padding:18px;margin-bottom:14px;border-left:5px solid #FF9800;">
        <div style="color:#FFB74D;font-weight:700;font-size:1.05em;margin-bottom:8px;">🔑 4. Conclusão — Dicotomia Clássica</div>
        Na visão clássica, a economia opera em dois planos independentes:
        o <b>setor real</b> (Y* = {Y_potencial:.1f}, w* = {salario_real_eq:.3f}) é determinado por
        produtividade, tecnologia, capital e trabalho — e o <b>setor nominal</b>
        (P* = {P_equilibrio:.3f}) é determinado pela quantidade de moeda e sua velocidade.
        Políticas de demanda (fiscal ou monetária) são incapazes de alterar Y* no longo prazo:
        apenas deslocam o nível de preços. O caminho para crescimento real passa
        exclusivamente por ganhos de produtividade, acumulação de capital ou expansão da força de trabalho.
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# ██████████████████  VISÃO KEYNESIANA  ████████████████████████
# ═══════════════════════════════════════════════════════════════
else:

    st.subheader("📊 Escola Keynesiana — Demanda Efetiva Determina o Produto")

    with st.expander("📖 Fundamentos da Escola Keynesiana", expanded=False):
        st.markdown("""
        | Princípio | Descrição |
        |-----------|-----------|
        | **Demanda Efetiva** | É a demanda agregada que determina o nível de produto e emprego |
        | **Rigidez de Preços/Salários** | Preços e salários são rígidos no curto prazo (especialmente para baixo) |
        | **Desemprego Involuntário** | A economia pode se equilibrar abaixo do pleno emprego |
        | **Multiplicador** | Variações em G ou I têm efeito amplificado sobre Y via multiplicador |
        | **Armadilha da Liquidez** | Em crises, política monetária pode ser ineficaz |
        | **Papel do Estado** | Política fiscal ativa é necessária para estabilizar a economia |
        """)

    # ── PAINEL DE CONTROLES ──────────────────────────────────────
    st.markdown("### ⚙️ Parâmetros")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**🏛️ Política Fiscal**")
        G  = st.slider("Gasto do Governo (G)", 0.0, 100.0, 30.0, 1.0,
                       help="Gasto público autônomo — desloca DA para cima")
        T  = st.slider("Impostos (T)", 0.0, 80.0, 20.0, 1.0,
                       help="Impostos — reduzem renda disponível e consumo")
        TR = st.slider("Transferências (TR)", 0.0, 50.0, 10.0, 1.0,
                       help="Transferências do governo — aumentam renda disponível")

    with col2:
        st.markdown("**🏠 Setor Privado**")
        C0  = st.slider("Consumo Autônomo (C₀)", 0.0, 80.0, 20.0, 1.0,
                        help="Consumo independente da renda")
        mpc = st.slider("Propensão Marginal a Consumir (c)", 0.50, 0.95, 0.75, 0.01,
                        help="Fração da renda disponível gasta em consumo")
        I0  = st.slider("Investimento Autônomo (I₀)", 0.0, 80.0, 25.0, 1.0,
                        help="Investimento independente da taxa de juros")

    with col3:
        st.markdown("**💹 Outros**")
        taxa_juros = st.slider("Taxa de Juros (r)", 0.0, 0.20, 0.05, 0.005,
                               format="%.3f",
                               help="Taxa de juros — reduz investimento sensível a juros")
        b_inv      = st.slider("Sensibilidade do Inv. a r (b)", 0.0, 200.0, 50.0, 5.0,
                               help="Quanto o investimento cai para cada 1% de aumento em r")
        Y_pleno    = st.slider("Produto Potencial (Ȳ)", 100.0, 400.0, 250.0, 10.0,
                               help="Produto de pleno emprego — referência para o hiato")

    # ── CÁLCULOS KEYNESIANOS ─────────────────────────────────────
    # Renda disponível: Yd = Y - T + TR
    # Consumo: C = C0 + c*(Y - T + TR)
    # Investimento: I = I0 - b*r
    # DA = C + I + G = C0 + c*(Y - T + TR) + I0 - b*r + G
    # Equilíbrio: Y = DA → Y* = [C0 + I0 - b*r + G - c*(T - TR)] / (1 - c)

    I_eq = I0 - b_inv * taxa_juros
    numerador = C0 + I_eq + G - mpc * (T - TR)
    multiplicador = 1 / (1 - mpc)
    Y_eq = numerador * multiplicador

    # Consumo de equilíbrio
    C_eq = C0 + mpc * (Y_eq - T + TR)

    # Hiato do produto
    hiato = Y_eq - Y_pleno
    hiato_pct = (hiato / Y_pleno) * 100

    # Taxa de desemprego via Lei de Okun: u = u_natural - λ*(Y-Ȳ)/Ȳ
    u_natural = 0.05
    lambda_okun = 0.5
    u_eq = u_natural - lambda_okun * (hiato / Y_pleno)
    u_eq = max(0.0, u_eq)

    # Multiplicadores teóricos
    mult_G  = multiplicador
    mult_T  = -mpc * multiplicador
    mult_TR = mpc * multiplicador

    # Curva DA (função de Y)
    Y_range = np.linspace(0, Y_pleno * 1.6, 300)
    DA_line = C0 + (I0 - b_inv * taxa_juros) + G - mpc * (T - TR) + mpc * Y_range
    # Linha de 45° (Y = DA)
    linha_45 = Y_range

    # ── MÉTRICAS ─────────────────────────────────────────────────
    st.markdown("### 📊 Equilíbrio Keynesiano")
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Produto de Equilíbrio (Y*)", f"{Y_eq:.1f}")
    m2.metric("Produto Potencial (Ȳ)", f"{Y_pleno:.1f}")
    m3.metric("Hiato do Produto", f"{hiato:+.1f}", delta_color="normal")
    m4.metric("Multiplicador Keynesiano", f"{multiplicador:.2f}x")
    m5.metric("Desemprego Estimado", f"{u_eq*100:.1f}%",
              delta=f"{(u_eq - u_natural)*100:+.1f}pp vs natural",
              delta_color="inverse")

    # ── GRÁFICOS ─────────────────────────────────────────────────
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=(
            "Diagrama de Cruz Keynesiana (DA × 45°)",
            "Oferta e Demanda Agregada — Curto Prazo Keynesiano"
        ),
        horizontal_spacing=0.12
    )

    # ── Gráfico 1: Cruz Keynesiana ──
    # Linha 45°
    fig.add_trace(go.Scatter(
        x=Y_range, y=linha_45,
        mode="lines", name="Y = DA (45°)",
        line=dict(color="#607D8B", width=1.5, dash="dot"),
    ), row=1, col=1)

    # Curva DA
    fig.add_trace(go.Scatter(
        x=Y_range, y=DA_line,
        mode="lines", name=f"DA (c={mpc:.2f})",
        line=dict(color="#2196F3", width=2.5),
    ), row=1, col=1)

    # Linha vertical do pleno emprego
    fig.add_trace(go.Scatter(
        x=[Y_pleno, Y_pleno],
        y=[0, Y_pleno * 1.1],
        mode="lines", name=f"Pleno Emprego (Ȳ={Y_pleno:.0f})",
        line=dict(color="#4CAF50", width=2, dash="dash"),
    ), row=1, col=1)

    # Ponto de equilíbrio
    DA_at_eq = C0 + (I0 - b_inv * taxa_juros) + G - mpc * (T - TR) + mpc * Y_eq
    fig.add_trace(go.Scatter(
        x=[Y_eq], y=[DA_at_eq],
        mode="markers+text",
        name=f"Equilíbrio Y*={Y_eq:.1f}",
        marker=dict(color="#FF9800", size=12),
        text=["E*"], textposition="top right",
        textfont=dict(size=13, color="#FF9800"),
    ), row=1, col=1)

    # Área sombreada do hiato (se recessão)
    if hiato < -1:
        fig.add_vrect(
            x0=Y_eq, x1=Y_pleno,
            fillcolor="rgba(244,67,54,0.10)",
            layer="below", line_width=0,
            annotation_text="Hiato Recessivo",
            annotation_position="top left",
            annotation_font_color="#F44336",
            row=1, col=1
        )
    elif hiato > 1:
        fig.add_vrect(
            x0=Y_pleno, x1=Y_eq,
            fillcolor="rgba(255,152,0,0.10)",
            layer="below", line_width=0,
            annotation_text="Hiato Inflacionário",
            annotation_position="top left",
            annotation_font_color="#FF9800",
            row=1, col=1
        )

    fig.update_xaxes(title_text="Produto (Y) →", row=1, col=1, showgrid=True, gridcolor="#eee",
                     range=[0, Y_pleno * 1.5])
    fig.update_yaxes(title_text="Demanda Agregada (DA) →", row=1, col=1, showgrid=True, gridcolor="#eee",
                     range=[0, Y_pleno * 1.5])

    # ── Gráfico 2: OA inclinada + DA ──
    # Nível de preços base
    P_base = 1.0
    P_range_k = np.linspace(0.2, 3.0, 300)

    # DA keynesiana: Y = [C0 + I0 - b*r + G - c*(T-TR)] / (1-c) × (P_base/P)
    # (efeito riqueza/Pigou simplificado)
    DA_k = Y_eq * (P_base / P_range_k)

    # OA keynesiana de curto prazo: positivamente inclinada
    # Y = Y_pleno + φ*(P - P_base)  com φ > 0
    phi = Y_pleno * 0.8
    OA_k = Y_pleno + phi * (P_range_k - P_base)
    OA_k = np.maximum(OA_k, 0)

    # Equilíbrio OA-DA keynesiano
    # Y_eq_k ≈ Y_eq (já calculado), P_eq_k = P_base * Y_eq / Y_eq = P_base (simplificado)
    P_eq_k = P_base * (Y_eq / Y_eq) if Y_eq > 0 else P_base

    fig.add_trace(go.Scatter(
        x=DA_k, y=P_range_k,
        mode="lines", name="DA (Keynesiana)",
        line=dict(color="#2196F3", width=2.5),
    ), row=1, col=2)

    fig.add_trace(go.Scatter(
        x=OA_k, y=P_range_k,
        mode="lines", name="OA (Curto Prazo — inclinada)",
        line=dict(color="#E91E63", width=2.5),
    ), row=1, col=2)

    # OA de longo prazo (referência clássica)
    fig.add_trace(go.Scatter(
        x=[Y_pleno, Y_pleno],
        y=[0.2, 3.0],
        mode="lines", name="OA Longo Prazo (Ȳ)",
        line=dict(color="#4CAF50", width=2, dash="dash"),
    ), row=1, col=2)

    # Ponto de equilíbrio keynesiano
    fig.add_trace(go.Scatter(
        x=[Y_eq], y=[P_eq_k],
        mode="markers+text",
        name="Equilíbrio Keynesiano",
        marker=dict(color="#FF9800", size=12),
        text=["E*"], textposition="top right",
        textfont=dict(size=13, color="#FF9800"),
        showlegend=False
    ), row=1, col=2)

    # Área de desemprego (se Y* < Ȳ)
    if Y_eq < Y_pleno - 1:
        fig.add_vrect(
            x0=Y_eq, x1=Y_pleno,
            fillcolor="rgba(244,67,54,0.08)",
            layer="below", line_width=0,
            annotation_text=f"Desemprego<br>u={u_eq*100:.1f}%",
            annotation_position="top left",
            annotation_font_color="#F44336",
            row=1, col=2
        )

    fig.update_xaxes(title_text="Produto (Y) →", row=1, col=2, showgrid=True, gridcolor="#eee",
                     range=[0, Y_pleno * 1.6])
    fig.update_yaxes(title_text="Nível de Preços (P) →", row=1, col=2, showgrid=True, gridcolor="#eee",
                     range=[0.2, 3.0])

    fig.update_layout(
        height=520,
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=-0.28, xanchor="center", x=0.5),
        margin=dict(t=60, b=90)
    )

    st.plotly_chart(fig, use_container_width=True, config={"staticPlot": True})

    # ── EXPLICAÇÃO NARRATIVA COMPLETA ────────────────────────────
    st.markdown("### 📝 Análise Completa da Situação Econômica")

    # Narrativa 1: Composição da demanda
    narrativa_demanda = (
        f"A demanda agregada é composta por consumo, investimento e gasto público. "
        f"O consumo autônomo é C₀ = {C0:.1f} e a propensão marginal a consumir é c = {mpc:.2f}, "
        f"o que significa que para cada R$ 1,00 adicional de renda disponível, "
        f"R$ {mpc:.2f} são consumidos e R$ {1-mpc:.2f} são poupados. "
        f"O investimento é sensível à taxa de juros: I = I₀ - b·r = {I0:.1f} - {b_inv:.0f}×{taxa_juros:.3f} = **{I_eq:.1f}**. "
        f"Com gasto público G = {G:.1f}, impostos T = {T:.1f} e transferências TR = {TR:.1f}, "
        f"a renda disponível líquida do setor público é Yd_gov = T - TR = {T-TR:.1f}."
    )

    # Narrativa 2: Multiplicador e equilíbrio
    narrativa_multiplicador = (
        f"A demanda autônoma total (intercepto da DA) é: "
        f"A = C₀ + I + G - c·(T-TR) = {C0:.1f} + {I_eq:.1f} + {G:.1f} - {mpc:.2f}×{T-TR:.1f} = **{numerador:.1f}**. "
        f"O multiplicador keynesiano é k = 1/(1-c) = 1/(1-{mpc:.2f}) = **{multiplicador:.2f}x**. "
        f"Isso significa que cada R$ 1,00 de demanda autônoma gera R$ {multiplicador:.2f} de produto final, "
        f"pois cada rodada de gasto se torna renda de outro agente, que por sua vez gasta {mpc*100:.0f}% dela. "
        f"O produto de equilíbrio é Y* = A × k = {numerador:.1f} × {multiplicador:.2f} = **{Y_eq:.1f}**."
    )

    # Narrativa 3: Hiato e desemprego
    if abs(hiato) < 5:
        cor_hiato = "✅"
        narrativa_hiato = (
            f"O produto de equilíbrio (Y* = {Y_eq:.1f}) está muito próximo do produto potencial "
            f"(Ȳ = {Y_pleno:.1f}), com hiato de apenas {hiato:+.1f} ({hiato_pct:+.1f}%). "
            f"A economia opera essencialmente no pleno emprego, com desemprego estimado em "
            f"{u_eq*100:.1f}% — próximo à taxa natural de {u_natural*100:.0f}%."
        )
        politica_rec = "Nenhuma intervenção fiscal urgente é necessária."
    elif hiato < -5:
        cor_hiato = "🔴"
        G_necessario = abs(hiato) / mult_G
        T_necessario = abs(hiato) / abs(mult_T)
        narrativa_hiato = (
            f"A economia está em **recessão**: o produto de equilíbrio (Y* = {Y_eq:.1f}) está "
            f"**{abs(hiato):.1f} abaixo** do pleno emprego (Ȳ = {Y_pleno:.1f}), "
            f"representando um hiato recessivo de {hiato_pct:.1f}%. "
            f"Pela Lei de Okun (λ = {lambda_okun}), isso implica desemprego de "
            f"**{u_eq*100:.1f}%** — {(u_eq-u_natural)*100:.1f}pp acima da taxa natural. "
            f"Preços e salários são rígidos para baixo, portanto o ajuste automático não ocorre "
            f"— justificando intervenção fiscal ativa."
        )
        politica_rec = (
            f"Para fechar o hiato de {abs(hiato):.1f}, a política keynesiana recomenda: "
            f"**ΔG ≈ +{G_necessario:.1f}** (aumento de gastos) "
            f"OU **ΔT ≈ -{T_necessario:.1f}** (corte de impostos). "
            f"O aumento de G é mais eficaz pois seu multiplicador ({mult_G:.2f}) é maior "
            f"em módulo que o de T ({abs(mult_T):.2f})."
        )
    else:
        cor_hiato = "🟡"
        G_corte = hiato / mult_G
        narrativa_hiato = (
            f"A economia está **superaquecida**: o produto de equilíbrio (Y* = {Y_eq:.1f}) "
            f"supera o pleno emprego (Ȳ = {Y_pleno:.1f}) em **+{hiato:.1f}** ({hiato_pct:+.1f}%). "
            f"Isso gera pressões inflacionárias, pois a demanda excede a capacidade produtiva. "
            f"O desemprego estimado ({u_eq*100:.1f}%) está abaixo da taxa natural ({u_natural*100:.0f}%), "
            f"indicando mercado de trabalho aquecido com risco de espiral salário-preço."
        )
        politica_rec = (
            f"Para conter o superaquecimento, recomenda-se contração fiscal: "
            f"**ΔG ≈ -{G_corte:.1f}** (corte de gastos) ou aumento equivalente de impostos. "
            f"Política monetária contracionista (aumento de r) também reduziria I e, "
            f"via multiplicador, o produto."
        )

    # Exibição em cards
    hiato_color = '#F44336' if hiato < -5 else '#FF9800' if hiato > 5 else '#4CAF50'
    hiato_title_color = '#EF9A9A' if hiato < -5 else '#FFB74D' if hiato > 5 else '#81C784'

    st.markdown(f"""
    <div style="background:#1e1e2e;color:#e0e0e0;border-radius:8px;padding:18px;margin-bottom:14px;border-left:5px solid #2196F3;">
    <div style="color:#64B5F6;font-weight:700;font-size:1.05em;margin-bottom:8px;">📦 1. Composição da Demanda Agregada</div>
    {narrativa_demanda}
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:#1e1e2e;color:#e0e0e0;border-radius:8px;padding:18px;margin-bottom:14px;border-left:5px solid #9C27B0;">
    <div style="color:#CE93D8;font-weight:700;font-size:1.05em;margin-bottom:8px;">⚙️ 2. Multiplicador Keynesiano e Equilíbrio</div>
    {narrativa_multiplicador}
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:#1e1e2e;color:#e0e0e0;border-radius:8px;padding:18px;margin-bottom:14px;border-left:5px solid {hiato_color};">
    <div style="color:{hiato_title_color};font-weight:700;font-size:1.05em;margin-bottom:8px;">{cor_hiato} 3. Hiato do Produto e Desemprego</div>
    {narrativa_hiato}
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:#2a2200;color:#e0e0e0;border-radius:8px;padding:18px;margin-bottom:14px;border-left:5px solid #FF9800;">
    <div style="color:#FFB74D;font-weight:700;font-size:1.05em;margin-bottom:8px;">🏛️ 4. Recomendação de Política Econômica</div>
    {politica_rec}<br><br>
    <span style="color:#FFB74D;font-weight:600;">Multiplicadores disponíveis:</span>
    ΔG → k<sub>G</sub> = <b>{mult_G:.2f}x</b> &nbsp;|&nbsp;
    ΔT → k<sub>T</sub> = <b>{mult_T:.2f}x</b> &nbsp;|&nbsp;
    ΔTR → k<sub>TR</sub> = <b>{mult_TR:.2f}x</b>
    </div>
    """, unsafe_allow_html=True)

    # ── COMPARATIVO RÁPIDO ───────────────────────────────────────
    with st.expander("📚 Clássico vs Keynesiano — Resumo Comparativo"):
        st.markdown("""
        | Dimensão | Escola Clássica | Escola Keynesiana |
        |----------|----------------|-------------------|
        | **Determinante do produto** | Oferta (fatores de produção) | Demanda efetiva |
        | **Preços e salários** | Flexíveis | Rígidos no curto prazo |
        | **Desemprego** | Apenas friccional/voluntário | Involuntário possível |
        | **Política fiscal** | Ineficaz (crowding-out total) | Eficaz via multiplicador |
        | **Política monetária** | Afeta apenas P (neutralidade) | Afeta Y no curto prazo |
        | **OA no curto prazo** | Vertical (pleno emprego) | Positivamente inclinada |
        | **Horizonte** | Longo prazo | Curto prazo |
        | **Frase síntese** | "No longo prazo, estamos todos mortos" (crítica) | "A demanda cria sua própria oferta" |
        """)