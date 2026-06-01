# ui/islmbp/grafico.py
"""
Funções de construção de gráficos para o modo didático IS-LM-BP.
Geometria normalizada (estilo livro-texto) com espaçamento visual corrigido.
"""

import numpy as np
import plotly.graph_objects as go

# ══════════════════════════════════════════════════════════════
# PALETA DE CORES
# ══════════════════════════════════════════════════════════════
COR = dict(
    IS      = "#2563eb",   # azul escuro
    IS1     = "#3b82f6",   # azul médio
    IS2     = "#7c3aed",   # roxo
    LM      = "#dc2626",   # vermelho escuro
    LM1     = "#f87171",   # vermelho claro
    BP_NULA = "#065f46",   # verde escuro
    BP_BAIXA= "#059669",   # verde médio
    BP_ALTA = "#10b981",   # verde claro
    BP_PERF = "#34d399",   # verde muito claro
    A       = "#2563eb",
    B       = "#d97706",
    C       = "#059669",
)

# ══════════════════════════════════════════════════════════════
# PARÂMETROS GEOMÉTRICOS
# Espaçamento ampliado para máxima legibilidade
# IS: r = IS_a - IS_b·Y  (negativa)
# LM: r = LM_a + LM_b·Y  (positiva)
# Equilíbrio A em Y≈1.30, r≈0.98
# ══════════════════════════════════════════════════════════════
IS_a, IS_b = 2.8, 1.4
LM_a, LM_b = 0.2, 0.6
SHIFT = 0.70   # deslocamento maior para separação visual clara

# Slopes da BP por mobilidade (recalibrados para LM_b=0.6)
SLOPE_BP = {
    "Nula":     None,   # vertical
    "Baixa":    1.3,    # mais íngreme que LM
    "Alta":     0.22,   # mais suave que LM
    "Perfeita": 0.0,    # horizontal
}

COR_BP = {
    "Nula":     COR["BP_NULA"],
    "Baixa":    COR["BP_BAIXA"],
    "Alta":     COR["BP_ALTA"],
    "Perfeita": COR["BP_PERF"],
}

Y_RANGE = np.linspace(0.05, 2.6, 500)


# ══════════════════════════════════════════════════════════════
# GEOMETRIA
# ══════════════════════════════════════════════════════════════

def equilibrio(IS_a_, LM_a_):
    YE = (IS_a_ - LM_a_) / (IS_b + LM_b)
    rE = IS_a_ - IS_b * YE
    return YE, rE


def geometria(politica, direcao, aberta, flex):
    fiscal   = (politica == "Fiscal")
    expansao = (direcao  == "Expansionista")

    YA, rA = equilibrio(IS_a, LM_a)

    if fiscal:
        IS_a1 = IS_a + (SHIFT if expansao else -SHIFT)
        LM_a1 = LM_a
    else:
        IS_a1 = IS_a
        LM_a1 = LM_a + (-SHIFT if expansao else SHIFT)

    YC, rC = equilibrio(IS_a1, LM_a1)

    # Ponto B: interseção da nova curva com a curva original
    if fiscal:
        YB, rB = YC, rA          # B está na LM₀ ao nível Y de C
    else:
        YB, rB = YA, rC          # B está na IS₀ ao nível r de C

    # Ajuste cambial em economia aberta flexível
    IS_a2  = None
    YC_fin = YC
    rC_fin = rC

    if aberta and flex:
        if fiscal and expansao:
            # Apreciação cambial → IS recua parcialmente
            IS_a2 = IS_a + SHIFT * 0.15
            YC_fin, rC_fin = equilibrio(IS_a2, LM_a1)
        elif not fiscal and expansao:
            # Depreciação cambial → IS avança
            IS_a2 = IS_a + SHIFT * 0.80
            YC_fin, rC_fin = equilibrio(IS_a2, LM_a1)

    return dict(
        YA=YA, rA=rA,
        YB=YB, rB=rB,
        YC=YC, rC=rC,
        YC_fin=YC_fin, rC_fin=rC_fin,
        IS_a0=IS_a,  IS_a1=IS_a1, IS_a2=IS_a2,
        LM_a0=LM_a,  LM_a1=LM_a1,
        fiscal=fiscal, expansao=expansao,
    )


