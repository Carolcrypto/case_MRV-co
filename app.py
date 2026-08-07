import streamlit as st
import pandas as pd
import plotly.express as px

from leitura import carregar_dados
from simulacoes import simular_vso


# ==========================================
# CONFIGURAÇÃO
# ==========================================

st.set_page_config(
    page_title="Diagnóstico Comercial MRV",
    page_icon="🏠",
    layout="wide"
)


# ==========================================
# CARREGAMENTO
# ==========================================

@st.cache_data
def carregar_base():

    caminho = (
        "dados/Base de Dados- Case Planning & Business Analytics.xlsx"
    )

    df = carregar_dados(caminho)

    return df



try:

    df = carregar_base()

except Exception as erro:

    st.error("Erro ao carregar a base.")

    st.write(erro)

    st.stop()



# ==========================================
# LIMPEZA INICIAL
# ==========================================

df.columns = (
    df.columns
    .str.strip()
)


# converter colunas numéricas

colunas_numericas = [

    "VOLUME DE LEADS",
    "DOCUMENTAÇÃO ENVIADA",
    "CPF ANALISADO",
    "CPF APROVADO",
    "UNIDADES VENDIDAS",
    "ESTOQUE",
    "VSO (VENDAS SOB OFERTA)",
    "VOLUME TOTAL DE CORRETORES",
    "Corretores Novatos (0 a 3 Meses)",
    "Corretores Iniciantes (4 a 6 Meses)",
    "Corretores em Formação (7 a 12 Meses)",
    "Corretores Expert (> 12 Meses)",
    "% EQUIPE PRODUTIVA",
    "VOLUME DE GERENTES",
    "TURNOVER CORRETORES",
    "TURNOVER GERENTES",
    "INVESTIMENTO MARKETING"

]


for coluna in colunas_numericas:

    if coluna in df.columns:

        df[coluna] = pd.to_numeric(
            df[coluna],
            errors="coerce"
        )



# ==========================================
# TITULO
# ==========================================

st.title(
    "🏠 Diagnóstico Executivo Comercial MRV"
)


st.write(
    """
    Dashboard executivo para análise de performance,
    identificação de oportunidades e simulação
    de cenários comerciais.
    """
)



# ==========================================
# FILTROS
# ==========================================

st.sidebar.header(
    "Filtros"
)


cidades = sorted(
    df["CIDADE"]
    .dropna()
    .unique()
)


cidade_selecionada = st.sidebar.multiselect(
    "Cidade",
    cidades,
    default=cidades
)



df_filtrado = df[
    df["CIDADE"]
    .isin(cidade_selecionada)
]


# ==========================================
# RESUMO EXECUTIVO
# ==========================================

st.header("Resumo Executivo")


media_vso = df_filtrado[
    "VSO (VENDAS SOB OFERTA)"
].mean()


cidade_melhor = (
    df_filtrado
    .groupby("CIDADE")
    ["VSO (VENDAS SOB OFERTA)"]
    .mean()
    .idxmax()
)


cidade_pior = (
    df_filtrado
    .groupby("CIDADE")
    ["VSO (VENDAS SOB OFERTA)"]
    .mean()
    .idxmin()
)


col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "VSO Médio Geral",
        f"{media_vso:.2f}%"
    )


with col2:

    st.metric(
        "🏆 Cidade Benchmark",
        cidade_melhor
    )


with col3:

    st.metric(
        "⚠️ Maior Atenção",
        cidade_pior
    )


st.write(
f"""
### Diagnóstico inicial

A cidade **{cidade_melhor}** apresenta o melhor desempenho comercial
considerando o VSO médio.

A cidade **{cidade_pior}** apresenta maior oportunidade de melhoria,
devendo ser investigados fatores como conversão do funil,
produtividade comercial e eficiência de marketing.
"""
)



# ==========================================
# 1 - VISÃO GERAL
# ==========================================

st.header(
    "1. Visão Geral"
)



col1, col2, col3, col4 = st.columns(4)



with col1:

    st.metric(
        "Registros analisados",
        len(df_filtrado)
    )



with col2:

    vso = df_filtrado[
        "VSO (VENDAS SOB OFERTA)"
    ].mean()

    st.metric(
        "VSO Médio",
        f"{vso:.2f}%"
    )



with col3:

    leads = df_filtrado[
        "VOLUME DE LEADS"
    ].sum()

    st.metric(
        "Total de Leads",
        f"{leads:,.0f}"
    )



with col4:

    corretores = df_filtrado[
        "VOLUME TOTAL DE CORRETORES"
    ].mean()

    st.metric(
        "Média Corretores",
        f"{corretores:.0f}"
    )



