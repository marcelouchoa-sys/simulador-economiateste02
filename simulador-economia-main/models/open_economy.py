# pages/4_🌍_Economia_Aberta.py
import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from core.parameters import DEFAULT_PARAMS
from models.open_economy import (
    curva_IS, curva_LM, curva_BP,
    solve_islm_open, exportacoes_liquidas
)

st.set_page_config(layout="wide", page_title="Economia Aberta — IS-LM-BP")

# ─────────────────────────────────────────────────────────────────
# ESTADO GLOBAL
# ─────────────────────────────────────────────────────────────────
if "params" not in st.session_state:
    st.session_state.params = DEFAULT_PARAMS.copy()

_defaults_aberta = {
    "x0": 50.0, "x1": 30.0, "m0": 20.0, "m1": 0.10,
    "kf": 80.0, "r_star": 0.05, "e": 1.0,
    "tipo_economia": "Aberta", "regime_cambial": "Flexível",
}
for k, v in _defaults_aberta.items():
    if k not in st.session_state.params:
        st.session_state.params[k] = v

p = st.session_state.params

# ─────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────
def _kappa_label(kf):
    if kf <= 1e-4:   return "Nula"
    if kf <= 20:     return "Baixa"
    if kf <= 80:     return "Moderada"
    if kf <= 300:    return "Alta"
    return "Perfeita"

def _kappa_norm(kf):
    return min(1.0, kf / 300.0)

# ─────────────────────────────────────────────────────────────────
# BP DIDÁTICA (separada da numérica)
# ─────────────────────────────────────────────────────────────────
def curva_BP_plot(Y_grid, r_star, kf, Y_anchor, r_anchor):
    """
    BP para fins didáticos/gráficos — não usa NX diretamente.
    - kf → ∞  : horizontal em r_star
    - kf → 0  : vertical (retornamos None, tratado separado)
    - intermediário: slope = 1/kf, ancorada no equilíbrio A
    """
    if kf >= 1e6:
        return np.full_like(Y_grid, r_star)
    slope = 1.0 / max(kf, 1e-6)
    return r_anchor + slope * (Y_grid - Y_anchor)

# ─────────────────────────────────────────────────────────────────
# PROJEÇÕES DIDÁTICAS (linhas tracejadas até os eixos)
# ─────────────────────────────────────────────────────────────────
def _add_projecoes(fig, pontos, x_min, y_min):
    """
    pontos: lista de (Y, r, label, color)
    Adiciona:
      - linha vertical tracejada do ponto até o eixo X
      - linha horizontal tracejada do ponto até o eixo Y
      - marcador com rótulo
    """
    for Y_pt, r_pt, label, color in pontos:
        # Vertical até eixo X
        fig.add_shape(
            type="line",
            x0=Y_pt, y0=y_min, x1=Y_pt, y1=r_pt,
            line=dict(color="gray", width=1, dash="dot")
        )
        # Horizontal até eixo Y
        fig.add_shape(
            type="line",
            x0=x_min, y0=r_pt, x1=Y_pt, y1=r_pt,
            line=dict(color="gray", width=1, dash="dot")
        )
        # Marcador
        fig.add_trace(go.Scatter(
            x=[Y_pt], y=[r_pt],
            mode="markers+text",
            marker=dict(color=color, size=13, symbol="circle",
                        line=dict(width=2, color="white")),
            text=[label],
            textposition="top right",
            textfont=dict(size=15, color="black"),
            showlegend=False
        ))