# ══════════════════════════════════════════════════════════════
# CONSTRUTORES DE ELEMENTOS GRÁFICOS
# ══════════════════════════════════════════════════════════════

def fig_base(titulo: str) -> go.Figure:
    fig = go.Figure()
    fig.update_layout(
        title=dict(
            text=titulo,
            font=dict(size=16, family="'Poppins', sans-serif"),
            x=0.5, xanchor="center", y=0.97,
        ),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=620,
        margin=dict(l=80, r=120, t=70, b=70),
        hovermode="closest",
        dragmode=False,
        legend=dict(
            x=0.01, y=0.99,
            bgcolor="rgba(128,128,128,0.10)",
            bordercolor="rgba(128,128,128,0.25)",
            borderwidth=1,
            font=dict(size=12),
        ),
        xaxis=dict(
            title=dict(text="Produto  Y", font=dict(size=14)),
            showgrid=True, gridcolor="rgba(128,128,128,0.15)", gridwidth=1,
            zeroline=False, showline=True,
            linecolor="rgba(128,128,128,0.4)", linewidth=1.5,
            tickfont=dict(size=13), fixedrange=True,
        ),
        yaxis=dict(
            title=dict(text="Taxa de Juros  i", font=dict(size=14)),
            showgrid=True, gridcolor="rgba(128,128,128,0.15)", gridwidth=1,
            zeroline=False, showline=True,
            linecolor="rgba(128,128,128,0.4)", linewidth=1.5,
            tickfont=dict(size=13), fixedrange=True,
        ),
    )
    return fig


def add_curva(fig, Y, r, name, color, width=3.5, dash="solid", label=None, label_side="right"):
    fig.add_trace(go.Scatter(
        x=Y, y=r, mode="lines", name=name,
        line=dict(color=color, width=width, dash=dash),
        showlegend=True,
        hovertemplate=f"<b>{name}</b><br>Y=%{{x:.3f}}<br>i=%{{y:.3f}}<extra></extra>",
    ))
    if label:
        lx = float(Y[-1]) if label_side == "right"else float(Y[0])
        ly = float(r[-1]) if label_side == "right"else float(r[0])
        xanchor = "left"if label_side == "right"else "right"
        xshift  = 10 if label_side == "right"else -10
        fig.add_annotation(
            x=lx, y=ly, text=f"<b>{label}</b>",
            showarrow=False, xanchor=xanchor, yanchor="middle",
            font=dict(color=color, size=14, family="Georgia, serif"),
            xshift=xshift,
        )


def add_ponto(fig, x, y, label, color, tpos="top left"):
    fig.add_trace(go.Scatter(
        x=[x], y=[y], mode="markers+text",
        marker=dict(size=16, color=color, symbol="circle",
                    line=dict(width=3, color="white")),
        text=[f"<b>{label}</b>"],
        textposition=tpos,
        textfont=dict(size=15, color=color, family="Georgia, serif"),
        showlegend=False,
        hovertemplate=f"<b>{label}</b><br>Y={x:.3f}<br>i={y:.3f}<extra></extra>",
    ))


def add_seta(fig, x0, y0, x1, y1, color, width=2.8):
    fig.add_annotation(
        ax=x0, ay=y0, x=x1, y=y1,
        xref="x", yref="y", axref="x", ayref="y",
        showarrow=True, arrowhead=4,
        arrowwidth=width, arrowcolor=color, arrowsize=1.1,
    )


