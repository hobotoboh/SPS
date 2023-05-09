import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import sqlite3

print('Получение данных...')
filename = r"A:\Files\Diploma\AIS_10_01_2021.db"
token = open("key.mapbox_token").read()

try:
    # получение данных из БД
    conn = sqlite3.connect(filename)

    sql = ("SELECT DISTINCT mmsi, "
           "longitude, "
           "latitude, "
           "referencePointA, "
           "referencePointB, "
           "referencePointC, "
           "referencePointD, "
           "draught, "
           "sog,"
           "time "
           "FROM location ")


    """sql = ("SELECT DISTINCT ais1.mmsi, "
           "ais1.longitude AS longitude, "
           "ais1.latitude AS latitude, "
           "Vessels.referencePointA, "
           "Vessels.referencePointB, "
           "Vessels.referencePointC, "
           "Vessels.referencePointD, "
           "Vessels.draught, "
           "ais1.sog, "
           "ais1.timestampExternal AS time "
           "FROM ais1, Vessels "
           "WHERE ais1.mmsi = Vessels.mmsi "
           "LIMIT 10"
           "")"""

    df = pd.read_sql(sql, conn)

    # расчет валовой вместимости
    df['gt'] = df.apply(
        lambda row: ((row['referencePointA'] + row['referencePointB'])
                    * (row['referencePointC'] + row['referencePointD'])
                     * row['draught']/10)/2,
        axis=1)

    # нахождение мощности
    df['impact'] = ''

    df.loc[(df['gt'] < 1000) & (df['sog'] != 0), 'impact'] = 23

    df.loc[(df['gt'] <= 3000) & (df['gt'] >= 1000) & (df['sog'] != 0), 'impact'] = 21

    df.loc[(df['gt'] <= 5000) & (df['gt'] >= 3000) & (df['sog'] != 0), 'impact'] = 22

    df.loc[(df['gt'] <= 15000) & (df['gt'] >= 5000) & (df['sog'] != 0), 'impact'] = 20

    df.loc[(df['gt'] <= 50000) & (df['gt'] >= 15000) & (df['sog'] != 0), 'impact'] = 17

    df.loc[(df['gt'] > 50000) & (df['sog'] != 0), 'impact'] = 16





    data_to_empty_df = {
        'longitude': 0,
        'latitude': 0,
    }

    empty_df = pd.DataFrame([data_to_empty_df])

    print(df.head(50))
    print(df.tail(50))
    fig = px.scatter_mapbox(empty_df,
                            lon=empty_df['longitude'],
                            lat=empty_df['latitude'],
                            zoom=5,
                            )

    frames = []

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
        z=df['impact'],
        radius=50,
        hoverinfo='skip',
        showscale=False,
        visible=False
        ))

    unique_times = df['time'].unique()
    previous_data = pd.DataFrame()
    all_results = pd.DataFrame()

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
            lat=all_results['latitude'],
            lon=all_results['longitude'],
            z=all_results['impact'],
            radius=10,
            showscale=False
        )]

        frame = go.Frame(
            name=str(time),
            data=dataFootprint + dataShips,
        )

        previous_data = combined_df

        frames.append(frame)

    sliders = [
        dict(
            active=0,
            pad={"t": 50},
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
        title='Ааааааааа',
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
                type="buttons",
                buttons=[
                    dict(label="►", method="animate", args=[None, {"fromcurrent": True}]),
                    dict(
                        label="❚❚",
                        method="animate",
                        args=[
                            [None],
                            {
                                "frame": {"duration": 0, "redraw": False},
                                "mode": "immediate",
                                "transition": {"duration": 0},
                            },
                        ],
                    ),
                ],
            )
        ],
        sliders=sliders,
    )

    fig.frames = frames

    map_center = go.layout.mapbox.Center(lat=60, lon=26.5)

    fig.update_layout(mapbox={
        'accesstoken': token,
        'style': "outdoors",
        'center': map_center,
        'zoom': 6.5},
        margin={"r": 0, "t": 50, "l": 0, "b": 10})

    # Отображаем карту
    fig.show()

    print("График построен")


except Exception as exc:
    print(exc)
finally:
    if conn:
        conn.close()
        print('Соединение прекращено')