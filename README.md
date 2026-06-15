import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date

# =========================================================
# CONFIGURAÇÃO DA PÁGINA
# =========================================================
st.set_page_config(
    page_title="Dashboard Financeiro",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Dashboard Financeiro Pessoal")
st.markdown("---")

# =========================================================
# CATEGORIAS
# =========================================================
CATEGORIAS = [
    "Alimentação",
    "Transporte",
    "Moradia",
    "Saúde",
    "Lazer",
    "Educação",
    "Roupas",
    "Assinaturas",
    "Outros",
]

# =========================================================
# ESTADO DA SESSÃO (armazena os lançamentos)
# =========================================================
if "lancamentos" not in st.session_state:
    st.session_state.lancamentos = pd.DataFrame(
        columns=["data", "descricao", "categoria", "valor", "tipo"]
    )

# =========================================================
# SIDEBAR — FORMULÁRIO DE LANÇAMENTO
# =========================================================
with st.sidebar:
    st.header("➕ Novo lançamento")

    tipo = st.radio("Tipo", ["Saída", "Entrada"], horizontal=True)

    data_lanc = st.date_input("Data", value=date.today())

    descricao = st.text_input("Descrição", placeholder="Ex: Supermercado")

    if tipo == "Saída":
        categoria = st.selectbox("Categoria", CATEGORIAS)
    else:
        categoria = "Renda"

    valor = st.number_input("Valor (R$)", min_value=0.01, step=0.01, format="%.2f")

    if st.button("Salvar lançamento", use_container_width=True, type="primary"):
        if descricao.strip() == "":
            st.error("Informe uma descrição.")
        else:
            novo = pd.DataFrame([{
                "data": pd.to_datetime(data_lanc),
                "descricao": descricao.strip(),
                "categoria": categoria,
                "valor": valor,
                "tipo": tipo.lower(),
            }])
            st.session_state.lancamentos = pd.concat(
                [st.session_state.lancamentos, novo],
                ignore_index=True
            )
            st.success(f"✅ Lançamento salvo!")

    st.markdown("---")

    # Botão para limpar tudo
    if st.button("🗑️ Limpar todos os dados", use_container_width=True):
        st.session_state.lancamentos = pd.DataFrame(
            columns=["data", "descricao", "categoria", "valor", "tipo"]
        )
        st.rerun()

# =========================================================
# DADOS
# =========================================================
df = st.session_state.lancamentos.copy()

# =========================================================
# SEM DADOS — tela inicial
# =========================================================
if df.empty:
    st.info("👈 Adicione seus lançamentos na barra lateral para começar.")
    st.markdown("### Como usar")
    st.markdown("""
    1. No menu lateral, escolha **Entrada** ou **Saída**
    2. Preencha a data, descrição, categoria e valor
    3. Clique em **Salvar lançamento**
    4. Os gráficos aparecerão automaticamente aqui
    """)
    st.stop()

# =========================================================
# FILTRO DE MÊS
# =========================================================
df["mes_ano"] = df["data"].dt.to_period("M").astype(str)
meses_disponiveis = sorted(df["mes_ano"].unique(), reverse=True)

col_filtro, _ = st.columns([2, 6])
with col_filtro:
    mes_selecionado = st.selectbox("Filtrar por mês", ["Todos"] + meses_disponiveis)

if mes_selecionado != "Todos":
    df_filtrado = df[df["mes_ano"] == mes_selecionado]
else:
    df_filtrado = df.copy()

# =========================================================
# MÉTRICAS NO TOPO
# =========================================================
entradas = df_filtrado[df_filtrado["tipo"] == "entrada"]["valor"].sum()
saidas   = df_filtrado[df_filtrado["tipo"] == "saída"]["valor"].sum()
saldo    = entradas - saidas

col1, col2, col3, col4 = st.columns(4)

col1.metric("💵 Total entradas", f"R$ {entradas:,.2f}")
col2.metric("💸 Total saídas",   f"R$ {saidas:,.2f}")
col3.metric(
    "📊 Saldo",
    f"R$ {saldo:,.2f}",
    delta=f"R$ {saldo:,.2f}",
    delta_color="normal"
)
col4.metric("📝 Lançamentos", len(df_filtrado))

st.markdown("---")

# =========================================================
# GRÁFICO 1 — GASTOS POR CATEGORIA (pizza)
# =========================================================
df_saidas = df_filtrado[df_filtrado["tipo"] == "saída"]

col_g1, col_g2 = st.columns(2)

with col_g1:
    st.subheader("🍕 Gastos por categoria")
    if df_saidas.empty:
        st.info("Nenhuma saída registrada.")
    else:
        cat_group = (
            df_saidas.groupby("categoria")["valor"]
            .sum()
            .reset_index()
            .sort_values("valor", ascending=False)
        )
        fig_pizza = px.pie(
            cat_group,
            names="categoria",
            values="valor",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel,
        )
        fig_pizza.update_traces(
            textposition="inside",
            textinfo="percent+label",
            hovertemplate="<b>%{label}</b><br>R$ %{value:,.2f}<br>%{percent}<extra></extra>"
        )
        fig_pizza.update_layout(
            showlegend=True,
            margin=dict(t=10, b=10, l=10, r=10),
            height=380,
        )
        st.plotly_chart(fig_pizza, use_container_width=True)

# =========================================================
# GRÁFICO 2 — SALDO ENTRADAS VS SAÍDAS (barras)
# =========================================================
with col_g2:
    st.subheader("⚖️ Entradas vs Saídas")
    resumo_tipo = df_filtrado.groupby("tipo")["valor"].sum().reset_index()
    resumo_tipo["tipo"] = resumo_tipo["tipo"].str.capitalize()

    cores = {"Entrada": "#1D9E75", "Saída": "#D85A30"}
    fig_bar = px.bar(
        resumo_tipo,
        x="tipo",
        y="valor",
        color="tipo",
        color_discrete_map=cores,
        text_auto=".2f",
    )
    fig_bar.update_traces(
        texttemplate="R$ %{y:,.2f}",
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>R$ %{y:,.2f}<extra></extra>"
    )
    fig_bar.update_layout(
        showlegend=False,
        xaxis_title="",
        yaxis_title="Valor (R$)",
        margin=dict(t=10, b=10, l=10, r=10),
        height=380,
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# =========================================================
# GRÁFICO 3 — EVOLUÇÃO MENSAL (linha)
# =========================================================
st.subheader("📈 Evolução mensal")

evolucao = (
    df.groupby(["mes_ano", "tipo"])["valor"]
    .sum()
    .reset_index()
)
evolucao["tipo"] = evolucao["tipo"].str.capitalize()

if len(evolucao["mes_ano"].unique()) < 2:
    st.info("Adicione lançamentos em mais de um mês para ver a evolução.")
else:
    fig_linha = px.line(
        evolucao,
        x="mes_ano",
        y="valor",
        color="tipo",
        markers=True,
        color_discrete_map={"Entrada": "#1D9E75", "Saída": "#D85A30"},
    )
    fig_linha.update_traces(
        hovertemplate="<b>%{x}</b><br>R$ %{y:,.2f}<extra></extra>",
        line=dict(width=2.5),
        marker=dict(size=8),
    )
    fig_linha.update_layout(
        xaxis_title="Mês",
        yaxis_title="Valor (R$)",
        legend_title="",
        margin=dict(t=10, b=10, l=10, r=10),
        height=350,
    )
    st.plotly_chart(fig_linha, use_container_width=True)

# =========================================================
# TABELA DE LANÇAMENTOS
# =========================================================
st.markdown("---")
st.subheader("📋 Lançamentos registrados")

df_exibir = df_filtrado.copy()
df_exibir["data"] = df_exibir["data"].dt.strftime("%d/%m/%Y")
df_exibir["valor"] = df_exibir["valor"].apply(lambda x: f"R$ {x:,.2f}")
df_exibir["tipo"] = df_exibir["tipo"].str.capitalize()
df_exibir = df_exibir.drop(columns=["mes_ano"], errors="ignore")
df_exibir.columns = ["Data", "Descrição", "Categoria", "Valor", "Tipo"]

st.dataframe(df_exibir, use_container_width=True, hide_index=True)

# =========================================================
# EXPORTAR CSV
# =========================================================
csv = df_filtrado.drop(columns=["mes_ano"], errors="ignore").to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇️ Exportar lançamentos (.csv)",
    data=csv,
    file_name=f"financeiro_{mes_selecionado}.csv",
    mime="text/csv",
)
