# pages/4_Modelo ISLMBP.py
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
#
# CORREÇÃO: Os parâmetros originais (IS_a=2.2, LM_a=-1.2) produziam
# equilíbrio em r≈-0.59 (negativo, fora da área visível), fazendo as
# curvas parecerem sobrepostas. Agora o equilíbrio A fica em Y≈1.30,
# r≈0.98 — bem visível, com separação clara entre os pontos A, B e C.
# ══════════════════════════════════════════════════════════════
IS_a, IS_b = 2.8, 1.4      # IS: r = IS_a - IS_b·Y  (intercepto maior, inclinação levemente mais suave)
LM_a, LM_b = 0.2, 0.6      # LM: r = LM_a + LM_b·Y  (intercepto positivo, mais íngreme → ângulo claro)
SHIFT       = 0.60          # deslocamento das curvas após o choque (levemente maior para separar A→C)

# ── SLOPE_MAP: kappa → inclinação da BP ──────────────────────
# Recalibrado para ficar coerente com a nova LM (slope=0.6):
#   BP Baixa (0.2) deve ser mais íngreme que LM  → slope > 0.6
#   BP Alta  (0.5) deve ser menos íngreme que LM → slope < 0.6
SLOPE_MAP = {
    0.0: 3.5,   # Nula  → quase vertical (muito acima de LM_b)
    0.2: 1.1,   # Baixa → íngreme (acima de LM_b=0.6)
    0.5: 0.20,  # Alta  → suave   (abaixo de LM_b=0.6)
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
    # CORREÇÃO: margem inferior reduzida de -0.25 para -0.15
    # evita espaço morto no rodapé sem cortar projeções pontilhadas
    y_floor = LM_a + LM_b * float(Y.min()) - 0.15

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
    if aberta:
        kappa_key = round(mobilidade_kappa, 1)
        if mobilidade_kappa >= 0.98:
            r_BP   = np.full_like(Y, geo["rA"])
            bp_tipo = "perfeita"
        elif mobilidade_kappa <= 0.02:
            r_BP   = None
            bp_tipo = "nula"
        else:
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

    BP_INFO = {
        "Nula": dict(
            inclinacao="vertical (↕)",
            geometria=(
                "No gráfico, observe que a curva **BP é vertical** — ela não depende da taxa de juros. "
                "Isso significa que nenhum fluxo de capital cruza as fronteiras, independentemente do diferencial de juros. "
                "O equilíbrio externo é determinado **exclusivamente pela balança comercial**: NX = 0."
            ),
            descricao=(
                "Com **mobilidade nula**, o país está completamente isolado dos mercados financeiros internacionais. "
                "Não há entrada nem saída de capital estrangeiro. "
                "O único canal de ajuste externo é o **comércio de bens**: exportações e importações. "
                "A posição da BP no eixo Y indica o nível de renda compatível com NX = 0."
            ),
            acima_bp=(
                "**Superávit no Balanço de Pagamentos (NX > 0)**  \n"
                "O ponto está à **esquerda** da BP vertical: a renda interna (Y) está baixa demais, "
                "gerando poucas importações. As exportações superam as importações → entrada líquida de divisas."
            ),
            abaixo_bp=(
                "**Déficit no Balanço de Pagamentos (NX < 0)**  \n"
                "O ponto está à **direita** da BP vertical: a renda interna (Y) está alta demais, "
                "gerando excesso de importações. As importações superam as exportações → saída líquida de divisas."
            ),
            ajuste_flex=(
                "**Câmbio Flexível + Mobilidade Nula:**  \n"
                "O déficit comercial pressiona a moeda para baixo (depreciação: e↑).  \n"
                "Com a moeda mais barata: exportações ficam mais competitivas (X↑) e importações encarecem (M↓).  \n"
                "A IS se desloca para a direita via NX↑, até que NX = 0 novamente.  \n"
                "⚠️ Os juros **não têm papel** neste ajuste — apenas o câmbio real importa."
            ),
            ajuste_fixo=(
                "**Câmbio Fixo + Mobilidade Nula:**  \n"
                "O BC defende o câmbio vendendo reservas internacionais (para cobrir o déficit).  \n"
                "Isso retira moeda local de circulação → M↓ → LM desloca para a esquerda.  \n"
                "Y cai até o nível compatível com NX = 0.  \n"
                "⚠️ A política monetária perde **autonomia total** — é endógena ao BP."
            ),
        ),
        "Baixa": dict(
            inclinacao="íngreme (positiva, mais vertical que a LM)",
            geometria=(
                "No gráfico, observe que a curva **BP tem inclinação positiva e íngreme** — "
                "mais vertical do que a curva LM. "
                "Isso significa que para sustentar um Y maior (que gera mais importações), "
                "é necessário um aumento **grande** de juros para atrair capital suficiente."
            ),
            descricao=(
                "Com **mobilidade baixa**, o capital responde pouco às variações de juros. "
                "Os fluxos financeiros internacionais são restritos (controles de capital, custos de transação elevados). "
                "O canal comercial (NX) ainda domina o ajuste externo. "
                "A BP é **mais inclinada que a LM**: para cada unidade de Y adicional, "
                "é preciso um aumento de juros maior do que o que a LM exigiria."
            ),
            acima_bp=(
                "**Superávit no BP** (NX + FC > 0)  \n"
                "Os juros internos estão **acima** do necessário para o equilíbrio externo naquele nível de Y. "
                "Há entrada excessiva de capital estrangeiro (FC > 0) que supera o déficit comercial. "
                "→ Pressão de apreciação cambial."
            ),
            abaixo_bp=(
                "**Déficit no BP** (NX + FC < 0)  \n"
                "Os juros internos estão **abaixo** do necessário. "
                "A saída de capital (FC < 0) supera o superávit comercial. "
                "→ Pressão de depreciação cambial."
            ),
            ajuste_flex=(
                "**Câmbio Flexível + Mobilidade Baixa:**  \n"
                "A saída de capital deprecia a moeda (e↑), mas o efeito é moderado.  \n"
                "NX melhora gradualmente → IS desloca levemente para a direita.  \n"
                "O ajuste é **lento**: o canal comercial domina, mas responde com defasagem.  \n"
                "Resultado: Y aumenta menos do que com alta mobilidade."
            ),
            ajuste_fixo=(
                "**Câmbio Fixo + Mobilidade Baixa:**  \n"
                "O BC precisa de intervenções **volumosas** para defender o câmbio.  \n"
                "Cada unidade de déficit exige grande venda de reservas → M↓ significativo → LM recua.  \n"
                "A política fiscal tem eficácia **moderada**: o crowding-out externo é parcial.  \n"
                "Quanto menor a mobilidade, maior a eficácia fiscal relativa."
            ),
        ),
        "Alta": dict(
            inclinacao="suave (positiva, menos inclinada que a LM)",
            geometria=(
                "No gráfico, observe que a curva **BP tem inclinação suave** — "
                "quase horizontal, menos inclinada que a LM. "
                "Isso significa que pequenas variações de juros geram grandes fluxos de capital, "
                "dominando o ajuste externo sobre o canal comercial."
            ),
            descricao=(
                "Com **mobilidade alta**, o capital é muito sensível ao diferencial de juros (r − r*). "
                "Este é o caso mais comum em economias emergentes integradas aos mercados globais. "
                "A BP é **menos inclinada que a LM**: o canal financeiro domina o ajuste. "
                "Pequenas diferenças entre r interno e r* internacional geram fluxos intensos."
            ),
            acima_bp=(
                "**Superávit no BP** (FC >> |NX|)  \n"
                "Os juros internos estão **acima de r***: grande entrada de capital estrangeiro. "
                "O fluxo financeiro supera amplamente qualquer déficit comercial. "
                "→ Forte pressão de apreciação cambial."
            ),
            abaixo_bp=(
                "**Déficit no BP** (|FC| >> NX)  \n"
                "Os juros internos estão **abaixo de r***: fuga de capital para o exterior. "
                "O fluxo financeiro supera qualquer superávit comercial. "
                "→ Forte pressão de depreciação cambial."
            ),
            ajuste_flex=(
                "**Câmbio Flexível + Mobilidade Alta:**  \n"
                "Qualquer diferencial r ≠ r* gera fluxos de capital intensos e rápidos.  \n"
                "Se r < r*: saída de capital → depreciação (e↑) → NX↑ → IS desloca para direita.  \n"
                "Se r > r*: entrada de capital → apreciação (e↓) → NX↓ → IS recua.  \n"
                "O ajuste é **rápido e poderoso** via canal cambial-comercial."
            ),
            ajuste_fixo=(
                "**Câmbio Fixo + Mobilidade Alta:**  \n"
                "O BC perde quase toda autonomia monetária.  \n"
                "Qualquer tentativa de alterar M é revertida pela intervenção cambial.  \n"
                "A política fiscal é **amplificada**: G↑ → i↑ → entrada de capital → BC compra divisas → M↑ → LM desloca direita.  \n"
                "O multiplicador fiscal é maior do que em economia fechada."
            ),
        ),
        "Perfeita": dict(
            inclinacao="horizontal (r = r* em todos os pontos)",
            geometria=(
                "No gráfico, observe que a curva **BP é perfeitamente horizontal** no nível r = r*. "
                "Isso representa o caso-limite: qualquer desvio de r em relação a r* "
                "gera fluxos de capital **infinitos** que instantaneamente restauram r = r*."
            ),
            descricao=(
                "Com **mobilidade perfeita**, os mercados financeiros são completamente integrados. "
                "A taxa de juros interna é **fixada exogenamente** em r = r* (paridade de juros). "
                "Este é o caso-limite do modelo Mundell-Fleming, que produz os resultados mais extremos "
                "e é o ponto de partida teórico para economias muito abertas (ex: países da zona do euro)."
            ),
            acima_bp=(
                "**Impossível em equilíbrio com mobilidade perfeita**  \n"
                "Se r > r*, a entrada de capital é instantânea e infinita → apreciação imediata → "
                "o sistema retorna a r = r* antes de qualquer ajuste real."
            ),
            abaixo_bp=(
                "**Impossível em equilíbrio com mobilidade perfeita**  \n"
                "Se r < r*, a saída de capital é instantânea e infinita → depreciação imediata → "
                "o sistema retorna a r = r* antes de qualquer ajuste real."
            ),
            ajuste_flex=(
                "**Câmbio Flexível + Mobilidade Perfeita (Mundell-Fleming clássico):**  \n\n"
                "🔴 **Política Fiscal COMPLETAMENTE INEFICAZ:**  \n"
                "G↑ → IS desloca direita → r tende a subir acima de r* → entrada de capital → "
                "apreciação (e↓) → NX↓ → IS recua exatamente à posição original.  \n"
                "**ΔY = 0, Δr = 0** — apenas o câmbio se apreciou.  \n\n"
                "🟢 **Política Monetária MUITO EFICAZ:**  \n"
                "M↑ → LM desloca direita → r tende a cair abaixo de r* → saída de capital → "
                "depreciação (e↑) → NX↑ → IS desloca direita → Y↑↑.  \n"
                "**ΔY máximo**, r retorna a r*."
            ),
            ajuste_fixo=(
                "**Câmbio Fixo + Mobilidade Perfeita (Mundell-Fleming clássico):**  \n\n"
                "🟢 **Política Fiscal MUITO EFICAZ:**  \n"
                "G↑ → IS desloca direita → r tende a subir → entrada de capital → "
                "BC compra divisas para manter câmbio → M↑ → LM desloca direita → Y↑↑.  \n"
                "**ΔY máximo**, multiplicador fiscal amplificado.  \n\n"
                "🔴 **Política Monetária COMPLETAMENTE INEFICAZ:**  \n"
                "M↑ → LM desloca direita → r tende a cair → saída de capital → "
                "BC vende divisas para manter câmbio → M↓ → LM retorna à posição original.  \n"
                "**ΔY = 0** — o BC reverte 100% do estímulo monetário."
            ),
        ),
    }

    bp = BP_INFO.get(mobilidade_label, BP_INFO["Alta"])

    if etapa == 0:
        blocos = [
            ("O que representa o Ponto A?",
             "A economia encontra-se em **equilíbrio simultâneo** nos mercados de "
             "**bens (IS)** e **moeda (LM)**" +
             (", e no **balanço de pagamentos (BP)**" if aberta else "") +
             ". O produto Y₀ e a taxa de juros i₀ são determinados pela interseção IS ∩ LM" +
             (" = BP" if aberta else "") + "."),

            ("Condições de equilíbrio nos 3 mercados",
             "**① Mercado de Bens — Curva IS:**  \n"
             "Demanda Agregada = Produto  \n"
             "→ C + I + G" + (" + NX" if aberta else "") + " = Y  \n"
             "→ A IS tem **inclinação negativa**: juros altos reduzem I, reduzindo Y.  \n\n"
             "**② Mercado Monetário — Curva LM:**  \n"
             "Oferta de Moeda Real = Demanda por Moeda  \n"
             "→ M/P = kY − hi  \n"
             "→ A LM tem **inclinação positiva**: Y maior exige mais moeda, elevando i.  \n" +
             ("\n**③ Balanço de Pagamentos — Curva BP:**  \n"
              "NX + FC = 0  \n"
              "→ Exportações Líquidas + Fluxo de Capital = 0  \n"
              "→ A inclinação da BP depende da **mobilidade de capital**." if aberta else "")),
        ]

        if aberta:
            blocos.append((
                f"📐 A Curva BP com Mobilidade {mobilidade_label}",
                bp["geometria"] + "  \n\n"
                "**Características desta configuração:**  \n"
                f"- Inclinação: **{bp['inclinacao']}**  \n"
                "- Pontos **acima** da BP → " + bp["acima_bp"].split("\\n")[0] + "  \n"
                "- Pontos **abaixo** da BP → " + bp["abaixo_bp"].split("\\n")[0] + "  \n\n"
                + bp["descricao"]
            ))

        blocos.append((
            "Próximo passo",
            f"Será aplicada uma **política {politica.lower()} {direcao.lower()}**. "
            "Avance para a **Etapa B** para ver o efeito imediato sobre os mercados."
        ))

        return dict(titulo="📍 Estado A — Equilíbrio Inicial", cor="blue", blocos=blocos)

    elif etapa == 1:
        if fiscal and expansao:
            mercado_afetado = "**Mercado de Bens (IS)**"
            instrumento = "aumento dos gastos públicos **(G↑)** ou redução de impostos **(T↓)**"
            causa = "A demanda agregada aumenta diretamente: C + I + **G↑** + NX = Y."
            curva_move = "A **IS desloca-se para a direita** (IS₀ → IS₁): para cada nível de juros, o produto de equilíbrio é maior."
            efeito_Y = "O produto tende a aumentar **(Y↑)** — efeito multiplicador keynesiano."
            efeito_r = "A maior renda eleva a demanda por moeda → juros sobem **(i↑)** ao longo da LM."
            mercado_estavel = "O mercado monetário (LM) **ainda não se ajustou** — a LM permanece fixa."
            ponto_B_desc = (
                "No Ponto B, a IS₁ intersecta a LM₀ original. "
                "O produto aumentou, mas os juros também subiram. "
                "O mercado de bens está em equilíbrio com a nova IS, mas o setor externo ainda não reagiu."
            )
        elif fiscal and not expansao:
            mercado_afetado = "**Mercado de Bens (IS)**"
            instrumento = "redução dos gastos públicos **(G↓)** ou aumento de impostos **(T↑)**"
            causa = "A demanda agregada cai diretamente: C + I + **G↓** + NX = Y."
            curva_move = "A **IS desloca-se para a esquerda** (IS₀ → IS₁): para cada nível de juros, o produto de equilíbrio é menor."
            efeito_Y = "O produto tende a cair **(Y↓)** — efeito multiplicador reverso."
            efeito_r = "A menor renda reduz a demanda por moeda → juros caem **(i↓)** ao longo da LM."
            mercado_estavel = "O mercado monetário (LM) **ainda não se ajustou** — a LM permanece fixa."
            ponto_B_desc = (
                "No Ponto B, a IS₁ intersecta a LM₀. "
                "O produto caiu e os juros também recuaram. "
                "O setor externo ainda não reagiu à nova configuração."
            )
        elif not fiscal and expansao:
            mercado_afetado = "**Mercado Monetário (LM)**"
            instrumento = "aumento da oferta de moeda **(M↑)** pelo Banco Central"
            causa = "A oferta de moeda real (M/P) aumenta, reduzindo o custo do crédito."
            curva_move = "A **LM desloca-se para a direita/baixo** (LM₀ → LM₁): para cada nível de Y, os juros de equilíbrio são menores."
            efeito_Y = "Com juros menores, o investimento privado aumenta **(I↑)** → produto cresce **(Y↑)**."
            efeito_r = "Os juros caem imediatamente **(i↓)** — efeito liquidez direto."
            mercado_estavel = "O mercado de bens (IS) **ainda não se ajustou** — a IS permanece fixa."
            ponto_B_desc = (
                "No Ponto B, a LM₁ intersecta a IS₀ original. "
                "Os juros caíram e o produto aumentou. "
                "Mas agora r < r*: o setor externo está em desequilíbrio."
            )
        else:
            mercado_afetado = "**Mercado Monetário (LM)**"
            instrumento = "redução da oferta de moeda **(M↓)** pelo Banco Central"
            causa = "A oferta de moeda real (M/P) cai, elevando o custo do crédito."
            curva_move = "A **LM desloca-se para a esquerda/cima** (LM₀ → LM₁): para cada nível de Y, os juros de equilíbrio são maiores."
            efeito_Y = "Com juros maiores, o investimento privado cai **(I↓)** → produto recua **(Y↓)**."
            efeito_r = "Os juros sobem imediatamente **(i↑)** — efeito contração monetária."
            mercado_estavel = "O mercado de bens (IS) **ainda não se ajustou** — a IS permanece fixa."
            ponto_B_desc = (
                "No Ponto B, a LM₁ intersecta a IS₀. "
                "Os juros subiram e o produto caiu. "
                "Agora r > r*: o setor externo está em desequilíbrio."
            )

        blocos = [
            ("1. O Choque — Qual mercado foi afetado?",
             f"O instrumento utilizado foi o {instrumento}, afetando o {mercado_afetado}.  \n\n"
             f"**Causa:** {causa}  \n\n"
             f"**Deslocamento:** {curva_move}  \n\n"
             f"**Efeito sobre Y:** {efeito_Y}  \n"
             f"**Efeito sobre i:** {efeito_r}  \n\n"
             f"⚠️ {mercado_estavel}"),

            ("2. Interpretação do Ponto B",
             ponto_B_desc + "  \n\n"
             "O **Ponto B** representa o **desequilíbrio transitório de curto prazo**:  \n"
             "- A economia saiu do Ponto A, mas **ainda não atingiu o novo equilíbrio**  \n"
             "- Existe excesso de demanda ou oferta em pelo menos um mercado  \n"
             "- As forças de ajuste já estão em ação, mas levam tempo para se completar"),
        ]

        if aberta:
            if not fiscal and expansao:
                pos_bp = "abaixo"
                cond_bp = bp["abaixo_bp"]
                pressao = (
                    "A queda dos juros internos cria um **diferencial negativo** em relação a r*: r < r*.  \n"
                    "Investidores preferem aplicar no exterior → **saída de capital (FC < 0)**.  \n"
                    "O BP entra em déficit: NX + FC < 0."
                )
            elif not fiscal and not expansao:
                pos_bp = "acima"
                cond_bp = bp["acima_bp"]
                pressao = (
                    "A alta dos juros internos cria um **diferencial positivo** em relação a r*: r > r*.  \n"
                    "Capital estrangeiro é atraído → **entrada de capital (FC > 0)**.  \n"
                    "O BP entra em superávit: NX + FC > 0."
                )
            elif fiscal and expansao:
                pos_bp = "acima"
                cond_bp = bp["acima_bp"]
                pressao = (
                    "O aumento do produto eleva as importações (NX↓), mas a alta dos juros atrai capital (FC↑).  \n"
                    f"Com mobilidade **{mobilidade_label.lower()}**, o efeito financeiro {'domina' if mobilidade_label in ['Alta','Perfeita'] else 'é moderado'}: "
                    f"{'o BP tende a superávit (FC > |NX|).' if mobilidade_label in ['Alta','Perfeita'] else 'o resultado depende da magnitude relativa dos fluxos.'}"
                )
            else:
                pos_bp = "abaixo"
                cond_bp = bp["abaixo_bp"]
                pressao = (
                    "A queda do produto reduz importações (NX↑), mas a queda dos juros afasta capital (FC↓).  \n"
                    f"Com mobilidade **{mobilidade_label.lower()}**, o efeito financeiro {'domina' if mobilidade_label in ['Alta','Perfeita'] else 'é moderado'}: "
                    f"{'o BP tende a déficit (|FC| > NX).' if mobilidade_label in ['Alta','Perfeita'] else 'o resultado depende da magnitude relativa dos fluxos.'}"
                )

            blocos.append((
                f"3. Posição do Ponto B em relação à BP (Mobilidade {mobilidade_label})",
                f"O Ponto B encontra-se **{pos_bp} da curva BP**.  \n\n"
                f"{cond_bp}  \n\n"
                f"**Pressão gerada no setor externo:**  \n{pressao}  \n\n"
                f"**Por que a BP tem inclinação {bp['inclinacao']}?**  \n"
                + bp["descricao"]
            ))

            blocos.append((
                f"4. O que o câmbio {regime} vai fazer agora?",
                (bp["ajuste_flex"] if flex else bp["ajuste_fixo"]) +
                "  \n\n→ Avance para a **Etapa C** para ver o resultado final."
            ))
        else:
            blocos.append((
                "3. Próximo passo (Economia Fechada)",
                "Sem setor externo, o ajuste ocorre apenas via variações em Y e i.  \n"
                "Os mercados de bens e moeda convergem para o novo equilíbrio IS-LM.  \n"
                "Avance para a **Etapa C** para ver o novo equilíbrio."
            ))

        return dict(titulo="⚡ Estado B — Choque de Curto Prazo", cor="orange", blocos=blocos)

    else:
        if aberta and flex and fiscal and expansao:
            if mobilidade_label == "Perfeita":
                resultado = (
                    "**Transmissão completa A → B → C:**  \n"
                    "1. G↑ → IS desloca para direita → Y↑ e i↑ (Ponto B)  \n"
                    "2. i > r* → entrada massiva de capital → **apreciação cambial (e↓)**  \n"
                    "3. e↓ → exportações encarecem, importações barateiam → **NX↓**  \n"
                    "4. NX↓ → IS recua exatamente à posição original (IS₂ ≈ IS₀)  \n\n"
                    "🔴 **Resultado: Política COMPLETAMENTE INEFICAZ**  \n"
                    "O crowding-out externo é **100%**: a IS retorna à posição original.  \n"
                    "**ΔY ≈ 0** — o câmbio absorveu todo o estímulo fiscal."
                )
                delta_Y = "≈ 0 (crowding-out externo 100%)"; delta_r = "≈ 0 (= r*)"; delta_e = "↓↓ (apreciação forte)"
            elif mobilidade_label == "Alta":
                resultado = (
                    "**Transmissão A → B → C:**  \n"
                    "1. G↑ → IS desloca para direita → Y↑ e i↑ (Ponto B)  \n"
                    "2. i > r* → entrada de capital → **apreciação cambial (e↓)**  \n"
                    "3. e↓ → NX↓ → IS recua parcialmente  \n\n"
                    "🟡 **Resultado: Política PARCIALMENTE INEFICAZ**  \n"
                    "O crowding-out externo é forte mas não total.  \n"
                    "Y aumenta levemente, muito menos que o multiplicador keynesiano simples sugeriria."
                )
                delta_Y = "↑ (pequeno)"; delta_r = "≈ r*"; delta_e = "↓ (apreciação moderada)"
            elif mobilidade_label == "Baixa":
                resultado = (
                    "**Transmissão A → B → C:**  \n"
                    "1. G↑ → IS desloca para direita → Y↑ e i↑ (Ponto B)  \n"
                    "2. i > r* → entrada moderada de capital → apreciação leve (e↓)  \n"
                    "3. NX↓ moderado → IS recua levemente  \n\n"
                    "🟢 **Resultado: Política PARCIALMENTE EFICAZ**  \n"
                    "Com baixa mobilidade, o canal cambial é fraco.  \n"
                    "Y aumenta de forma mais próxima ao multiplicador keynesiano."
                )
                delta_Y = "↑↑"; delta_r = "↑"; delta_e = "↓ (leve)"
            else:
                resultado = (
                    "**Transmissão A → B → C:**  \n"
                    "1. G↑ → IS desloca para direita → Y↑ e i↑ (Ponto B)  \n"
                    "2. Sem fluxo de capital: o ajuste externo é via NX apenas  \n"
                    "3. Y↑ → importações↑ → NX↓ → IS recua levemente  \n\n"
                    "🟢 **Resultado: Política EFICAZ** (mobilidade nula)  \n"
                    "Sem crowding-out financeiro, o estímulo fiscal é mais efetivo.  \n"
                    "O câmbio flexível deprecia para restaurar NX = 0."
                )
                delta_Y = "↑↑"; delta_r = "↑"; delta_e = "↑ (depreciação para equilibrar NX)"

        elif aberta and not flex and fiscal and expansao:
            if mobilidade_label == "Perfeita":
                resultado = (
                    "**Transmissão A → B → C:**  \n"
                    "1. G↑ → IS desloca para direita → Y↑ e i↑ (Ponto B)  \n"
                    "2. i > r* → entrada massiva de capital → pressão de apreciação  \n"
                    "3. BC intervém: **compra divisas** para manter câmbio fixo → M↑  \n"
                    "4. M↑ → LM desloca para direita → i↓, Y↑↑  \n\n"
                    "🟢 **Resultado: Política MUITO EFICAZ**  \n"
                    "O multiplicador fiscal é **máximo**: a expansão monetária endógena amplifica o estímulo.  \n"
                    "**ΔY >> ΔG**, com i mantido em r*."
                )
                delta_Y = "↑↑↑ (máximo)"; delta_r = "≈ 0 (= r*)"; delta_e = "fixo"
            else:
                resultado = (
                    "**Transmissão A → B → C:**  \n"
                    "1. G↑ → IS desloca para direita → Y↑ e i↑ (Ponto B)  \n"
                    f"2. i > r* → entrada de capital ({'intensa' if mobilidade_label == 'Alta' else 'moderada'}) → pressão de apreciação  \n"
                    "3. BC compra divisas → M↑ → LM desloca para direita  \n\n"
                    "🟢 **Resultado: Política EFICAZ**  \n"
                    "A intervenção do BC amplifica o efeito fiscal.  \n"
                    f"Quanto maior a mobilidade, maior a amplificação. Com mobilidade {mobilidade_label.lower()}, o efeito é {'forte' if mobilidade_label == 'Alta' else 'moderado'}."
                )
                delta_Y = "↑↑"; delta_r = "↑ (leve)"; delta_e = "fixo"

        elif aberta and flex and not fiscal and expansao:
            if mobilidade_label == "Perfeita":
                resultado = (
                    "**Transmissão A → B → C:**  \n"
                    "1. M↑ → LM desloca para direita → Y↑ e i↓ (Ponto B)  \n"
                    "2. i < r* → saída massiva de capital → **depreciação cambial (e↑)**  \n"
                    "3. e↑ → exportações barateiam, importações encarecem → **NX↑**  \n"
                    "4. NX↑ → IS desloca para direita → Y↑↑  \n\n"
                    "🟢 **Resultado: Política MUITO EFICAZ**  \n"
                    "O canal cambial amplifica completamente o estímulo monetário.  \n"
                    "**ΔY máximo**, i retorna a r*."
                )
                delta_Y = "↑↑↑ (máximo)"; delta_r = "↓ → r*"; delta_e = "↑↑ (depreciação forte)"
            else:
                resultado = (
                    "**Transmissão A → B → C:**  \n"
                    "1. M↑ → LM desloca para direita → Y↑ e i↓ (Ponto B)  \n"
                    f"2. i < r* → saída de capital ({'intensa' if mobilidade_label == 'Alta' else 'moderada'}) → depreciação (e↑)  \n"
                    "3. e↑ → NX↑ → IS desloca para direita  \n\n"
                    "🟢 **Resultado: Política EFICAZ**  \n"
                    "O canal cambial amplifica o efeito monetário.  \n"
                    f"Com mobilidade {mobilidade_label.lower()}, a amplificação é {'forte' if mobilidade_label == 'Alta' else 'moderada'}."
                )
                delta_Y = "↑↑"; delta_r = "↓"; delta_e = "↑ (depreciação)"

        elif aberta and not flex and not fiscal and expansao:
            if mobilidade_label == "Perfeita":
                resultado = (
                    "**Transmissão A → B → C:**  \n"
                    "1. M↑ → LM desloca para direita → i↓ (Ponto B)  \n"
                    "2. i < r* → saída massiva de capital → pressão de depreciação  \n"
                    "3. BC intervém: **vende divisas** para manter câmbio fixo → M↓  \n"
                    "4. M↓ → LM retorna exatamente à posição original  \n\n"
                    "🔴 **Resultado: Política COMPLETAMENTE INEFICAZ**  \n"
                    "A intervenção do BC reverte 100% do estímulo monetário.  \n"
                    "**ΔY = 0** — a LM retorna ao ponto de partida."
                )
                delta_Y = "≈ 0 (revertido pelo BC)"; delta_r = "≈ 0 (= r*)"; delta_e = "fixo"
            else:
                resultado = (
                    "**Transmissão A → B → C:**  \n"
                    "1. M↑ → LM desloca para direita → i↓ (Ponto B)  \n"
                    f"2. i < r* → saída de capital ({'intensa' if mobilidade_label == 'Alta' else 'moderada'}) → pressão de depreciação  \n"
                    "3. BC vende divisas → M↓ → LM recua  \n\n"
                    "🔴 **Resultado: Política INEFICAZ**  \n"
                    "A intervenção cambial neutraliza o estímulo monetário.  \n"
                    f"Com mobilidade {mobilidade_label.lower()}, a neutralização é {'quase total' if mobilidade_label == 'Alta' else 'parcial'}."
                )
                delta_Y = "≈ 0"; delta_r = "≈ 0"; delta_e = "fixo"

        elif aberta and flex and fiscal and not expansao:
            resultado = (
                "**Transmissão A → B → C (Contração Fiscal + Câmbio Flexível):**  \n"
                "1. G↓ → IS desloca para esquerda → Y↓ e i↓ (Ponto B)  \n"
                "2. i < r* → saída de capital → **depreciação cambial (e↑)**  \n"
                "3. e↑ → NX↑ → IS desloca para direita (parcialmente)  \n\n"
                f"🟡 **Resultado: Política PARCIALMENTE EFICAZ** (mobilidade {mobilidade_label})  \n"
                "A depreciação cambial atenua o efeito contracionista."
            )
            delta_Y = "↓ (atenuado pelo câmbio)"; delta_r = "↓"; delta_e = "↑ (depreciação)"

        elif aberta and not flex and fiscal and not expansao:
            resultado = (
                "**Transmissão A → B → C (Contração Fiscal + Câmbio Fixo):**  \n"
                "1. G↓ → IS desloca para esquerda → Y↓ e i↓ (Ponto B)  \n"
                "2. i < r* → saída de capital → pressão de depreciação  \n"
                "3. BC vende divisas → M↓ → LM desloca para esquerda → Y↓↓  \n\n"
                "🔴 **Resultado: Política MUITO EFICAZ** (no sentido contracionista)  \n"
                "O ajuste monetário endógeno amplifica a contração fiscal."
            )
            delta_Y = "↓↓ (amplificado)"; delta_r = "≈ 0 (= r*)"; delta_e = "fixo"

        elif aberta and flex and not fiscal and not expansao:
            resultado = (
                "**Transmissão A → B → C (Contração Monetária + Câmbio Flexível):**  \n"
                "1. M↓ → LM desloca para esquerda → i↑ (Ponto B)  \n"
                "2. i > r* → entrada de capital → **apreciação cambial (e↓)**  \n"
                "3. e↓ → NX↓ → IS desloca para esquerda → Y↓↓  \n\n"
                "🔴 **Resultado: Política MUITO EFICAZ** (no sentido contracionista)  \n"
                "O canal cambial amplifica a contração monetária."
            )
            delta_Y = "↓↓ (amplificado)"; delta_r = "↑ → r*"; delta_e = "↓ (apreciação)"

        elif aberta and not flex and not fiscal and not expansao:
            resultado = (
                "**Transmissão A → B → C (Contração Monetária + Câmbio Fixo):**  \n"
                "1. M↓ → LM desloca para esquerda → i↑ (Ponto B)  \n"
                "2. i > r* → entrada de capital → pressão de apreciação  \n"
                "3. BC compra divisas → M↑ → LM retorna à posição original  \n\n"
                "🔴 **Resultado: Política COMPLETAMENTE INEFICAZ**  \n"
                "O BC reverte 100% da contração monetária."
            )
            delta_Y = "≈ 0"; delta_r = "≈ 0 (= r*)"; delta_e = "fixo"

        elif fiscal and expansao:
            resultado = (
                "**Transmissão A → B → C (Economia Fechada):**  \n"
                "1. G↑ → IS desloca para direita → Y↑ (Ponto B)  \n"
                "2. Y↑ → demanda por moeda aumenta → i↑ ao longo da LM  \n"
                "3. i↑ → investimento privado cai **(crowding-out)**: I↓  \n\n"
                "🟡 **Resultado: Política PARCIALMENTE EFICAZ**  \n"
                "O aumento de Y é menor que o multiplicador keynesiano simples 1/(1−c₁)  \n"
                "porque o crowding-out reduz o investimento privado."
            )
            delta_Y = "↑ (< multiplicador simples)"; delta_r = "↑ (crowding-out)"; delta_e = "N/A"

        elif fiscal and not expansao:
            resultado = (
                "**Transmissão A → B → C (Economia Fechada):**  \n"
                "1. G↓ → IS desloca para esquerda → Y↓  \n"
                "2. Y↓ → demanda por moeda cai → i↓  \n"
                "3. i↓ → investimento privado aumenta (crowding-in parcial)  \n\n"
                "🟡 **Resultado: Política PARCIALMENTE EFICAZ** (contracionista)  \n"
                "O crowding-in atenua a queda do produto."
            )
            delta_Y = "↓ (atenuado pelo crowding-in)"; delta_r = "↓"; delta_e = "N/A"

        elif not fiscal and expansao:
            resultado = (
                "**Transmissão A → B → C (Economia Fechada):**  \n"
                "1. M↑ → LM desloca para direita → i↓  \n"
                "2. i↓ → investimento privado aumenta **(I↑)**  \n"
                "3. I↑ → demanda agregada sobe → Y↑  \n\n"
                "🟢 **Resultado: Política EFICAZ** (sem crowding-out)  \n"
                "A política monetária estimula o investimento sem pressionar os juros para cima."
            )
            delta_Y = "↑"; delta_r = "↓"; delta_e = "N/A"

        else:
            resultado = (
                "**Transmissão A → B → C (Economia Fechada):**  \n"
                "1. M↓ → LM desloca para esquerda → i↑  \n"
                "2. i↑ → investimento privado cai **(I↓)**  \n"
                "3. I↓ → demanda agregada cai → Y↓  \n\n"
                "🔴 **Resultado: Política EFICAZ** (no sentido contracionista)"
            )
            delta_Y = "↓"; delta_r = "↑"; delta_e = "N/A"

        blocos = [
            ("1. Mecanismo de Ajuste Completo (A → B → C)", resultado),

            ("2. Variações em relação ao Estado A",
             f"| Variável | Direção | Interpretação |\n"
             f"|---|---|---|\n"
             f"| **ΔY** | {delta_Y} | Variação no produto/renda |\n"
             f"| **Δi** | {delta_r} | Variação na taxa de juros |\n"
             + (f"| **Δe** | {delta_e} | Variação na taxa de câmbio |\n" if aberta else "")),

            ("3. Síntese Mundell-Fleming",
             "O modelo IS-LM-BP demonstra que a **eficácia das políticas econômicas depende criticamente de:**  \n\n"
             "| Fator | Impacto |\n"
             "|---|---|\n"
             "| Regime cambial (fixo vs. flexível) | Determina o canal de ajuste (LM ou IS) |\n"
             "| Grau de mobilidade de capital | Determina a velocidade e magnitude do ajuste |\n"
             "| Tipo de política (fiscal vs. monetária) | Interage com o regime cambial |\n\n"
             "**Regra geral de Mundell-Fleming:**  \n"
             "- Câmbio **Flexível** → Política **Monetária** eficaz, Fiscal ineficaz  \n"
             "- Câmbio **Fixo** → Política **Fiscal** eficaz, Monetária ineficaz"),
        ]

        if aberta:
            blocos.append((
                f"4. O papel da BP com mobilidade {mobilidade_label}",
                f"**Inclinação da BP:** {bp['inclinacao']}  \n\n"
                + bp["descricao"] + "  \n\n"
                f"**Mecanismo de ajuste com câmbio {regime.lower()}:**  \n\n"
                + (bp["ajuste_flex"] if flex else bp["ajuste_fixo"])
            ))

        return dict(titulo="✅ Estado C — Novo Equilíbrio", cor="green", blocos=blocos)


# ══════════════════════════════════════════════════════════════
# CAMADA DIDÁTICA — CONCLUSÃO (só aparece na Etapa C)
# ══════════════════════════════════════════════════════════════

def _conclusao_etapa(politica, direcao, tipo_eco, regime, mobilidade_label):
    fiscal   = politica == "Fiscal"
    expansao = direcao  == "Expansionista"
    aberta   = tipo_eco == "Aberta"
    flex     = regime   == "Flexível"

    COR_MAP = {
        "eficaz":   {"bg_light": "#f0fdf4", "bg_dark": "rgba(16,185,129,0.13)",
                     "border": "#059669",    "txt_light": "#064e3b", "txt_dark": "#6ee7b7"},
        "parcial":  {"bg_light": "#fefce8", "bg_dark": "rgba(234,179,8,0.13)",
                     "border": "#ca8a04",    "txt_light": "#713f12", "txt_dark": "#fde68a"},
        "ineficaz": {"bg_light": "#fef2f2", "bg_dark": "rgba(220,38,38,0.13)",
                     "border": "#dc2626",    "txt_light": "#7f1d1d", "txt_dark": "#fca5a5"},
    }

    if not aberta:
        if fiscal:
            veredicto = "parcial"; emoji = "🟡"
            titulo = "Política Fiscal — Parcialmente Eficaz (Economia Fechada)"
            razao = (
                "A política fiscal **aumentou o produto (Y↑)**, mas o efeito foi **atenuado pelo crowding-out**: "
                "o aumento dos gastos públicos elevou a demanda por moeda, pressionando os juros para cima (i↑), "
                "o que reduziu o investimento privado (I↓). "
                "O resultado líquido é um ΔY **menor** do que o multiplicador keynesiano simples 1/(1−c₁) preveria."
            )
            canal = "Canal dominante: **Demanda Agregada → Mercado Monetário → Crowding-Out de Investimento**"
            contrafactual = (
                "Se a economia fosse **aberta com câmbio fixo e alta mobilidade**, "
                "a política fiscal seria ainda mais eficaz — a LM se expandiria endogenamente via entrada de capital.  \n"
                "Se fosse **aberta com câmbio flexível e mobilidade perfeita**, "
                "seria completamente ineficaz — o crowding-out externo cancelaria todo o estímulo."
            )
            licao = "📌 Em economia fechada, a política fiscal sempre enfrenta crowding-out parcial via mercado monetário."
        else:
            veredicto = "eficaz"; emoji = "🟢"
            titulo = "Política Monetária — Eficaz (Economia Fechada)"
            razao = (
                "A política monetária **aumentou o produto (Y↑) e reduziu os juros (i↓)** sem crowding-out. "
                "A expansão da oferta de moeda reduziu o custo do crédito, estimulando o investimento privado (I↑), "
                "que elevou a demanda agregada e o produto. "
                "Não há conflito com o mercado de bens — IS e LM se movem na mesma direção."
            )
            canal = "Canal dominante: **Oferta de Moeda → Taxa de Juros → Investimento → Produto**"
            contrafactual = (
                "Se a economia fosse **aberta com câmbio fixo**, "
                "a política monetária seria completamente ineficaz — o BC seria forçado a reverter a expansão para defender o câmbio.  \n"
                "Se fosse **aberta com câmbio flexível**, "
                "seria ainda mais eficaz — a depreciação cambial amplificaria o estímulo via NX↑."
            )
            licao = "📌 Em economia fechada, a política monetária é o instrumento mais eficiente — sem crowding-out."

    elif flex and fiscal and expansao:
        if mobilidade_label == "Perfeita":
            veredicto = "ineficaz"; emoji = "🔴"
            titulo = "Política Fiscal Expansionista — INEFICAZ (Câmbio Flexível + Mobilidade Perfeita)"
            razao = (
                "A política fiscal foi **completamente neutralizada pelo crowding-out externo**. "
                "O aumento de G elevou os juros acima de r*, atraindo capital estrangeiro e apreciando a moeda (e↓). "
                "A apreciação reduziu as exportações líquidas (NX↓) na **exata mesma magnitude** do estímulo fiscal, "
                "fazendo a IS retornar à posição original. **ΔY ≈ 0.**"
            )
            canal = "Canal dominante: **Juros → Entrada de Capital → Apreciação Cambial → NX↓ → IS recua**"
            contrafactual = (
                "Se o regime fosse **câmbio fixo**, a mesma política seria muito eficaz: "
                "a entrada de capital forçaria o BC a expandir M, amplificando o estímulo fiscal.  \n"
                "Se a mobilidade fosse **baixa ou nula**, o crowding-out externo seria parcial "
                "e Y aumentaria significativamente."
            )
            licao = "📌 Mundell-Fleming: câmbio flexível + mobilidade perfeita → política fiscal completamente ineficaz."
        elif mobilidade_label == "Alta":
            veredicto = "parcial"; emoji = "🟡"
            titulo = "Política Fiscal Expansionista — Parcialmente Ineficaz (Câmbio Flexível + Alta Mobilidade)"
            razao = (
                "A política fiscal teve **efeito muito limitado** sobre o produto. "
                "O crowding-out externo foi intenso: a entrada de capital apreciou a moeda (e↓), "
                "reduzindo NX e fazendo a IS recuar parcialmente. "
                "Y aumentou levemente, mas muito abaixo do multiplicador keynesiano simples."
            )
            canal = "Canal dominante: **Juros → Entrada de Capital → Apreciação → NX↓ → IS recua (parcialmente)**"
            contrafactual = (
                "Com **mobilidade perfeita**, o efeito seria zero (crowding-out 100%).  \n"
                "Com **mobilidade baixa ou nula**, o canal cambial seria fraco e Y aumentaria mais."
            )
            licao = "📌 Quanto maior a mobilidade de capital com câmbio flexível, menor a eficácia da política fiscal."
        else:
            veredicto = "eficaz"; emoji = "🟢"
            titulo = "Política Fiscal Expansionista — Eficaz (Câmbio Flexível + Baixa/Nula Mobilidade)"
            razao = (
                "Com baixa mobilidade de capital, o canal financeiro externo é fraco. "
                "O crowding-out externo é **mínimo**: a apreciação cambial é pequena e NX cai pouco. "
                "O estímulo fiscal se transmite quase integralmente ao produto (Y↑↑), "
                "próximo ao multiplicador keynesiano."
            )
            canal = "Canal dominante: **Demanda Agregada → Produto** (canal cambial fraco)"
            contrafactual = (
                "Com **alta mobilidade**, o crowding-out externo seria intenso e Y aumentaria pouco.  \n"
                "Com **câmbio fixo**, a política seria ainda mais eficaz — a LM se expandiria endogenamente."
            )
            licao = "📌 Com baixa mobilidade de capital, a política fiscal recupera sua eficácia mesmo com câmbio flexível."

    elif not flex and fiscal and expansao:
        veredicto = "eficaz"; emoji = "🟢"
        titulo = "Política Fiscal Expansionista — Muito Eficaz (Câmbio Fixo)"
        razao = (
            "A política fiscal foi **amplificada pelo ajuste monetário endógeno**. "
            "O aumento de G elevou os juros, atraindo capital estrangeiro. "
            "Para defender o câmbio fixo, o BC comprou divisas, expandindo a oferta de moeda (M↑). "
            "A LM deslocou-se para a direita, reduzindo os juros e amplificando o estímulo fiscal. "
            f"Com mobilidade **{mobilidade_label.lower()}**, a amplificação foi "
            f"{'máxima' if mobilidade_label == 'Perfeita' else 'significativa'}."
        )
        canal = "Canal dominante: **G↑ → i↑ → Entrada de Capital → BC compra divisas → M↑ → LM↓ → Y↑↑**"
        contrafactual = (
            "Se o regime fosse **câmbio flexível**, a política seria ineficaz (com alta mobilidade) "
            "ou apenas parcialmente eficaz (com baixa mobilidade) — "
            "pois a apreciação cambial reduziria NX e faria a IS recuar."
        )
        licao = "📌 Mundell-Fleming: câmbio fixo → política fiscal eficaz, independentemente da mobilidade de capital."

    elif flex and not fiscal and expansao:
        if mobilidade_label == "Perfeita":
            veredicto = "eficaz"; emoji = "🟢"
            titulo = "Política Monetária Expansionista — MUITO Eficaz (Câmbio Flexível + Mobilidade Perfeita)"
            razao = (
                "A política monetária foi **amplificada ao máximo pelo canal cambial**. "
                "A expansão de M reduziu os juros abaixo de r*, provocando saída massiva de capital "
                "e forte depreciação cambial (e↑). "
                "A depreciação elevou as exportações líquidas (NX↑), deslocando a IS para a direita. "
                "O produto aumentou muito além do efeito direto da expansão monetária. **ΔY máximo.**"
            )
            canal = "Canal dominante: **M↑ → i↓ → Saída de Capital → Depreciação (e↑) → NX↑ → IS↑ → Y↑↑**"
            contrafactual = (
                "Se o regime fosse **câmbio fixo**, a política seria completamente ineficaz: "
                "o BC reverteria toda a expansão monetária para defender o câmbio."
            )
            licao = "📌 Mundell-Fleming: câmbio flexível + mobilidade perfeita → política monetária maximamente eficaz."
        else:
            veredicto = "eficaz"; emoji = "🟢"
            titulo = f"Política Monetária Expansionista — Eficaz (Câmbio Flexível + Mobilidade {mobilidade_label})"
            razao = (
                "A política monetária foi **eficaz e amplificada pelo canal cambial**. "
                "A queda dos juros gerou saída de capital e depreciação (e↑), "
                "elevando NX e deslocando a IS para a direita. "
                f"Com mobilidade **{mobilidade_label.lower()}**, a amplificação cambial foi "
                f"{'forte' if mobilidade_label == 'Alta' else 'moderada'}."
            )
            canal = "Canal dominante: **M↑ → i↓ → Depreciação → NX↑ → IS↑ → Y↑**"
            contrafactual = (
                "Com **mobilidade perfeita**, o efeito seria ainda maior.  \n"
                "Com **câmbio fixo**, a política seria completamente neutralizada pelo BC."
            )
            licao = "📌 Com câmbio flexível, a política monetária é sempre eficaz — e mais eficaz quanto maior a mobilidade."

    elif not flex and not fiscal and expansao:
        veredicto = "ineficaz"; emoji = "🔴"
        titulo = "Política Monetária Expansionista — INEFICAZ (Câmbio Fixo)"
        razao = (
            "A política monetária foi **completamente neutralizada pela defesa do câmbio fixo**. "
            "A expansão de M reduziu os juros abaixo de r*, provocando saída de capital "
            "e pressão de depreciação cambial. "
            "Para defender o câmbio, o BC vendeu reservas, contraindo a oferta de moeda (M↓). "
            "A LM retornou à posição original. **ΔY ≈ 0.**"
        )
        canal = "Canal dominante: **M↑ → i↓ → Saída de Capital → BC vende divisas → M↓ → LM retorna**"
        contrafactual = (
            "Se o regime fosse **câmbio flexível**, a política seria muito eficaz: "
            "a depreciação cambial amplificaria o estímulo via NX↑.  \n"
            "Com câmbio fixo, **apenas a política fiscal** tem poder de alterar o produto."
        )
        licao = "📌 Mundell-Fleming: câmbio fixo → política monetária completamente ineficaz."

    elif flex and fiscal and not expansao:
        veredicto = "parcial"; emoji = "🟡"
        titulo = "Política Fiscal Contracionista — Parcialmente Eficaz (Câmbio Flexível)"
        razao = (
            "A contração fiscal reduziu o produto (Y↓), mas o efeito foi **atenuado pela depreciação cambial**. "
            "A queda dos juros gerou saída de capital e depreciação (e↑), "
            "elevando NX e fazendo a IS recuar menos do que o esperado. "
            "O resultado líquido é uma queda de Y menor do que o multiplicador simples preveria."
        )
        canal = "Canal dominante: **G↓ → i↓ → Depreciação → NX↑ → IS recua menos**"
        contrafactual = (
            "Com **câmbio fixo**, a contração seria amplificada: "
            "a saída de capital forçaria o BC a contrair M, reduzindo Y ainda mais."
        )
        licao = "📌 Com câmbio flexível, o câmbio atua como amortecedor automático de choques fiscais."

    elif not flex and fiscal and not expansao:
        veredicto = "ineficaz"; emoji = "🔴"
        titulo = "Política Fiscal Contracionista — Amplificada (Câmbio Fixo)"
        razao = (
            "A contração fiscal foi **amplificada pelo ajuste monetário endógeno**. "
            "A queda dos juros gerou saída de capital e pressão de depreciação. "
            "O BC vendeu reservas para defender o câmbio, contraindo M (M↓). "
            "A LM deslocou-se para a esquerda, amplificando a queda do produto. **ΔY↓↓.**"
        )
        canal = "Canal dominante: **G↓ → i↓ → Saída de Capital → BC vende divisas → M↓ → LM↑ → Y↓↓**"
        contrafactual = (
            "Com **câmbio flexível**, a depreciação cambial atenuaria a contração — "
            "NX↑ compensaria parcialmente a queda da demanda interna."
        )
        licao = "📌 Com câmbio fixo, a política fiscal contracionista é amplificada — o BC retira moeda para defender o câmbio."

    elif flex and not fiscal and not expansao:
        veredicto = "ineficaz"; emoji = "🔴"
        titulo = "Política Monetária Contracionista — Amplificada (Câmbio Flexível)"
        razao = (
            "A contração monetária foi **amplificada pelo canal cambial**. "
            "A alta dos juros atraiu capital estrangeiro e apreciou a moeda (e↓). "
            "A apreciação reduziu NX, deslocando a IS para a esquerda. "
            "O produto caiu mais do que o efeito direto da contração monetária. **ΔY↓↓.**"
        )
        canal = "Canal dominante: **M↓ → i↑ → Entrada de Capital → Apreciação → NX↓ → IS↓ → Y↓↓**"
        contrafactual = (
            "Com **câmbio fixo**, a contração seria completamente revertida pelo BC — "
            "a entrada de capital forçaria expansão de M para defender o câmbio."
        )
        licao = "📌 Com câmbio flexível, a política monetária contracionista é amplificada pelo canal cambial."

    else:
        veredicto = "eficaz"; emoji = "🟢"
        titulo = "Política Monetária Contracionista — Revertida (Câmbio Fixo)"
        razao = (
            "A contração monetária foi **completamente revertida pela defesa do câmbio fixo**. "
            "A alta dos juros atraiu capital estrangeiro e pressionou o câmbio para apreciar. "
            "O BC comprou divisas para manter o câmbio fixo, expandindo M (M↑). "
            "A LM retornou à posição original. **ΔY ≈ 0.**"
        )
        canal = "Canal dominante: **M↓ → i↑ → Entrada de Capital → BC compra divisas → M↑ → LM retorna**"
        contrafactual = (
            "Com **câmbio flexível**, a contração seria amplificada: "
            "a apreciação cambial reduziria NX e faria Y cair ainda mais."
        )
        licao = "📌 Com câmbio fixo, a política monetária contracionista também é ineficaz — o BC reverte o movimento."

    cores = COR_MAP[veredicto]
    return dict(
        veredicto=veredicto, emoji=emoji, titulo=titulo,
        razao=razao, canal=canal, contrafactual=contrafactual,
        licao=licao, cores=cores,
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

st.markdown('<div class="main-title"> IS-LM-BP — Simulador Macroeconômico</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Modelo Mundell-Fleming &nbsp;|&nbsp; Economia Aberta &nbsp;|&nbsp; Economia Fechada </div>', unsafe_allow_html=True)
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

            if etapa == 2:
                conc = _conclusao_etapa(politica_s, direcao_s, tipo_eco_s, regime_s, mob_s)
                c = conc["cores"]
                st.markdown("---")
                st.markdown(
                    f'<style>'
                    f'#conc-card {{ background:{c["bg_light"]}; border-left:5px solid {c["border"]}; '
                    f'border-radius:10px; padding:18px 20px; font-family:"EB Garamond",Georgia,serif; margin-top:8px; }}'
                    f'#conc-card .conc-title {{ color:{c["txt_light"]}; font-size:1.15rem; font-weight:700; }}'
                    f'@media (prefers-color-scheme: dark) {{'
                    f'  #conc-card {{ background:{c["bg_dark"]}; }}'
                    f'  #conc-card .conc-title {{ color:{c["txt_dark"]}; }}'
                    f'}}'
                    f'</style>'
                    f'<div id="conc-card">'
                    f'<span class="conc-title">{conc["emoji"]} Conclusão — {conc["titulo"]}</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )
                st.markdown("")
                with st.expander("📝 Por que a política foi (in)eficaz?", expanded=True):
                    st.markdown(conc["razao"])
                with st.expander("🔗 Canal econômico dominante", expanded=True):
                    st.markdown(conc["canal"])
                with st.expander("🔄 E se fosse diferente? (Contrafactual)", expanded=False):
                    st.markdown(conc["contrafactual"])
                st.markdown(
                    f'<div style="margin-top:10px; padding:10px 14px; border-radius:6px; '
                    f'background:{c["bg_light"]}; border:1px solid {c["border"]}; '
                    f'font-family:\'Poppins\',sans-serif; font-size:0.9rem; color:{c["txt_light"]};">'
                    f'{conc["licao"]}'
                    f'</div>',
                    unsafe_allow_html=True
                )

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