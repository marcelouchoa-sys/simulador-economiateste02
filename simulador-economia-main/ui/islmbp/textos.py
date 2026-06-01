# ui/islmbp/textos.py
"""
Textos explicativos por etapa do modo didático IS-LM-BP.
Separado do código de interface para facilitar manutenção.
"""

# ══════════════════════════════════════════════════════════════
# DICIONÁRIO BP_INFO — descrições por mobilidade
# ══════════════════════════════════════════════════════════════

BP_INFO = {
    "Nula": dict(
        inclinacao="vertical (↕)",
        geometria=(
            "A curva **BP é vertical** — não depende da taxa de juros. "
            "O equilíbrio externo é determinado **exclusivamente pela balança comercial**: NX = 0."
        ),
        descricao=(
            "Com **mobilidade nula**, o país está completamente isolado dos mercados financeiros internacionais. "
            "O único canal de ajuste externo é o **comércio de bens**."
        ),
        acima_bp="**Superávit (NX > 0):** Y baixo → poucas importações → entrada líquida de divisas.",
        abaixo_bp="**Déficit (NX < 0):** Y alto → excesso de importações → saída líquida de divisas.",
        ajuste_flex=(
            "**Câmbio Flexível + Mobilidade Nula:**\n"
            "Déficit → depreciação (e↑) → X↑ e M↓ → IS desloca direita via NX↑.\n"
            "Os juros **não têm papel** — só o câmbio real importa."
        ),
        ajuste_fixo=(
            "**Câmbio Fixo + Mobilidade Nula:**\n"
            "BC vende reservas → M↓ → LM desloca esquerda → Y cai até NX = 0.\n"
            "Política monetária perde **autonomia total**."
        ),
    ),
    "Baixa": dict(
        inclinacao="íngreme (positiva, mais vertical que a LM)",
        geometria=(
            "A **BP tem inclinação positiva e íngreme** — mais vertical que a LM. "
            "Para sustentar Y maior, é necessário aumento **grande** de juros."
        ),
        descricao=(
            "Com **mobilidade baixa**, o capital responde pouco aos juros. "
            "O canal comercial (NX) ainda domina o ajuste externo."
        ),
        acima_bp="**Superávit:** juros acima do necessário → entrada de capital supera déficit comercial.",
        abaixo_bp="**Déficit:** juros abaixo do necessário → saída de capital supera superávit comercial.",
        ajuste_flex=(
            "**Câmbio Flexível + Mobilidade Baixa:**\n"
            "Saída de capital → depreciação moderada (e↑) → NX melhora gradualmente.\n"
            "Ajuste **lento**: canal comercial domina com defasagem."
        ),
        ajuste_fixo=(
            "**Câmbio Fixo + Mobilidade Baixa:**\n"
            "BC precisa de intervenções **volumosas** → M↓ significativo → LM recua.\n"
            "Política fiscal tem eficácia **moderada**."
        ),
    ),
    "Alta": dict(
        inclinacao="suave (positiva, menos inclinada que a LM)",
        geometria=(
            "A **BP tem inclinação suave** — quase horizontal, menos inclinada que a LM. "
            "Pequenas variações de juros geram grandes fluxos de capital."
        ),
        descricao=(
            "Com **mobilidade alta**, o capital é muito sensível ao diferencial de juros (r − r*). "
            "O canal financeiro domina o ajuste externo."
        ),
        acima_bp="**Superávit (FC >> |NX|):** juros acima de r* → grande entrada de capital → apreciação.",
        abaixo_bp="**Déficit (|FC| >> NX):** juros abaixo de r* → fuga de capital → depreciação.",
        ajuste_flex=(
            "**Câmbio Flexível + Mobilidade Alta:**\n"
            "r ≠ r* → fluxos intensos e rápidos.\n"
            "r < r*: saída → depreciação (e↑) → NX↑ → IS direita.\n"
            "r > r*: entrada → apreciação (e↓) → NX↓ → IS recua."
        ),
        ajuste_fixo=(
            "**Câmbio Fixo + Mobilidade Alta:**\n"
            "BC perde quase toda autonomia monetária.\n"
            "G↑ → i↑ → entrada de capital → BC compra divisas → M↑ → LM direita.\n"
            "Multiplicador fiscal **amplificado**."
        ),
    ),
    "Perfeita": dict(
        inclinacao="horizontal (r = r* em todos os pontos)",
        geometria=(
            "A **BP é perfeitamente horizontal** em r = r*. "
            "Qualquer desvio gera fluxos **infinitos** que instantaneamente restauram r = r*."
        ),
        descricao=(
            "Com **mobilidade perfeita**, a taxa de juros interna é **fixada exogenamente** em r = r*. "
            "Este é o caso-limite do modelo Mundell-Fleming."
        ),
        acima_bp="**Impossível em equilíbrio:** r > r* → entrada infinita → apreciação imediata → r = r*.",
        abaixo_bp="**Impossível em equilíbrio:** r < r* → saída infinita → depreciação imediata → r = r*.",
        ajuste_flex=(
            "**Câmbio Flexível + Mobilidade Perfeita (Mundell-Fleming clássico):**\n\n"
            " **Política Fiscal COMPLETAMENTE INEFICAZ:**\n"
            "G↑ → IS direita → r tende ↑ → entrada de capital → apreciação (e↓) → NX↓ → IS recua.\n"
            "**ΔY = 0** — o câmbio absorveu tudo.\n\n"
            " **Política Monetária MUITO EFICAZ:**\n"
            "M↑ → LM direita → r tende ↓ → saída de capital → depreciação (e↑) → NX↑ → IS direita → Y↑↑."
        ),
        ajuste_fixo=(
            "**Câmbio Fixo + Mobilidade Perfeita (Mundell-Fleming clássico):**\n\n"
            " **Política Fiscal MUITO EFICAZ:**\n"
            "G↑ → IS direita → r tende ↑ → entrada de capital → BC compra divisas → M↑ → LM direita → Y↑↑.\n\n"
            " **Política Monetária COMPLETAMENTE INEFICAZ:**\n"
            "M↑ → LM direita → r tende ↓ → saída de capital → BC vende divisas → M↓ → LM retorna.\n"
            "**ΔY = 0**."
        ),
    ),
}


