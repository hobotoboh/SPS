import plotly.graph_objs as go
def adding_additional_traces(df, fig):
    fig.add_trace(go.Scattermapbox(
        lat=df['latitude'],
        lon=df['longitude'],
        mode='markers',
        marker=dict(symbol='ferry', size=10),
        hoverinfo='skip',
        showlegend=False,
    ))

    fig.add_trace(go.Densitymapbox(
        lat=df['latitude'],
        lon=df['longitude'],
        z=df['carbon_footprint'],
        radius=50,
        hoverinfo='skip',
        showscale=False,
        visible=False
    ))

def adding_traces_on_frames(df, pd, frames, datetime, all_results):
    unique_times = df['time'].unique()
    unique_times = sorted(unique_times)
    previous_data = pd.DataFrame()

    for time in unique_times:

        filtered_df = df[df['time'] == time]

        if not previous_data.empty:
            no_future_time_options = previous_data.loc[~previous_data['mmsi'].isin(filtered_df['mmsi'])]
        else:
            no_future_time_options = pd.DataFrame()

        combined_df = pd.concat([filtered_df, no_future_time_options])
        all_results = pd.concat([all_results, combined_df]).drop_duplicates()

        dataShips = [
            go.Scattermapbox(
                lat=combined_df['latitude'],
                lon=combined_df['longitude'],
                mode='markers',
                marker=dict(symbol='ferry', size=10),
                opacity=0.8,
                hovertemplate=(
                        '<b>MMSI</b>: %{customdata[0]}<br>' +
                        '<b>latitude</b>: %{customdata[1]:.5f}<br>' +
                        '<b>longitude</b>: %{customdata[2]:.5f}<br>'
                ),
                customdata=df[['mmsi', 'latitude', 'longitude']].values,
            ),
        ]

        dataFootprint = [go.Densitymapbox(
            lat=all_results['new_latitude'],
            lon=all_results['new_longitude'],
            z=all_results['carbon_footprint'],
            radius=13,
            showscale=False,
            hovertemplate=(
                    '<b>NOx</b>: %{customdata[0]}<br>' +
                    '<b>CO</b>: %{customdata[1]:.2f}<br>' +
                    '<b>CH</b>: %{customdata[2]:.2f}<br>' +
                    '<b>C</b>: %{customdata[3]:.2f}<br>' +
                    '<b>SO2</b>: %{customdata[4]:.2f}<br>' +
                    '<b>Overall</b>: %{customdata[5]:.2f}<br>'
            ),
            customdata=df[['carbon_footprint_NOx', 'carbon_footprint_CO',
                           'carbon_footprint_CH', 'carbon_footprint_C',
                           'carbon_footprint_SO2', 'carbon_footprint']].values,
        )]

        epoch_time = datetime.datetime.fromtimestamp(time)
        time_formatted = epoch_time.strftime('%Y-%m-%d %H:%M')

        frame = go.Frame(
            name=str(time_formatted),
            data=dataFootprint + dataShips,
        )

        previous_data = combined_df

        frames.append(frame)

    return all_results

def adding_sliders_and_frames(fig, frames):
    sliders = [
        dict(
            active=0,
            pad={"b": 50, "r": 50, "l": 50},
            steps=[
                dict(
                    method="animate",
                    args=[[frame.name], {"frame": {"duration": 300, "redraw": True}, "mode": "immediate"}],
                    label=str(frame.name),
                )
                for frame in frames
            ],
        )
    ]

    fig.update_layout(
        legend_orientation="h",
        updatemenus=[
            dict(
                direction="left",
                pad={"r": 10, "t": 80},
                x=0.1,
                xanchor="right",
                y=0,
                yanchor="top",
                showactive=False,
            )
        ],
        sliders=sliders,
    )

    fig.frames = frames

def map_display(fig, token):
    map_center = go.layout.mapbox.Center(lat=60, lon=26.5)

    fig.update_layout(mapbox={
        'accesstoken': token,
        'style': "outdoors",
        'center': map_center,
        'zoom': 6.5},
        plot_bgcolor='#D2B48C', paper_bgcolor='#D2B48C',
        margin={"r": 0, "t": 50, "l": 0, "b": 10})

    return fig