# ==========================================
# PERFORMANCE POR CIDADE
# ==========================================

st.subheader(
    "Performance por cidade"
)



vso_cidade = (

    df_filtrado
    .groupby("CIDADE")
    [
        "VSO (VENDAS SOB OFERTA)"
    ]
    .mean()
    .reset_index()

)



grafico = px.bar(

    vso_cidade,
    x="CIDADE",
    y="VSO (VENDAS SOB OFERTA)",
    title="VSO médio por cidade"

)


st.plotly_chart(
    grafico,
    use_container_width=True
)

# ==========================================
# FUNIL COMERCIAL
# ==========================================

st.subheader(
    "Funil Comercial"
)


funil = pd.DataFrame({

    "Etapa": [

        "Leads",
        "Documentação Enviada",
        "CPF Analisado",
        "CPF Aprovado",
        "Unidades Vendidas"

    ],

    "Quantidade": [

        df_filtrado["VOLUME DE LEADS"].sum(),

        df_filtrado["DOCUMENTAÇÃO ENVIADA"].sum(),

        df_filtrado["CPF ANALISADO"].sum(),

        df_filtrado["CPF APROVADO"].sum(),

        df_filtrado["UNIDADES VENDIDAS"].sum()

    ]

})


grafico_funil = px.funnel(

    funil,

    x="Quantidade",

    y="Etapa",

    title="Conversão do Funil Comercial"

)


st.plotly_chart(

    grafico_funil,

    use_container_width=True

)



# Taxas de conversão

st.subheader(
    "Taxas de Conversão"
)


conversoes = pd.DataFrame({

    "Indicador": [

        "Lead → Documentação",

        "Documentação → CPF Analisado",

        "CPF Analisado → CPF Aprovado",

        "CPF Aprovado → Venda"

    ],

    "Conversão (%)": [

        (
            df_filtrado["DOCUMENTAÇÃO ENVIADA"].sum()
            /
            df_filtrado["VOLUME DE LEADS"].sum()
            * 100
        ),

        (
            df_filtrado["CPF ANALISADO"].sum()
            /
            df_filtrado["DOCUMENTAÇÃO ENVIADA"].sum()
            * 100
        ),

        (
            df_filtrado["CPF APROVADO"].sum()
            /
            df_filtrado["CPF ANALISADO"].sum()
            * 100
        ),

        (
            df_filtrado["UNIDADES VENDIDAS"].sum()
            /
            df_filtrado["CPF APROVADO"].sum()
            * 100
        )

    ]

})


st.dataframe(
    conversoes.style.format(
        {
            "Conversão (%)": "{:.2f}%"
        }
    ),
    use_container_width=True
)

# ==========================================
# 2 - DIAGNÓSTICO EXECUTIVO
# ==========================================


st.header(
    "2. Diagnóstico Executivo"
)



ranking = (

    df_filtrado
    .groupby("CIDADE")
    .agg(

        VSO=(
            "VSO (VENDAS SOB OFERTA)",
            "mean"
        ),

        Leads=(
            "VOLUME DE LEADS",
            "sum"
        ),

        Turnover=(
            "TURNOVER CORRETORES",
            "mean"
        )

    )
    .reset_index()

)



col1, col2 = st.columns(2)



with col1:

    st.subheader(
        "🏆 Cidades Benchmark"
    )

    st.dataframe(

        ranking
        .sort_values(
            "VSO",
            ascending=False
        )
        .head(10)

    )



with col2:

    st.subheader(
        "⚠️ Cidades com Atenção"
    )

    st.dataframe(

        ranking
        .sort_values(
            "VSO"
        )
        .head(10)

    )


# ==========================================
# 3 - ANÁLISE EXPLORATÓRIA
# ==========================================


st.header(
    "3. Análise Exploratória"
)



st.subheader(
    "Correlação dos indicadores"
)



colunas_correlacao = [

    "VSO (VENDAS SOB OFERTA)",
    "VOLUME DE LEADS",
    "INVESTIMENTO MARKETING",
    "VOLUME TOTAL DE CORRETORES",
    "TURNOVER CORRETORES",
    "% EQUIPE PRODUTIVA"

]



correlacao = (

    df_filtrado[
        colunas_correlacao
    ]
    .corr()

)



fig_corr = px.imshow(

    correlacao,
    text_auto=True,
    title="Influência dos indicadores no VSO"

)



st.plotly_chart(
    fig_corr,
    use_container_width=True
)



st.subheader(
    "Relação entre Marketing e Leads"
)