def add_projecoes(fig, x, y, x_left, y_floor, color):
    """Linhas tracejadas do ponto até os eixos."""
    fig.add_shape(type="line", x0=x, y0=y_floor, x1=x, y1=y,
                  line=dict(color=color, width=1.2, dash="dot"))
    fig.add_shape(type="line", x0=x_left, y0=y, x1=x, y1=y,
                  line=dict(color=color, width=1.2, dash="dot"))


def add_seta_deslocamento(fig, Y, r_base, r_novo, expansao, color, eh_IS=True):
    """Seta de deslocamento da curva no ponto médio."""
    idx = len(Y) // 2
    if eh_IS:
        dx = SHIFT * 0.50 if expansao else -SHIFT * 0.50
        fig.add_annotation(
            ax=Y[idx], ay=r_base[idx],
            x=Y[idx] + dx, y=r_base[idx],
            xref="x", yref="y", axref="x", ayref="y",
            showarrow=True, arrowhead=3, arrowwidth=2.5,
            arrowcolor=color, arrowsize=1.2,
        )
    else:
        dy = -SHIFT * 0.50 if expansao else SHIFT * 0.50
        fig.add_annotation(
            ax=Y[idx], ay=r_base[idx],
            x=Y[idx], y=r_base[idx] + dy,
            xref="x", yref="y", axref="x", ayref="y",
            showarrow=True, arrowhead=3, arrowwidth=2.5,
            arrowcolor=color, arrowsize=1.2,
        )


def set_eixos(fig, geo, etapa):
    """Define ranges e tick labels dos eixos."""
    YA, rA     = geo["YA"], geo["rA"]
    YC_fin     = geo["YC_fin"]
    rC_fin     = geo["rC_fin"]
    x_left     = float(Y_RANGE.min())
    y_floor    = LM_a + LM_b * x_left - 0.18

    # Tick labels qualitativos
    if etapa == 0:
        xv, xt = [YA], ["Y<sub>A</sub>"]
        yv, yt = [rA], ["i<sub>A</sub>"]
    elif etapa == 1:
        xv = [YA, geo["YB"]]; xt = ["Y<sub>A</sub>", "Y<sub>B</sub>"]
        yv = [rA, geo["rB"]]; yt = ["i<sub>A</sub>", "i<sub>B</sub>"]
    else:
        xv = [YA, YC_fin]; xt = ["Y<sub>A</sub>", "Y<sub>C</sub>"]
        yv = [rA, rC_fin]; yt = ["i<sub>A</sub>", "i<sub>C</sub>"]
        if abs(YA - YC_fin) < 0.03:
            xv, xt = [YA], ["Y<sub>A</sub>=Y<sub>C</sub>"]
        if abs(rA - rC_fin) < 0.03:
            yv, yt = [rA], ["i<sub>A</sub>=i<sub>C</sub>"]

    IS_a_max = max(geo["IS_a0"], geo["IS_a1"])
    if geo["IS_a2"] is not None:
        IS_a_max = max(IS_a_max, geo["IS_a2"])
    r_top = IS_a_max - IS_b * x_left + 0.35

    fig.update_layout(
        xaxis=dict(tickvals=xv, ticktext=xt,
                   range=[x_left - 0.05, float(Y_RANGE.max()) + 0.25]),
        yaxis=dict(tickvals=yv, ticktext=yt,
                   range=[y_floor - 0.05, r_top]),
    )
    return x_left, y_floor


# ══════════════════════════════════════════════════════════════
# GRÁFICO PRINCIPAL POR ETAPA
# ══════════════════════════════════════════════════════════════