# ─────────────────────────────────────────────────────────────────
# GRÁFICO QUALITATIVO (MODO SIMPLIFICADO)
# ─────────────────────────────────────────────────────────────────
def grafico_simplificado(politica, direcao, tipo_eco, regime, kf=80.0):
    fiscal   = politica == "Fiscal"
    expansao = direcao  == "Expansionista"
    aberta   = tipo_eco == "Aberta"
    flex     = regime   == "Flexível"
    kappa    = _kappa_norm(kf)

    # Range do gráfico — fixo e normalizado
    X_MIN, X_MAX = 0.0, 2.0
    Y_MIN, Y_MAX = 0.0, 1.15

    Y = np.linspace(0.05, 1.95, 300)

    # ── Curvas base ──────────────────────────────────────────────
    r_IS0 = 1.20 - 0.80 * Y
    r_LM0 = -0.40 + 0.60 * Y

    # Equilíbrio A = IS0 ∩ LM0
    YA = 1.60 / 1.40
    rA = 1.20 - 0.80 * YA

    shift = 0.35

    # ── Choque e pontos B, C ─────────────────────────────────────
    r_IS1 = r_IS0.copy()
    r_LM1 = r_LM0.copy()
    r_IS2 = None

    if fiscal:
        s = shift if expansao else -shift
        r_IS1 = r_IS0 + s
        YB = (1.60 + s) / 1.40
        rB = 1.20 + s - 0.80 * YB
        YC, rC = YB, rB
        if aberta and flex:
            s2 = s * (1.0 - kappa * 0.85)
            r_IS2 = r_IS0 + s2
            YC = (1.60 + s2) / 1.40
            rC = 1.20 + s2 - 0.80 * YC
    else:
        s = -shift if expansao else shift
        r_LM1 = r_LM0 + s
        YB = (1.60 - s) / 1.40
        rB = 1.20 - 0.80 * YB
        YC, rC = YB, rB
        if aberta and flex:
            s_is = (shift * 0.6 * kappa) * (1 if expansao else -1)
            r_IS2 = r_IS0 + s_is
            YC = (1.60 + s_is - s) / 1.40
            rC = 1.20 + s_is - 0.80 * YC

    fig = go.Figure()

    # ── BP DIDÁTICA ───────────────────────────────────────────────
    if aberta:
        if kf <= 1e-4:
            # Vertical em YA
            fig.add_shape(
                type="line",
                x0=YA, y0=Y_MIN, x1=YA, y1=Y_MAX,
                line=dict(color="#2e7d32", width=2.5, dash="dash")
            )
            fig.add_trace(go.Scatter(
                x=[YA], y=[Y_MAX * 0.95],
                mode="text", text=["BP (imobilidade)"],
                textfont=dict(color="#2e7d32", size=11),
                showlegend=False
            ))
        else:
            r_BP = curva_BP_plot(Y, r_star=rA, kf=kf, Y_anchor=YA, r_anchor=rA)
            fig.add_trace(go.Scatter(
                x=Y, y=r_BP,
                name=f"BP ({_kappa_label(kf)})",
                line=dict(color="#2e7d32", width=2.5, dash="dash")
            ))

    # ── Curvas base ──────────────────────────────────────────────
    fig.add_trace(go.Scatter(x=Y, y=r_IS0, name="IS₀",
                             line=dict(color="#1565c0", width=3)))
    fig.add_trace(go.Scatter(x=Y, y=r_LM0, name="LM₀",
                             line=dict(color="#c62828", width=3)))

    # ── Curvas deslocadas ─────────────────────────────────────────
    if fiscal:
        fig.add_trace(go.Scatter(x=Y, y=r_IS1,
                                 name="IS₁  ← choque fiscal",
                                 line=dict(color="#1565c0", width=2.5, dash="dot")))
    else:
        fig.add_trace(go.Scatter(x=Y, y=r_LM1,
                                 name="LM₁  ← choque monetário",
                                 line=dict(color="#c62828", width=2.5, dash="dot")))

    if r_IS2 is not None:
        fig.add_trace(go.Scatter(x=Y, y=r_IS2,
                                 name="IS₂  ← ajuste cambial",
                                 line=dict(color="#6a1b9a", width=2.5, dash="longdash")))

    # ── Projeções tracejadas até os eixos ────────────────────────
    pontos_proj = [
        (YA, rA, "A", "#1565c0"),
        (YB, rB, "B", "#f9a825"),
    ]
    if abs(YC - YB) > 1e-4 or abs(rC - rB) > 1e-4:
        pontos_proj.append((YC, rC, "C", "#2e7d32"))

    _add_projecoes(fig, pontos_proj, x_min=X_MIN, y_min=Y_MIN)

    # ── Setas A → B e B → C ──────────────────────────────────────
    fig.add_annotation(
        ax=YA, ay=rA, x=YB, y=rB,
        xref="x", yref="y", axref="x", ayref="y",
        showarrow=True, arrowhead=3, arrowwidth=2.5,
        arrowcolor="#f9a825"
    )
    if abs(YC - YB) > 1e-4 or abs(rC - rB) > 1e-4:
        fig.add_annotation(
            ax=YB, ay=rB, x=YC, y=rC,
            xref="x", yref="y", axref="x", ayref="y",
            showarrow=True, arrowhead=3, arrowwidth=2.5,
            arrowcolor="#2e7d32"
        )

    # ── Anotações textuais ────────────────────────────────────────
    if fiscal and expansao:
        fig.add_annotation(x=YA + 0.05, y=rA + 0.08,
            text="G↑ → IS →", showarrow=False,
            font=dict(size=11, color="#1565c0"))
        if aberta and flex:
            fig.add_annotation(x=YC - 0.05, y=rC - 0.10,
                text="NX↓ → IS ←", showarrow=False,
                font=dict(size=11, color="#6a1b9a"))
    elif not fiscal and expansao:
        fig.add_annotation(x=YA - 0.15, y=rA - 0.12,
            text="M↑ → LM →", showarrow=False,
            font=dict(size=11, color="#c62828"))

    # ── Rótulos qualitativos nos eixos ────────────────────────────
    # Coleta os Y e r únicos dos pontos para tickvals
    tick_Y_vals = [YA, YB]
    tick_Y_text = ["Yₐ", "Y_b"]
    tick_r_vals = [rA, rB]
    tick_r_text = ["iₐ", "i_b"]

    if abs(YC - YB) > 1e-4:
        tick_Y_vals.append(YC)
        tick_Y_text.append("Y_c")
    if abs(rC - rB) > 1e-4:
        tick_r_vals.append(rC)
        tick_r_text.append("i_c")

    fig.update_layout(
        title=dict(
            text=f"IS-LM {'+ BP' if aberta else ''} — {politica} {direcao}",
            font=dict(size=16)
        ),
        xaxis=dict(
            title="Produto / Renda (Y) →",
            showgrid=False,
            zeroline=True, zerolinecolor="#999", zerolinewidth=2,
            range=[X_MIN, X_MAX],
            tickvals=tick_Y_vals,
            ticktext=tick_Y_text,
            tickfont=dict(size=13),
            fixedrange=True   # 🔒 trava zoom/pan no eixo X
        ),
        yaxis=dict(
            title="Taxa de Juros (i) →",
            showgrid=False,
            zeroline=True, zerolinecolor="#999", zerolinewidth=2,
            range=[Y_MIN, Y_MAX],
            tickvals=tick_r_vals,
            ticktext=tick_r_text,
            tickfont=dict(size=13),
            fixedrange=True   # 🔒 trava zoom/pan no eixo Y
        ),
        template="plotly_white",
        height=520,
        legend=dict(x=0.01, y=0.99, bgcolor="rgba(255,255,255,0.85)",
                    bordercolor="#ccc", borderwidth=1),
        plot_bgcolor="#fafafa",
        margin=dict(l=60, r=30, t=60, b=60),
        dragmode=False   # 🔒 desativa arraste
    )
    return fig

