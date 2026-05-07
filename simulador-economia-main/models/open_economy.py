# models/open_economy.py

import numpy as np

# ─────────────────────────────────────────────
# EXPORTAÇÕES LÍQUIDAS (NX)
# ─────────────────────────────────────────────
def exportacoes_liquidas(Y, e, x0, x1, m0, m1):
    """
    NX = X - M

    X = x0 + x1*e
    M = m0 + m1*Y

    Logo:
    NX = x0 + x1*e - m0 - m1*Y
    """
    return x0 + x1 * e - m0 - m1 * Y


# ─────────────────────────────────────────────
# CURVA IS (aberta)
# ─────────────────────────────────────────────
def curva_IS(Y, p, e):
    """
    Retorna r como função de Y

    Equilíbrio:
    Y = C + I + G + NX

    C = c0 + c1(Y - T)
    I = I0 - b*r
    NX = x0 + x1*e - m0 - m1*Y
    """

    c0, c1 = p["c0"], p["c1"]
    T = p["T"]
    I0, b = p["I0"], p["b"]
    G = p["G"]

    x0, x1 = p["x0"], p["x1"]
    m0, m1 = p["m0"], p["m1"]

    # reorganizando para r(Y)
    numerator = (
        c0
        - c1 * T
        + I0
        + G
        + x0
        + x1 * e
        - m0
        - (1 - c1 + m1) * Y
    )

    r = numerator / b
    return r


# ─────────────────────────────────────────────
# CURVA LM
# ─────────────────────────────────────────────
def curva_LM(Y, p):
    """
    M/P = kY - h*r  → r(Y)
    """

    k, h = p["k"], p["h"]
    M, P = p["M"], p.get("P", 1.0)

    r = (k * Y - M / P) / h
    return r


# ─────────────────────────────────────────────
# CURVA BP
# ─────────────────────────────────────────────
def curva_BP(Y, e, x0, x1, m0, m1, kf, r_star):
    """
    BP: NX + fluxo de capitais = 0

    NX(Y) + kf*(r - r*) = 0

    → r = r* - NX(Y)/kf

    Casos:
    - kf → 0  : vertical
    - kf → ∞  : horizontal
    """

    if kf <= 1e-8:
        return np.full_like(Y, np.nan)

    NX = exportacoes_liquidas(Y, e, x0, x1, m0, m1)

    r = r_star - NX / kf
    return r


# ─────────────────────────────────────────────
# SOLVER IS-LM (com abertura)
# ─────────────────────────────────────────────
def solve_islm_open(p, e):
    """
    Solver IS-LM-BP com mobilidade de capital

    Considera:
    - Economia aberta
    - Aproximação de Mundell-Fleming
    """

    try:
        c0, c1 = p["c0"], p["c1"]
        T = p["T"]
        I0, b = p["I0"], p["b"]
        G = p["G"]

        x0, x1 = p["x0"], p["x1"]
        m0, m1 = p["m0"], p["m1"]

        kf = p.get("kf", 80.0)
        r_star = p.get("r_star", 0.05)

        # ─────────────────────────────
        # CASO 1: ALTA MOBILIDADE → r = r*
        # ─────────────────────────────
        if kf >= 1e5:
            r_eq = r_star

            Y_eq = (
                c0
                - c1 * T
                + I0
                - b * r_eq
                + G
                + x0
                + x1 * e
                - m0
            ) / (1 - c1 + m1)

        # ─────────────────────────────
        # CASO 2: MOBILIDADE FINITA
        # Resolve IS + BP
        # ─────────────────────────────
        else:
            # Sistema:
            # IS: Y = ...
            # BP: r = r* - NX/kf

            # Substituindo BP dentro da IS

            A = 1 - c1 + m1 + (b * m1) / kf

            B = (
                c0
                - c1 * T
                + I0
                + G
                + x0
                + x1 * e
                - m0
                + b * r_star
                - (b / kf) * (x0 + x1 * e - m0)
            )

            Y_eq = B / A

            NX = exportacoes_liquidas(Y_eq, e, x0, x1, m0, m1)
            r_eq = r_star - NX / kf

        # ─────────────────────────────
        # Variáveis finais
        # ─────────────────────────────
        C = c0 + c1 * (Y_eq - T)
        I = I0 - b * r_eq
        NX = exportacoes_liquidas(Y_eq, e, x0, x1, m0, m1)

        return {
            "Y": Y_eq,
            "r": r_eq,
            "C": C,
            "I": I,
            "NX": NX
        }

    except Exception as err:
        print("Erro no solver aberto:", err)
        return None