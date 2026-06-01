# ui/islmbp/nucleo.py
"""
Núcleo econômico do modelo IS-LM-BP (Mundell-Fleming).
Solvers numéricos e funções de comportamento.
"""

import numpy as np

try:
    from scipy.optimize import fsolve
    SCIPY_OK = True
except ImportError:
    SCIPY_OK = False


# ══════════════════════════════════════════════════════════════
# FUNÇÕES DE COMPORTAMENTO
# ══════════════════════════════════════════════════════════════

def consumo(c0, c1, Y, T):
    return c0 + c1 * (Y - T)

def investimento(I0, b, r):
    return I0 - b * r

def exportacoes(x0, x1, Y_star, e):
    return x0 + x1 * Y_star * e

def importacoes(m0, m1, Y, e):
    return m0 + m1 * Y / max(e, 1e-9)

def balanca_comercial(x0, x1, Y_star, m0, m1, Y, e):
    return exportacoes(x0, x1, Y_star, e) - importacoes(m0, m1, Y, e)

def fluxo_capital(kf, r, r_star):
    return kf * (r - r_star)


# ══════════════════════════════════════════════════════════════
# EQUAÇÕES DE EQUILÍBRIO
# ══════════════════════════════════════════════════════════════

def eq_IS(Y, r, e, p):
    C  = consumo(p["c0"], p["c1"], Y, p["T"])
    I  = investimento(p["I0"], p["b"], r)
    nx = balanca_comercial(p["x0"], p["x1"], p["Y_star"],
                           p["m0"], p["m1"], Y, e) if p.get("aberta") else 0.0
    return Y - C - I - p["G"] - nx

def eq_LM(Y, r, M, p):
    return M / p["P"] - p["k"] * Y + p["h"] * r

def eq_BP(Y, r, e, p):
    nx = balanca_comercial(p["x0"], p["x1"], p["Y_star"], p["m0"], p["m1"], Y, e)
    cf = fluxo_capital(p["kf"], r, p["r_star"])
    return nx + cf


# ══════════════════════════════════════════════════════════════
# SOLVER NEWTON-RAPHSON
# ══════════════════════════════════════════════════════════════

def newton_solve(F, x0, tol=1e-10, max_iter=500):
    x = np.array(x0, dtype=float)
    for _ in range(max_iter):
        fx = np.array(F(x), dtype=float)
        if np.max(np.abs(fx)) < tol:
            return x, True
        n  = len(x)
        J  = np.zeros((n, n))
        dx = 1e-6
        for j in range(n):
            xp = x.copy(); xp[j] += dx
            J[:, j] = (np.array(F(xp)) - fx) / dx
        try:
            delta = np.linalg.solve(J, -fx)
        except Exception:
            return x, False
        x = x + delta
    return x, False


# ══════════════════════════════════════════════════════════════
# SOLVERS POR REGIME
# ══════════════════════════════════════════════════════════════

def solve_flex(p):
    """Câmbio flexível: resolve Y, r, e simultaneamente."""
    def F(v):
        Y, r, e = v
        return [eq_IS(Y, r, e, p), eq_LM(Y, r, p["M"], p), eq_BP(Y, r, e, p)]

    x0  = [p.get("Yn", 1200.), p["r_star"], p.get("e", 1.)]
    sol, ok = newton_solve(F, x0)
    if not ok and SCIPY_OK:
        sol = fsolve(F, sol)
    return _resultado(*sol, p, "flex")


def solve_fixo(p):
    """Câmbio fixo: resolve Y, r, M_eq (M endógeno)."""
    e = p.get("e_fixed", 1.0)

    def F(v):
        Y, r, M_eq = v
        return [eq_IS(Y, r, e, p), eq_LM(Y, r, M_eq, p), eq_BP(Y, r, e, p)]

    x0  = [p.get("Yn", 1200.), p["r_star"], p["M"]]
    sol, ok = newton_solve(F, x0)
    if not ok and SCIPY_OK:
        sol = fsolve(F, sol)
    Y, r, M_eq = sol
    return _resultado(Y, r, e, p, "fixo", M_eq=M_eq)


