import numpy as np

def resolver_consumo(Y_grid, c0, c1, T, t=0.0, r=0.0, theta=0.0, W=0.0, alpha_w=0.0, escola="Keynesiana"):
    """
    Calcula o consumo considerando renda, impostos, juros e riqueza.
    C = c0 + c1 * Yd - theta * r + alpha_w * W
    """
    Yd = Y_grid * (1 - t) - T
    
    if escola == "Keynesiana":
        C = c0 + c1 * Yd - (theta * r) + (alpha_w * W)
        juros_str = f" - {theta}·r" if theta > 0 else ""
        riqueza_str = f" + {alpha_w}·W" if alpha_w > 0 else ""
        eq = f"C = {c0:.0f} + {c1:.2f}·Yd{juros_str}{riqueza_str}"
    else:
        C = c1 * Yd
        eq = f"C = {c1:.2f}·Yd"
        
    return C, eq

def resolver_poupanca(Y_grid, c0, c1, T, t=0.0, r=0.0, theta=0.0, W=0.0, alpha_w=0.0, escola="Keynesiana"):
    """S ≡ Yd - C"""
    Yd = Y_grid * (1 - t) - T
    C, _ = resolver_consumo(Y_grid, c0, c1, T, t, r, theta, W, alpha_w, escola)
    S = Yd - C
    return S

def multiplicador_fiscal(c1, t=0.0, m=0.0):
    """k = 1 / [1 - c1(1 - t) + m]"""
    denominador = 1 - c1 * (1 - t) + m
    return 1.0 / max(1e-9, denominador)

def multiplicador_imposto(c1, t=0.0, m=0.0):
    """Impacto de impostos fixos (T)"""
    k = multiplicador_fiscal(c1, t, m)
    return -c1 * k

def analise_proporcional(Y_grid, C):
    """Calcula a Propensão Média a Consumir (PMeC)"""
    Y_safe = np.where(Y_grid == 0, 1e-9, Y_grid)
    return C / Y_safe

def calcular_ponto_equilibrio(c0, c1, T, t, r, theta, W, alpha_w):
    """Calcula o Break-even point onde C = Y"""
    numerador = c0 - c1 * T - theta * r + alpha_w * W
    denominador = 1 - c1 * (1 - t)
    return numerador / denominador if denominador > 0 else None