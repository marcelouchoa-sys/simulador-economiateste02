# ui/escolas/comparativo_ui.py
"""
Comparativo entre todas as escolas econômicas.
Reutiliza a função render_theory_comparison() de ui/explanations.py
e adiciona visualização gráfica das diferenças.
"""

import numpy as np
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ui.escolas.classica_ui import _card


def render() -> None:
    st.subheader("⚖️ Comparativo entre Escolas Econômicas")
    st.markdown(
        "Como cada escola interpreta o **mesmo choque** e propõe soluções diferentes."
    )

    # ══════════════════════════════════════════════════════════════
    # SELETOR DE CHOQUE
    # ══════════════════════════════════════════════════════════════
    col1, col2 = st.columns(2)
    with col1:
        choque = st.selectbox("Selecione o choque para comparar:", [
            "Expansão Fiscal (↑G)",
            "Recessão de Demanda (↓C privado)",
            "Choque de Oferta Negativo (↑custos)",
            "Expansão Monetária (↑M)",
        ], key="comp_choque")
    with col2:
        intensidade = st.select_slider("Intensidade:", ["Leve", "Moderada", "Forte"],
                                       value="Moderada", key="comp_intens")

    st.divider()

    # ══════════════════════════════════════════════════════════════
    # TABELA COMPARATIVA DINÂMICA
    # ══════════════════════════════════════════════════════════════
    respostas = _get_respostas(choque, intensidade)

    st.markdown("### 📊 Como cada escola responde ao choque?")
    _render_tabela_comparativa(respostas)

    st.divider()

    # ══════════════════════════════════════════════════════════════
    # GRÁFICO COMPARATIVO — OA e CP por escola
    # ══════════════════════════════════════════════════════════════
    st.markdown("### 📈 Visualização Gráfica — Curvas por Escola")
    _render_grafico_comparativo(choque)

    st.divider()

    # ══════════════════════════════════════════════════════════════
    # TEORIA DETALHADA POR ESCOLA
    # ══════════════════════════════════════════════════════════════
    st.markdown("### 📚 Aprofundamento por Escola")
    _render_theory_cards()


# ══════════════════════════════════════════════════════════════════
# FUNÇÕES INTERNAS
# ══════════════════════════════════════════════════════════════════