def solve_fechada(p):
    """Economia fechada: IS-LM analítico."""
    A = np.array([[1 - p["c1"], p["b"]], [p["k"], -p["h"]]])
    B = np.array([
        p["c0"] - p["c1"] * p["T"] + p["I0"] + p["G"],
        p["M"] / p["P"],
    ])
    try:
        Y, r = np.linalg.solve(A, B)
    except Exception:
        Y, r = p.get("Yn", 1200.), p["r_star"]
    return _resultado(Y, r, p.get("e", 1.), p, "fechada")


def _resultado(Y, r, e, p, regime, M_eq=None):
    C   = consumo(p["c0"], p["c1"], Y, p["T"])
    I   = investimento(p["I0"], p["b"], r)
    nx  = balanca_comercial(p["x0"], p["x1"], p["Y_star"],
                            p["m0"], p["m1"], Y, e) if p.get("aberta") else 0.
    cf  = fluxo_capital(p["kf"], r, p["r_star"]) if p.get("aberta") else 0.
    Mu  = M_eq if M_eq is not None else p["M"]
    return dict(
        Y=Y, r=r, e=e, C=C, I=I,
        NX=nx, CF=cf, BP=nx + cf, M_eq=Mu, regime=regime,
        IS_res=Y - C - I - p["G"] - nx,
        LM_res=Mu / p["P"] - p["k"] * Y + p["h"] * r,
        BP_res=nx + cf if p.get("aberta") else 0.,
    )


# ══════════════════════════════════════════════════════════════
# CURVAS PARA PLOTAGEM
# ══════════════════════════════════════════════════════════════

def curva_IS(Y_grid, e, p, aberta=True):
    r_vals = []
    for Y in Y_grid:
        nx = balanca_comercial(p["x0"], p["x1"], p["Y_star"],
                               p["m0"], p["m1"], Y, e) if aberta else 0.
        A  = p["c0"] - p["c1"] * p["T"] + p["I0"] + p["G"] + nx
        r_vals.append((A - (1 - p["c1"]) * Y) / max(p["b"], 1e-9))
    return np.array(r_vals)


def curva_LM(Y_grid, M, p):
    return (p["k"] * Y_grid - M / p["P"]) / max(p["h"], 1e-9)


def curva_BP(Y_grid, e, p, Y_anchor=None, r_anchor=None):
    """Curva BP para plotagem — slope calibrado pela mobilidade kf."""
    kf     = p.get("kf", 80.)
    r_star = p.get("r_star", 0.05)

    # Mobilidade perfeita → horizontal
    if kf >= 1e6:
        return np.full_like(Y_grid, r_star, dtype=float)

    if Y_anchor is None:
        Y_anchor = float(np.mean(Y_grid))
    if r_anchor is None:
        r_anchor = r_star

    # Slope inversamente proporcional à mobilidade
    slope = 1.0 / (max(kf, 1e-6) ** 0.6)
    return r_anchor + slope * (Y_grid - Y_anchor)


def multiplas_bp(Y_grid, Y_anchor, r_anchor):
    """
    Retorna as 4 curvas BP canônicas (Nula, Baixa, Alta, Perfeita)
    para exibição comparativa no modo complexo.
    """
    slopes = {
        "Nula (vertical)":   None,          # tratada separadamente
        "Baixa (íngreme)":   1.8,
        "Alta (suave)":      0.25,
        "Perfeita (horiz.)": 0.0,
    }
    result = {}
    for label, slope in slopes.items():
        if slope is None:
            result[label] = None   # linha vertical em Y_anchor
        elif slope == 0.0:
            result[label] = np.full_like(Y_grid, r_anchor, dtype=float)
        else:
            result[label] = r_anchor + slope * (Y_grid - Y_anchor)
    return result