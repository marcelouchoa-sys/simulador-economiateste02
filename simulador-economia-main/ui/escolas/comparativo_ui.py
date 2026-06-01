# ui/escolas/comparativo_ui.py
"""
Comparativo entre todas as escolas econômicas.
"""

import numpy as np
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ui.escolas.classica_ui import _card


def render() -> None:
    st.subheader("Comparativo entre Escolas Econômicas")
    st.markdown(
        "Como cada escola interpreta o **mesmo choque** e propõe soluções diferentes."
    )

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

    respostas = _get_respostas(choque, intensidade)

    st.markdown("### Como cada escola responde ao choque?")
    _render_tabela_comparativa(respostas)

    st.divider()

    st.markdown("### Visualização Grafica — Curvas por Escola")
    _render_grafico_comparativo(choque)

    st.divider()

    st.markdown("### Aprofundamento por Escola")
    _render_theory_cards()


def _get_respostas(choque: str, intensidade: str) -> dict:
    fator = {"Leve": "pequeno", "Moderada": "moderado", "Forte": "grande"}[intensidade]

    respostas = {
        "Expansão Fiscal (↑G)": {
            "Clássica":      {"efeito_Y": "Nulo (LP)",       "efeito_P": "↑ inflação",        "efeito_u": "Nulo",           "politica": "Não intervir — crowding-out total",          "cor": "red"},
            "Keynesiana":    {"efeito_Y": f"↑ Y ({fator})",  "efeito_P": "↑ leve",            "efeito_u": "↓ desemprego",   "politica": "Recomendar — multiplicador amplifica",       "cor": "green"},
            "Monetarista":   {"efeito_Y": "↑ temporário",    "efeito_P": "↑ inflação (LP)",   "efeito_u": "↓ temporário",   "politica": "Evitar — déficit + inflação no LP",          "cor": "orange"},
            "Pós-Keynesiana":{"efeito_Y": f"↑ Y ({fator})",  "efeito_P": "Depende do markup", "efeito_u": "↓ desemprego",   "politica": "Fundamental e permanente",                   "cor": "green"},
        },
        "Recessão de Demanda (↓C privado)": {
            "Clássica":      {"efeito_Y": "Transitório",     "efeito_P": "↓ preços",          "efeito_u": "Transitório",    "politica": "Não intervir — ajuste automático via ↓W e ↓P","cor": "blue"},
            "Keynesiana":    {"efeito_Y": f"↓ Y ({fator})",  "efeito_P": "Rígido (↓ difícil)","efeito_u": "↑ involuntário", "politica": "Expansão fiscal urgente (↑G ou ↓T)",         "cor": "red"},
            "Monetarista":   {"efeito_Y": "↓ temporário",    "efeito_P": "↓ gradual",         "efeito_u": "↑ temporário",   "politica": "Manter regra de M — ajuste natural ocorrerá","cor": "orange"},
            "Pós-Keynesiana":{"efeito_Y": "↓ Y persistente", "efeito_P": "Estável (markup)",  "efeito_u": "↑ persistente",  "politica": "Gasto público permanente + crédito direcionado","cor": "red"},
        },
        "Choque de Oferta Negativo (↑custos)": {
            "Clássica":      {"efeito_Y": "↓ Y*",            "efeito_P": "↑ P*",              "efeito_u": "↑ uₙ",           "politica": "Não intervir — novo equilíbrio real",        "cor": "blue"},
            "Keynesiana":    {"efeito_Y": "↓ Y + ↑P",        "efeito_P": "↑↑",               "efeito_u": "↑",              "politica": "Dilema: acomodar ou contrair",               "cor": "orange"},
            "Monetarista":   {"efeito_Y": "↓ temporário",    "efeito_P": "↑ transitória",     "efeito_u": "↑ transitório",  "politica": "Não acomodar — manter M estável",            "cor": "red"},
            "Pós-Keynesiana":{"efeito_Y": "↓ Y",             "efeito_P": "↑ por markup",      "efeito_u": "↑",              "politica": "Controle de markup + política de rendas",    "cor": "purple"},
        },
        "Expansão Monetária (↑M)": {
            "Clássica":      {"efeito_Y": "Nulo (neutralidade)","efeito_P": "↑↑ proporcional","efeito_u": "Nulo",           "politica": "Evitar — só gera inflação",                  "cor": "red"},
            "Keynesiana":    {"efeito_Y": "↑ Y (se não armadilha)","efeito_P": "↑ leve",      "efeito_u": "↓",             "politica": "Eficaz no CP — mas menos que fiscal",        "cor": "green"},
            "Monetarista":   {"efeito_Y": "↑ temporário",    "efeito_P": "↑ no LP",          "efeito_u": "↓ temporário",   "politica": "Perigosa se discricionária — usar regra",    "cor": "orange"},
            "Pós-Keynesiana":{"efeito_Y": "Limitado",        "efeito_P": "Depende",          "efeito_u": "Limitado",       "politica": "BC fixa r; M endógena — crédito direcionado","cor": "purple"},
        },
    }
    return respostas.get(choque, {})