# config para passar no st.plotly_chart — remove barra de ferramentas
CONFIG_SIMPLIFICADO = {
    "staticPlot": False,
    "scrollZoom": False,
    "doubleClick": False,
    "showAxisDragHandles": False,
    "showAxisRangeEntryBoxes": False,
    "displayModeBar": False   # 🔒 remove botões de zoom/pan/download
}

# ─────────────────────────────────────────────────────────────────
# EXPLICAÇÃO CAUSAL A → B → C  (inalterada)
# ─────────────────────────────────────────────────────────────────
def gerar_explicacao(tipo_eco, regime, politica, direcao, kf):
    fiscal   = politica == "Fiscal"
    expansao = direcao  == "Expansionista"
    aberta   = tipo_eco == "Aberta"
    flex     = regime   == "Flexível"
    mob_label = _kappa_label(kf)
    kappa     = _kappa_norm(kf)

    exp = []

    if fiscal and expansao:
        exp.append(("ponto_a", f"""
**Choque no Mercado de Bens — `G ↑`**

O aumento dos gastos públicos ($G \\uparrow$) **desloca a curva IS para a direita**.

- A IS representa o equilíbrio no mercado de bens: $Y = C + I + G + NX$.
- Com $G \\uparrow$, a demanda agregada supera a produção corrente → **excesso de demanda por bens**.
- As firmas reagem elevando a produção: **renda cresce** ($Y \\uparrow$).

> 📌 No gráfico: IS₀ → IS₁. O equilíbrio se move do ponto **A** para um ponto intermediário.
"""))
        exp.append(("ponto_b", f"""
**Mecanismo Monetário — Pressão sobre os Juros**

Com $Y \\uparrow$, a demanda por moeda aumenta:

$$L = L(Y, i) \\quad \\Rightarrow \\quad L \\uparrow$$

- A oferta monetária está **fixa** ($M$ constante).
- O excesso de demanda por moeda força a **taxa de juros a subir** ($i \\uparrow$).
- Juros maiores encarecem o crédito e **reduzem o investimento privado**:

$$I = I_0 - b \\cdot i \\quad \\Rightarrow \\quad I \\downarrow$$

- Esse efeito é o **crowding-out**: parte do estímulo fiscal é anulada pela queda do investimento.

> 📌 No gráfico: o equilíbrio sobe ao longo da LM₀ até o ponto **B** (Y maior, i maior).
"""))
        if aberta and flex:
            intensidade = "muito forte" if kappa >= 0.8 else "moderada" if kappa >= 0.4 else "fraca"
            exp.append(("ponto_c", f"""
**Setor Externo — Mobilidade de Capital e Câmbio Flexível**

Com $i > i^*$ (juros domésticos acima do externo):

1. **Entrada de capital financeiro** — investidores estrangeiros buscam o diferencial de juros.
2. **Apreciação cambial** — a demanda por moeda doméstica valoriza a taxa de câmbio ($e \\downarrow$).
3. **Exportações líquidas caem** ($NX \\downarrow$) — produtos domésticos ficam mais caros no exterior.
4. **IS recua parcialmente** — a queda de $NX$ desloca a IS de volta para a esquerda (IS₁ → IS₂).

**Mobilidade de capital selecionada:** {mob_label} ($\\kappa \\approx {kappa:.2f}$)

- Intensidade do efeito cambial: **{intensidade}**
- Quanto maior $\\kappa$, mais capital entra, mais forte a apreciação e maior o recuo da IS.

> 📌 No gráfico: IS₁ → IS₂ (linha roxa). Equilíbrio final no ponto **C**.
"""))
        elif aberta and not flex:
            exp.append(("ponto_c", f"""
**Setor Externo — Câmbio Fixo**

Com $i > i^*$, há **entrada de capital**.

- Sob câmbio fixo, o Banco Central **intervém comprando moeda estrangeira** para manter a paridade.
- Essa intervenção **expande a base monetária** → LM se desloca para a direita.
- O resultado é uma **amplificação da política fiscal** (sem o crowding-out cambial).

**Mobilidade:** {mob_label} ($\\kappa \\approx {kappa:.2f}$)

> 📌 Resultado clássico de Mundell-Fleming: política fiscal é **mais eficaz** sob câmbio fixo.
"""))
        else:
            exp.append(("ponto_c", """
**Economia Fechada — Sem Canal Externo**

Não há setor externo operando. O ajuste termina no sistema IS-LM.

- Resultado final: $Y \\uparrow$, $i \\uparrow$, crowding-out parcial do investimento.
"""))
        exp.append(("conclusao", f"""
**Síntese da Política Fiscal Expansionista**

| Etapa | Mercado | Efeito |
|-------|---------|--------|
| A | Bens | $G \\uparrow$ → IS desloca → $Y \\uparrow$ |
| B | Monetário | $Y \\uparrow$ → $L \\uparrow$ → $i \\uparrow$ → $I \\downarrow$ (crowding-out) |
| C | Externo | $i > i^*$ → capital entra → câmbio aprecia → $NX \\downarrow$ → IS recua |

O impacto líquido sobre $Y$ depende da **mobilidade de capital** e do **regime cambial**.
"""))

    elif fiscal and not expansao:
        exp.append(("ponto_a", """
**Choque no Mercado de Bens — `G ↓`**

A redução dos gastos públicos **desloca a IS para a esquerda**.

- Queda da demanda agregada → **excesso de oferta de bens**.
- Firmas reduzem produção: **renda cai** ($Y \\downarrow$).
"""))
        exp.append(("ponto_b", """
**Mecanismo Monetário — Queda dos Juros**

Com $Y \\downarrow$, a demanda por moeda cai ($L \\downarrow$).

- Excesso de oferta de moeda → **juros caem** ($i \\downarrow$).
- Juros menores estimulam o investimento ($I \\uparrow$), **amortecendo parcialmente** a recessão.
"""))
        if aberta and flex:
            exp.append(("ponto_c", f"""
**Setor Externo — Câmbio Flexível**

Com $i < i^*$: **saída de capital** → **depreciação cambial** ($e \\uparrow$).

- Depreciação melhora competitividade: $NX \\uparrow$.
- IS se desloca parcialmente de volta para a direita.
- O setor externo **compensa parte da contração fiscal**.

**Mobilidade:** {mob_label} ($\\kappa \\approx {kappa:.2f}$)
"""))
        exp.append(("conclusao", """
**Síntese:** Contração fiscal reduz $Y$ e $i$. Em economia aberta com câmbio flexível,
a depreciação cambial e a melhora das exportações líquidas amortecem parcialmente a queda.
"""))

    elif not fiscal and expansao:
        exp.append(("ponto_a", """
**Choque no Mercado Monetário — `M ↑`**

O aumento da oferta monetária **desloca a LM para a direita**.

- Excesso de oferta de moeda → **juros caem** ($i \\downarrow$).
"""))
        exp.append(("ponto_b", """
**Transmissão ao Mercado de Bens**

Com $i \\downarrow$, o investimento privado aumenta:

$$I = I_0 - b \\cdot i \\quad \\Rightarrow \\quad I \\uparrow$$

- Maior investimento eleva a demanda agregada → **renda cresce** ($Y \\uparrow$).
"""))
        if aberta and flex:
            exp.append(("ponto_c", f"""
**Setor Externo — Câmbio Flexível**

Com $i < i^*$: **saída de capital** → **depreciação cambial** ($e \\uparrow$).

- Depreciação melhora exportações líquidas ($NX \\uparrow$).
- IS se desloca para a direita → **amplifica a política monetária**.

**Mobilidade:** {mob_label} ($\\kappa \\approx {kappa:.2f}$)

> 📌 Resultado clássico: política monetária é **mais eficaz** sob câmbio flexível.
"""))
        exp.append(("conclusao", """
**Síntese:** $M \\uparrow$ → $i \\downarrow$ → $I \\uparrow$ → $Y \\uparrow$.
Em economia aberta com câmbio flexível, a depreciação reforça o efeito via $NX \\uparrow$.
"""))

    else:
        exp.append(("ponto_a", """
**Choque no Mercado Monetário — `M ↓`**

A redução da oferta monetária **desloca a LM para a esquerda**.

- Escassez de moeda → **juros sobem** ($i \\uparrow$).
"""))
        exp.append(("ponto_b", """
**Transmissão ao Mercado de Bens**

Com $i \\uparrow$, o investimento cai ($I \\downarrow$) → demanda agregada cai → **renda cai** ($Y \\downarrow$).
"""))
        if aberta and flex:
            exp.append(("ponto_c", f"""
**Setor Externo — Câmbio Flexível**

Com $i > i^*$: **entrada de capital** → **apreciação cambial** ($e \\downarrow$).

- Apreciação reduz exportações líquidas ($NX \\downarrow$).
- IS se desloca para a esquerda → **amplifica a contração monetária**.

**Mobilidade:** {mob_label} ($\\kappa \\approx {kappa:.2f}$)
"""))
        exp.append(("conclusao", """
**Síntese:** $M \\downarrow$ → $i \\uparrow$ → $I \\downarrow$ → $Y \\downarrow$.
Em economia aberta com câmbio flexível, a apreciação reforça a contração via $NX \\downarrow$.
"""))

    return exp


