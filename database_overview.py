def percentage_days(px, df, pd):
    df['date'] = df['date'].dt.strftime('%Y-%m-%d')
    day_counts = df.groupby('date').size().reset_index(name='count')

    fig = px.pie(day_counts, values='count', names='date')

    fig.update_layout(plot_bgcolor='#FFDAB9', paper_bgcolor='#FFDAB9',)

    return fig

def percentage_mmsi(px, df):

    shipTypeCounts = df.groupby('shipType').size().reset_index(name='count')

    fig = px.pie(shipTypeCounts, values='count', names='shipType')

    fig.update_layout(plot_bgcolor='#FFDAB9', paper_bgcolor='#FFDAB9')

    return fig