def grafico_etapa(politica, direcao, tipo_eco, regime, mobilidade_label, etapa):
    """
    Constrói o gráfico IS-LM-BP para uma etapa específica (0=A, 1=B, 2=C).
    Mobilidade_label: "Nula" | "Baixa" | "Alta" | "Perfeita"
    """
    fiscal   = (politica == "Fiscal")
    expansao = (direcao  == "Expansionista")
    aberta   = (tipo_eco == "Aberta")
    flex     = (regime   == "Flexível")

    geo = geometria(politica, direcao, aberta, flex)
    Y   = Y_RANGE

    # Curvas IS e LM
    r_IS0 = geo["IS_a0"] - IS_b * Y
    r_IS1 = geo["IS_a1"] - IS_b * Y
    r_LM0 = geo["LM_a0"] + LM_b * Y
    r_LM1 = geo["LM_a1"] + LM_b * Y
    r_IS2 = (geo["IS_a2"] - IS_b * Y) if geo["IS_a2"] is not None else None

    # Curva(s) BP
    bp_slope = SLOPE_BP.get(mobilidade_label, 0.22)
    bp_cor   = COR_BP.get(mobilidade_label, COR["BP_ALTA"])

    etapa_labels = [
        "A — Equilíbrio Inicial",
        "B — Choque de Curto Prazo",
        "C — Novo Equilíbrio",
    ]
    titulo = (
        f"IS-LM{'·BP 'if aberta else ' '}— {politica} {direcao}"
        f"  │  Etapa {etapa_labels[etapa]}"
    )
    fig = fig_base(titulo)

    # ── ETAPA A: IS₀, LM₀, BP inicial, Ponto A ───────────────
    if etapa >= 0:
        add_curva(fig, Y, r_IS0, "IS₀", COR["IS"], label="IS₀")
        add_curva(fig, Y, r_LM0, "LM₀", COR["LM"], label="LM₀")

        if aberta:
            _add_bp(fig, Y, geo, mobilidade_label, bp_slope, bp_cor, sufixo="₀")

    # ── ETAPA B: curva deslocada + seta + ponto B ─────────────
    if etapa >= 1:
        if fiscal:
            add_curva(fig, Y, r_IS1, "IS₁ (após choque)", COR["IS1"],
                      dash="dash", label="IS₁")
            add_seta_deslocamento(fig, Y, r_IS0, r_IS1, expansao, COR["IS1"], eh_IS=True)
        else:
            add_curva(fig, Y, r_LM1, "LM₁ (após choque)", COR["LM1"],
                      dash="dash", label="LM₁")
            add_seta_deslocamento(fig, Y, r_LM0, r_LM1, expansao, COR["LM1"], eh_IS=False)

        add_ponto(fig, geo["YA"], geo["rA"], "A", COR["A"], "top left")
        add_ponto(fig, geo["YB"], geo["rB"], "B", COR["B"], "top right")
        add_seta(fig, geo["YA"], geo["rA"], geo["YB"], geo["rB"], COR["B"])

    # ── ETAPA C: IS₂ cambial + Ponto C + trajetória ──────────
    if etapa >= 2:
        if r_IS2 is not None:
            add_curva(fig, Y, r_IS2, "IS₂ (ajuste cambial)", COR["IS2"],
                      width=2.8, dash="longdash", label="IS₂")

        add_ponto(fig, geo["YA"],     geo["rA"],     "A", COR["A"], "top left")
        add_ponto(fig, geo["YB"],     geo["rB"],     "B", COR["B"], "top right")
        add_ponto(fig, geo["YC_fin"], geo["rC_fin"], "C", COR["C"], "bottom right")
        add_seta(fig, geo["YA"],  geo["rA"],    geo["YB"],     geo["rB"],     COR["B"])
        add_seta(fig, geo["YB"],  geo["rB"],    geo["YC_fin"], geo["rC_fin"], COR["C"])

    # ── Projeções e eixos ─────────────────────────────────────
    x_left, y_floor = set_eixos(fig, geo, etapa)

    if etapa == 0:
        add_projecoes(fig, geo["YA"], geo["rA"], x_left, y_floor, COR["A"])
        add_ponto(fig, geo["YA"], geo["rA"], "A", COR["A"], "top left")
    elif etapa == 1:
        add_projecoes(fig, geo["YA"], geo["rA"], x_left, y_floor, COR["A"])
        add_projecoes(fig, geo["YB"], geo["rB"], x_left, y_floor, COR["B"])
    else:
        add_projecoes(fig, geo["YA"],     geo["rA"],     x_left, y_floor, COR["A"])
        add_projecoes(fig, geo["YC_fin"], geo["rC_fin"], x_left, y_floor, COR["C"])

    return fig