# ─────────────────────────────────────────────────────────────────
# GRÁFICO NUMÉRICO (MODO COMPLEXO — inalterado)
# ─────────────────────────────────────────────────────────────────
def grafico_numerico(p_base, p_choque, mostrar_bp=True):
    e = p_base.get("e", 1.0)
    Y_max = max(
        p_base.get("G", 200) + p_base.get("I0", 150) + p_base.get("c0", 100),
        3500
    )
    Y_grid = np.linspace(10, Y_max, 400)

    eq_base   = solve_islm_open(p_base,   e)
    eq_choque = solve_islm_open(p_choque, e)

    r_IS_b = curva_IS(Y_grid, p_base,   e)
    r_LM_b = curva_LM(Y_grid, p_base)
    r_IS_c = curva_IS(Y_grid, p_choque, e)
    r_LM_c = curva_LM(Y_grid, p_choque)

    kf     = p_base.get("kf",     80.0)
    r_star = p_base.get("r_star", 0.05)
    m1     = p_base.get("m1",     0.10)
    x0     = p_base.get("x0",     50.0)
    x1     = p_base.get("x1",     30.0)
    m0     = p_base.get("m0",     20.0)
    r_BP   = curva_BP(Y_grid, e, x0, x1, m0, m1, kf, r_star)

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=Y_grid, y=r_IS_b, name="IS (Base)",
                             line=dict(color="#1565c0", width=3)))
    fig.add_trace(go.Scatter(x=Y_grid, y=r_LM_b, name="LM (Base)",
                             line=dict(color="#c62828", width=3)))
    fig.add_trace(go.Scatter(x=Y_grid, y=r_IS_c, name="IS (Choque)",
                             line=dict(color="#1565c0", width=2.5, dash="dot")))
    fig.add_trace(go.Scatter(x=Y_grid, y=r_LM_c, name="LM (Choque)",
                             line=dict(color="#c62828", width=2.5, dash="dot")))

    if mostrar_bp and p_base.get("tipo_economia") == "Aberta":
        if kf <= 1e-6:
            Y_bp = (x0 + x1 * e - m0) / max(m1, 1e-9)
            r_range = [r_IS_b.min(), r_IS_b.max()]
            fig.add_trace(go.Scatter(
                x=[Y_bp, Y_bp], y=r_range,
                name="BP (imobilidade)",
                line=dict(color="#2e7d32", width=2.5, dash="dash")
            ))
        else:
            fig.add_trace(go.Scatter(
                x=Y_grid, y=r_BP,
                name=f"BP ({_kappa_label(kf)})",
                line=dict(color="#2e7d32", width=2.5, dash="dash")
            ))

    if eq_base:
        fig.add_trace(go.Scatter(
            x=[eq_base["Y"]], y=[eq_base["r"]],
            mode="markers+text",
            marker=dict(color="#1565c0", size=12, symbol="circle"),
            text=["E₀"], textposition="top right",
            name="Equilíbrio Base"
        ))
    if eq_choque:
        fig.add_trace(go.Scatter(
            x=[eq_choque["Y"]], y=[eq_choque["r"]],
            mode="markers+text",
            marker=dict(color="#c62828", size=12, symbol="diamond"),
            text=["E₁"], textposition="top right",
            name="Equilíbrio Choque"
        ))
        if eq_base:
            fig.add_annotation(
                ax=eq_base["Y"], ay=eq_base["r"],
                x=eq_choque["Y"], y=eq_choque["r"],
                xref="x", yref="y", axref="x", ayref="y",
                showarrow=True, arrowhead=3, arrowwidth=2,
                arrowcolor="#f9a825"
            )

    fig.update_layout(
        title="IS-LM-BP — Modo Numérico",
        xaxis_title="Produto / Renda (Y)",
        yaxis_title="Taxa de Juros (r)",
        template="plotly_white",
        height=520,
        legend=dict(x=0.01, y=0.99),
    )
    return fig, eq_base, eq_choque


