import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime
import locale
import base64
from pathlib import Path
import re
from PIL import Image
import requests
from io import BytesIO
from tenacity import _unset
import streamlit as st
from pathlib import Path
import re
from PIL import Image
import requests
from io import BytesIO
from tenacity import _unset

# Config
st.set_page_config(page_title="Visão Geral de Incidentes", layout="wide", page_icon="📊")


# Font Awesome
st.markdown("""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
""", unsafe_allow_html=True)

# Seletor de tema
modo_claro = st.sidebar.toggle("🌗 Sair do modo claro", value=True)

# Define o CSS com base na escolha
if modo_claro:
    cor_fundo = "#F5F5F5"
    cor_sidebar = "#FFFFFF"
    cor_texto = "#947952"
    cor_kpi_fundo = "#E6E6E6"
else:
    cor_fundo = "#000000"
    cor_sidebar = "#000000F8"
    cor_texto = "#987748"
    cor_kpi_fundo = "#010618"
# Insere o CSS dinâmico
st.markdown(f"""
<style>
html {{
    color-scheme: {'light' if modo_claro else 'dark'};
}}

html, body, .main {{
    background-color: {cor_fundo} !important;
    color: {cor_texto} !important;
}}

.block-container {{
    padding: 1rem 2rem;
    max-width: 100% !important;
    width: 100% !important;
}}

header {{
    visibility: hidden;
}}

section[data-testid="stSidebar"] {{
    background-color: {cor_sidebar} !important;
    color: {cor_texto} !important;
}}

section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div,
section[data-testid="stSidebar"] p {{
    color: {cor_texto} !important;
}}

input, select, textarea, button {{
    background-color: {cor_sidebar} !important;
    color: {cor_texto} !important;
    border: 1px solid #A6A6A6 !important;
    border-radius: 6px !important;
}}

option {{
    background-color: {cor_sidebar} !important;
    color: {cor_texto} !important;
}}

input[type="checkbox"], input[type="radio"] {{
    accent-color: #A6A6A6;
}}

select:hover, input:hover, textarea:hover {{
    border-color: #A6A6A6 !important;
}}

select:focus, input:focus, textarea:focus {{
    border-color: #5BC0BE !important;
    box-shadow: 0 0 0 0.1rem #A6A6A6 !important;
    outline: none !important;
}}

.kpi-container {{
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    justify-content: center;
}}

.kpi {{
    background-color: {cor_kpi_fundo};
    padding: 20px;
    border-radius: 12px;
    color: {cor_texto};
    display: flex;
    align-items: center;
    gap: 15px;
    box-shadow: 0 0 15px rgba(0,0,0,0.1);
    max-width: 250px;
    min-width: 150px;
    height: 120px;
    box-sizing: border-box;
    transition: all 0.3s ease;
}}

.kpi i {{
    font-size: 28px;
    padding: 15px;
    border-radius: 10px;
    background-color: #3A506B;
    color: #FFFFFF;
    display: flex;
    justify-content: center;
    align-items: center;
    min-width: 50px;
    min-height: 50px;
}}

.kpi .text {{
    display: flex;
    flex-direction: column;
    justify-content: center;
    flex: 1;
    overflow: hidden;
}}

.kpi .value {{
    font-size: 1.4rem;
    font-weight: bold;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}

.kpi .label {{
    font-size: 0.8rem;
    color: #A6A6A6;
    word-break: break-word;
}}

@media (max-width: 768px) {{
    .kpi {{
        flex-direction: column;
        height: auto;
        min-width: 100%;
    }}
}}
</style>
""", unsafe_allow_html=True)

def check_password():
    if "senha_correta" not in st.session_state:
        st.session_state.senha_correta = False

    if not st.session_state.senha_correta:
        senha = st.text_input("Senha:", type="password")
        if senha == "Feminina@1105":
            st.session_state.senha_correta = True
        else:
            if senha:
                st.error("Senha incorreta. Tente novamente.")
        return False
    else:
        return True

    
