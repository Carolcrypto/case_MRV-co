def resumo_cidades(df):

    resultado = (
        df.groupby("Cidade")
        .agg({
            "VSO":"mean",
            "Leads":"sum",
            "Corretores":"mean",
            "Turnover":"mean"
        })
        .reset_index()
    )


    pior = (
        resultado
        .sort_values(
            "VSO"
        )
        .head(5)
    )


    melhor = (
        resultado
        .sort_values(
            "VSO",
            ascending=False
        )
        .head(5)
    )


    return pior, melhor