# ─────────────────────────────────────────────────────────────────
# INTERFACE PRINCIPAL
# ─────────────────────────────────────────────────────────────────
st.title("🌍 Economia Aberta — IS-LM-BP")
st.caption("Modelo de Mundell-Fleming | UFRRJ")

aba_simples, aba_complexa = st.tabs([
    "🎓 Modo Simplificado (didático)",
    "🔢 Modo Complexo (numérico)"
])

# ═══════════════════════════════════════════════════════════════
# ABA 1 — MODO SIMPLIFICADO
# ═══════════════════════════════════════════════════════════════
with aba_simples:
    st.markdown("### Configuração do Cenário")

    col_cfg1, col_cfg2, col_cfg3, col_cfg4 = st.columns(4)
    with col_cfg1:
        tipo_eco_s = st.selectbox("Tipo de Economia", ["Aberta", "Fechada"], key="s_tipo")
    with col_cfg2:
        regime_s = st.selectbox("Regime Cambial", ["Flexível", "Fixo"], key="s_regime",
                                disabled=(tipo_eco_s == "Fechada"))
    with col_cfg3:
        politica_s = st.selectbox("Política Econômica", ["Fiscal", "Monetária"], key="s_pol")
    with col_cfg4:
        direcao_s = st.selectbox("Direção", ["Expansionista", "Contracionista"], key="s_dir")

    st.markdown("---")
    col_mob1, col_mob2 = st.columns([1, 2])
    with col_mob1:
        kf_s = st.select_slider(
            "Mobilidade de Capital (κ)",
            options=[0.0, 10.0, 50.0, 80.0, 150.0, 300.0, 1e7],
            value=80.0,
            format_func=lambda v: {
                0.0: "Nula (BP vertical)",
                10.0: "Baixa",
                50.0: "Moderada-baixa",
                80.0: "Moderada",
                150.0: "Alta",
                300.0: "Muito Alta",
                1e7: "Perfeita (BP horizontal)"
            }.get(v, str(v)),
            key="s_kf",
            disabled=(tipo_eco_s == "Fechada")
        )
    with col_mob2:
        st.markdown("""
        **Interpretação de κ:**
        - **Nula:** BP vertical — fluxos de capital não respondem ao diferencial de juros
        - **Baixa/Moderada:** BP positivamente inclinada — resposta parcial
        - **Perfeita:** BP horizontal — qualquer diferencial $i - i^*$ gera fluxo infinito
        """)

    st.markdown("---")

    col_g, col_e = st.columns([3, 2])
    with col_g:
        fig_s = grafico_simplificado(
            politica_s, direcao_s, tipo_eco_s, regime_s,
            kf=kf_s if tipo_eco_s == "Aberta" else 0.0
        )
        # 🔒 CONFIG_SIMPLIFICADO trava zoom/pan e remove barra de ferramentas
        st.plotly_chart(fig_s, use_container_width=True, config=CONFIG_SIMPLIFICADO)

    with col_e:
        st.markdown("### 🗺️ Legenda dos Pontos")
        st.markdown("""
        | Ponto | Significado |
        |-------|-------------|
        | 🔵 **A** | Equilíbrio inicial (IS₀ ∩ LM₀) |
        | 🟡 **B** | Após choque interno (IS-LM) |
        | 🟢 **C** | Após ajuste externo (câmbio) |
        """)
        st.markdown("### 🎨 Curvas")
        st.markdown("""
        - **Azul sólido** — IS₀ (base)
        - **Azul pontilhado** — IS₁ (após choque fiscal)
        - **Roxo tracejado** — IS₂ (após ajuste cambial)
        - **Vermelho sólido** — LM₀ (base)
        - **Vermelho pontilhado** — LM₁ (após choque monetário)
        - **Verde tracejado** — BP
        """)

    st.markdown("---")
    st.markdown("## 📖 Análise Causal: A → B → C")

    explicacao = gerar_explicacao(
        tipo_eco_s, regime_s, politica_s, direcao_s,
        kf=kf_s if tipo_eco_s == "Aberta" else 0.0
    )

    for tipo, texto in explicacao:
        if tipo == "ponto_a":
            st.markdown("#### 1️⃣ Ponto A — Choque Inicial")
            st.info(texto)
        elif tipo == "ponto_b":
            st.markdown("#### 2️⃣ Ponto B — Mecanismo de Transmissão")
            st.warning(texto)
        elif tipo == "ponto_c":
            st.markdown("#### 3️⃣ Ponto C — Setor Externo e Mobilidade de Capital")
            st.success(texto)
        elif tipo == "conclusao":
            st.markdown("#### 4️⃣ Conclusão")
            with st.expander("📊 Ver síntese completa", expanded=True):
                st.success(texto)