def _get_respostas(choque: str, intensidade: str) -> dict:
    """Retorna o diagnóstico de cada escola para o choque selecionado."""
    fator = {"Leve": "pequeno", "Moderada": "moderado", "Forte": "grande"}[intensidade]

    respostas = {
        "Expansão Fiscal (↑G)": {
            "Clássica": {
                "efeito_Y": "Nulo (LP)",
                "efeito_P": "↑ inflação",
                "efeito_u": "Nulo",
                "politica": "Não intervir — crowding-out total",
                "cor": "red",
                "icone": "🏺",
            },
            "Keynesiana": {
                "efeito_Y": f"↑ Y ({fator})",
                "efeito_P": "↑ leve",
                "efeito_u": "↓ desemprego",
                "politica": "Recomendar — multiplicador amplifica",
                "cor": "green",
                "icone": "📘",
            },
            "Monetarista": {
                "efeito_Y": "↑ temporário",
                "efeito_P": "↑ inflação (LP)",
                "efeito_u": "↓ temporário",
                "politica": "Evitar — déficit + inflação no LP",
                "cor": "orange",
                "icone": "🔴",
            },
            "Pós-Keynesiana": {
                "efeito_Y": f"↑ Y ({fator})",
                "efeito_P": "Depende do markup",
                "efeito_u": "↓ desemprego",
                "politica": "Fundamental e permanente",
                "cor": "green",
                "icone": "🟣",
            },
        },
        "Recessão de Demanda (↓C privado)": {
            "Clássica": {
                "efeito_Y": "Transitório",
                "efeito_P": "↓ preços",
                "efeito_u": "Transitório",
                "politica": "Não intervir — ajuste automático via ↓W e ↓P",
                "cor": "blue",
                "icone": "🏺",
            },
            "Keynesiana": {
                "efeito_Y": f"↓ Y ({fator})",
                "efeito_P": "Rígido (↓ difícil)",
                "efeito_u": "↑ desemprego involuntário",
                "politica": "Expansão fiscal urgente (↑G ou ↓T)",
                "cor": "red",
                "icone": "📘",
            },
            "Monetarista": {
                "efeito_Y": "↓ temporário",
                "efeito_P": "↓ gradual",
                "efeito_u": "↑ temporário",
                "politica": "Manter regra de M — ajuste natural ocorrerá",
                "cor": "orange",
                "icone": "🔴",
            },
            "Pós-Keynesiana": {
                "efeito_Y": f"↓ Y persistente",
                "efeito_P": "Estável (markup)",
                "efeito_u": "↑ persistente",
                "politica": "Gasto público permanente + crédito direcionado",
                "cor": "red",
                "icone": "🟣",
            },
        },
        "Choque de Oferta Negativo (↑custos)": {
            "Clássica": {
                "efeito_Y": "↓ Y*",
                "efeito_P": "↑ P*",
                "efeito_u": "↑ uₙ",
                "politica": "Não intervir — novo equilíbrio real",
                "cor": "blue",
                "icone": "🏺",
            },
            "Keynesiana": {
                "efeito_Y": "↓ Y + ↑P (estagflação)",
                "efeito_P": "↑↑",
                "efeito_u": "↑",
                "politica": "Dilema: acomodar (aceitar inflação) ou contrair (mais desemprego)",
                "cor": "orange",
                "icone": "📘",
            },
            "Monetarista": {
                "efeito_Y": "↓ temporário",
                "efeito_P": "↑ transitória",
                "efeito_u": "↑ transitório",
                "politica": "Não acomodar — manter M estável, aceitar recessão temporária",
                "cor": "red",
                "icone": "🔴",
            },
            "Pós-Keynesiana": {
                "efeito_Y": "↓ Y",
                "efeito_P": "↑ por markup",
                "efeito_u": "↑",
                "politica": "Controle de markup + política de rendas (negociação tripartite)",
                "cor": "purple",
                "icone": "🟣",
            },
        },
        "Expansão Monetária (↑M)": {
            "Clássica": {
                "efeito_Y": "Nulo (neutralidade)",
                "efeito_P": "↑↑ proporcional",
                "efeito_u": "Nulo",
                "politica": "Evitar — só gera inflação",
                "cor": "red",
                "icone": "🏺",
            },
            "Keynesiana": {
                "efeito_Y": f"↑ Y (se não armadilha)",
                "efeito_P": "↑ leve",
                "efeito_u": "↓",
                "politica": "Eficaz no curto prazo — mas menos que fiscal",
                "cor": "green",
                "icone": "📘",
            },
            "Monetarista": {
                "efeito_Y": "↑ temporário",
                "efeito_P": "↑ no LP",
                "efeito_u": "↓ temporário",
                "politica": "Perigosa se discricionária — usar regra fixa de M",
                "cor": "orange",
                "icone": "🔴",
            },
            "Pós-Keynesiana": {
                "efeito_Y": "Limitado",
                "efeito_P": "Depende",
                "efeito_u": "Limitado",
                "politica": "BC fixa r; M é endógena — política via crédito direcionado",
                "cor": "purple",
                "icone": "🟣",
            },
        },
    }
    return respostas.get(choque, {})


def _render_tabela_comparativa(respostas: dict) -> None:
    if not respostas:
        st.info("Selecione um choque para ver a comparação.")
        return

    emoji_cor = {
        "red":    "🔴",
        "green":  "🟢",
        "orange": "🟡",
        "blue":   "🔵",
        "purple": "🟣",
    }

    cols = st.columns(len(respostas))
    for col, (escola, dados) in zip(cols, respostas.items()):
        with col:
            icone_cor = emoji_cor.get(dados["cor"], "⚪")
            st.markdown(f"**{dados['icone']} {escola}** {icone_cor}")
            st.markdown(f"📈 **Y:** {dados['efeito_Y']}")
            st.markdown(f"💲 **P:** {dados['efeito_P']}")
            st.markdown(f"👷 **u:** {dados['efeito_u']}")
            st.markdown("---")
            st.caption(f"🏛️ {dados['politica']}")


