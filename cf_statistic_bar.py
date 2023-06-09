def bar_display(pd, all_results, datetime, px):
    carbon_results = pd.DataFrame({'time': all_results['time'],
                                   'carbon_footprint_NOx': all_results['carbon_footprint_NOx'],
                                   'carbon_footprint_CH': all_results['carbon_footprint_CH'],
                                   'carbon_footprint_C': all_results['carbon_footprint_C'],
                                   'carbon_footprint_CO': all_results['carbon_footprint_CO'],
                                   'carbon_footprint_SO2': all_results['carbon_footprint_SO2']})

    carbon_results['time'] = carbon_results['time'].apply(
        lambda x: datetime.datetime.fromtimestamp(x).strftime('%Y-%m-%d'))

    carbon_results['time'] = pd.to_datetime(carbon_results['time'])
    carbon_results = carbon_results.groupby('time').sum().reset_index()

    carbon_results_melted = carbon_results.melt(id_vars='time', var_name='column', value_name='value')

    fig_plot = px.bar(carbon_results_melted,
                      x='time',
                      y='value',
                      color='column',
                      title='Результаты углеродного следа по дням')

    fig_plot.update_layout(plot_bgcolor='#D2B48C', paper_bgcolor='#D2B48C',
                           xaxis_title="Дата",
                           yaxis_title="Углеродный след",
                           )

    return fig_plot