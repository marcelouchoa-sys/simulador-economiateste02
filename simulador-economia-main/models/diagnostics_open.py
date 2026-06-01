def diagnosticar_choque_aberto(base, choque, params_b, params_c):
    dY  = choque["Y"]  - base["Y"]
    dr  = choque["r"]  - base["r"]
    de  = choque["e"]  - base["e"]
    dNX = choque["NX"] - base["NX"]
    dCF = choque["CF"] - base["CF"]
    dBP = choque["BP"] - base["BP"]

    dG = params_c["G"] - params_b["G"]
    dT = params_c["T"] - params_b["T"]
    dM = params_c["M"] - params_b["M"]
    dr_star = params_c["r_star"] - params_b["r_star"]

    regime = params_c.get("regime", "flex")
    kf     = params_c["kf"]

    linhas = []

    # ── Tipo de choque ─────────────────────────────
    if abs(dG) > 0.1:
        linhas.append(f"Choque Fiscal: ΔG = {dG:+.1f}")
    if abs(dM) > 0.1:
        linhas.append(f"Choque Monetário: ΔM = {dM:+.1f}")
    if abs(dr_star) > 0.001:
        linhas.append(f"Choque Externo: Δr* = {dr_star*100:+.2f} pp")

    # ── Regime ────────────────────────────────────
    linhas.append(f"\n Regime Cambial: {'Flexível'if regime=='flex'else 'Fixo'}")

    # ── Coerência macro ───────────────────────────
    bp_teorico = dNX + dCF
    erro = dBP - bp_teorico

    linhas.append("\n Consistência Macroeconômica:")
    linhas.append(f"- ΔBP observado: {dBP:+.3f}")
    linhas.append(f"- ΔNX + ΔCF: {bp_teorico:+.3f}")
    linhas.append(f"- Erro: {erro:+.5f}")

    if abs(erro) > 0.01:
        linhas.append("Inconsistência detectada no balanço de pagamentos!")
    else:
        linhas.append("BP consistente com NX + CF")

    # ── Interpretação externa ─────────────────────
    linhas.append("\n Setor Externo:")

    if dNX > 0:
        linhas.append("- Exportações líquidas aumentaram (ganho de competitividade)")
    elif dNX < 0:
        linhas.append("- Exportações líquidas caíram (apreciação cambial)")

    if dCF > 0:
        linhas.append("- Entrada de capital (juros domésticos atrativos)")
    elif dCF < 0:
        linhas.append("- Saída de capital (juros domésticos baixos)")

    # ── Regime cambial efeito ─────────────────────
    linhas.append("\n Mecanismo de Ajuste:")

    if regime == "flex":
        if de > 0:
            linhas.append("- Depreciação cambial → estímulo às exportações")
        elif de < 0:
            linhas.append("- Apreciação cambial → redução das exportações")
    else:
        linhas.append("- Banco Central ajusta oferta monetária para manter o câmbio fixo")

    # ── Multiplicador ─────────────────────────────
    if abs(dG) > 0.1:
        mult = dY / dG
        linhas.append(f"\n Multiplicador Fiscal: {mult:.3f}")

        if regime == "flex"and dNX < 0:
            linhas.append("Reduzido por apreciação cambial (crowding-out externo)")
        if regime == "flex"and dNX > 0:
            linhas.append("Amplificado por depreciação cambial")

    return "\n".join(linhas)