grafico_marketing = px.scatter(

    df_filtrado,

    x="INVESTIMENTO MARKETING",

    y="VOLUME DE LEADS",

    title="Marketing x Geração de Leads"

)


st.plotly_chart(
    grafico_marketing,
    use_container_width=True
)

# ==========================================
# TURNOVER X PRODUTIVIDADE
# ==========================================

st.subheader(
    "Impacto do Turnover na Produtividade"
)


turnover_prod = (

    df_filtrado
    .groupby("CIDADE")
    .agg(

        Turnover=(
            "TURNOVER CORRETORES",
            "mean"
        ),

        Produtividade=(
            "% EQUIPE PRODUTIVA",
            "mean"
        ),

        VSO=(
            "VSO (VENDAS SOB OFERTA)",
            "mean"
        )

    )
    .reset_index()

)



grafico_turnover = px.scatter(

    turnover_prod,

    x="Turnover",

    y="Produtividade",

    size="VSO",

    color="CIDADE",

    title="Turnover x Produtividade da Equipe"

)


st.plotly_chart(

    grafico_turnover,

    use_container_width=True

)

# ==========================================
# ANÁLISE DO FUNIL COMERCIAL
# ==========================================

st.subheader(
    "Funil Comercial"
)


funil = pd.DataFrame({

    "Etapa": [

        "Leads",

        "Documentação Enviada",

        "CPF Analisado",

        "CPF Aprovado",

        "Unidades Vendidas"

    ],


    "Quantidade": [

        df_filtrado["VOLUME DE LEADS"].sum(),

        df_filtrado["DOCUMENTAÇÃO ENVIADA"].sum(),

        df_filtrado["CPF ANALISADO"].sum(),

        df_filtrado["CPF APROVADO"].sum(),

        df_filtrado["UNIDADES VENDIDAS"].sum()

    ]

})


grafico_funil = px.funnel(

    funil,

    x="Quantidade",

    y="Etapa",

    title="Conversão do Funil Comercial"

)


st.plotly_chart(
    grafico_turnover,
    use_container_width=True,
    key="turnover_produtividade"
)


# ==========================================
# ANÁLISE DA EQUIPE COMERCIAL
# ==========================================

st.subheader(
    "Influência da estrutura comercial no VSO"
)


equipe = (

    df_filtrado
    .groupby("CIDADE")
    .agg(

        VSO=(
            "VSO (VENDAS SOB OFERTA)",
            "mean"
        ),

        Corretores=(
            "VOLUME TOTAL DE CORRETORES",
            "mean"
        ),

        Produtividade=(
            "% EQUIPE PRODUTIVA",
            "mean"
        ),

        Turnover=(
            "TURNOVER CORRETORES",
            "mean"
        )

    )
    .reset_index()

)


st.dataframe(
    equipe.sort_values(
        "VSO",
        ascending=False
    ),
    use_container_width=True
)

# ==========================================
# IMPACTO DE NOVOS LANÇAMENTOS
# ==========================================

st.subheader(
    "Impacto de novos lançamentos no desempenho comercial"
)


lancamentos = (

    df_filtrado
    .groupby("EMPREENDIMENTOS LANÇADOS")
    .agg(

        VSO_Medio=(
            "VSO (VENDAS SOB OFERTA)",
            "mean"
        ),

        Leads_Medio=(
            "VOLUME DE LEADS",
            "mean"
        ),

        Vendas_Medias=(
            "UNIDADES VENDIDAS",
            "mean"
        ),

        Estoque_Medio=(
            "ESTOQUE",
            "mean"
        )

    )
    .reset_index()

)


lancamentos["Tipo"] = (
    lancamentos["EMPREENDIMENTOS LANÇADOS"]
    .map(
        {
            1:"Com lançamento",
            0:"Sem lançamento"
        }
    )
)


st.dataframe(
    lancamentos[
        [
            "Tipo",
            "VSO_Medio",
            "Leads_Medio",
            "Vendas_Medias",
            "Estoque_Medio"
        ]
    ]
)



grafico_lancamento = px.bar(

    lancamentos,

    x="Tipo",

    y="VSO_Medio",

    title="VSO médio: com vs sem lançamento"

)


st.plotly_chart(
    grafico_lancamento,
    use_container_width=True
)

# ==========================================
# 4 - PRINCIPAIS INSIGHTS
# ==========================================

st.header(
    "4. Principais Insights"
)


# Médias gerais

vso_medio = df_filtrado[
    "VSO (VENDAS SOB OFERTA)"
].mean()


cidade_melhor = (
    ranking
    .sort_values(
        "VSO",
        ascending=False
    )
    .iloc[0]
)