# Carregar dados
df = pd.read_csv("https://docs.google.com/spreadsheets/d/e/2PACX-1vQoWbw52QOM46a6cXlB_rbpgRx3mvHxPW-NbcBqH5rGz0paWFkHpZx8jEjPpsBjnAeEtJTZng0rpHcx/pub?output=csv")

# Tratamento de datas
df["Dia/hora do incidente:"] = pd.to_datetime(df["Dia/hora do incidente:"], errors='coerce', dayfirst=True)
df = df.dropna(subset=["Dia/hora do incidente:"])
df = df.sort_values("Dia/hora do incidente:")

meses_pt = {1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho",
            7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"}

df["MêsAnoLabel"] = df["Dia/hora do incidente:"].apply(lambda x: f"{meses_pt[x.month]} de {x.year}")
df["MêsAnoValor"] = df["Dia/hora do incidente:"].apply(lambda x: f"{x.year}-{x.month:02d}")

# Sidebar com filtros organizados
with st.sidebar:
    with st.expander("🔎 Filtros configurados:", expanded=True):
        visualizar_todos = st.checkbox("Visualizar todos os dados")

        if not visualizar_todos:
            # Filtro por data
            filtro_tipo = st.radio("Tipo de Filtro por Data", ["Mês/Ano", "Período"], help="Escolha se deseja filtrar por mês ou intervalo de datas.")

            if filtro_tipo == "Mês/Ano":
                opcoes = df[["MêsAnoValor", "MêsAnoLabel"]].drop_duplicates().sort_values("MêsAnoValor", ascending=False)
                opcao_selecionada = st.selectbox(
                    "Selecione o Mês/Ano:",
                    options=opcoes["MêsAnoValor"],
                    format_func=lambda x: opcoes.set_index("MêsAnoValor").loc[x, "MêsAnoLabel"]
                )
                df = df[df["MêsAnoValor"] == opcao_selecionada]
            else:
                min_data = df["Dia/hora do incidente:"].min().date()
                max_data = df["Dia/hora do incidente:"].max().date()
                data_inicio, data_fim = st.date_input(
                    "Período do Incidente:",
                    value=(min_data, max_data),
                    min_value=min_data,
                    max_value=max_data
                )
                data_inicio = datetime.combine(data_inicio, datetime.min.time())
                data_fim = datetime.combine(data_fim, datetime.max.time())
                df = df[(df["Dia/hora do incidente:"] >= data_inicio) & (df["Dia/hora do incidente:"] <= data_fim)]

            # Filtro por loja
            if "Local do incidente:" in df.columns:
                loja_options = df["Local do incidente:"].dropna().unique()
                selected_loja = st.multiselect("Local do Incidente", loja_options, default=list(loja_options))
                df = df[df["Local do incidente:"].isin(selected_loja)]
                
            if "Tipo de incidente:" in df.columns:
                tipos_incidentes = df["Tipo de incidente:"].dropna().unique().tolist()
                opcoes = ["Selecionar Todos"] + tipos_incidentes
                selected_tipos = st.multiselect("Tipo de Incidente:", opcoes, default=opcoes)

            if "Selecionar Todos" not in selected_tipos:
                df = df[df["Tipo de incidente:"].isin(selected_tipos)]
            else:
                st.info("Todos os tipos de incidentes estão sendo exibidos.")
                
            if "Nome" in df.columns:
                responsaveis = df["Nome"].dropna().unique()
                responsavel_sel = st.selectbox("Filtrar por Responsável", ["Todos"] + list(responsaveis))
                if responsavel_sel != "Todos":
                    df = df[df["Nome"] == responsavel_sel] 
                    
                def classificar_turno(hora):
                    if 5 <= hora < 12:
                        return "Manhã"
                    elif 12 <= hora < 18:
                        return "Tarde"
                    else:
                        return "Noite"

                df["Turno"] = df["Dia/hora do incidente:"].dt.hour.apply(classificar_turno)

                turnos_disponiveis = df["Turno"].unique()
                turnos_selecionados = st.multiselect("Turno do Incidente", turnos_disponiveis, default=list(turnos_disponiveis))
                df = df[df["Turno"].isin(turnos_selecionados)]       
            
            df_filtrado = df.copy()

    with st.expander("🔍 Filtro Personalizado", expanded=False):
        colunas_texto = df.select_dtypes(include=["object", "string"]).columns.tolist()
        
        if colunas_texto:
            coluna_filtro = st.selectbox("Escolha a coluna para filtrar:", colunas_texto)
            texto_filtro = st.text_input(f"Filtrar valores em '{coluna_filtro}':")

            if texto_filtro:
                df = df[df[coluna_filtro].fillna("").str.contains(texto_filtro, case=False, na=False)]

            df_filtrado = df.copy()
    
    
# KPIs
col1, col2, col3, col4 = st.columns(4)

with col1:
    kpi_html = f"""
    <div class='kpi'>
        <i class="fa-regular fa-file"></i>
        <div class='text'>
            <div class='value'>{df_filtrado.shape[0]}</div>
            <div class='label'>Total de Incidentes</div>
        </div>
    </div>
    """
    st.markdown(kpi_html, unsafe_allow_html=True)

with col2:
    desta_inci = df_filtrado["Tipo de incidente:"].mode(). iloc[0] if not df_filtrado["Tipo de incidente:"].empty else '-'
    kpi_html = f"""
    <div class='kpi'>
        <i class="fa-solid fa-user-secret"></i>
        <div class='text'>
            <div class='value'>{desta_inci}</div>
            <div class='label'>Destaque de incidente</div>
        </div>
    </div>
    """
    st.markdown(kpi_html, unsafe_allow_html=True)

with col3:
    df_filtrado['Hora do Incidente'] = df_filtrado['Dia/hora do incidente:'].dt.strftime('%Hh')
    hora_mais_frequente = df_filtrado['Hora do Incidente'].mode().iloc[0] if not df_filtrado['Hora do Incidente'].empty else '-'
    kpi_html = f"""
    <div class='kpi'>
        <i class="fas fa-clock"></i>
        <div class='text'>
            <div class='value'>{hora_mais_frequente}</div>
            <div class='label'>Hora Mais Frequente</div>
        </div>
    </div>
    """
    st.markdown(kpi_html, unsafe_allow_html=True)

with col4:
    loja = df_filtrado['Local do incidente:'].mode().iloc[0] if 'Local do incidente:' in df_filtrado.columns and not df_filtrado.empty else '-'
    kpi_html = f"""
    <div class='kpi'>
        <i class="fas fa-store"></i>
        <div class='text'>
            <div class='value'>{loja}</div>
            <div class='label'>Loja Destaque</div>
        </div>
    </div>
    """
    st.markdown(kpi_html, unsafe_allow_html=True)

 #Gráficos - Linha 2
st.markdown("---")
st.markdown("## Desempenho por fiscais ")
col5, col6 = st.columns(2)
with col5:
    atendente_counts = df_filtrado["Nome"].value_counts().reset_index()
    atendente_counts.columns = ["Atendente", "Quantidade"]
    fig3 = px.bar(atendente_counts, x="Atendente", y="Quantidade", title="👤 Registros por Fiscal")
    fig3.update_traces(marker_color="#6DADF1")
    st.plotly_chart(fig3, use_container_width=True)
    
with col6:
    status_counts = df_filtrado["Nome"].value_counts().reset_index()
    status_counts.columns = ["Nome", "Quantidade"]
    fig4 = px.pie(status_counts, names="Nome", values="Quantidade", title="📌 Incidente por Fiscal")
    fig4.update_traces(marker=dict(colors=["#23B0D7","#0d4158"]))
    st.plotly_chart(fig4, use_container_width=True)
    
col7, col8 = st.columns(2)
with col7:
    
    if "Turno" in df_filtrado.columns:
        st.markdown("## 🌗 Incidentes por Turno")
        turno_counts = df_filtrado["Turno"].value_counts().reset_index()
        turno_counts.columns = ["Turno", "Quantidade"]

        fig_turno = px.pie(turno_counts, names="Turno", values="Quantidade", title="🕐 Distribuição de Incidentes por Turno")
        st.plotly_chart(fig_turno, use_container_width=True)
        
with col8:
# Pizza - Registro de Fiscais por colaborador
    regi_colabora = (df_filtrado.groupby(["Nome", "Tipo de incidente:"]).size().reset_index(name="count"))
    # Cria gráfico de barras
fig_regi_colabora = px.pie(
    regi_colabora,
    x="Nome",
    y="count",
    color="Tipo de incidente:",
    title="Total de registro de loja e colaborador"
)
st.plotly_chart(fig_regi_colabora, use_container_width=True)

# Gráfico - Incidentes por Hora
st.markdown("## 📊 Incidentes por Hora do Dia")
df_filtrado['Hora'] = df_filtrado['Dia/hora do incidente:'].dt.hour
incidentes_por_hora = df_filtrado.groupby("Hora").size().reset_index(name="Quantidade")
fig_horas = px.bar(incidentes_por_hora, x="Hora", y="Quantidade", title="Incidentes por Hora", labels={"Hora": "Hora do Dia", "Quantidade": "Quantidade de Incidentes"}, template="plotly_dark")
fig_horas.update_traces(marker_color='#5BC0BE')
st.plotly_chart(fig_horas, use_container_width=True)


# Gráfico - Incidentes por Colaborador
if "Responsável" in df_filtrado.columns:
    st.markdown("## 👤 Incidentes por Colaborador")
    incidentes_por_colaborador = df_filtrado["Responsável"].value_counts().reset_index()
    incidentes_por_colaborador.columns = ["Colaborador", "Quantidade"]
    fig_colab = px.bar(incidentes_por_colaborador, x="Colaborador", y="Quantidade", title="Incidentes por Colaborador", labels={"Colaborador": "Responsável", "Quantidade": "Quantidade de Incidentes"}, template="plotly_dark")
    fig_colab.update_traces(marker_color='#5BC0BE')
    st.plotly_chart(fig_colab, use_container_width=True)

# Gráfico - Incidentes por Loja
if "Local do incidente:" in df_filtrado.columns:
    st.markdown("## 🏪 Incidentes por Loja")
    incidentes_por_loja = df_filtrado["Local do incidente:"].value_counts().reset_index()
    incidentes_por_loja.columns = ["Loja", "Quantidade"]
    fig_lojas = px.bar(incidentes_por_loja, x="Loja", y="Quantidade", title="Incidentes por Loja", labels={"Loja": "Local do Incidente", "Quantidade": "Quantidade de Incidentes"}, template="plotly_dark")
    fig_lojas.update_traces(marker_color='#5BC0BE')
    st.plotly_chart(fig_lojas, use_container_width=True)

# Gráfico - numero de incidente por cada loja
    st.markdown("## 🏬 Total de incidentes por loja e tipo:")

# Agrupa e conta
total_inci = (
    df_filtrado
    .groupby(["Local do incidente:", "Tipo de incidente:"])
    .size()
    .reset_index(name="count")
)

# Cria gráfico de barras
fig_total_inci = px.bar(
    total_inci,
    x="Local do incidente:",
    y="count",
    color="Tipo de incidente:",
    labels={"count": "Número de incidentes"},
    title="Incidentes por Loja e Tipo"
)

# Exibe o gráfico responsivamente
st.plotly_chart(fig_total_inci, use_container_width=True)
    
# Gráfico - Linha 3 (empilhado)
st.markdown("### 📑 Incidentes por Fiscal e Tipo")
inci_fiscal = df_filtrado.groupby(["Nome", "Tipo de incidente:"]).size().reset_index(name="Quantidade")
fig5 = px.bar(
    inci_fiscal,
    x="Nome",
    y="Quantidade",
    color="Tipo de incidente:",
    title="🧩 Registro por Colaborador (Empilhado por Tipo de Incidente)",
)
fig5.update_layout(barmode="stack")
st.plotly_chart(fig5, use_container_width=True)

# Gráfico - Incidentes por Hora
df_filtrado["Hora"] = df_filtrado["Dia/hora do incidente:"].dt.hour
incidentes_por_hora = df_filtrado.groupby("Hora").size().reset_index(name="Quantidade")

fig_horas = px.bar(
    incidentes_por_hora,
    x="Hora",
    y="Quantidade",
    title="⏰ Incidentes por Hora do Dia",
    labels={"Hora": "Hora do Dia", "Quantidade": "Quantidade de Incidentes"}
)
fig_horas.update_traces(marker_color="#10C2FE")

st.plotly_chart(fig_horas, use_container_width=True)


# Calcular diferença de tempo entre ocorrências
df_sorted = df_filtrado.sort_values("Dia/hora do incidente:").copy()
df_sorted["Hora"] = df_sorted["Dia/hora do incidente:"].dt.hour
df_sorted["Delta"] = df_sorted["Dia/hora do incidente:"].diff()

# Remover a primeira linha (Delta será NaT)
df_sorted = df_sorted.dropna(subset=["Delta"])

# Converter para minutos
df_sorted["Delta_minutos"] = df_sorted["Delta"].dt.total_seconds() / 60

# Agrupar por hora e calcular a média de tempo entre ocorrências
media_tempo_por_hora = df_sorted.groupby("Hora")["Delta_minutos"].mean().reset_index()
media_tempo_por_hora.columns = ["Hora", "Tempo Médio entre Ocorrências (min)"]

# Gráfico
fig_tempo = px.line(
    media_tempo_por_hora,
    x="Hora",
    y="Tempo Médio entre Ocorrências (min)",
    markers=True,
    title="🕒 Tempo Médio entre Incidentes por Hora do Dia",
    labels={"Hora": "Hora do Dia", "Tempo Médio entre Ocorrências (min)": "Tempo Médio (min)"},
)
fig_tempo.update_traces(line=dict(color="#23C2F7"))

st.plotly_chart(fig_tempo, use_container_width=True)

#Gráfico Distribuição
pivot_tipo_loja = df_filtrado.pivot_table(index="Local do incidente:", columns="Tipo de incidente:", aggfunc="size", fill_value=0)
fig_heatmap = px.imshow(pivot_tipo_loja, labels=dict(x="Tipo de Incidente", y="Loja", color="Quantidade"), 
                        title="🚨 Frequência de Tipos de Incidentes por Loja", aspect="auto", color_continuous_scale="Viridis")
st.plotly_chart(fig_heatmap, use_container_width=True)

fig_hist = px.histogram(df_sorted, x="Delta_minutos", nbins=30, title="🧮 Distribuição de Tempo Entre Ocorrências (min)", 
                        labels={"Delta_minutos": "Intervalo (min)"}, template="plotly_dark")
fig_hist.update_traces(marker_color="#6A5ACD")
st.plotly_chart(fig_hist, use_container_width=True)


# Mapear dia da semana manualmente
dias_semana = {
    0: "segunda-feira",
    1: "terça-feira",
    2: "quarta-feira",
    3: "quinta-feira",
    4: "sexta-feira",
    5: "sábado",
    6: "domingo"
}

# Criar coluna com nome do dia da semana
df_filtrado["Dia da Semana"] = df_filtrado["Dia/hora do incidente:"].dt.dayofweek.map(dias_semana)

# Definir ordem correta
ordem_dias = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado", "domingo"]

# Contar e reordenar
incidentes_dia_semana = df_filtrado["Dia da Semana"].value_counts().reindex(ordem_dias).reset_index()
incidentes_dia_semana.columns = ["Dia da Semana", "Quantidade"]

# Criar gráfico
fig_dia_semana = px.bar(
    incidentes_dia_semana,
    x="Dia da Semana",
    y="Quantidade",
    title="📅 Incidentes por Dia da Semana",
    template="plotly_dark"
)
fig_dia_semana.update_traces(marker_color="#F9A03F")
st.plotly_chart(fig_dia_semana, use_container_width=True)

with st.expander("📊 Visualizar dados brutos", expanded=False):
    mostrar = st.toggle("👁️ Mostrar dados")
    if mostrar:
        st.dataframe(df, use_container_width=True)