# ══════════════════════════════════════════════════════════════
# FUNÇÃO PRINCIPAL — texto_etapa
# ══════════════════════════════════════════════════════════════

def texto_etapa(politica, direcao, tipo_eco, regime, mobilidade_label, etapa):
    fiscal   = (politica == "Fiscal")
    expansao = (direcao  == "Expansionista")
    aberta   = (tipo_eco == "Aberta")
    flex     = (regime   == "Flexível")
    bp       = BP_INFO.get(mobilidade_label, BP_INFO["Alta"])

    if etapa == 0:
        return _etapa_A(fiscal, expansao, aberta, flex, mobilidade_label, bp)
    elif etapa == 1:
        return _etapa_B(fiscal, expansao, aberta, flex, mobilidade_label, bp)
    else:
        return _etapa_C(fiscal, expansao, aberta, flex, mobilidade_label, bp)


# ══════════════════════════════════════════════════════════════
# ETAPA A — Equilíbrio Inicial
# ══════════════════════════════════════════════════════════════

def _etapa_A(fiscal, expansao, aberta, flex, mobilidade_label, bp):
    blocos = [
        (
            "O que é o Ponto A?",
            "A economia está em **equilíbrio simultâneo** nos mercados de "
            "**bens (IS)** e **moeda (LM)**"
            + (", e no **balanço de pagamentos (BP)**"if aberta else "")
            + ". O produto Y₀ e a taxa de juros i₀ são determinados pela interseção das curvas.",
        ),
        (
            "Como interpretar as curvas?",
            "**① Curva IS — Mercado de Bens:**\n"
            "- Inclinação **negativa**: juros altos → I↓ → Y↓\n"
            "- Equação: C + I + G" + (" + NX"if aberta else "") + " = Y\n\n"
            "**② Curva LM — Mercado Monetário:**\n"
            "- Inclinação **positiva**: Y alto → demanda por moeda ↑ → r↑\n"
            "- Equação: M/P = kY − hi\n"
            + (
                "\n**③ Curva BP — Balanço de Pagamentos:**\n"
                "- NX + FC = 0\n"
                f"- Inclinação **{bp['inclinacao']}** com mobilidade {mobilidade_label}\n"
                f"- {bp['geometria']}"
                if aberta else ""
            ),
        ),
    ]

    if aberta:
        blocos.append((
            f"A Curva BP com Mobilidade {mobilidade_label}",
            bp["descricao"] + "\n\n"
            f"**Pontos acima da BP:** {bp['acima_bp']}\n\n"
            f"**Pontos abaixo da BP:** {bp['abaixo_bp']}",
        ))

    politica_str = "Fiscal"if fiscal else "Monetária"
    direcao_str  = "expansionista"if expansao else "contracionista"
    blocos.append((
        "Próximo passo",
        f"Será aplicada uma **política {politica_str.lower()} {direcao_str}**. "
        "Avance para a **Etapa B** para ver o efeito imediato sobre os mercados.",
    ))

    return dict(titulo="Estado A — Equilíbrio Inicial", cor="blue", blocos=blocos)


