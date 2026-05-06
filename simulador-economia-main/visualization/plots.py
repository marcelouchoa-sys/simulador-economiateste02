import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from models.islm import solve_islm

# ============================================================
# Helpers de Cálculo
# ============================================================
def _get_c(p):
    return p.get("c1", p.get("c", 0.8))

def _calc_price(eq, p):
    Yn = p.get("Yn", eq["Y"])
    Pe = p.get("Pe", 1.0)
    alpha = p.get("alpha", 100.0)
    if alpha == 0: alpha = 1.0
    return Pe + (eq["Y"] - Yn) / alpha

def _calc_unemployment(eq, p):
    un = p.get("un", 0.05)
    lambda_ = p.get("lambda", 0.5)
    Yn = p.get("Yn", eq["Y"])
    gap = (eq["Y"] - Yn) / Yn if Yn != 0 else 0.0
    return max(0.0, un - lambda_ * gap)

def _calc_inflation(P, Pe):
    return (P / Pe - 1.0) if Pe != 0 else 0.0

def _is_curve(p, y_grid):
    c = _get_c(p)
    b = p.get("b", 50.0)
    c0 = p.get("c0", 100.0)
    I0 = p.get("I0", 150.0)
    G = p.get("G", 200.0)
    T = p.get("T", 100.0)
    if abs(b) < 1e-9: b = 1e-9
    A = c0 - c * T + I0 + G
    r_grid = (A - (1 - c) * y_grid) / b
    return y_grid, r_grid

def _lm_curve(p, y_grid, price_level):
    k = p.get("k", 0.5)
    h = p.get("h", 100.0)
    M = p.get("M", 500.0)
    if abs(h) < 1e-9: h = 1e-9
    if abs(price_level) < 1e-9: price_level = 1e-9
    r_grid = (k * y_grid - M / price_level) / h
    return y_grid, r_grid

def _bp_curve(p, y_grid):
    r_world = p.get("r_world", 0.03)
    kf = p.get("kf", 50.0)
    m = p.get("m", 0.2)
    if abs(kf) < 1e-9: kf = 1e-9
    r_grid = r_world + (m / kf) * y_grid
    return y_grid, r_grid

def _ad_curve(p, p_grid):
    c = _get_c(p)
    b = p.get("b", 50.0)
    k = p.get("k", 0.5)
    h = p.get("h", 100.0)
    M = p.get("M", 500.0)
    c0 = p.get("c0", 100.0)
    I0 = p.get("I0", 150.0)
    G = p.get("G", 200.0)
    T = p.get("T", 100.0)
    A = c0 - c * T + I0 + G
    mult = 1.0 / max(1e-9, (1 - c))
    denom = 1.0 + mult * b * k / max(h, 1e-9)
    y_vals = [(mult * A + mult * b * M / (h * max(P, 1e-9))) / denom for P in p_grid]
    return np.array(y_vals), p_grid

def _as_curve(p, y_grid):
    Pe = p.get("Pe", 1.0)
    Yn = p.get("Yn", 1000.0)
    alpha = p.get("alpha", 100.0)
    if abs(alpha) < 1e-9: alpha = 1e-9
    p_grid = Pe + (y_grid - Yn) / alpha
    return y_grid, p_grid

def _phillips_curve(p, u_grid):
    un = p.get("un", 0.05)
    beta = p.get("beta", 1.0)
    pi_e = p.get("pi_e", 0.02)
    pi_grid = pi_e - beta * (u_grid - un)
    return u_grid, pi_grid

