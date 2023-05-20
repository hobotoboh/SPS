import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import sqlite3
import datetime

import gross_tonnage
import power
import carbon_footprint

filename = r"A:\Files\Diploma\AIS_10_01_2021.db"
token = open("key.mapbox_token").read()

try:
    # получение данных из БД
    conn = sqlite3.connect(filename)

    """sql = ("SELECT DISTINCT mmsi, "
           "longitude, "
           "latitude, "
           "referencePointA, "
           "referencePointB, "
           "referencePointC, "
           "referencePointD, "
           "draught, "
           "sog,"
           "time "
           "FROM location ")"""

    print("NOTE! Date must be in this format 'YYYY-MM-DD'")
    """startdate = input("Enter the first date: ")
    enddate = input("Enter the second date: ")

    startdate = datetime.datetime.strptime(startdate, "%Y-%m-%d")
    enddate = datetime.datetime.strptime(enddate, "%Y-%m-%d")

    enddate += datetime.timedelta(days=1, milliseconds=-1)

    startdate = int(startdate.timestamp()) * 1000
    enddate = int(enddate.timestamp()) * 1000"""

    startdate = 1636848000000
    enddate = 1637366399000

    sql = ("SELECT DISTINCT ais1.mmsi, "
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
           "AND ais1.timestampExternal >= :startdate "
           "AND ais1.timestampExternal <= :enddate "
           ""
           ""
           "")
    print('Получение данных...')

    df = pd.read_sql(sql, conn, params={"startdate": startdate, "enddate": enddate})

    gross_tonnage.calculation(df)
    power.finding_power(df)

    carbon_footprint.carbon_footprint_parameters(df)
    carbon_footprint.cf_Sea_Canal(df)
    carbon_footprint.cf_low_speed_and_maneuvering(df)
    carbon_footprint.cf_mooring(df)
    carbon_footprint.cf_calculation(df)

    # Карта судов и углеродного следа
    data_to_empty_df = {
        'longitude': 0,
        'latitude': 0,
    }

    empty_df = pd.DataFrame([data_to_empty_df])

    print(df['time'].tail(1))

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
        z=df['carbon_footprint'],
        radius=50,
        hoverinfo='skip',
        showscale=False,
        visible=False
        ))

    df['time'] = df['time'].divide(10000)
    df['time'] = df['time'].round(0)
    df['time'] = df['time'].multiply(10)

    unique_times = df['time'].unique()
    unique_times = sorted(unique_times)
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
            z=all_results['carbon_footprint'],
            radius=10,
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


    # Гистограмма углеродного следа по дням

    carbon_results = pd.DataFrame({'time': all_results['time'],
                                   'carbon_footprint_NOx': all_results['carbon_footprint_NOx'],
                                   'carbon_footprint_CH': all_results['carbon_footprint_CH'],
                                   'carbon_footprint_C': all_results['carbon_footprint_C'],
                                   'carbon_footprint_CO': all_results['carbon_footprint_CO'],
                                   'carbon_footprint_SO2': all_results['carbon_footprint_SO2']})


    carbon_results['time'] = carbon_results['time'].apply(
        lambda x: datetime.datetime.fromtimestamp(x).strftime('%Y-%m-%d'))


    print(carbon_results.head(15))
    carbon_results['time'] = pd.to_datetime(carbon_results['time'])
    carbon_results = carbon_results.groupby('time').sum().reset_index()

    carbon_results_melted = carbon_results.melt(id_vars='time', var_name='column', value_name='value')

    print(carbon_results.head(10))

    fig_plot = px.bar(carbon_results_melted,
                      x='time',
                      y='value',
                      color='column',
                      title='Результаты углеродного следа по дням')


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

    map_center = go.layout.mapbox.Center(lat=60, lon=26.5)

    fig.update_layout(mapbox={
        'accesstoken': token,
        'style': "outdoors",
        'center': map_center,
        'zoom': 6.5},
        margin={"r": 0, "t": 50, "l": 0, "b": 10})

    # График углеродного следа
    #fig_graph


    # Отображаем карту
    #fig.show()
    fig_plot.show()



    #map_div = fig.to_html(full_html=False)

    """with open('myplot.html', 'w', encoding="utf-8") as f:
        f.write('<!DOCTYPE html>\n')
        f.write('<html>\n')
        f.write('<head>\n')
        f.write('<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>\n')
        f.write('</head>\n')
        f.write('<body>\n')
        f.write(map_div + '\n')
        f.write('</body>\n')
        f.write('</html>\n')"""

    print("График построен")


except Exception as exc:
    print(exc)
finally:
    if conn:
        conn.close()
        print('Соединение прекращено')