# ══════════════════════════════════════════════════════════════
# ETAPA B — Choque de Curto Prazo
# ══════════════════════════════════════════════════════════════

def _etapa_B(fiscal, expansao, aberta, flex, mobilidade_label, bp):
    if fiscal and expansao:
        instrumento  = "aumento dos gastos públicos **(G↑)** ou redução de impostos **(T↓)**"
        curva_move   = "A **IS desloca para a direita** (IS₀ → IS₁): para cada nível de juros, o produto de equilíbrio é maior."
        efeito_Y     = "Produto tende a **aumentar (Y↑)** — efeito multiplicador keynesiano."
        efeito_r     = "Maior renda eleva demanda por moeda → juros sobem **(i↑)** ao longo da LM."
        ponto_B_desc = "IS₁ intersecta LM₀. Produto e juros subiram. Setor externo ainda não reagiu."
    elif fiscal and not expansao:
        instrumento  = "redução dos gastos públicos **(G↓)** ou aumento de impostos **(T↑)**"
        curva_move   = "A **IS desloca para a esquerda** (IS₀ → IS₁): para cada nível de juros, o produto de equilíbrio é menor."
        efeito_Y     = "Produto tende a **cair (Y↓)** — efeito multiplicador reverso."
        efeito_r     = "Menor renda reduz demanda por moeda → juros caem **(i↓)**."
        ponto_B_desc = "IS₁ intersecta LM₀. Produto e juros caíram. Setor externo ainda não reagiu."
    elif not fiscal and expansao:
        instrumento  = "aumento da oferta de moeda **(M↑)** pelo Banco Central"
        curva_move   = "A **LM desloca para a direita/baixo** (LM₀ → LM₁): juros menores para cada nível de Y."
        efeito_Y     = "Juros menores → investimento sobe **(I↑)** → produto cresce **(Y↑)**."
        efeito_r     = "Juros caem imediatamente **(i↓)** — efeito liquidez direto."
        ponto_B_desc = "LM₁ intersecta IS₀. Juros caíram e produto subiu. Agora r < r*: desequilíbrio externo."
    else:
        instrumento  = "redução da oferta de moeda **(M↓)** pelo Banco Central"
        curva_move   = "A **LM desloca para a esquerda/cima** (LM₀ → LM₁): juros maiores para cada nível de Y."
        efeito_Y     = "Juros maiores → investimento cai **(I↓)** → produto recua **(Y↓)**."
        efeito_r     = "Juros sobem imediatamente **(i↑)** — contração monetária."
        ponto_B_desc = "LM₁ intersecta IS₀. Juros subiram e produto caiu. Agora r > r*: desequilíbrio externo."

    blocos = [
        (
            " 1. O Choque — Qual mercado foi afetado?",
            f"**Instrumento:** {instrumento}\n\n"
            f"**Deslocamento:** {curva_move}\n\n"
            f"**Efeito sobre Y:** {efeito_Y}\n"
            f"**Efeito sobre i:** {efeito_r}",
        ),
        (
            " 2. Interpretação do Ponto B",
            ponto_B_desc + "\n\n"
            "O **Ponto B** é um **desequilíbrio transitório de curto prazo**:\n"
            "- A economia saiu de A mas **ainda não atingiu o novo equilíbrio**\n"
            "- Forças de ajuste já estão em ação\n"
            "- No setor externo (se aberta): pressão cambial sendo gerada",
        ),
    ]

    if aberta:
        # Posição em relação à BP
        if not fiscal and expansao:
            pos_bp = "abaixo"
            pressao = "r < r* → **saída de capital (FC < 0)** → BP em déficit: NX + FC < 0."
        elif not fiscal and not expansao:
            pos_bp = "acima"
            pressao = "r > r* → **entrada de capital (FC > 0)** → BP em superávit: NX + FC > 0."
        elif fiscal and expansao:
            pos_bp = "acima"
            mob = mobilidade_label
            pressao = (
                f"Y↑ → importações↑ (NX↓), mas i↑ atrai capital (FC↑). "
                f"Com mobilidade **{mob.lower()}**, {'FC domina → superávit.'if mob in ['Alta','Perfeita'] else 'resultado depende dos fluxos relativos.'}"
            )
        else:
            pos_bp = "abaixo"
            mob = mobilidade_label
            pressao = (
                f"Y↓ → importações↓ (NX↑), mas i↓ afasta capital (FC↓). "
                f"Com mobilidade **{mob.lower()}**, {'FC domina → déficit.'if mob in ['Alta','Perfeita'] else 'resultado depende dos fluxos relativos.'}"
            )

        blocos.append((
            f" 3. Posição do Ponto B em relação à BP ({mobilidade_label})",
            f"O Ponto B encontra-se **{pos_bp} da curva BP**.\n\n"
            f"**Pressão gerada:** {pressao}\n\n"
            f"**Por que a BP tem inclinação {bp['inclinacao']}?**\n{bp['descricao']}",
        ))
        blocos.append((
            f" 4. O que o câmbio {('Flexível'if flex else 'Fixo')} vai fazer?",
            (bp["ajuste_flex"] if flex else bp["ajuste_fixo"])
            + "\n\n→ Avance para a **Etapa C** para ver o resultado final.",
        ))
    else:
        blocos.append((
            " 3. Próximo passo (Economia Fechada)",
            "Sem setor externo, o ajuste ocorre via variações em Y e i.\n"
            "Os mercados de bens e moeda convergem para o novo equilíbrio IS-LM.\n"
            "Avance para a **Etapa C**.",
        ))

    return dict(titulo="Estado B — Choque de Curto Prazo", cor="orange", blocos=blocos)


