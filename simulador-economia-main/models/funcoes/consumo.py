# models/funcoes/consumo.py
"""
Motor do modelo de consumo (apenas lógica).
Funções exportadas:
- resolver_consumo(Y_grid, c0, c1, T, t=0.0, r=0.0, theta=0.0, W=0.0, alpha_w=0.0, escola="Keynesiana")
- resolver_poupanca(...)
- multiplicador_fiscal(...)
- multiplicador_imposto(...)
- analise_proporcional(...)
- calcular_ponto_equilibrio(...)
"""

from typing import Tuple, List, Optional
import numpy as np


def resolver_consumo(
    Y_grid: np.ndarray,
    c0: float,
    c1: float,
    T: float,
    t: float = 0.0,
    r: float = 0.0,
    theta: float = 0.0,
    W: float = 0.0,
    alpha_w: float = 0.0,
    escola: str = "Keynesiana",
) -> Tuple[np.ndarray, str]:
    """
    Retorna (C_vals_array, eq_str)
    Aceita Y_grid (1D array) ou escalar; sempre retorna array (np.ndarray).
    Duas especificações exemplares:
    - "Keynesiana": C = c0 + c1 * Yd - theta * r + alpha_w * W
    - "Simples":    C = c1 * Yd   (consumo totalmente induzido, sem autônomos)
    """
    Y_grid = np.asarray(Y_grid, dtype=float)
    Yd = (1.0 - t) * Y_grid - T

    if escola.lower().startswith("key"):
        C = c0 + c1 * Yd - theta * r + alpha_w * W
        juros_str = f" - {theta}·r" if theta != 0 else ""
        riqueza_str = f" + {alpha_w}·W" if alpha_w != 0 else ""
        eq = f"C = {c0:.2f} + {c1:.2f}·Yd{juros_str}{riqueza_str}"
    else:
        C = c1 * Yd
        eq = f"C = {c1:.2f}·Yd"

    return C.astype(float), eq


def resolver_poupanca(
    Y_grid: np.ndarray,
    c0: float,
    c1: float,
    T: float,
    t: float = 0.0,
    r: float = 0.0,
    theta: float = 0.0,
    W: float = 0.0,
    alpha_w: float = 0.0,
    escola: str = "Keynesiana",
) -> np.ndarray:
    """
    Poupança agregada S = Yd - C(Y)
    """
    Y_grid = np.asarray(Y_grid, dtype=float)
    C_vals, _ = resolver_consumo(Y_grid, c0, c1, T, t=t, r=r, theta=theta, W=W, alpha_w=alpha_w, escola=escola)
    Yd = (1.0 - t) * Y_grid - T
    S = Yd - C_vals
    return S.astype(float)


def multiplicador_fiscal(c1: float, t: float = 0.0, m: float = 0.0) -> float:
    """
    Multiplicador da economia para choque em G (simplificado):
    k = 1 / (1 - c1*(1 - t) + m)
    Onde m é a propensão marginal a importar (vazamento).
    """
    denom = 1.0 - c1 * (1.0 - t) + m
    return 1.0 / max(1e-9, denom)


def multiplicador_imposto(c1: float, t: float = 0.0, m: float = 0.0) -> float:
    """
    Derivada de Y* em relação a T (imposto fixo).
    ∂Y*/∂T = -c1 / (1 - c1*(1-t) + m)
    """
    k = multiplicador_fiscal(c1, t=t, m=m)
    return -c1 * k


def analise_proporcional(Y_grid: np.ndarray, C_vals: np.ndarray) -> np.ndarray:
    """
    Retorna C / Y (propensão média). Evita divisão por zero.
    """
    Y = np.asarray(Y_grid, dtype=float)
    C = np.asarray(C_vals, dtype=float)
    denom = np.where(np.isclose(Y, 0.0), 1e-9, Y)
    return (C / denom).astype(float)


def calcular_ponto_equilibrio(
    c0: float,
    c1: float,
    T: float,
    t: float,
    r: float,
    theta: float,
    W: float,
    alpha_w: float,
) -> Optional[float]:
    """
    Resolve analiticamente Y* tal que C(Y*) = Y* no modelo linear.
    Retorna None se denominador <= 0 (sem solução estável no método linear simples).
    """
    numer = c0 - c1 * T - theta * r + alpha_w * W
    denom = 1.0 - c1 * (1.0 - t)
    if denom <= 0:
        return None
    return float(numer / denom)