# pages/4_🌍_Economia_Aberta.py
"""
IS-LM-BP — Economia Aberta (Mundell-Fleming)
Modo Simplificado (didático, estilo FGV/MIT) + Modo Complexo (numérico)
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go

try:
    from scipy.optimize import fsolve
    SCIPY_OK = True
except ImportError:
    SCIPY_OK = False

from core.parameters import DEFAULT_PARAMS

# ══════════════════════════════════════════════════════════════
# CONFIGURAÇÃO DA PÁGINA
# ══════════════════════════════════════════════════════════════
st.set_page_config(layout="wide", page_title="IS-LM-BP | Simulador Macroeconômico")

if "params" not in st.session_state:
    st.session_state.params = DEFAULT_PARAMS.copy()

if "settings" not in st.session_state:
    st.session_state.settings = {
        "nivel": "Médio",
        "mobilidade_capital": "Alta",
    }

# ══════════════════════════════════════════════════════════════
# NÚCLEO ECONÔMICO
# ══════════════════════════════════════════════════════════════

def consumo(c0, c1, Y, T):       return c0 + c1 * (Y - T)
def investimento(I0, b, r):      return I0 - b * r
def exportacoes(x0, x1, Y_s, e): return x0 + x1 * Y_s * e
def importacoes(m0, m1, Y, e):   return m0 + m1 * Y / max(e, 1e-9)
def NX(x0,x1,Y_s,m0,m1,Y,e):    return exportacoes(x0,x1,Y_s,e) - importacoes(m0,m1,Y,e)
def fluxo_capital(kf, r, r_s):   return kf * (r - r_s)

def eq_IS(Y, r, e, p):
    C  = consumo(p["c0"], p["c1"], Y, p["T"])
    I  = investimento(p["I0"], p["b"], r)
    nx = NX(p["x0"],p["x1"],p["Y_star"],p["m0"],p["m1"],Y,e) if p.get("aberta") else 0.0
    return Y - C - I - p["G"] - nx

def eq_LM(Y, r, M, p):
    return M / p["P"] - p["k"] * Y + p["h"] * r

def eq_BP(Y, r, e, p):
    nx = NX(p["x0"],p["x1"],p["Y_star"],p["m0"],p["m1"],Y,e)
    cf = fluxo_capital(p["kf"], r, p["r_star"])
    return nx + cf

def newton_solve(F, x0, tol=1e-10, max_iter=500):
    x = np.array(x0, dtype=float)
    for _ in range(max_iter):
        fx = np.array(F(x), dtype=float)
        if np.max(np.abs(fx)) < tol:
            return x, True
        n = len(x); J = np.zeros((n, n)); dx = 1e-6
        for j in range(n):
            xp = x.copy(); xp[j] += dx
            J[:, j] = (np.array(F(xp)) - fx) / dx
        try:    delta = np.linalg.solve(J, -fx)
        except: return x, False
        x = x + delta
    return x, False

def solve_flex(p):
    def F(v):
        Y, r, e = v
        return [eq_IS(Y,r,e,p), eq_LM(Y,r,p["M"],p), eq_BP(Y,r,e,p)]
    sol, ok = newton_solve(F, [p.get("Yn",1200.), p["r_star"], p.get("e",1.)])
    if not ok and SCIPY_OK: sol = fsolve(F, sol)
    return _result(*sol, p, "flex")

def solve_fixo(p):
    e = p.get("e_fixed", 1.0)
    def F(v):
        Y, r, M_eq = v
        return [eq_IS(Y,r,e,p), eq_LM(Y,r,M_eq,p), eq_BP(Y,r,e,p)]
    sol, ok = newton_solve(F, [p.get("Yn",1200.), p["r_star"], p["M"]])
    if not ok and SCIPY_OK: sol = fsolve(F, sol)
    Y, r, M_eq = sol
    return _result(Y, r, e, p, "fixo", M_eq=M_eq)

def solve_fechada(p):
    A = np.array([[1-p["c1"], p["b"]], [p["k"], -p["h"]]])
    B = np.array([p["c0"]-p["c1"]*p["T"]+p["I0"]+p["G"], p["M"]/p["P"]])
    try:    Y, r = np.linalg.solve(A, B)
    except: Y, r = p.get("Yn",1200.), p["r_star"]
    return _result(Y, r, p.get("e",1.), p, "fechada")

def _result(Y, r, e, p, regime, M_eq=None):
    C  = consumo(p["c0"],p["c1"],Y,p["T"])
    I  = investimento(p["I0"],p["b"],r)
    nx = NX(p["x0"],p["x1"],p["Y_star"],p["m0"],p["m1"],Y,e) if p.get("aberta") else 0.
    cf = fluxo_capital(p["kf"],r,p["r_star"]) if p.get("aberta") else 0.
    Mu = M_eq if M_eq is not None else p["M"]
    return dict(Y=Y,r=r,e=e,C=C,I=I,NX=nx,CF=cf,BP=nx+cf,M_eq=Mu,regime=regime,
                IS_res=Y-C-I-p["G"]-nx,
                LM_res=Mu/p["P"]-p["k"]*Y+p["h"]*r,
                BP_res=nx+cf if p.get("aberta") else 0.)

def curva_IS(Y_grid, e, p, aberta=True):
    r_vals = []
    for Y in Y_grid:
        nx = NX(p["x0"],p["x1"],p["Y_star"],p["m0"],p["m1"],Y,e) if aberta else 0.
        A  = p["c0"]-p["c1"]*p["T"]+p["I0"]+p["G"]+nx
        r_vals.append((A-(1-p["c1"])*Y)/max(p["b"],1e-9))
    return np.array(r_vals)

def curva_LM(Y_grid, M, p):
    return (p["k"]*Y_grid - M/p["P"]) / max(p["h"],1e-9)

def curva_BP_plot(Y_grid, e, p, Y_anchor=None, r_anchor=None):
    kf = p.get("kf",80.); r_star = p.get("r_star",0.05)
    if kf >= 1e6: return np.full_like(Y_grid, r_star, dtype=float)
    if Y_anchor is None: Y_anchor = float(np.mean(Y_grid))
    if r_anchor is None: r_anchor = r_star
    slope = 1 / (max(kf,1e-6)**0.6)
    return r_anchor + slope*(Y_grid - Y_anchor)

# ══════════════════════════════════════════════════════════════
# PALETA DE CORES ACADÊMICA
# ══════════════════════════════════════════════════════════════
C = dict(
    IS   = "#2563eb",
    IS1  = "#60a5fa",
    IS2  = "#7c3aed",
    LM   = "#dc2626",
    LM1  = "#f87171",
    BP   = "#059669",
    A    = "#2563eb",
    B    = "#d97706",
    C    = "#059669",
    grid = "#f1f5f9",
    axis = "#94a3b8",
    dot  = "#94a3b8",
)

# ══════════════════════════════════════════════════════════════
# GEOMETRIA DAS CURVAS (normalizada, estilo livro-texto)
# ══════════════════════════════════════════════════════════════
IS_a, IS_b = 2.2, 1.6
LM_a, LM_b = -1.2, 0.35  # LM: r = LM_a + LM_b·Y
SHIFT       = 0.55

# ── SLOPE_MAP: kappa → inclinação da BP ──────────────────────
# Valores maiores = mais vertical (imobilidade)
# Valores menores = mais horizontal (alta mobilidade)
# Nula (0.0)  → muito íngreme (quase vertical)
# Baixa (0.2) → íngreme
# Alta (0.5)  → suave
# Perfeita    → horizontal (tratada separadamente)
SLOPE_MAP = {
    0.0: 2.5,   # Nula  → quase vertical
    0.2: 1.2,   # Baixa → íngreme
    0.5: 0.15,  # Alta  → quase horizontal
}

def _equilibrio(IS_a_, LM_a_):
    YE = (IS_a_ - LM_a_) / (IS_b + LM_b)
    rE = IS_a_ - IS_b * YE
    return YE, rE

def _geometria(politica, direcao, aberta, flex):
    fiscal   = politica == "Fiscal"
    expansao = direcao  == "Expansionista"

    YA, rA = _equilibrio(IS_a, LM_a)

    if fiscal:
        IS_a1 = IS_a + (SHIFT if expansao else -SHIFT)
        LM_a1 = LM_a
    else:
        IS_a1 = IS_a
        LM_a1 = LM_a + (-SHIFT if expansao else SHIFT)

    YC, rC = _equilibrio(IS_a1, LM_a1)

    if fiscal:
        YB, rB = YC, rA
    else:
        YB, rB = YA, rC

    IS_a2   = None
    YC_fin  = YC
    rC_fin  = rC

    if aberta and flex:
        if fiscal and expansao:
            IS_a2  = IS_a + SHIFT * 0.12
            YC_fin, rC_fin = _equilibrio(IS_a2, LM_a1)
        elif not fiscal and expansao:
            IS_a2  = IS_a + SHIFT * 0.75
            YC_fin, rC_fin = _equilibrio(IS_a2, LM_a1)

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
# CONSTRUTOR DO GRÁFICO POR ETAPA
# ══════════════════════════════════════════════════════════════

def _base_fig(titulo):
    fig = go.Figure()
    fig.update_layout(
        title=dict(text=titulo, font=dict(size=15, color=None, family="'Poppins', sans-serif"),
                   x=0.5, xanchor="center", y=0.97),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        height=600,
        margin=dict(l=70, r=100, t=65, b=65),
        hovermode="closest",
        dragmode=False,
        legend=dict(x=0.01, y=0.99, bgcolor="rgba(128,128,128,0.12)",
                    bordercolor="rgba(128,128,128,0.3)", borderwidth=1,
                    font=dict(size=11, family="'EB Garamond', Georgia, serif")),
        xaxis=dict(
            title=dict(text="Produto  Y", font=dict(size=13)),
            showgrid=True, gridcolor="rgba(128,128,128,0.2)", gridwidth=1,
            zeroline=False, showline=True, linecolor="rgba(128,128,128,0.5)", linewidth=1.5,
            tickfont=dict(size=12), fixedrange=True,
        ),
        yaxis=dict(
            title=dict(text="Taxa de Juros  i", font=dict(size=13)),
            showgrid=True, gridcolor="rgba(128,128,128,0.2)", gridwidth=1,
            zeroline=False, showline=True, linecolor="rgba(128,128,128,0.5)", linewidth=1.5,
            tickfont=dict(size=12), fixedrange=True,
        ),
    )
    return fig

def _add_curve(fig, Y, r, name, color, width=3.2, dash="solid", label=None, label_side="right"):
    fig.add_trace(go.Scatter(
        x=Y, y=r, mode="lines", name=name,
        line=dict(color=color, width=width, dash=dash),
        showlegend=True,
        hovertemplate=f"<b>{name}</b><br>Y=%{{x:.3f}}<br>i=%{{y:.3f}}<extra></extra>"
    ))
    if label:
        if label_side == "right":
            lx, ly = float(Y[-1]), float(r[-1])
            xanchor = "left"; xshift = 8
        else:
            lx, ly = float(Y[0]), float(r[0])
            xanchor = "right"; xshift = -8
        fig.add_annotation(x=lx, y=ly, text=f"<b>{label}</b>",
                           showarrow=False, xanchor=xanchor, yanchor="middle",
                           font=dict(color=color, size=13, family="Georgia, serif"),
                           xshift=xshift)

def _add_point(fig, x, y, label, color, tpos="top left"):
    fig.add_trace(go.Scatter(
        x=[x], y=[y], mode="markers+text",
        marker=dict(size=14, color=color, symbol="circle",
                    line=dict(width=2.5, color="white")),
        text=[f"<b>{label}</b>"],
        textposition=tpos,
        textfont=dict(size=14, color=color, family="Georgia, serif"),
        showlegend=False,
        hovertemplate=f"<b>Ponto {label}</b><br>Y={x:.3f}<br>i={y:.3f}<extra></extra>"
    ))

def _add_projections(fig, x, y, x_left, y_floor, color):
    fig.add_shape(type="line", x0=x, y0=y_floor, x1=x, y1=y,
                  line=dict(color=color, width=1.1, dash="dot"))
    fig.add_shape(type="line", x0=x_left, y0=y, x1=x, y1=y,
                  line=dict(color=color, width=1.1, dash="dot"))

def _add_trajectory_arrow(fig, x0, y0, x1, y1, color):
    fig.add_annotation(
        ax=x0, ay=y0, x=x1, y=y1,
        xref="x", yref="y", axref="x", ayref="y",
        showarrow=True, arrowhead=4, arrowwidth=2.5,
        arrowcolor=color, arrowsize=1.0
    )

def _set_axes(fig, Y, geo, etapa, aberta):
    YA, rA = geo["YA"], geo["rA"]
    YC_fin, rC_fin = geo["YC_fin"], geo["rC_fin"]

    x_left = float(Y.min())
    y_floor = LM_a + LM_b * float(Y.min()) - 0.25

    if etapa == 0:
        xv = [YA]; xt = ["Y<sub>A</sub>"]
        yv = [rA]; yt = ["i<sub>A</sub>"]
    elif etapa == 1:
        xv = [YA, geo["YB"]]; xt = ["Y<sub>A</sub>", "Y<sub>B</sub>"]
        yv = [rA, geo["rB"]]; yt = ["i<sub>A</sub>", "i<sub>B</sub>"]
    else:
        xv = [YA, YC_fin]; xt = ["Y<sub>A</sub>", "Y<sub>C</sub>"]
        yv = [rA, rC_fin]; yt = ["i<sub>A</sub>", "i<sub>C</sub>"]
        if abs(YA - YC_fin) < 0.02:
            xv = [YA]; xt = ["Y<sub>A</sub>=Y<sub>C</sub>"]
        if abs(rA - rC_fin) < 0.02:
            yv = [rA]; yt = ["i<sub>A</sub>=i<sub>C</sub>"]

    IS_a_max = max(geo["IS_a0"], geo["IS_a1"])
    if geo["IS_a2"] is not None:
        IS_a_max = max(IS_a_max, geo["IS_a2"])
    r_top = IS_a_max - IS_b * float(Y.min()) + 0.3

    fig.update_layout(
        xaxis=dict(
            tickvals=xv, ticktext=xt,
            range=[x_left - 0.05, float(Y.max()) + 0.22],
        ),
        yaxis=dict(
            tickvals=yv, ticktext=yt,
            range=[y_floor - 0.05, r_top],
        ),
    )
    return x_left, y_floor

# ══════════════════════════════════════════════════════════════
# GRÁFICO POR ETAPA
# ══════════════════════════════════════════════════════════════

def grafico_etapa(politica, direcao, tipo_eco, regime, mobilidade_kappa, etapa):
    """
    etapa: 0 = Estado A, 1 = Estado B, 2 = Estado C
    """
    fiscal   = politica == "Fiscal"
    expansao = direcao  == "Expansionista"
    aberta   = tipo_eco == "Aberta"
    flex     = regime   == "Flexível"

    geo = _geometria(politica, direcao, aberta, flex)
    Y   = np.linspace(0.1, 2.4, 400)

    # Curvas IS e LM
    r_IS0 = geo["IS_a0"] - IS_b * Y
    r_IS1 = geo["IS_a1"] - IS_b * Y
    r_LM0 = geo["LM_a0"] + LM_b * Y
    r_LM1 = geo["LM_a1"] + LM_b * Y
    r_IS2 = (geo["IS_a2"] - IS_b * Y) if geo["IS_a2"] is not None else None

    # ── BP: lógica corrigida ──────────────────────────────────
    # Perfeita (kappa ≥ 0.98) → horizontal no nível rA
    # Nula (kappa ≤ 0.02)     → vertical em YA (shape separado)
    # Baixa (0.2) / Alta (0.5) → slope do SLOPE_MAP
    if aberta:
        kappa_key = round(mobilidade_kappa, 1)
        if mobilidade_kappa >= 0.98:
            # Perfeita: linha horizontal
            r_BP   = np.full_like(Y, geo["rA"])
            bp_tipo = "perfeita"
        elif mobilidade_kappa <= 0.02:
            # Nula: linha vertical (plotada como shape, não como trace)
            r_BP   = None
            bp_tipo = "nula"
        else:
            # Baixa ou Alta: usa SLOPE_MAP
            slope  = SLOPE_MAP.get(kappa_key, 0.3)
            r_BP   = geo["rA"] + slope * (Y - geo["YA"])
            bp_tipo = {0.2: "baixa", 0.5: "alta"}.get(kappa_key, f"κ={mobilidade_kappa:.1f}")
    else:
        r_BP   = None
        bp_tipo = None

    etapa_labels = ["A — Equilíbrio Inicial", "B — Choque de Curto Prazo", "C — Novo Equilíbrio"]
    titulo = f"IS-LM{'+ BP ' if aberta else ' '}— {politica} {direcao}  │  Etapa {etapa_labels[etapa]}"
    fig = _base_fig(titulo)

    # ── ETAPA 0: IS₀, LM₀, BP, ponto A ──────────────────────
    if etapa >= 0:
        _add_curve(fig, Y, r_IS0, "IS₀", C["IS"], label="IS₀")
        _add_curve(fig, Y, r_LM0, "LM₀", C["LM"], label="LM₀")

        if aberta:
            if bp_tipo == "nula":
                # Linha vertical em YA
                y_min_bp = float(r_IS0.min()) - 0.1
                y_max_bp = float(r_IS0.max()) + 0.1
                fig.add_shape(type="line",
                    x0=geo["YA"], y0=y_min_bp, x1=geo["YA"], y1=y_max_bp,
                    line=dict(color=C["BP"], width=2.8, dash="dash"))
                fig.add_annotation(x=geo["YA"], y=y_max_bp + 0.05,
                    text="<b>BP</b><br><span style='font-size:10px'>(imobilidade)</span>",
                    showarrow=False, xanchor="center",
                    font=dict(color=C["BP"], size=12, family="Georgia, serif"))
            elif r_BP is not None:
                bp_lbl = f"BP ({bp_tipo})"
                _add_curve(fig, Y, r_BP, bp_lbl, C["BP"], width=2.8, dash="dash",
                           label=f"BP<br><span style='font-size:10px'>({bp_tipo})</span>")

    # ── ETAPA 1: curva deslocada + seta + ponto B ─────────────
    if etapa >= 1:
        if fiscal:
            _add_curve(fig, Y, r_IS1, "IS₁ (após choque)", C["IS1"], dash="dash", label="IS₁")
            idx = len(Y) // 2
            dx = SHIFT * 0.45 if expansao else -SHIFT * 0.45
            fig.add_annotation(
                ax=Y[idx], ay=r_IS0[idx],
                x=Y[idx] + dx, y=r_IS0[idx],
                xref="x", yref="y", axref="x", ayref="y",
                showarrow=True, arrowhead=2, arrowwidth=2.2,
                arrowcolor=C["IS1"], arrowsize=1.1
            )
        else:
            _add_curve(fig, Y, r_LM1, "LM₁ (após choque)", C["LM1"], dash="dash", label="LM₁")
            idx = len(Y) // 2
            dy = -SHIFT * 0.45 if expansao else SHIFT * 0.45
            fig.add_annotation(
                ax=Y[idx], ay=r_LM0[idx],
                x=Y[idx], y=r_LM0[idx] + dy,
                xref="x", yref="y", axref="x", ayref="y",
                showarrow=True, arrowhead=2, arrowwidth=2.2,
                arrowcolor=C["LM1"], arrowsize=1.1
            )
        _add_point(fig, geo["YA"], geo["rA"], "A", C["A"], "top left")
        _add_point(fig, geo["YB"], geo["rB"], "B", C["B"], "top right")
        _add_trajectory_arrow(fig, geo["YA"], geo["rA"], geo["YB"], geo["rB"], C["B"])

    # ── ETAPA 2: IS₂ (se houver) + ponto C ───────────────────
    if etapa >= 2:
        if r_IS2 is not None:
            _add_curve(fig, Y, r_IS2, "IS₂ (ajuste cambial)", C["IS2"],
                       width=2.5, dash="longdash", label="IS₂")
        _add_point(fig, geo["YA"],     geo["rA"],     "A", C["A"], "top left")
        _add_point(fig, geo["YB"],     geo["rB"],     "B", C["B"], "top right")
        _add_point(fig, geo["YC_fin"], geo["rC_fin"], "C", C["C"], "bottom right")
        _add_trajectory_arrow(fig, geo["YA"],  geo["rA"],    geo["YB"],     geo["rB"],     C["B"])
        _add_trajectory_arrow(fig, geo["YB"],  geo["rB"],    geo["YC_fin"], geo["rC_fin"], C["C"])

    # ── Projeções nos eixos ───────────────────────────────────
    x_left, y_floor = _set_axes(fig, Y, geo, etapa, aberta)

    if etapa == 0:
        _add_projections(fig, geo["YA"], geo["rA"], x_left, y_floor, C["A"])
    elif etapa == 1:
        _add_projections(fig, geo["YA"], geo["rA"], x_left, y_floor, C["A"])
        _add_projections(fig, geo["YB"], geo["rB"], x_left, y_floor, C["B"])
    else:
        _add_projections(fig, geo["YA"],     geo["rA"],     x_left, y_floor, C["A"])
        _add_projections(fig, geo["YC_fin"], geo["rC_fin"], x_left, y_floor, C["C"])

    # Ponto A sempre visível na etapa 0
    if etapa == 0:
        _add_point(fig, geo["YA"], geo["rA"], "A", C["A"], "top left")

    return fig

# ══════════════════════════════════════════════════════════════
# CAMADA DIDÁTICA — TEXTOS POR ETAPA
# ══════════════════════════════════════════════════════════════

def _texto_etapa(politica, direcao, tipo_eco, regime, mobilidade_label, etapa):
    fiscal   = politica == "Fiscal"
    expansao = direcao  == "Expansionista"
    aberta   = tipo_eco == "Aberta"
    flex     = regime   == "Flexível"

    if etapa == 0:
        return dict(
            titulo="📍 Estado A — Equilíbrio Inicial",
            cor="blue",
            blocos=[
                ("O que representa?",
                 "A economia encontra-se em equilíbrio simultâneo nos mercados de **bens (IS)** "
                 "e **moeda (LM)**" + (", e no balanço de pagamentos **(BP)**" if aberta else "") + ". "
                 "O produto Y₀ e a taxa de juros i₀ são determinados pela interseção IS-LM."),
                ("Condições de equilíbrio",
                 "- **Mercado de bens (IS):** Demanda agregada = Produto  \n"
                 "- **Mercado monetário (LM):** Oferta de moeda = Demanda por moeda  \n"
                 + ("- **Balanço de pagamentos (BP):** NX + FC = 0" if aberta else "")),
                ("Próximo passo",
                 f"Será aplicada uma **política {politica.lower()} {direcao.lower()}**. "
                 "Avance para a Etapa B para ver o efeito imediato."),
            ]
        )

    elif etapa == 1:
        if fiscal and expansao:
            causa = "O aumento dos gastos públicos (G↑) ou redução de impostos (T↓) eleva a demanda agregada."
            efeito_curva = "A **curva IS desloca-se para a direita** (IS₀ → IS₁)."
            efeito_Y = "O produto tende a aumentar (Y↑)."
            efeito_r = "A maior demanda por moeda pressiona os juros para cima (i↑)."
        elif fiscal and not expansao:
            causa = "A redução dos gastos públicos (G↓) ou aumento de impostos (T↑) contrai a demanda."
            efeito_curva = "A **curva IS desloca-se para a esquerda** (IS₀ → IS₁)."
            efeito_Y = "O produto tende a cair (Y↓)."
            efeito_r = "A menor demanda por moeda reduz os juros (i↓)."
        elif not fiscal and expansao:
            causa = "O aumento da oferta de moeda (M↑) pelo Banco Central reduz o custo do crédito."
            efeito_curva = "A **curva LM desloca-se para a direita** (LM₀ → LM₁)."
            efeito_Y = "Com juros menores, o investimento aumenta e o produto cresce (Y↑)."
            efeito_r = "Os juros caem imediatamente (i↓)."
        else:
            causa = "A redução da oferta de moeda (M↓) eleva o custo do crédito."
            efeito_curva = "A **curva LM desloca-se para a esquerda** (LM₀ → LM₁)."
            efeito_Y = "Com juros maiores, o investimento cai e o produto recua (Y↓)."
            efeito_r = "Os juros sobem imediatamente (i↑)."

        return dict(
            titulo="⚡ Estado B — Choque de Curto Prazo",
            cor="orange",
            blocos=[
                ("O que aconteceu?", causa),
                ("Deslocamento da curva", efeito_curva + "  \n" + efeito_Y + "  \n" + efeito_r),
                ("Interpretação do Ponto B",
                 "O ponto B representa o **desequilíbrio transitório**: a economia saiu do ponto A "
                 "mas ainda não atingiu o novo equilíbrio. O mercado de " +
                 ("moeda" if fiscal else "bens") + " ainda está se ajustando."),
                ("Próximo passo",
                 "Os mercados se ajustam automaticamente. Avance para a Etapa C para ver o novo equilíbrio."),
            ]
        )

    else:  # etapa == 2
        if fiscal and expansao and aberta and flex:
            resultado = ("Com câmbio flexível e alta mobilidade de capital, a entrada de capital aprecia "
                         "a moeda (e↓), reduzindo as exportações líquidas (NX↓). A IS recua quase à posição "
                         "original. **Resultado Mundell-Fleming: política fiscal é ineficaz** — o crowding-out "
                         "externo cancela o estímulo fiscal.")
            delta_Y = "≈ 0 (crowding-out externo completo)"
            delta_r = "≈ 0 (retorna ao nível internacional)"
        elif fiscal and expansao and aberta and not flex:
            resultado = ("Com câmbio fixo, a entrada de capital força o BC a comprar divisas, expandindo "
                         "a oferta de moeda (M↑). A LM desloca-se para a direita, amplificando o estímulo. "
                         "**Resultado Mundell-Fleming: política fiscal é muito eficaz.**")
            delta_Y = "↑↑ (amplificado pelo ajuste monetário)"
            delta_r = "≈ 0 (mantido pelo câmbio fixo)"
        elif not fiscal and expansao and aberta and flex:
            resultado = ("Com câmbio flexível, a queda dos juros provoca saída de capital e depreciação "
                         "cambial (e↑). As exportações aumentam (NX↑), deslocando a IS para a direita. "
                         "**Resultado Mundell-Fleming: política monetária é muito eficaz.**")
            delta_Y = "↑↑ (amplificado pelo canal cambial)"
            delta_r = "↓ (retorna ao nível internacional)"
        elif not fiscal and expansao and aberta and not flex:
            resultado = ("Com câmbio fixo, a queda dos juros provoca saída de capital. O BC vende divisas "
                         "para defender o câmbio, contraindo a oferta de moeda. A LM retorna à posição original. "
                         "**Resultado Mundell-Fleming: política monetária é ineficaz.**")
            delta_Y = "≈ 0 (revertido pelo ajuste do BC)"
            delta_r = "≈ 0 (retorna ao nível inicial)"
        elif fiscal and expansao:
            resultado = ("O novo equilíbrio apresenta **Y maior e i maior**. O aumento dos juros reduz "
                         "parcialmente o investimento privado — efeito **crowding-out** parcial.")
            delta_Y = "↑ (menor que o multiplicador simples)"
            delta_r = "↑ (crowding-out parcial)"
        elif fiscal and not expansao:
            resultado = "O novo equilíbrio apresenta **Y menor e i menor**."
            delta_Y = "↓"; delta_r = "↓"
        elif not fiscal and expansao:
            resultado = ("O novo equilíbrio apresenta **Y maior e i menor**. "
                         "A política monetária estimulou o investimento sem pressionar os juros.")
            delta_Y = "↑"; delta_r = "↓"
        else:
            resultado = "O novo equilíbrio apresenta **Y menor e i maior**."
            delta_Y = "↓"; delta_r = "↑"

        return dict(
            titulo="✅ Estado C — Novo Equilíbrio",
            cor="green",
            blocos=[
                ("Ajuste e novo equilíbrio", resultado),
                ("Variações em relação ao Estado A",
                 f"- **ΔY:** {delta_Y}  \n- **Δi:** {delta_r}"),
                ("Síntese teórica",
                 "O modelo IS-LM-BP de Mundell-Fleming demonstra que a **eficácia das políticas econômicas "
                 "depende criticamente do regime cambial e do grau de mobilidade de capital**. "
                 "Em economias abertas, os canais externos modificam substancialmente os multiplicadores fiscais e monetários."),
            ]
        )

# ══════════════════════════════════════════════════════════════
# INTERFACE PRINCIPAL
# ══════════════════════════════════════════════════════════════

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Poppins:ital,wght@0,300;0,400;0,600;0,700;1,400&display=swap" rel="stylesheet">
<style>
    .main-title {
        font-family: 'Poppins', sans-serif;
        font-size: 1.85rem;
        font-weight: 700;
        letter-spacing: 0.01em;
        background: linear-gradient(90deg, #3b82f6 0%, #8b5cf6 55%, #10b981 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 2px;
    }
    .sub-title {
        font-family: 'Poppins', sans-serif;
        font-size: 0.95rem;
        font-weight: 300;
        letter-spacing: 0.03em;
        margin-top: -4px;
    }
    .etapa-card {
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 10px;
        border-left: 4px solid;
        font-family: 'Poppins', sans-serif;
    }
    .etapa-blue   {border-color: #1a3a6b; background: #eef2ff; color: #1e3a5f;}
    .etapa-orange {border-color: #b45309; background: #fef9ee; color: #7c3a00;}
    .etapa-green  {border-color: #065f46; background: #f0fdf4; color: #064e3b;}
    .sub-title { color: #64748b; }
    @media (prefers-color-scheme: dark) {
        .sub-title { color: #94a3b8; }
        .etapa-blue   {border-color: #4a7fc1; background: rgba(74,127,193,0.13); color: #93c5fd;}
        .etapa-orange {border-color: #d97706; background: rgba(217,119,6,0.13);  color: #fcd34d;}
        .etapa-green  {border-color: #10b981; background: rgba(16,185,129,0.13); color: #6ee7b7;}
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🌍 IS-LM-BP — Simulador Macroeconômico</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Modelo Mundell-Fleming &nbsp;|&nbsp; Economia Aberta &nbsp;|&nbsp; Nível Universitário</div>', unsafe_allow_html=True)
st.divider()

modo = st.radio(
    "Modo de simulação:",
    ["🎓 Modo Simplificado (didático)", "🔢 Modo Complexo (numérico)"],
    horizontal=True
)
st.divider()

# ══════════════════════════════════════════════════════════════
# MODO SIMPLIFICADO
# ══════════════════════════════════════════════════════════════
if "Simplificado" in modo:

    with st.sidebar:
        st.markdown("### ⚙️ Configurações")
        tipo_eco = st.radio("Economia:", ["Fechada", "Aberta"])
        aberta   = tipo_eco == "Aberta"
        regime   = "Flexível"
        if aberta:
            regime = st.radio("Regime cambial:", ["Flexível", "Fixo"])
        st.divider()
        politica = st.radio("Política:", ["Fiscal", "Monetária"])
        direcao  = st.radio("Direção:", ["Expansionista", "Contracionista"])
        if aberta:
            mob_opts = ["Nula", "Baixa", "Alta", "Perfeita"]
            default_mob = st.session_state.settings.get("mobilidade_capital", "Alta")
            if default_mob not in mob_opts:
                default_mob = "Alta"
            sel_mob = st.selectbox("Mobilidade de capital:", mob_opts,
                                   index=mob_opts.index(default_mob))
            st.session_state.settings["mobilidade_capital"] = sel_mob
            MOB_MAP = {"Nula": 0.0, "Baixa": 0.2, "Alta": 0.5, "Perfeita": 1.0}
            kappa = MOB_MAP[sel_mob]
            st.caption(f"κ = {kappa}")
        else:
            kappa = 0.5; sel_mob = "Alta"
        st.divider()
        executar = st.button("Simular economia", type="primary", use_container_width=True)

    if executar:
        st.session_state["simp_ok"]  = True
        st.session_state["simp_cfg"] = (tipo_eco, regime, politica, direcao, kappa, sel_mob)
        st.session_state["etapa"]    = 0

    if st.session_state.get("simp_ok"):
        tipo_eco_s, regime_s, politica_s, direcao_s, kappa_s, mob_s = st.session_state["simp_cfg"]

        col_nav1, col_nav2, col_nav3, col_nav4 = st.columns([1, 1, 1, 3])
        with col_nav1:
            if st.button("◀ Anterior", use_container_width=True):
                st.session_state["etapa"] = max(0, st.session_state.get("etapa", 0) - 1)
        with col_nav2:
            if st.button("Próximo ▶", use_container_width=True):
                st.session_state["etapa"] = min(2, st.session_state.get("etapa", 0) + 1)
        with col_nav3:
            etapa_sel = st.selectbox("Etapa:", [0, 1, 2],
                                     index=st.session_state.get("etapa", 0),
                                     format_func=lambda x: ["A — Inicial", "B — Choque", "C — Equilíbrio"][x],
                                     label_visibility="collapsed")
            st.session_state["etapa"] = etapa_sel

        etapa = st.session_state.get("etapa", 0)

        prog_cols = st.columns(3)
        for i, (lbl, cor_cls) in enumerate([
            ("A — Equilíbrio Inicial",    "etapa-blue"),
            ("B — Choque de Curto Prazo", "etapa-orange"),
            ("C — Novo Equilíbrio",       "etapa-green"),
        ]):
            with prog_cols[i]:
                ativo = "**" if i == etapa else ""
                st.markdown(
                    f'<div class="etapa-card {cor_cls if i == etapa else ""}" '
                    f'style="opacity:{"1" if i <= etapa else "0.35"}; padding:8px 12px;">'
                    f'{ativo}{"●" if i == etapa else "○"} {lbl}{ativo}</div>',
                    unsafe_allow_html=True
                )

        st.divider()

        col_graf, col_exp = st.columns([3, 2])

        with col_graf:
            fig = grafico_etapa(politica_s, direcao_s, tipo_eco_s, regime_s, kappa_s, etapa)
            st.plotly_chart(fig, use_container_width=True)

            if etapa >= 1:
                lc1, lc2, lc3 = st.columns(3)
                lc1.info("🔵 **A** — Equilíbrio inicial")
                if etapa >= 1: lc2.warning("🟡 **B** — Desequilíbrio transitório")
                if etapa >= 2: lc3.success("🟢 **C** — Novo equilíbrio")

        with col_exp:
            txt = _texto_etapa(politica_s, direcao_s, tipo_eco_s, regime_s, mob_s, etapa)
            cor_border   = {"blue": "#2563eb", "orange": "#d97706", "green": "#059669"}[txt["cor"]]
            cor_txt_light= {"blue": "#1e3a5f", "orange": "#7c3a00", "green": "#064e3b"}[txt["cor"]]
            cor_txt_dark = {"blue": "#93c5fd", "orange": "#fcd34d", "green": "#6ee7b7"}[txt["cor"]]
            bg_light     = {"blue": "#eef2ff", "orange": "#fef9ee", "green": "#f0fdf4"}[txt["cor"]]
            bg_dark      = {"blue": "rgba(37,99,235,0.12)", "orange": "rgba(217,119,6,0.12)", "green": "rgba(5,150,105,0.12)"}[txt["cor"]]
            card_id      = f"exp-card-{txt['cor']}"

            st.markdown(
                f'<style>'
                f'#{card_id} {{ background:{bg_light}; border-left:4px solid {cor_border}; '
                f'border-radius:8px; padding:16px 18px; font-family:"EB Garamond",Georgia,serif; }}'
                f'#{card_id} .card-title {{ color:{cor_txt_light}; font-size:1.1rem; font-weight:700; }}'
                f'@media (prefers-color-scheme: dark) {{'
                f'  #{card_id} {{ background:{bg_dark}; }}'
                f'  #{card_id} .card-title {{ color:{cor_txt_dark}; }}'
                f'}}'
                f'</style>'
                f'<div id="{card_id}"><span class="card-title">{txt["titulo"]}</span></div>',
                unsafe_allow_html=True
            )
            st.markdown("")

            for subtitulo, conteudo in txt["blocos"]:
                with st.expander(f"📖 {subtitulo}", expanded=True):
                    st.markdown(conteudo)

    else:
        st.info("Configure os parâmetros na barra lateral e clique em **▶ Simular**.")

# ══════════════════════════════════════════════════════════════
# MODO COMPLEXO
# ══════════════════════════════════════════════════════════════
else:
    p = DEFAULT_PARAMS.copy()
    p["aberta"] = False

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### 🏛️ Política Econômica")
        p["G"] = st.number_input("G — Gasto do Governo", value=float(p["G"]), step=10.)
        p["T"] = st.number_input("T — Impostos",         value=float(p["T"]), step=10.)
        p["M"] = st.number_input("M — Oferta Monetária", value=float(p["M"]), step=50.)
        p["P"] = st.number_input("P — Nível de Preços",  value=float(p["P"]), step=0.1)
        st.markdown("#### 📐 Parâmetros Estruturais")
        p["c0"] = st.number_input("c0 — Consumo Autônomo",     value=float(p["c0"]), step=10.)
        p["c1"] = st.number_input("c1 — Propensão a Consumir", value=float(p["c1"]), step=0.01, format="%.2f")
        p["I0"] = st.number_input("I0 — Investimento Autônomo",value=float(p["I0"]), step=10.)
        p["b"]  = st.number_input("b — Sensibilidade I a r",   value=float(p["b"]),  step=5.)
        p["k"]  = st.number_input("k — Sensibilidade L a Y",   value=float(p["k"]),  step=0.05, format="%.2f")
        p["h"]  = st.number_input("h — Sensibilidade L a r",   value=float(p["h"]),  step=10.)

    with col2:
        st.markdown("#### 🌐 Economia Aberta")
        aberta_cx = st.checkbox("Ativar economia aberta (IS-LM-BP)", value=False)
        p["aberta"] = aberta_cx
        if aberta_cx:
            regime_cx = st.radio("Regime cambial:", ["flex", "fixo"],
                                  format_func=lambda x: "Câmbio Flexível" if x == "flex" else "Câmbio Fixo")
            p["regime"]  = regime_cx
            p["Y_star"]  = st.number_input("Y* — Renda Externa",        value=float(p["Y_star"]), step=50.)
            p["r_star"]  = st.number_input("r* — Juros Internacionais",  value=float(p["r_star"]), step=0.005, format="%.4f")
            p["e"]       = st.number_input("e — Câmbio Inicial",         value=float(p["e"]),      step=0.05)
            p["x0"]      = st.number_input("x0 — Exportações Autônomas", value=float(p["x0"]),     step=10.)
            p["x1"]      = st.number_input("x1 — Sensib. X a Y*",        value=float(p["x1"]),     step=0.01, format="%.3f")
            p["m0"]      = st.number_input("m0 — Importações Autônomas", value=float(p["m0"]),     step=10.)
            p["m1"]      = st.number_input("m1 — Propensão a Importar",  value=float(p["m1"]),     step=0.01, format="%.3f")
            kf_preset    = st.select_slider("Mobilidade de Capital:",
                                             options=["Nula", "Baixa", "Alta", "Perfeita"], value="Alta")
            p["kf"] = {"Nula": 0., "Baixa": 10., "Alta": 700., "Perfeita": 1e7}[kf_preset]
            if regime_cx == "fixo":
                p["e_fixed"] = st.number_input("e fixo (meta BC)", value=float(p.get("e_fixed", 1.)), step=0.05)

    with col3:
        st.markdown("#### 🔀 Choque (Cenário 2)")
        dG = st.number_input("ΔG", value=0., step=10.)
        dT = st.number_input("ΔT", value=0., step=10.)
        dM = st.number_input("ΔM", value=0., step=50.)
        if aberta_cx:
            dr_star = st.number_input("Δr*", value=0., step=0.005, format="%.4f")
            dY_star = st.number_input("ΔY*", value=0., step=50.)
        else:
            dr_star = dY_star = 0.
        executar_cx = st.button("🚀 Calcular Equilíbrio", type="primary", use_container_width=True)

    if executar_cx:
        p_shock = p.copy()
        p_shock["G"] += dG; p_shock["T"] += dT; p_shock["M"] += dM
        p_shock["r_star"] += dr_star; p_shock["Y_star"] += dY_star
        try:
            if not aberta_cx:
                eq_b = solve_fechada(p); eq_c = solve_fechada(p_shock)
            elif p["regime"] == "flex":
                eq_b = solve_flex(p);    eq_c = solve_flex(p_shock)
            else:
                eq_b = solve_fixo(p);    eq_c = solve_fixo(p_shock)

            st.divider()
            st.markdown("### 📊 Resultados")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Y*", f"{eq_b['Y']:.2f}", f"{eq_c['Y']-eq_b['Y']:+.2f}")
            c2.metric("r*", f"{eq_b['r']*100:.3f}%", f"{(eq_c['r']-eq_b['r'])*100:+.3f}pp")
            c3.metric("e*", f"{eq_b['e']:.4f}", f"{eq_c['e']-eq_b['e']:+.4f}")
            c4.metric("NX", f"{eq_b['NX']:.2f}", f"{eq_c['NX']-eq_b['NX']:+.2f}")

            st.markdown(f"""
