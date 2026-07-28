def correlacoes(df):

    colunas = [
        "Marketing",
        "Leads",
        "Corretores",
        "Turnover",
        "VSO"
    ]


    return (
        df[colunas]
        .corr()
    )