# ══════════════════════════════════════════════════════════════
# ETAPA C — Novo Equilíbrio
# ══════════════════════════════════════════════════════════════

def _etapa_C(fiscal, expansao, aberta, flex, mobilidade_label, bp):
    resultado, delta_Y, delta_r, delta_e = _calcular_resultado(
        fiscal, expansao, aberta, flex, mobilidade_label
    )

    blocos = [
        (" 1. Mecanismo de Ajuste Completo (A → B → C)", resultado),
        (
            " 2. Variações em relação ao Estado A",
            f"| Variável | Direção | Interpretação |\n"
            f"|---|---|---|\n"
            f"| **ΔY** | {delta_Y} | Variação no produto/renda |\n"
            f"| **Δi** | {delta_r} | Variação na taxa de juros |\n"
            + (f"| **Δe** | {delta_e} | Variação na taxa de câmbio |\n"if aberta else ""),
        ),
        (
            " 3. Síntese Mundell-Fleming",
            "A eficácia das políticas depende de:\n\n"
            "| Fator | Impacto |\n"
            "|---|---|\n"
            "| Regime cambial (fixo vs. flexível) | Canal de ajuste (LM ou IS) |\n"
            "| Grau de mobilidade de capital | Velocidade e magnitude |\n"
            "| Tipo de política (fiscal vs. monetária) | Interage com o regime |\n\n"
            "**Regra geral:**\n"
            "- Câmbio **Flexível** → Política **Monetária** eficaz, Fiscal ineficaz\n"
            "- Câmbio **Fixo** → Política **Fiscal** eficaz, Monetária ineficaz",
        ),
    ]

    if aberta:
        blocos.append((
            f" 4. O papel da BP com mobilidade {mobilidade_label}",
            f"**Inclinação:** {bp['inclinacao']}\n\n"
            + bp["descricao"] + "\n\n"
            f"**Mecanismo com câmbio {'flexível'if flex else 'fixo'}:**\n\n"
            + (bp["ajuste_flex"] if flex else bp["ajuste_fixo"]),
        ))

    return dict(titulo="Estado C — Novo Equilíbrio", cor="green", blocos=blocos)