cidade_pior = (
    ranking
    .sort_values(
        "VSO"
    )
    .iloc[0]
)


turnover_medio = df_filtrado[
    "TURNOVER CORRETORES"
].mean()


produtividade_media = df_filtrado[
    "% EQUIPE PRODUTIVA"
].mean()



# ------------------------------------------
# Achados quantitativos
# ------------------------------------------

st.subheader(
    "📊 Achados quantitativos"
)


st.write(

f"""
- O VSO médio analisado foi de **{vso_medio:.2f}%**.

- A cidade com melhor desempenho foi
**{cidade_melhor['CIDADE']}**, com VSO médio de
**{cidade_melhor['VSO']:.2f}%**.

- A cidade com menor desempenho foi
**{cidade_pior['CIDADE']}**, com VSO médio de
**{cidade_pior['VSO']:.2f}%**.

- A produtividade média da equipe foi de
**{produtividade_media:.2f}%**.

- O turnover médio de corretores foi de
**{turnover_medio:.2f}%**.
"""

)



# ------------------------------------------
# Insights de negócio
# ------------------------------------------

st.subheader(
    "💡 Insights de negócio"
)


st.info(

"""
- Cidades com maior VSO devem ser utilizadas como
benchmark para replicação de práticas comerciais.

- Regiões com baixo VSO devem ser avaliadas considerando
eficiência do funil, produtividade da equipe e capacidade
de conversão.

- O aumento de eficiência da equipe pode representar uma
alavanca mais sustentável do que apenas ampliar volume
de corretores.
"""

)



# ------------------------------------------
# Hipóteses
# ------------------------------------------

st.subheader(
    "🔎 Hipóteses relevantes"
)


st.warning(

"""
- A diferença de desempenho entre cidades pode estar
relacionada à maturidade da equipe comercial.

- Altos níveis de turnover podem reduzir produtividade
e impactar a conversão.

- Investimentos em marketing podem gerar maior retorno
quando combinados com equipes mais produtivas.
"""

)



# ------------------------------------------
# Oportunidades
# ------------------------------------------

st.subheader(
    "🚀 Oportunidades identificadas"
)


st.success(

"""
1. Replicar práticas das cidades benchmark.

2. Desenvolver planos específicos para cidades abaixo
da média.

3. Aumentar conversão do funil comercial.

4. Melhorar retenção e produtividade dos corretores.
"""

)


# ==========================================
# 5 - SENSIBILIDADE DAS VARIÁVEIS
# ==========================================

st.header(
    "5. Sensibilidade das Variáveis"
)


st.write(
"""
Análise das variáveis com maior associação ao VSO.
Valores próximos de 1 indicam relação positiva,
enquanto valores próximos de -1 indicam relação inversa.
"""
)


sensibilidade = (

    correlacao[
        "VSO (VENDAS SOB OFERTA)"
    ]
    .drop(
        "VSO (VENDAS SOB OFERTA)"
    )
    .sort_values(
        ascending=False
    )
    .reset_index()

)


sensibilidade.columns = [
    "Variável",
    "Correlação com VSO"
]


st.dataframe(
    sensibilidade,
    use_container_width=True
)



grafico_sensibilidade = px.bar(

    sensibilidade,

    x="Correlação com VSO",

    y="Variável",

    orientation="h",

    title="Variáveis associadas ao VSO"

)



st.plotly_chart(

    grafico_sensibilidade,

    use_container_width=True

)



# Recomendações automáticas

st.subheader(
    "Principais alavancas recomendadas"
)


top3 = (
    sensibilidade
    .head(3)
    ["Variável"]
    .tolist()
)


for item in top3:

    st.success(
        f"Priorizar melhoria em: {item}"
    )


# ==========================================
# 6 - PLANO DE AÇÃO
# ==========================================

st.header(
    "6. Plano de Ação Executivo"
)


st.write(
"""
Recomendações priorizadas considerando os principais
fatores relacionados ao desempenho comercial.
"""
)



plano_acao = pd.DataFrame({

    "Prioridade":[
        "1",
        "2",
        "3",
        "4"
    ],


    "Ação Recomendada":[

        "Aumentar produtividade da equipe comercial",

        "Atuar nas cidades com menor VSO",

        "Reduzir turnover de corretores",

        "Otimizar investimento em marketing"
    ],


    "Problema Atacado":[

        "Baixa eficiência na conversão de oportunidades",

        "Diferença de performance entre regiões",

        "Perda de conhecimento e relacionamento comercial",

        "Possível baixa eficiência na geração de demanda"
    ],


    "Indicador Impactado":[

        "% Equipe Produtiva e VSO",

        "VSO e Unidades Vendidas",

        "Turnover e Produtividade",

        "Leads e Conversão"
    ],


    "Benefício Esperado":[

        "Maior aproveitamento da equipe atual",

        "Recuperação de mercados abaixo do benchmark",

        "Maior estabilidade operacional",

        "Maior retorno sobre investimento"
    ]

})