# ═══════════════════════════════════════════════════════════════
# ABA 2 — MODO COMPLEXO (NUMÉRICO — inalterado)
# ═══════════════════════════════════════════════════════════════
with aba_complexa:
    st.markdown("### ⚙️ Parâmetros Numéricos")

    col_b, col_c = st.columns(2)

    def _num_input(label, key, default, min_v, max_v, step, col):
        return col.number_input(label, min_value=min_v, max_value=max_v,
                                value=float(p.get(key, default)),
                                step=step, key=f"cx_{key}")

    with col_b:
        st.markdown("**📘 Cenário Base**")
        c0_b  = _num_input("c0 — Consumo autônomo",    "c0",  100.0, 0.0,  500.0, 10.0, col_b)
        c1_b  = _num_input("c1 — PMgC",                "c1",  0.80,  0.01, 0.99,  0.01, col_b)
        T_b   = _num_input("T — Impostos",             "T",   100.0, 0.0,  500.0, 10.0, col_b)
        I0_b  = _num_input("I0 — Invest. autônomo",    "I0",  150.0, 0.0,  500.0, 10.0, col_b)
        b_b   = _num_input("b — Sensib. invest. juros","b",   50.0,  1.0,  300.0, 5.0,  col_b)
        G_b   = _num_input("G — Gastos do governo",    "G",   200.0, 0.0, 1000.0, 10.0, col_b)
        k_b   = _num_input("k — Sensib. demanda moeda","k",   0.50,  0.01, 2.0,   0.05, col_b)
        h_b   = _num_input("h — Sensib. LM a juros",  "h",   100.0, 1.0,  500.0, 10.0, col_b)
        M_b   = _num_input("M — Oferta monetária",     "M",   500.0, 10.0,5000.0, 50.0, col_b)

    with col_c:
        st.markdown("**📕 Cenário Choque**")
        c0_c  = col_c.number_input("c0", value=c0_b, step=10.0, key="cx_c0c")
        c1_c  = col_c.number_input("c1", value=c1_b, step=0.01, key="cx_c1c")
        T_c   = col_c.number_input("T",  value=T_b,  step=10.0, key="cx_Tc")
        I0_c  = col_c.number_input("I0", value=I0_b, step=10.0, key="cx_I0c")
        b_c   = col_c.number_input("b",  value=b_b,  step=5.0,  key="cx_bc")
        G_c   = col_c.number_input("G",  value=G_b + 50.0, step=10.0, key="cx_Gc",
                                   help="Padrão: +50 em relação à base (choque fiscal)")
        k_c   = col_c.number_input("k",  value=k_b,  step=0.05, key="cx_kc")
        h_c   = col_c.number_input("h",  value=h_b,  step=10.0, key="cx_hc")
        M_c   = col_c.number_input("M",  value=M_b,  step=50.0, key="cx_Mc")

    st.markdown("---")
    st.markdown("**🌐 Parâmetros de Economia Aberta**")
    col_oa1, col_oa2, col_oa3 = st.columns(3)
    with col_oa1:
        tipo_eco_c = st.selectbox("Tipo de Economia", ["Fechada", "Aberta"], key="cx_tipo")
        regime_c   = st.selectbox("Regime Cambial",   ["Flexível", "Fixo"],  key="cx_regime",
                                  disabled=(tipo_eco_c == "Fechada"))
    with col_oa2:
        x0_c  = st.number_input("x0 — Export. autônomas",      value=float(p.get("x0", 50.0)),  step=5.0,  key="cx_x0")
        x1_c  = st.number_input("x1 — Sensib. export. câmbio", value=float(p.get("x1", 30.0)),  step=5.0,  key="cx_x1")
        m0_c  = st.number_input("m0 — Import. autônomas",      value=float(p.get("m0", 20.0)),  step=5.0,  key="cx_m0")
    with col_oa3:
        m1_c    = st.number_input("m1 — Prop. marginal importar", value=float(p.get("m1", 0.10)), step=0.01, key="cx_m1")
        kf_c    = st.number_input("κ — Mobilidade de capital",    value=float(p.get("kf", 80.0)),  step=10.0, key="cx_kf")
        rstar_c = st.number_input("i* — Juros externos",          value=float(p.get("r_star", 0.05)), step=0.01, key="cx_rstar")
        e_c     = st.number_input("e — Taxa de câmbio real",      value=float(p.get("e", 1.0)),    step=0.1,  key="cx_e")
        mostrar_bp_c = st.checkbox("Mostrar curva BP", value=True, key="cx_showbp")

    p_base_num = {
        "c0": c0_b, "c1": c1_b, "T": T_b, "I0": I0_b, "b": b_b,
        "G": G_b, "k": k_b, "h": h_b, "M": M_b, "P": 1.0,
        "x0": x0_c, "x1": x1_c, "m0": m0_c, "m1": m1_c,
        "kf": kf_c, "r_star": rstar_c, "e": e_c,
        "tipo_economia": tipo_eco_c
    }
    p_choque_num = {
        "c0": c0_c, "c1": c1_c, "T": T_c, "I0": I0_c, "b": b_c,
        "G": G_c, "k": k_c, "h": h_c, "M": M_c, "P": 1.0,
        "x0": x0_c, "x1": x1_c, "m0": m0_c, "m1": m1_c,
        "kf": kf_c, "r_star": rstar_c, "e": e_c,
        "tipo_economia": tipo_eco_c
    }

    st.markdown("---")
    fig_num, eq_b, eq_c_num = grafico_numerico(
        p_base_num, p_choque_num, mostrar_bp=mostrar_bp_c
    )
    st.plotly_chart(fig_num, use_container_width=True)

    if eq_b and eq_c_num:
        st.markdown("### 📊 Comparativo de Equilíbrios")
        delta_Y = eq_c_num["Y"] - eq_b["Y"]
        delta_r = eq_c_num["r"] - eq_b["r"]
        delta_I = eq_c_num["I"] - eq_b["I"]
        delta_C = eq_c_num["C"] - eq_b["C"]

        col_t1, col_t2, col_t3, col_t4 = st.columns(4)
        col_t1.metric("ΔY (Renda)",       f"{delta_Y:+.2f}", f"{delta_Y:+.2f}")
        col_t2.metric("Δr (Juros)",        f"{delta_r:+.4f}", f"{delta_r*100:+.2f} p.p.")
        col_t3.metric("ΔI (Investimento)", f"{delta_I:+.2f}", f"{delta_I:+.2f}")
        col_t4.metric("ΔC (Consumo)",      f"{delta_C:+.2f}", f"{delta_C:+.2f}")

        if abs(delta_Y) > 1e-6:
            mult_realizado = delta_Y / max(abs(G_c - G_b), 1e-9) if abs(G_c - G_b) > 1e-6 else None
            mult_teorico   = 1.0 / max(1 - c1_b, 1e-9)
            if mult_realizado is not None:
                crowding = (1 - mult_realizado / mult_teorico) * 100
                st.markdown(f"""
**📐 Análise do Multiplicador:**
- Multiplicador teórico (sem crowding-out): **{mult_teorico:.3f}**
- Multiplicador realizado: **{mult_realizado:.3f}**
- Crowding-out estimado: **{crowding:.1f}%** do estímulo fiscal foi anulado
""")

        if tipo_eco_c == "Aberta" and kf_c > 1e-6:
            r_bp_eq = rstar_c + (m1_c / kf_c) * eq_c_num["Y"] - (x0_c + x1_c * e_c - m0_c) / kf_c
            diff_bp = eq_c_num["r"] - r_bp_eq
            if abs(diff_bp) < 0.001:
                st.success("✅ Equilíbrio final **sobre a BP** — balanço de pagamentos equilibrado.")
            elif diff_bp > 0:
                st.warning(f"⬆️ Equilíbrio **acima da BP** (Δ = {diff_bp:.4f}) — superávit no balanço de capitais.")
            else:
                st.error(f"⬇️ Equilíbrio **abaixo da BP** (Δ = {diff_bp:.4f}) — déficit no balanço de pagamentos.")