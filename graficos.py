import plotly.express as px


def grafico_vso_cidade(df):

    dados = (
        df.groupby("Cidade")
        ["VSO"]
        .mean()
        .reset_index()
    )


    fig = px.bar(
        dados,
        x="Cidade",
        y="VSO",
        title="VSO médio por cidade"
    )

    return fig
