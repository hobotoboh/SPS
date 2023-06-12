def percentage_days(px, df, pd):
    df['date'] = df['date'].dt.strftime('%Y-%m-%d')
    day_counts = df.groupby('date').size().reset_index(name='count')

    fig = px.pie(day_counts, values='count', names='date')

    fig.update_layout(plot_bgcolor='#D2B48C', paper_bgcolor='#D2B48C',)

    return fig

def percentage_mmsi(px, df):

    mmsi_counts = df.groupby('mmsi').size().reset_index(name='count')

    fig = px.pie(mmsi_counts, values='count', names='mmsi')

    fig.update_layout(plot_bgcolor='#D2B48C', paper_bgcolor='#D2B48C', showlegend=False)
    fig.update_traces(textinfo='none')

    return fig