def _calcular_resultado(fiscal, expansao, aberta, flex, mob):
    """Retorna (resultado_texto, delta_Y, delta_r, delta_e) para cada combinação."""

    if aberta and flex and fiscal and expansao:
        if mob == "Perfeita":
            return (
                "1. G↑ → IS direita → Y↑ e i↑ (B)\n"
                "2. i > r* → entrada massiva de capital → **apreciação (e↓)**\n"
                "3. e↓ → NX↓ → IS recua à posição original\n\n"
                " **Política COMPLETAMENTE INEFICAZ** — crowding-out externo 100%.\n**ΔY ≈ 0**",
                "≈ 0 (crowding-out 100%)", "≈ 0 (= r*)", "↓↓ (apreciação forte)"
            )
        elif mob == "Alta":
            return (
                "1. G↑ → IS direita → Y↑ e i↑ (B)\n"
                "2. i > r* → entrada de capital → **apreciação (e↓)**\n"
                "3. e↓ → NX↓ → IS recua parcialmente\n\n"
                " **Política PARCIALMENTE INEFICAZ** — crowding-out externo forte.",
                "↑ (pequeno)", "≈ r*", "↓ (apreciação moderada)"
            )
        elif mob == "Baixa":
            return (
                "1. G↑ → IS direita → Y↑ e i↑ (B)\n"
                "2. i > r* → entrada moderada de capital → apreciação leve\n"
                "3. NX↓ moderado → IS recua levemente\n\n"
                " **Política PARCIALMENTE EFICAZ** — canal cambial fraco.",
                "↑↑", "↑", "↓ (leve)"
            )
        else:
            return (
                "1. G↑ → IS direita → Y↑ e i↑ (B)\n"
                "2. Sem fluxo de capital: ajuste via NX apenas\n"
                "3. Y↑ → importações↑ → NX↓ → IS recua levemente\n\n"
                " **Política EFICAZ** (mobilidade nula).",
                "↑↑", "↑", "↑ (depreciação para NX = 0)"
            )

    elif aberta and not flex and fiscal and expansao:
        if mob == "Perfeita":
            return (
                "1. G↑ → IS direita → Y↑ e i↑ (B)\n"
                "2. i > r* → entrada massiva → pressão de apreciação\n"
                "3. BC compra divisas → M↑ → LM direita → i↓, Y↑↑\n\n"
                " **Política MUITO EFICAZ** — multiplicador máximo.",
                "↑↑↑ (máximo)", "≈ 0 (= r*)", "fixo"
            )
        else:
            return (
                "1. G↑ → IS direita → Y↑ e i↑ (B)\n"
                f"2. i > r* → entrada {'intensa'if mob == 'Alta'else 'moderada'} → pressão de apreciação\n"
                "3. BC compra divisas → M↑ → LM direita\n\n"
                " **Política EFICAZ** — BC amplifica o estímulo fiscal.",
                "↑↑", "↑ (leve)", "fixo"
            )

    elif aberta and flex and not fiscal and expansao:
        if mob == "Perfeita":
            return (
                "1. M↑ → LM direita → Y↑ e i↓ (B)\n"
                "2. i < r* → saída massiva → **depreciação (e↑)**\n"
                "3. e↑ → NX↑ → IS direita → Y↑↑\n\n"
                " **Política MUITO EFICAZ** — canal cambial amplifica ao máximo.",
                "↑↑↑ (máximo)", "↓ → r*", "↑↑ (depreciação forte)"
            )
        else:
            return (
                "1. M↑ → LM direita → Y↑ e i↓ (B)\n"
                f"2. i < r* → saída {'intensa'if mob == 'Alta'else 'moderada'} → depreciação (e↑)\n"
                "3. e↑ → NX↑ → IS direita\n\n"
                " **Política EFICAZ** — canal cambial amplifica.",
                "↑↑", "↓", "↑ (depreciação)"
            )

    elif aberta and not flex and not fiscal and expansao:
        if mob == "Perfeita":
            return (
                "1. M↑ → LM direita → i↓ (B)\n"
                "2. i < r* → saída massiva → pressão de depreciação\n"
                "3. BC vende divisas → M↓ → LM retorna à posição original\n\n"
                " **Política COMPLETAMENTE INEFICAZ** — BC reverte 100%.\n**ΔY = 0**",
                "≈ 0 (revertido)", "≈ 0 (= r*)", "fixo"
            )
        else:
            return (
                "1. M↑ → LM direita → i↓ (B)\n"
                f"2. i < r* → saída {'intensa'if mob == 'Alta'else 'moderada'} → pressão de depreciação\n"
                "3. BC vende divisas → M↓ → LM recua\n\n"
                " **Política INEFICAZ** — intervenção cambial neutraliza.",
                "≈ 0", "≈ 0", "fixo"
            )

    elif aberta and flex and fiscal and not expansao:
        return (
            "1. G↓ → IS esquerda → Y↓ e i↓ (B)\n"
            "2. i < r* → saída de capital → **depreciação (e↑)**\n"
            "3. e↑ → NX↑ → IS direita (atenuação)\n\n"
            " **Política PARCIALMENTE EFICAZ** — câmbio atenua a contração.",
            "↓ (atenuado)", "↓", "↑ (depreciação)"
        )

    elif aberta and not flex and fiscal and not expansao:
        return (
            "1. G↓ → IS esquerda → Y↓ e i↓ (B)\n"
            "2. i < r* → saída de capital → pressão de depreciação\n"
            "3. BC vende divisas → M↓ → LM esquerda → Y↓↓\n\n"
            " **Política AMPLIFICADA** — ajuste monetário endógeno amplifica a contração.",
            "↓↓ (amplificado)", "≈ 0 (= r*)", "fixo"
        )

    elif aberta and flex and not fiscal and not expansao:
        return (
            "1. M↓ → LM esquerda → i↑ (B)\n"
            "2. i > r* → entrada de capital → **apreciação (e↓)**\n"
            "3. e↓ → NX↓ → IS esquerda → Y↓↓\n\n"
            " **Política AMPLIFICADA** — canal cambial amplifica a contração.",
            "↓↓ (amplificado)", "↑ → r*", "↓ (apreciação)"
        )

    elif aberta and not flex and not fiscal and not expansao:
        return (
            "1. M↓ → LM esquerda → i↑ (B)\n"
            "2. i > r* → entrada de capital → pressão de apreciação\n"
            "3. BC compra divisas → M↑ → LM retorna\n\n"
            " **Política COMPLETAMENTE INEFICAZ** — BC reverte 100%.",
            "≈ 0", "≈ 0 (= r*)", "fixo"
        )

    elif fiscal and expansao:
        return (
            "1. G↑ → IS direita → Y↑ (B)\n"
            "2. Y↑ → demanda por moeda↑ → i↑ ao longo da LM\n"
            "3. i↑ → investimento privado cai **(crowding-out)**: I↓\n\n"
            " **Política PARCIALMENTE EFICAZ** — crowding-out reduz o multiplicador.",
            "↑ (< multiplicador simples)", "↑ (crowding-out)", "N/A"
        )

    elif fiscal and not expansao:
        return (
            "1. G↓ → IS esquerda → Y↓\n"
            "2. Y↓ → demanda por moeda↓ → i↓\n"
            "3. i↓ → investimento privado sobe (crowding-in parcial)\n\n"
            " **Política PARCIALMENTE EFICAZ** — crowding-in atenua a queda.",
            "↓ (atenuado)", "↓", "N/A"
        )

    elif not fiscal and expansao:
        return (
            "1. M↑ → LM direita → i↓\n"
            "2. i↓ → investimento privado sobe **(I↑)**\n"
            "3. I↑ → demanda agregada sobe → Y↑\n\n"
            " **Política EFICAZ** — sem crowding-out, canal de transmissão direto.",
            "↑", "↓", "N/A"
        )

    else:
        return (
            "1. M↓ → LM esquerda → i↑\n"
            "2. i↑ → investimento privado cai **(I↓)**\n"
            "3. I↓ → demanda agregada cai → Y↓\n\n"
            " **Política EFICAZ** (sentido contracionista).",
            "↓", "↑", "N/A"
        )