def _add_bp(fig, Y, geo, mobilidade_label, bp_slope, bp_cor, sufixo="₀"):
    """Adiciona curva BP ao gráfico conforme mobilidade."""
    YA, rA = geo["YA"], geo["rA"]
    label  = f"BP{sufixo} ({mobilidade_label.lower()})"

    if mobilidade_label == "Nula":
        # Vertical em YA
        r_min = LM_a + LM_b * float(Y.min()) - 0.1
        r_max = IS_a - IS_b * float(Y.min()) + 0.15
        fig.add_shape(
            type="line", x0=YA, y0=r_min, x1=YA, y1=r_max,
            line=dict(color=bp_cor, width=3, dash="dash"),
        )
        fig.add_annotation(
            x=YA, y=r_max + 0.06,
            text=f"<b>BP{sufixo}</b><br><span style='font-size:10px'>(imobilidade)</span>",
            showarrow=False, xanchor="center",
            font=dict(color=bp_cor, size=13),
        )
        # Trace fantasma para a legenda
        fig.add_trace(go.Scatter(
            x=[None], y=[None], mode="lines",
            name=label, line=dict(color=bp_cor, width=3, dash="dash"),
            showlegend=True,
        ))

    elif mobilidade_label == "Perfeita":
        r_BP = np.full_like(Y, rA)
        add_curva(fig, Y, r_BP, label, bp_cor, width=3, dash="dot",
                  label=f"BP{sufixo}<br><span style='font-size:10px'>(perfeita)</span>")

    else:
        r_BP = rA + bp_slope * (Y - YA)
        add_curva(fig, Y, r_BP, label, bp_cor, width=3, dash="dash",
                  label=f"BP{sufixo}<br><span style='font-size:10px'>({mobilidade_label.lower()})</span>")


# ══════════════════════════════════════════════════════════════
# GRÁFICO COMPARATIVO DE MOBILIDADES (todas as BPs ao mesmo tempo)
# ══════════════════════════════════════════════════════════════

def grafico_multiplas_bp(politica, direcao, tipo_eco, regime):
    """
    Mostra IS₀, LM₀ e as 4 curvas BP simultaneamente
    para comparação visual das mobilidades.
    """
    geo = geometria(politica, direcao, True, regime == "Flexível")
    Y   = Y_RANGE
    r_IS0 = geo["IS_a0"] - IS_b * Y
    r_LM0 = geo["LM_a0"] + LM_b * Y

    fig = fig_base("Comparação das Curvas BP — Todos os Graus de Mobilidade")
    add_curva(fig, Y, r_IS0, "IS₀", COR["IS"], label="IS₀")
    add_curva(fig, Y, r_LM0, "LM₀", COR["LM"], label="LM₀")

    for mob in ["Nula", "Baixa", "Alta", "Perfeita"]:
        slope = SLOPE_BP[mob]
        cor   = COR_BP[mob]
        _add_bp(fig, Y, geo, mob, slope, cor)

    add_ponto(fig, geo["YA"], geo["rA"], "A", COR["A"], "top left")
    set_eixos(fig, geo, 0)

    # Anotações explicativas
    fig.add_annotation(
        x=geo["YA"] * 1.35, y=geo["rA"] * 1.45,
        text="<b>Graus de mobilidade de capital:</b><br>"
             "Nula → BP vertical<br>"
             "Baixa → BP íngreme (acima da LM)<br>"
             "Alta → BP suave (abaixo da LM)<br>"
             "Perfeita → BP horizontal",
        showarrow=False,
        align="left",
        font=dict(size=11),
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor="rgba(128,128,128,0.3)",
        borderwidth=1,
        borderpad=8,
    )
    return fig