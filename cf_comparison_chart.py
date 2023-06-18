import plotly.graph_objs as go

def chart_display(all_results):
    all_results['shipType'] = all_results['shipType'].astype(str)

    average_carbon_footprint = all_results.groupby('shipType')['carbon_footprint'].mean()

    fig = go.Figure()

    for ship_type, avg_footprint in average_carbon_footprint.items():
        fig.add_trace(go.Bar(x=[ship_type], y=[avg_footprint], name=ship_type))

    fig.update_layout(
        title="Среднее значение углеродного следа разных типов судов",
        xaxis_title="Типы судов",
        yaxis_title="Углеродный след",
        plot_bgcolor='#FFDAB9', paper_bgcolor='#FFDAB9',
    )

    return fig
