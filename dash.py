import streamlit as st
import pandas as pd
import plotly.express as px

# Configurações iniciais
st.set_page_config(page_title="Dashboard NF", layout="wide")

# CSS para personalizar o visual
st.markdown("""
    <style>
    .card {
        background-color: #2c2c2c;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        color: white;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    .big-font {
        font-size: 25px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Upload do Excel
st.sidebar.header("📤 Upload do Arquivo")
arquivo = st.sidebar.file_uploader("Envie a planilha (.xlsx)", type=["xlsx"])

if arquivo:
    df = pd.read_excel(arquivo, sheet_name="Historico")

    df.columns = df.columns.str.strip()
    df = df[df["Valor Bruto"].notna()]
    df["Data da Solicitação"] = pd.to_datetime(df["Data da Solicitação"], errors='coerce')

    # Filtro Razão Social
    razoes = df["Razão Social Emissor"].dropna().unique()
    filtro_razao = st.sidebar.multiselect("🔍 Filtrar por Razão Social Emissor", razoes, default=razoes)
    df_filtrado = df[df["Razão Social Emissor"].isin(filtro_razao)]

    # Tabs
    aba1, aba2, aba3 = st.tabs(["📊 Visão Geral", "📈 Evolução Mensal", "📂 Tabela de Dados"])

    with aba1:
        st.subheader("📊 Visão Geral")

        total_notas = len(df_filtrado)
        total_valor = df_filtrado["Valor Bruto"].sum()
        empresas_unicas = df_filtrado["Razão Social Emissor"].nunique()
        automacoes = df_filtrado["Automação existia?"].value_counts().to_dict()

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"<div class='card'><h3>🧾 Total de Notas</h3><p class='big-font'>{total_notas}</p></div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='card'><h3>💰 Valor Bruto Total</h3><p class='big-font'>R$ {total_valor:,.2f}</p></div>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<div class='card'><h3>🏢 Empresas Únicas</h3><p class='big-font'>{empresas_unicas}</p></div>", unsafe_allow_html=True)
        with col4:
            auto = automacoes.get("Sim", 0)
            manual = automacoes.get("Não", 0)
            st.markdown(f"<div class='card'><h3>⚙️ Automatizadas</h3><p class='big-font'>{auto} Sim / {manual} Não</p></div>", unsafe_allow_html=True)

        st.markdown("---")

        grafico_df = df_filtrado.groupby("Razão Social Emissor")["Valor Bruto"].sum().reset_index()
        fig = px.bar(
            grafico_df.sort_values("Valor Bruto", ascending=False),
            x="Razão Social Emissor",
            y="Valor Bruto",
            color="Valor Bruto",
            color_continuous_scale="Blues",
            labels={"Valor Bruto": "Valor (R$)"},
            title="Valor Bruto por Razão Social"
        )
        fig.update_layout(
            xaxis_tickangle=-45,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='#1e1e1e',
            font=dict(color="white"),
            title_font=dict(size=20)
        )
        st.plotly_chart(fig, use_container_width=True)

    with aba2:
        st.subheader("📈 Evolução Mensal do Valor Bruto")

        df_filtrado['AnoMes'] = df_filtrado['Data da Solicitação'].dt.to_period("M").astype(str)
        mensal = df_filtrado.groupby("AnoMes")["Valor Bruto"].sum().reset_index()

        fig2 = px.line(
            mensal, x="AnoMes", y="Valor Bruto",
            markers=True, title="Evolução Mensal",
            labels={"AnoMes": "Ano-Mês", "Valor Bruto": "Valor (R$)"}
        )
        fig2.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='#1e1e1e',
            font=dict(color="white")
        )
        st.plotly_chart(fig2, use_container_width=True)

    with aba3:
        st.subheader("📂 Tabela de Dados Filtrados")
        st.dataframe(df_filtrado, use_container_width=True)

        # Botão para download
        csv = df_filtrado.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Baixar CSV", data=csv, file_name="dados_filtrados.csv", mime="text/csv")
else:
    st.warning("Envie uma planilha .xlsx com a aba 'Historico'.")