def _render_tabela_comparativa(respostas: dict) -> None:
    if not respostas:
        st.info("Selecione um choque para ver a comparação.")
        return

    cor_label = {
        "red":    "Contrario",
        "green":  "A favor",
        "orange": "Cauteloso",
        "blue":   "Neutro",
        "purple": "Alternativo",
    }

    cols = st.columns(len(respostas))
    for col, (escola, dados) in zip(cols, respostas.items()):
        with col:
            st.markdown(f"**{escola}**")
            st.markdown(f"Y: **{dados['efeito_Y']}**")
            st.markdown(f"P: **{dados['efeito_P']}**")
            st.markdown(f"u: **{dados['efeito_u']}**")
            st.markdown("---")
            st.caption(dados['politica'])


def _render_grafico_comparativo(choque: str) -> None:
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=(
            "Curva de Oferta Agregada por Escola",
            "Curva de Phillips por Escola",
        ),
        horizontal_spacing=0.12,
    )

    Y_range = np.linspace(600, 1800, 300)
    Yn      = 1200.0
    P_base  = 1.0

    fig.add_trace(go.Scatter(
        x=[Yn, Yn], y=[0.3, 3.0], mode="lines",
        name="Classica (vertical)",
        line=dict(color="#F44336", width=2.5),
    ), row=1, col=1)

    P_kn = P_base + (Y_range - Yn) / (Yn * 0.8)
    fig.add_trace(go.Scatter(
        x=Y_range, y=np.maximum(P_kn, 0.2), mode="lines",
        name="Keynesiana (inclinada)",
        line=dict(color="#2196F3", width=2.5),
    ), row=1, col=1)

    P_mn = P_base + (Y_range - Yn) / (Yn * 1.5)
    fig.add_trace(go.Scatter(
        x=Y_range, y=np.maximum(P_mn, 0.2), mode="lines",
        name="Monetarista (CP inclinada)",
        line=dict(color="#FF9800", width=2, dash="dash"),
    ), row=1, col=1)

    fig.add_hline(y=P_base, line=dict(color="#9C27B0", width=2, dash="dot"),
                  annotation_text="Pos-Keynesiana (markup fixo)",
                  annotation_position="right", row=1, col=1)
    fig.add_vline(x=Yn, line=dict(color="#4CAF50", dash="dot", width=1.5),
                  annotation_text=f"Yn={Yn:.0f}", row=1, col=1)

    fig.update_xaxes(title_text="Produto (Y)", row=1, col=1, showgrid=True)
    fig.update_yaxes(title_text="Nivel de Precos (P)", row=1, col=1,
                     showgrid=True, range=[0.2, 3.0])

    u_range = np.linspace(1, 15, 300)
    u_n  = 5.0
    pi_e = 3.0
    beta = 1.5

    fig.add_trace(go.Scatter(
        x=[u_n, u_n], y=[-5, 20], mode="lines",
        name="Classica LP (vertical)",
        line=dict(color="#F44336", width=2.5),
    ), row=1, col=2)

    pi_kn = pi_e - beta * (u_range - u_n)
    fig.add_trace(go.Scatter(
        x=u_range, y=pi_kn, mode="lines",
        name="Keynesiana CP (trade-off)",
        line=dict(color="#2196F3", width=2.5),
    ), row=1, col=2)

    pi_mn_1 = pi_e - beta * (u_range - u_n)
    pi_mn_2 = (pi_e + 3) - beta * (u_range - u_n)
    fig.add_trace(go.Scatter(
        x=u_range, y=pi_mn_1, mode="lines",
        name="Monetarista (pe=3%)",
        line=dict(color="#FF9800", width=1.8, dash="dash"),
    ), row=1, col=2)
    fig.add_trace(go.Scatter(
        x=u_range, y=pi_mn_2, mode="lines",
        name="Monetarista (pe=6%)",
        line=dict(color="#FF5722", width=1.8, dash="dash"),
    ), row=1, col=2)

    fig.add_vline(x=u_n, line=dict(color="#4CAF50", dash="dot", width=1.5),
                  annotation_text=f"un={u_n:.0f}%", row=1, col=2)
    fig.add_hline(y=0, line=dict(color="gray", width=1), row=1, col=2)

    fig.update_xaxes(title_text="Desemprego (u %)", row=1, col=2,
                     showgrid=True, range=[1, 15])
    fig.update_yaxes(title_text="Inflacao (pi %)", row=1, col=2,
                     showgrid=True, range=[-5, 20])

    fig.update_layout(
        height=470, template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=-0.28, xanchor="center", x=0.5),
        margin=dict(t=60, b=90),
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_theory_cards() -> None:
    teorias = [
        {
            "nome": "Escola Classica",
            "foco": "Longo Prazo — Lado da Oferta",
            "moeda": "**Neutra no longo prazo.** MV = PY — variacoes em M afetam apenas P.",
            "precos": "**Totalmente flexiveis.** Ajuste instantaneo. Sem desemprego involuntario.",
            "politica_fiscal": "**Ineficaz.** Crowding-out total. AS vertical.",
            "politica_monetaria": "**Ineficaz para Y.** So gera inflacao.",
            "curva_as": "**Vertical** em Yn.",
            "phillips": "**Vertical** na taxa natural — sem trade-off no LP.",
            "autores": "Adam Smith, Ricardo, Say, Mill",
        },
        {
            "nome": "Escola Keynesiana",
            "foco": "Curto Prazo — Lado da Demanda",
            "moeda": "**Nao neutra no CP.** Pode estimular Y com recursos ociosos.",
            "precos": "**Rigidos para baixo.** Ajuste lento. Desemprego involuntario possivel.",
            "politica_fiscal": "**Muito eficaz.** Multiplicador amplifica G.",
            "politica_monetaria": "**Menos eficaz** — especialmente na armadilha da liquidez.",
            "curva_as": "**Inclinada positivamente** no CP.",
            "phillips": "**Trade-off no CP** — menos u custa mais pi.",
            "autores": "Keynes, Hicks, Hansen, Samuelson",
        },
        {
            "nome": "Escola Monetarista",
            "foco": "Longo Prazo — Regras e Expectativas",
            "moeda": "**Neutra no LP, nao neutra no CP.** Regra de Friedman: M fixo.",
            "precos": "**Flexiveis no LP.** Expectativas adaptativas criam rigidez aparente.",
            "politica_fiscal": "**Ineficaz no LP** — crowding-out + deficit.",
            "politica_monetaria": "**Perigosa se discricionaria.** Defasagens longas.",
            "curva_as": "**CP inclinada, LP vertical.**",
            "phillips": "**Acelerada** — manter u < un gera inflacao crescente.",
            "autores": "Friedman, Phelps, Schwartz",
        },
        {
            "nome": "Escola Pos-Keynesiana",
            "foco": "Incerteza — Distribuicao — Instabilidade",
            "moeda": "**Endogena.** Bancos criam moeda ao conceder credito.",
            "precos": "**Markup.** Preco = custo x (1+m). Nao ha equilibrio O-D.",
            "politica_fiscal": "**Fundamental e permanente.** Estado garante pleno emprego.",
            "politica_monetaria": "**Limitada.** BC fixa r, nao M.",
            "curva_as": "**Horizontal** (markup constante).",
            "phillips": "**Instavel.** Inflacao = conflito distributivo.",
            "autores": "Kalecki, Minsky, Kaldor, Davidson",
        },
    ]

    for t in teorias:
        with st.expander(f"{t['nome']} — {t['foco']}", expanded=False):
            st.markdown(f"**Autores de Referencia:** {t['autores']}")
            st.divider()
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Papel da Moeda**")
                st.markdown(t["moeda"])
                st.markdown("**Precos**")
                st.markdown(t["precos"])
                st.markdown("**Curva OA**")
                st.markdown(t["curva_as"])
            with col2:
                st.markdown("**Politica Fiscal**")
                st.markdown(t["politica_fiscal"])
                st.markdown("**Politica Monetaria**")
                st.markdown(t["politica_monetaria"])
                st.markdown("**Curva de Phillips**")
                st.markdown(t["phillips"])