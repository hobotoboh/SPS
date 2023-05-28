import plotly.express as px

def correlation_matrix(pd, df):
    correlation_matrix = df.corr()
    print(correlation_matrix)

def correlation(pd, df):
    df['time'] = pd.to_datetime(df['time'])
    df['time'] = (df['time'] - pd.Timestamp("1970-01-01")) // pd.Timedelta('1D')
    correlation_matrix(pd, df)

    fig = px.scatter(
        x=list(correlation_matrix.columns),
        y=list(correlation_matrix.columns),
        hover_name='x',
        text=' correlation',
        labels={
            'x': 'Factors',
            'y': 'Factors',
            'text': 'Correlation',
        },
        title='Correlation Matrix'
    )

    fig.update_layout(
        width=800,
        height=600,
        margin=dict(l=60, r=40, b=60, t=40)
    )

    fig.show()