def _render_grafico_comparativo(choque: str) -> None:
    """Gráfico comparativo das curvas OA e Phillips por escola."""
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=(
            "Curva de Oferta Agregada por Escola",
            "Curva de Phillips por Escola",
        ),
        horizontal_spacing=0.12,
    )

    Y_range = np.linspace(600, 1800, 300)
    Yn = 1200.0
    P_base = 1.0

    # OA Clássica: vertical
    fig.add_trace(go.Scatter(
        x=[Yn, Yn], y=[0.3, 3.0], mode="lines",
        name="🏺 Clássica (vertical)",
        line=dict(color="#F44336", width=2.5),
    ), row=1, col=1)

    # OA Keynesiana: inclinada positivamente
    P_kn = P_base + (Y_range - Yn) / (Yn * 0.8)
    fig.add_trace(go.Scatter(
        x=Y_range, y=np.maximum(P_kn, 0.2), mode="lines",
        name="📘 Keynesiana (inclinada)",
        line=dict(color="#2196F3", width=2.5),
    ), row=1, col=1)

    # OA Monetarista: inclinada CP, vertical LP
    P_mn = P_base + (Y_range - Yn) / (Yn * 1.5)
    fig.add_trace(go.Scatter(
        x=Y_range, y=np.maximum(P_mn, 0.2), mode="lines",
        name="🔴 Monetarista (CP inclinada)",
        line=dict(color="#FF9800", width=2, dash="dash"),
    ), row=1, col=1)

    # OA Pós-Keynesiana: horizontal (preço determinado por markup)
    fig.add_hline(y=P_base, line=dict(color="#9C27B0", width=2, dash="dot"),
                  annotation_text="🟣 Pós-Keynesiana (markup fixo)",
                  annotation_position="right", row=1, col=1)

    fig.add_vline(x=Yn, line=dict(color="#4CAF50", dash="dot", width=1.5),
                  annotation_text=f"Yₙ={Yn:.0f}", row=1, col=1)

    fig.update_xaxes(title_text="Produto (Y)", row=1, col=1, showgrid=True)
    fig.update_yaxes(title_text="Nível de Preços (P)", row=1, col=1,
                     showgrid=True, range=[0.2, 3.0])

    # ── Curvas de Phillips ────────────────────────────────────────
    u_range = np.linspace(1, 15, 300)
    u_n = 5.0
    pi_e = 3.0
    beta = 1.5

    # CP Clássica LP: vertical
    fig.add_trace(go.Scatter(
        x=[u_n, u_n], y=[-5, 20], mode="lines",
        name="🏺 Clássica LP (vertical)",
        line=dict(color="#F44336", width=2.5),
    ), row=1, col=2)

    # CP Keynesiana CP: inclinada
    pi_kn = pi_e - beta * (u_range - u_n)
    fig.add_trace(go.Scatter(
        x=u_range, y=pi_kn, mode="lines",
        name="📘 Keynesiana CP (trade-off)",
        line=dict(color="#2196F3", width=2.5),
    ), row=1, col=2)

    # CP Monetarista acelerada
    pi_mn_1 = pi_e - beta * (u_range - u_n)
    pi_mn_2 = (pi_e + 3) - beta * (u_range - u_n)
    fig.add_trace(go.Scatter(
        x=u_range, y=pi_mn_1, mode="lines",
        name="🔴 Monetarista (πᵉ=3%)",
        line=dict(color="#FF9800", width=1.8, dash="dash"),
    ), row=1, col=2)
    fig.add_trace(go.Scatter(
        x=u_range, y=pi_mn_2, mode="lines",
        name="🔴 Monetarista (πᵉ=6%)",
        line=dict(color="#FF5722", width=1.8, dash="dash"),
    ), row=1, col=2)

    fig.add_vline(x=u_n, line=dict(color="#4CAF50", dash="dot", width=1.5),
                  annotation_text=f"uₙ={u_n:.0f}%", row=1, col=2)
    fig.add_hline(y=0, line=dict(color="gray", width=1), row=1, col=2)

    fig.update_xaxes(title_text="Desemprego (u %)", row=1, col=2,
                     showgrid=True, range=[1, 15])
    fig.update_yaxes(title_text="Inflação (π %)", row=1, col=2,
                     showgrid=True, range=[-5, 20])

    fig.update_layout(
        height=470, template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=-0.28, xanchor="center", x=0.5),
        margin=dict(t=60, b=90),
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_theory_cards() -> None:
    """Cards de aprofundamento por escola — reutilizando estrutura do diagnostics."""
    teorias = [
        {
            "nome": "🏺 Escola Clássica",
            "foco": "Longo Prazo — Lado da Oferta",
            "moeda": "**Neutra no longo prazo.** MV = PY — variações em M afetam apenas P.",
            "precos": "**Totalmente flexíveis.** Ajuste instantâneo. Sem desemprego involuntário.",
            "politica_fiscal": "**Ineficaz.** Crowding-out total. AS é vertical.",
            "politica_monetaria": "**Ineficaz para Y.** Só gera inflação.",
            "curva_as": "**Vertical** em Yₙ.",
            "phillips": "**Vertical** na taxa natural — sem trade-off no LP.",
            "autores": "Adam Smith, Ricardo, Say, Mill",
            "cor": "blue",
        },
        {
            "nome": "📘 Escola Keynesiana",
            "foco": "Curto Prazo — Lado da Demanda",
            "moeda": "**Não neutra no CP.** Pode estimular Y com recursos ociosos.",
            "precos": "**Rígidos para baixo.** Ajuste lento. Desemprego involuntário possível.",
            "politica_fiscal": "**Muito eficaz.** Multiplicador amplifica ΔG.",
            "politica_monetaria": "**Menos eficaz** — especialmente na armadilha da liquidez.",
            "curva_as": "**Inclinada positivamente** no CP.",
            "phillips": "**Trade-off no CP** — menos u custa mais π.",
            "autores": "Keynes, Hicks, Hansen, Samuelson",
            "cor": "green",
        },
        {
            "nome": "🔴 Escola Monetarista",
            "foco": "Longo Prazo — Regras e Expectativas",
            "moeda": "**Neutra no LP, não neutra no CP.** Regra de Friedman: ΔM fixo.",
            "precos": "**Flexíveis no LP.** Expectativas adaptativas criam rigidez aparente.",
            "politica_fiscal": "**Ineficaz no LP** — crowding-out + déficit.",
            "politica_monetaria": "**Perigosa se discricionária.** Defasagens longas e variáveis.",
            "curva_as": "**CP inclinada, LP vertical.**",
            "phillips": "**Acelerada** — tentativa de manter u < uₙ gera inflação crescente.",
            "autores": "Friedman, Phelps, Schwartz",
            "cor": "orange",
        },
        {
            "nome": "🟣 Escola Pós-Keynesiana",
            "foco": "Incerteza — Distribuição — Instabilidade",
            "moeda": "**Endógena.** Bancos criam moeda ao conceder crédito.",
            "precos": "**Markup.** Firmas definem preço = custo × (1+m). Não há equilíbrio O-D.",
            "politica_fiscal": "**Fundamental e permanente.** Estado garante pleno emprego.",
            "politica_monetaria": "**Limitada.** BC fixa r, não M.",
            "curva_as": "**Horizontal** (markup constante) — rejeitam a formulação padrão.",
            "phillips": "**Instável.** Inflação = conflito distributivo, não excesso de demanda.",
            "autores": "Kalecki, Minsky, Kaldor, Davidson",
            "cor": "purple",
        },
    ]

    for t in teorias:
        with st.expander(f"{t['nome']} — {t['foco']}", expanded=False):
            st.markdown(f"**Autores de Referência:** {t['autores']}")
            st.divider()
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### 💵 Papel da Moeda")
                st.markdown(t["moeda"])
                st.markdown("#### 🏷️ Preços")
                st.markdown(t["precos"])
                st.markdown("#### 📈 Curva OA")
                st.markdown(t["curva_as"])
            with col2:
                st.markdown("#### 🏛️ Política Fiscal")
                st.markdown(t["politica_fiscal"])
                st.markdown("#### 🏦 Política Monetária")
                st.markdown(t["politica_monetaria"])
                st.markdown("#### 📉 Curva de Phillips")
                st.markdown(t["phillips"])