| Variável | Base | Choque | Δ |
|---|---|---|---|
| **Y** | {eq_b['Y']:.2f} | {eq_c['Y']:.2f} | **{eq_c['Y']-eq_b['Y']:+.2f}** |
| **r** | {eq_b['r']*100:.3f}% | {eq_c['r']*100:.3f}% | **{(eq_c['r']-eq_b['r'])*100:+.3f}pp** |
| **e** | {eq_b['e']:.4f} | {eq_c['e']:.4f} | **{eq_c['e']-eq_b['e']:+.4f}** |
| **NX** | {eq_b['NX']:.2f} | {eq_c['NX']:.2f} | **{eq_c['NX']-eq_b['NX']:+.2f}** |
| **CF** | {eq_b['CF']:.2f} | {eq_c['CF']:.2f} | **{eq_c['CF']-eq_b['CF']:+.2f}** |
| **C** | {eq_b['C']:.2f} | {eq_c['C']:.2f} | **{eq_c['C']-eq_b['C']:+.2f}** |
| **I** | {eq_b['I']:.2f} | {eq_c['I']:.2f} | **{eq_c['I']-eq_b['I']:+.2f}** |
""")
            with st.expander("🔬 Verificação de Consistência"):
                for lbl, res in [("IS", eq_c["IS_res"]), ("LM", eq_c["LM_res"]), ("BP", eq_c["BP_res"])]:
                    ok = abs(res) < 0.01
                    st.markdown(f"{'✅' if ok else '⚠️'} **{lbl}** resíduo = `{res:.6f}`")

            # Gráfico complexo
            Y_grid = np.linspace(200, 2500, 500)
            r_min, r_max = -0.3, 0.8
            fig2 = go.Figure()
            for r_c, nm, col, dsh in [
                (curva_IS(Y_grid, eq_b["e"], p, aberta_cx),       "IS base",   C["IS"],  "solid"),
                (curva_IS(Y_grid, eq_c["e"], p_shock, aberta_cx), "IS choque", C["IS1"], "dash"),
                (curva_LM(Y_grid, p["M"], p),                     "LM base",   C["LM"],  "solid"),
                (curva_LM(Y_grid, p_shock["M"], p_shock),         "LM choque", C["LM1"], "dash"),
            ]:
                mask = (r_c > r_min) & (r_c < r_max)
                fig2.add_trace(go.Scatter(x=Y_grid[mask], y=r_c[mask], name=nm,
                                          line=dict(color=col, width=2.5, dash=dsh)))
            if aberta_cx:
                for r_c, nm, dsh in [
                    (curva_BP_plot(Y_grid, eq_b["e"], p),       "BP base",   "solid"),
                    (curva_BP_plot(Y_grid, eq_c["e"], p_shock), "BP choque", "dash"),
                ]:
                    mask = (r_c > r_min) & (r_c < r_max)
                    fig2.add_trace(go.Scatter(x=Y_grid[mask], y=r_c[mask], name=nm,
                                              line=dict(color=C["BP"], width=2.5, dash=dsh)))
            fig2.add_trace(go.Scatter(
                x=[eq_b["Y"], eq_c["Y"]], y=[eq_b["r"], eq_c["r"]],
                mode="markers+text",
                marker=dict(size=14, color=[C["IS"], C["LM"]], symbol="star",
                            line=dict(width=1, color="white")),
                text=["E₀", "E₁"], textposition="top right",
                textfont=dict(size=14), name="Equilíbrios"
            ))
            fig2.add_annotation(ax=eq_b["Y"], ay=eq_b["r"], x=eq_c["Y"], y=eq_c["r"],
                                 xref="x", yref="y", axref="x", ayref="y",
                                 showarrow=True, arrowhead=3, arrowwidth=2.5, arrowcolor="#0f172a")
            fig2.update_layout(title="IS-LM-BP: Base vs. Choque",
                                xaxis_title="Produto (Y)", yaxis_title="Taxa de Juros (r)",
                                template="plotly_white", height=520,
                                legend=dict(x=0.01, y=0.99))
            st.plotly_chart(fig2, use_container_width=True)

        except Exception as ex:
            st.error(f"Erro no solver: {ex}")
            st.info("Verifique os parâmetros — o sistema pode não ter solução com esses valores.")