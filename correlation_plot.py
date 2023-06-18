import plotly.graph_objects as go

def correlation_power(pd, df):
    carbon_results = pd.DataFrame({'power': df['power'],
                                   'carbon_footprint_NOx': df['carbon_footprint_NOx'],
                                   'carbon_footprint_CH': df['carbon_footprint_CH'],
                                   'carbon_footprint_C': df['carbon_footprint_C'],
                                   'carbon_footprint_CO': df['carbon_footprint_CO'],
                                   'carbon_footprint_SO2': df['carbon_footprint_SO2']})

    color_map = {'carbon_footprint_NOx': 'red',
                 'carbon_footprint_CH': 'green',
                 'carbon_footprint_C': 'blue',
                 'carbon_footprint_CO': 'orange',
                 'carbon_footprint_SO2': 'purple'}

    #carbon_results = carbon_results.groupby('power').sum().reset_index()

    carbon_results_melted = carbon_results.melt(id_vars='power', var_name='column', value_name='value')
    carbon_results_melted['color'] = carbon_results_melted['column'].apply(lambda x: color_map[x])

    fig = go.Figure(data=go.Scattergl(
        x=carbon_results_melted['power'],
        y=carbon_results_melted['value'],
        mode='markers',
        marker=dict(
            color=carbon_results_melted['color'],
            line_width=1,
            size=15,

        ),
        hovertemplate=('<b>power</b>: %{customdata[0]}<br>' +
                      '<b>%{customdata[1]}</b>: %{customdata[2]}<br>'),
        customdata=carbon_results_melted[['power', 'column', 'value']]
    ))
    fig.update_layout(plot_bgcolor='#FFDAB9', paper_bgcolor='#FFDAB9',
                      title='Связь между мощностью и углеродным следом')

    return fig


def correlation_gt(pd, df):
    carbon_results = pd.DataFrame({'gt': df['gt'],
                                   'carbon_footprint_NOx': df['carbon_footprint_NOx'],
                                   'carbon_footprint_CH': df['carbon_footprint_CH'],
                                   'carbon_footprint_C': df['carbon_footprint_C'],
                                   'carbon_footprint_CO': df['carbon_footprint_CO'],
                                   'carbon_footprint_SO2': df['carbon_footprint_SO2']})

    color_map = {'carbon_footprint_NOx': 'red',
                 'carbon_footprint_CH': 'green',
                 'carbon_footprint_C': 'blue',
                 'carbon_footprint_CO': 'orange',
                 'carbon_footprint_SO2': 'purple'}

    carbon_results_melted = carbon_results.melt(id_vars='gt', var_name='column', value_name='value')
    carbon_results_melted['color'] = carbon_results_melted['column'].apply(lambda x: color_map[x])

    fig = go.Figure(data=go.Scattergl(
        x=carbon_results_melted['gt'],
        y=carbon_results_melted['value'],
        mode='markers',
        marker=dict(
            color=carbon_results_melted['color'],
            line_width=1,
            size=15,

        ),
        hovertemplate=('<b>gross tonnage</b>: %{customdata[0]}<br>' +
                       '<b>%{customdata[1]}</b>: %{customdata[2]}<br>'),
        customdata=carbon_results_melted[['gt', 'column', 'value']]
    ))
    fig.update_layout(plot_bgcolor='#FFDAB9', paper_bgcolor='#FFDAB9',
                      title='Связь между валовой вместимостью и углеродным следом')

    return fig