# ══════════════════════════════════════════════════════════════
# CONCLUSÃO — só aparece na Etapa C
# ══════════════════════════════════════════════════════════════

def conclusao_etapa(politica, direcao, tipo_eco, regime, mobilidade_label):
    fiscal   = (politica == "Fiscal")
    expansao = (direcao  == "Expansionista")
    aberta   = (tipo_eco == "Aberta")
    flex     = (regime   == "Flexível")

    resultado, delta_Y, delta_r, delta_e = _calcular_resultado(
        fiscal, expansao, aberta, flex, mobilidade_label
    )

    # Determinar veredicto a partir do resultado
    if "COMPLETAMENTE INEFICAZ"in resultado or "ΔY ≈ 0"in resultado or "ΔY = 0"in resultado:
        veredicto = "ineficaz"; emoji = ""
    elif "MUITO EFICAZ"in resultado or "máximo"in delta_Y:
        veredicto = "eficaz"; emoji = ""
    elif "PARCIALMENTE"in resultado or "atenuado"in delta_Y:
        veredicto = "parcial"; emoji = ""
    elif "EFICAZ"in resultado:
        veredicto = "eficaz"; emoji = ""
    else:
        veredicto = "parcial"; emoji = ""

    # Canal dominante
    if fiscal and expansao:
        if aberta and flex:
            canal = "**G↑ → i↑ → Entrada de Capital → Apreciação Cambial → NX↓ → IS recua**"
        elif aberta and not flex:
            canal = "**G↑ → i↑ → Entrada de Capital → BC compra divisas → M↑ → LM↓ → Y↑↑**"
        else:
            canal = "**G↑ → IS direita → Y↑ → demanda moeda↑ → i↑ → I↓ (crowding-out)**"
    elif not fiscal and expansao:
        if aberta and flex:
            canal = "**M↑ → i↓ → Saída de Capital → Depreciação (e↑) → NX↑ → IS direita → Y↑**"
        elif aberta and not flex:
            canal = "**M↑ → i↓ → Saída de Capital → BC vende divisas → M↓ → LM retorna**"
        else:
            canal = "**M↑ → LM direita → i↓ → I↑ → DA↑ → Y↑**"
    else:
        canal = "Veja a análise acima para o canal dominante."

    # Contrafactual
    if aberta:
        if flex:
            contrafactual = (
                "Com **câmbio fixo**, o resultado seria diferente: "
                "a política fiscal seria mais eficaz (BC expande M endogenamente) "
                "e a monetária seria ineficaz (BC reverte a expansão)."
            )
        else:
            contrafactual = (
                "Com **câmbio flexível**, o resultado seria diferente: "
                "a política fiscal seria menos eficaz (apreciação cambial anularia parte do estímulo) "
                "e a monetária seria mais eficaz (depreciação ampliaria via NX)."
            )
    else:
        contrafactual = (
            "Em **economia aberta com câmbio fixo e alta mobilidade**, "
            "a política fiscal seria amplificada pela expansão monetária endógena. "
            "Com **câmbio flexível e mobilidade perfeita**, seria completamente ineficaz."
        )

    # Lição
    licoes = {
        ("ineficaz", True,  True,  True):  "Câmbio flexível + mobilidade perfeita → política fiscal completamente ineficaz.",
        ("ineficaz", False, True,  False): "Câmbio fixo → política monetária completamente ineficaz.",
        ("eficaz",   True,  False, True):  "Câmbio flexível + mobilidade perfeita → política monetária maximamente eficaz.",
        ("eficaz",   True,  True,  False): "Câmbio fixo → política fiscal muito eficaz (multiplicador amplificado).",
    }
    licao = licoes.get(
        (veredicto, fiscal, aberta, flex),
        "A eficácia das políticas depende do regime cambial e da mobilidade de capital."
    )

    titulo_map = {
        "eficaz":   f"{'Política Fiscal'if fiscal else 'Política Monetária'} — Eficaz",
        "parcial":  f"{'Política Fiscal'if fiscal else 'Política Monetária'} — Parcialmente Eficaz",
        "ineficaz": f"{'Política Fiscal'if fiscal else 'Política Monetária'} — Ineficaz",
    }

    return dict(
        veredicto=veredicto,
        emoji=emoji,
        titulo=titulo_map[veredicto],
        razao=resultado,
        canal=canal,
        contrafactual=contrafactual,
        licao=licao,
    )