st.dataframe(

    plano_acao,

    use_container_width=True,

    hide_index=True

)


# ==========================================
# 7 - CENÁRIOS E SIMULAÇÕES
# ==========================================

st.header(
    "7. Cenários e Simulações"
)


st.write(
"""
Simulações de impacto considerando possíveis
alavancas comerciais identificadas na análise.
"""
)



# Valores atuais

vendas_atual = df_filtrado[
    "UNIDADES VENDIDAS"
].sum()


vso_atual = df_filtrado[
    "VSO (VENDAS SOB OFERTA)"
].mean()


produtividade_atual = df_filtrado[
    "% EQUIPE PRODUTIVA"
].mean()



# -------------------------------
# Cenário 1 - Conversão
# -------------------------------

st.subheader(
    "📈 Cenário 1 - Aumento de conversão do funil"
)


aumento_conversao = st.slider(

    "Melhoria esperada na conversão (%)",

    0,

    50,

    10

)


novas_vendas_conversao = (

    vendas_atual *

    (1 + aumento_conversao / 100)

)


st.metric(

    "Vendas estimadas",

    f"{novas_vendas_conversao:,.0f}"

)



# -------------------------------
# Cenário 2 - Produtividade
# -------------------------------

st.subheader(
    "👥 Cenário 2 - Aumento da produtividade da equipe"
)


aumento_produtividade = st.slider(

    "Aumento da produtividade (%)",

    0,

    50,

    10

)



nova_produtividade = (

    produtividade_atual *

    (1 + aumento_produtividade / 100)

)



st.metric(

    "Nova produtividade estimada",

    f"{nova_produtividade:.2f}%"

)



# -------------------------------
# Cenário 3 - Turnover
# -------------------------------

st.subheader(
    "🔄 Cenário 3 - Redução de turnover"
)



turnover_atual = df_filtrado[
    "TURNOVER CORRETORES"
].mean()



reducao_turnover = st.slider(

    "Redução esperada de turnover (%)",

    0,

    50,

    10

)



novo_turnover = (

    turnover_atual *

    (1 - reducao_turnover / 100)

)



st.metric(

    "Novo turnover estimado",

    f"{novo_turnover:.2f}%"

)



# Resumo executivo

st.subheader(
    "Impacto potencial"
)


st.info(
f"""
Caso a companhia consiga:

- aumentar conversão em {aumento_conversao}%;
- elevar produtividade em {aumento_produtividade}%;
- reduzir turnover em {reducao_turnover}%;

existe potencial de melhoria dos indicadores comerciais,
principalmente através de maior eficiência do funil
e melhor aproveitamento da equipe existente.
"""
)

# ==========================================
# 8 - LIMITAÇÕES DA ANÁLISE
# ==========================================

st.header(
    "8. Limitações da Análise"
)


st.write(
"""
Toda análise baseada em dados possui limitações.
Os resultados apresentados devem ser interpretados
como direcionadores para tomada de decisão.
"""
)



st.subheader(
    "✅ Perguntas respondidas com maior confiança"
)


st.success(
"""
- Quais cidades apresentam melhor e pior desempenho de VSO.

- Quais indicadores apresentam maior associação com vendas.

- Como marketing, leads, equipe comercial e turnover
se relacionam com os resultados.

- Quais regiões apresentam maior oportunidade de melhoria.
"""
)



st.subheader(
    "🔎 Hipóteses ainda abertas"
)


st.warning(
"""
- A relação entre investimento em marketing e vendas
pode depender da qualidade dos leads gerados.

- Diferenças entre cidades podem estar relacionadas a
fatores externos como mercado local, concorrência e perfil
dos clientes.

- O impacto real de treinamentos e ações comerciais
precisa ser validado com acompanhamento histórico.
"""
)



st.subheader(
    "📌 Dados adicionais recomendados"
)


st.info(
"""
Para decisões definitivas, seria interessante complementar
a análise com:

- Histórico mensal mais longo de vendas.

- Dados de conversão por etapa do funil.

- Perfil dos clientes e motivos de perda.

- Dados de concorrência e mercado regional.

- Informações sobre campanhas específicas de marketing.
"""
)
