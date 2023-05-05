# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
# Press Ctrl+F8 to toggle the breakpoint.

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
    sql = ("SELECT mmsi, "
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
    df = pd.read_sql(sql, conn)

    # расчет валовой вместимости
    df['gt'] = df.apply(
        lambda row: ((row['referencePointA'] + row['referencePointB'])
                    * (row['referencePointC'] + row['referencePointD'])
                     * row['draught']/10)/2,
        axis=1)

    # нахождение мощности
    df['impact'] = ''

    df.loc[df['gt'] < 1000, 'impact'] = 23

    df.loc[(df['gt'] <= 3000) & (df['gt'] >= 1000), 'impact'] = 21

    df.loc[(df['gt'] <= 5000) & (df['gt'] >= 3000), 'impact'] = 22

    df.loc[(df['gt'] <= 15000) & (df['gt'] >= 5000), 'impact'] = 20

    df.loc[(df['gt'] <= 50000) & (df['gt'] >= 15000), 'impact'] = 17

    df.loc[df['gt'] > 50000, 'impact'] = 16

    print(df.head(8))
    fig = px.scatter_mapbox(df,
                            lon=df['longitude'],
                            lat=df['latitude'],
                            zoom=5,
                            size_max=1,
                            width=1200,
                            height=600,
                            title='AIS',
                            hover_name=df['mmsi'],
                            )


    fig2 = px.scatter_mapbox(df,
                            lon=df['longitude'],
                            lat=df['latitude'],
                            size=df['referencePointA']*10,
                            hover_name=df['mmsi'],
                            opacity= 0.5
                            )

    # fig.add_scattermapbox(
    #     lat=df['latitude'],
    #     lon=df['longitude'],
    #     mode='markers',
    #     marker=dict(symbol='ferry',
    #                 size=10),
    #     name='Ships',
    #     hoverinfo='skip',
    # )

    fig.add_trace(fig2.data[0])

    for i in range(len(df)):
        fig.add_trace(go.Scattermapbox(
            mode="lines",
            lon=[df['longitude'][i], df['longitude'][i]+1],
            lat=[df['latitude'][i], df['latitude'][i]+1],
            marker={'size': 10},
            name=f'Carbon Footprint of {df["mmsi"][i]}'))

    frames = []

    unique_times = df['time'].unique()

    for time in unique_times:

        filtered_df = df[df['time'] == time]

        frame = go.Frame(
            name=str(time),
            data=[
                # Add the data traces for the current frame
                # You can modify this part based on your specific requirements
                go.Scattermapbox(
                    lat=filtered_df['latitude'],
                    lon=filtered_df['longitude'],
                    mode='markers',
                    marker=dict(symbol='ferry', size=10),
                    name='Ships',
                    hoverinfo='skip',
                )
            ]
        )

        # Add the frame to the frames list
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
        title='По России на поезде',
        legend_orientation="h",
        mapbox_style="open-street-map",
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

    # Add the frames to the figure
    fig.frames = frames

    map_center = go.layout.mapbox.Center(lat=60, lon=26.5)

    fig.update_layout(mapbox = {
        'accesstoken': token,
        'style': "outdoors",
        'center': map_center,
        'zoom': 6.5},
                      margin={"r" : 0,"t" : 50,"l" : 0,"b" : 10})

    # Отображаем карту
    fig.show()

    print("График построен")


except Exception as exc:
    print(exc)
finally:
    if conn:
        conn.close()
        print('Соединение прекращено')