# ============================================================
# Helpers de Estilização
# ============================================================
def _add_equilibrium_guides(fig, x, y, row, col, color, showlegend=False, name="Equilíbrio", label_x=None, label_y=None):
    """Adiciona marcador e linhas de projeção pontilhadas até os eixos."""
    fig.add_trace(
        go.Scatter(x=[x], y=[y], mode="markers", 
                   marker=dict(size=10, color=color, line=dict(color="white", width=1)),
                   name=name, showlegend=showlegend),
        row=row, col=col
    )
    # Projeções Horizontal e Vertical
    fig.add_shape(type="line", x0=0, x1=x, y0=y, y1=y, line=dict(color=color, width=1, dash="dot"), row=row, col=col)
    fig.add_shape(type="line", x0=x, x1=x, y0=0, y1=y, line=dict(color=color, width=1, dash="dot"), row=row, col=col)

    if label_x:
        fig.add_annotation(x=x, y=0, text=label_x, showarrow=False, yanchor="top", yshift=-5,
                           font=dict(color=color, size=12, family="serif"), row=row, col=col)
    if label_y:
        fig.add_annotation(x=0, y=y, text=label_y, showarrow=False, xanchor="right", xshift=-5,
                           font=dict(color=color, size=12, family="serif"), row=row, col=col)

def _add_arrow(fig, x0, y0, x1, y1, row, col, color):
    fig.add_annotation(
        x=x1, y=y1, ax=x0, ay=y0, xref=f"x{col}", yref=f"y{col}",
        axref=f"x{col}", ayref=f"y{col}", showarrow=True, arrowhead=3,
        arrowsize=1.2, arrowwidth=2, arrowcolor=color
    )

# ============================================================
# Função Principal do Dashboard
# ============================================================
def build_comparison_dashboard(
    p_base, p_shock, modo_simplificado=False, show_bp=True, show_arrows=True, 
    show_grid=True, color_base="#1565c0", color_shock="#c62828", color_bp="#2e7d32", 
    line_width=2, show_islm=True, show_adas=True, show_phillips=True, bp_b=None, bp_s=None
):
    # Solução dos modelos
    eq_b = solve_islm(p_base)
    eq_s = solve_islm(p_shock)

    P_b = _calc_price(eq_b, p_base)
    P_s = _calc_price(eq_s, p_shock)

    u_b = _calc_unemployment(eq_b, p_base)
    u_s = _calc_unemployment(eq_s, p_shock)

    pi_b = _calc_inflation(P_b, p_base.get("Pe", 1.0))
    pi_s = _calc_inflation(P_s, p_shock.get("Pe", 1.0))

    y_max = max(eq_b["Y"], eq_s["Y"]) * 1.5
    y_grid = np.linspace(1.0, y_max, 250)

    fig = make_subplots(rows=1, cols=3, subplot_titles=("IS-LM-BP", "AD-AS", "Curva de Phillips"), horizontal_spacing=0.08)

    # 1) Bloco IS-LM-BP
    if show_islm:
        y_is_b, r_is_b = _is_curve(p_base, y_grid)
        y_is_s, r_is_s = _is_curve(p_shock, y_grid)
        y_lm_b, r_lm_b = _lm_curve(p_base, y_grid, P_b)
        y_lm_s, r_lm_s = _lm_curve(p_shock, y_grid, P_s)

        fig.add_trace(go.Scatter(x=y_is_b, y=r_is_b, mode="lines", line=dict(color=color_base, width=line_width), name="IS Base"), 1, 1)
        fig.add_trace(go.Scatter(x=y_lm_b, y=r_lm_b, mode="lines", line=dict(color=color_base, width=line_width, dash="dot"), name="LM Base"), 1, 1)
        fig.add_trace(go.Scatter(x=y_is_s, y=r_is_s, mode="lines", line=dict(color=color_shock, width=line_width), name="IS Choque"), 1, 1)
        fig.add_trace(go.Scatter(x=y_lm_s, y=r_lm_s, mode="lines", line=dict(color=color_shock, width=line_width, dash="dot"), name="LM Choque"), 1, 1)

        if show_bp:
            y_bp_b, r_bp_b = _bp_curve(p_base, y_grid)
            fig.add_trace(go.Scatter(x=y_bp_b, y=r_bp_b, mode="lines", line=dict(color=color_bp, width=line_width, dash="dash"), name="BP Base"), 1, 1)

        # Configuração qualitativa vs quantitativa
        lx_a, ly_a = ("Y<sub>a</sub>", "i<sub>a</sub>") if modo_simplificado else (None, None)
        lx_c, ly_c = ("Y<sub>c</sub>", "i<sub>c</sub>") if modo_simplificado else (None, None)

        _add_equilibrium_guides(fig, eq_b["Y"], eq_b["r"], 1, 1, color_base, True, "Início (A)", lx_a, ly_a)
        _add_equilibrium_guides(fig, eq_s["Y"], eq_s["r"], 1, 1, color_shock, True, "Final (C)", lx_c, ly_c)

        if modo_simplificado:
            # Marcação de pontos A e C
            fig.add_annotation(x=eq_b["Y"], y=eq_b["r"], text="<b>A</b>", showarrow=False, yshift=15, font=dict(size=14, color=color_base), row=1, col=1)
            fig.add_annotation(x=eq_s["Y"], y=eq_s["r"], text="<b>C</b>", showarrow=False, yshift=15, font=dict(size=14, color=color_shock), row=1, col=1)
            
            # Lógica para o Ponto B (Desequilíbrio transitório conforme PDF)[cite: 1]
            if p_shock.get("G", 0) > p_base.get("G", 0) or p_shock.get("T", 0) < p_base.get("T", 0): # Fiscal Expansionista
                fig.add_annotation(x=eq_s["Y"], y=eq_b["r"], text="<b>B</b>", showarrow=False, xshift=10, font=dict(size=14, color="orange"), row=1, col=1)

        if show_arrows:
            _add_arrow(fig, eq_b["Y"], eq_b["r"], eq_s["Y"], eq_s["r"], 1, 1, "#2e7d32")

    # 2) Bloco AD-AS
    if show_adas:
        p_grid = np.linspace(0.2, 2.5, 250)
        y_ad_b, p_ad_b = _ad_curve(p_base, p_grid)
        y_as_b, p_as_b = _as_curve(p_base, y_grid)
        fig.add_trace(go.Scatter(x=y_ad_b, y=p_ad_b, mode="lines", line=dict(color=color_base, width=line_width), name="AD Base"), 1, 2)
        fig.add_trace(go.Scatter(x=y_as_b, y=p_as_b, mode="lines", line=dict(color=color_base, width=line_width, dash="dot"), name="AS Base"), 1, 2)
        _add_equilibrium_guides(fig, eq_b["Y"], P_b, 1, 2, color_base)

    # 3) Bloco Phillips
    if show_phillips:
        u_grid = np.linspace(0.0, 0.15, 250)
        u_pc_b, pi_pc_b = _phillips_curve(p_base, u_grid)
        fig.add_trace(go.Scatter(x=u_grid * 100, y=pi_pc_b * 100, mode="lines", line=dict(color=color_base, width=line_width), name="PC Base"), 1, 3)
        _add_equilibrium_guides(fig, u_b * 100, pi_b * 100, 1, 3, color_base)

    # Layout Final e Travas de Eixo
    r_max = max(eq_b["r"], eq_s["r"]) * 1.5
    
    # Eixos IS-LM (Coluna 1) ajustados conforme o modo[cite: 1]
    fig.update_xaxes(title_text="Produto (Y)", row=1, col=1, range=[0, y_max], 
                     showticklabels=not modo_simplificado, showgrid=not modo_simplificado)
    fig.update_yaxes(title_text="Juros (i)", row=1, col=1, range=[0, r_max], 
                     showticklabels=not modo_simplificado, showgrid=not modo_simplificado)

    # Eixos AD-AS e Phillips (Colunas 2 e 3) sempre quantitativos
    fig.update_xaxes(title_text="Produto (Y)", row=1, col=2, showgrid=show_grid)
    fig.update_yaxes(title_text="Preços (P)", row=1, col=2, showgrid=show_grid)
    fig.update_xaxes(title_text="Desemprego (u%)", row=1, col=3, showgrid=show_grid)
    fig.update_yaxes(title_text="Inflação (π%)", row=1, col=3, showgrid=show_grid)

    fig.update_layout(height=600, template="plotly_white", showlegend=True,
                      margin=dict(l=50, r=30, t=100, b=50),
                      title=dict(text="Simulador Macroeconômico: Trajetória de Equilíbrio", x=0.5))

    return fig