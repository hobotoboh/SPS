import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import sqlite3
import datetime

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
    startdate = input("Enter the first date: ")
    enddate = input("Enter the second date: ")

    startdate = datetime.datetime.strptime(startdate, "%Y-%m-%d")
    enddate = datetime.datetime.strptime(enddate, "%Y-%m-%d")

    enddate += datetime.timedelta(days=1, milliseconds=-1)

    startdate = int(startdate.timestamp()) * 1000
    enddate = int(enddate.timestamp()) * 1000

    startdate = 1620731537000
    enddate = 1622373137000

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
           "LIMIT 1000 "
           "")

    print('Получение данных...')
    df = pd.read_sql(sql, conn, params={"startdate": startdate, "enddate": enddate})

    # расчет валовой вместимости
    df['gt'] = df.apply(
        lambda row: ((row['referencePointA'] + row['referencePointB'])
                    * (row['referencePointC'] + row['referencePointD'])
                     * row['draught']/10)/2,
        axis=1)

    # нахождение мощности
    df['power'] = ''

    # мощность главных двигателей при режиме прохода по Морскому каналу
    df.loc[(df['gt'] < 1000) & (df['latitude'] < 60.03)
           & (df['latitude'] > 59.84) & (df['longitude'] > 29.4702) & (df['sog'] > 1), 'power'] = 480
    df.loc[(df['gt'] <= 3000) & (df['gt'] >= 1000) & (df['latitude'] < 60.03)
           & (df['latitude'] > 59.84) & (df['longitude'] > 29.4702) & (df['sog'] > 1), 'power'] = 1000
    df.loc[(df['gt'] <= 5000) & (df['gt'] > 3000) & (df['latitude'] < 60.03)
           & (df['latitude'] > 59.84) & (df['longitude'] > 29.4702) & (df['sog'] > 1), 'power'] = 1700
    df.loc[(df['gt'] <= 15000) & (df['gt'] > 5000) & (df['latitude'] < 60.03)
           & (df['latitude'] > 59.84) & (df['longitude'] > 29.4702) & (df['sog'] > 1), 'power'] = 3500
    df.loc[(df['gt'] <= 50000) & (df['gt'] > 15000) & (df['latitude'] < 60.03)
           & (df['latitude'] > 59.84) & (df['longitude'] > 29.4702) & (df['sog'] > 1), 'power'] = 7500
    df.loc[(df['gt'] > 50000) & (df['latitude'] < 60.03)
           & (df['latitude'] > 59.84) & (df['longitude'] > 29.4702) & (df['sog'] > 1), 'power'] = 25000

    # мощность главных двигателей при режиме малого хода
    df.loc[(df['gt'] < 1000) & (df['power'] == '') & (df['sog'] > 1), 'power'] = 150
    df.loc[(df['gt'] <= 3000) & (df['gt'] >= 1000) & (df['power'] == '') & (df['sog'] > 1), 'power'] = 310
    df.loc[(df['gt'] <= 5000) & (df['gt'] > 3000) & (df['power'] == '') & (df['sog'] > 1), 'power'] = 530
    df.loc[(df['gt'] <= 15000) & (df['gt'] > 5000) & (df['power'] == '') & (df['sog'] > 1), 'power'] = 1750
    df.loc[(df['gt'] <= 50000) & (df['gt'] > 15000) & (df['power'] == '') & (df['sog'] > 1), 'power'] = 3750
    df.loc[(df['gt'] > 50000) & (df['power'] == '') & (df['sog'] > 1), 'power'] = 12500

    # мощность главных двигателей при режиме маневрирования
    df.loc[(df['gt'] < 1000) & (df['sog'] < 1) & (df['sog'] >= 0.4), 'power'] = 90
    df.loc[(df['gt'] <= 3000) & (df['gt'] >= 1000) & (df['sog'] < 1) & (df['sog'] >= 0.4), 'power'] = 190
    df.loc[(df['gt'] <= 5000) & (df['gt'] > 3000) & (df['sog'] < 1) & (df['sog'] >= 0.4), 'power'] = 320
    df.loc[(df['gt'] <= 15000) & (df['gt'] > 5000) & (df['sog'] < 1) & (df['sog'] >= 0.4), 'power'] = 1050
    df.loc[(df['gt'] <= 50000) & (df['gt'] > 15000) & (df['sog'] < 1) & (df['sog'] >= 0.4), 'power'] = 1500
    df.loc[(df['gt'] > 50000) & (df['sog'] < 1) & (df['sog'] >= 0.4), 'power'] = 5000

    # мощность вспомогательных двигателей при режиме стоянки судна
    df.loc[(df['gt'] < 1000) & (df['sog'] < 0.4) & (df['sog'] >= 0), 'power'] = 80
    df.loc[(df['gt'] <= 3000) & (df['gt'] >= 1000) & (df['sog'] < 0.4) & (df['sog'] >= 0), 'power'] = 150
    df.loc[(df['gt'] <= 5000) & (df['gt'] > 3000) & (df['sog'] < 0.4) & (df['sog'] >= 0), 'power'] = 300
    df.loc[(df['gt'] <= 15000) & (df['gt'] > 5000) & (df['sog'] < 0.4) & (df['sog'] >= 0), 'power'] = 500
    df.loc[(df['gt'] <= 50000) & (df['gt'] > 15000) & (df['sog'] < 0.4) & (df['sog'] >= 0), 'power'] = 700
    df.loc[(df['gt'] > 50000) & (df['sog'] < 0.4) & (df['sog'] >= 0), 'power'] = 3000

    # параметры углеродного следа
    df['carbon_footprint_NOx'] = ''
    df['carbon_footprint_CO'] = ''
    df['carbon_footprint_CH'] = ''
    df['carbon_footprint_C'] = ''
    df['carbon_footprint_SO2'] = ''
    df['carbon_footprint'] = ''

    # нахождение выбросов загрязняющих веществ для судов с режимом прохода по Морскому каналу
    df.loc[(df['gt'] < 1000) & (df['power'] == 480), 'carbon_footprint_NOx'] = 13
    df.loc[(df['gt'] < 1000) & (df['power'] == 480), 'carbon_footprint_CO'] = 8
    df.loc[(df['gt'] < 1000) & (df['power'] == 480), 'carbon_footprint_CH'] = 1.3
    df.loc[(df['gt'] < 1000) & (df['power'] == 480), 'carbon_footprint_C'] = 1.4
    df.loc[(df['gt'] < 1000) & (df['power'] == 480), 'carbon_footprint_SO2'] = 0.75

    df.loc[(df['gt'] <= 3000) & (df['gt'] >= 1000) & (df['power'] == 1000), 'carbon_footprint_NOx'] = 14
    df.loc[(df['gt'] <= 3000) & (df['gt'] >= 1000) & (df['power'] == 1000), 'carbon_footprint_CO'] = 5
    df.loc[(df['gt'] <= 3000) & (df['gt'] >= 1000) & (df['power'] == 1000), 'carbon_footprint_CH'] = 1
    df.loc[(df['gt'] <= 3000) & (df['gt'] >= 1000) & (df['power'] == 1000), 'carbon_footprint_C'] = 1.3
    df.loc[(df['gt'] <= 3000) & (df['gt'] >= 1000) & (df['power'] == 1000), 'carbon_footprint_SO2'] = 0.75

    df.loc[(df['gt'] <= 5000) & (df['gt'] > 3000) & (df['power'] == 1700), 'carbon_footprint_NOx'] = 14
    df.loc[(df['gt'] <= 5000) & (df['gt'] > 3000) & (df['power'] == 1700), 'carbon_footprint_CO'] = 5
    df.loc[(df['gt'] <= 5000) & (df['gt'] > 3000) & (df['power'] == 1700), 'carbon_footprint_CH'] = 1
    df.loc[(df['gt'] <= 5000) & (df['gt'] > 3000) & (df['power'] == 1700), 'carbon_footprint_C'] = 1.3
    df.loc[(df['gt'] <= 5000) & (df['gt'] > 3000) & (df['power'] == 1700), 'carbon_footprint_SO2'] = 0.69

    df.loc[(df['gt'] <= 15000) & (df['gt'] > 5000) & (df['power'] == 3500), 'carbon_footprint_NOx'] = 16
    df.loc[(df['gt'] <= 15000) & (df['gt'] > 5000) & (df['power'] == 3500), 'carbon_footprint_CO'] = 3
    df.loc[(df['gt'] <= 15000) & (df['gt'] > 5000) & (df['power'] == 3500), 'carbon_footprint_CH'] = 0.4
    df.loc[(df['gt'] <= 15000) & (df['gt'] > 5000) & (df['power'] == 3500), 'carbon_footprint_C'] = 0.7
    df.loc[(df['gt'] <= 15000) & (df['gt'] > 5000) & (df['power'] == 3500), 'carbon_footprint_SO2'] = 0.63

    df.loc[(df['gt'] <= 50000) & (df['gt'] > 15000) & (df['power'] == 7500), 'carbon_footprint_NOx'] = 17
    df.loc[(df['gt'] <= 50000) & (df['gt'] > 15000) & (df['power'] == 7500), 'carbon_footprint_CO'] = 1
    df.loc[(df['gt'] <= 50000) & (df['gt'] > 15000) & (df['power'] == 7500), 'carbon_footprint_CH'] = 0.3
    df.loc[(df['gt'] <= 50000) & (df['gt'] > 15000) & (df['power'] == 7500), 'carbon_footprint_C'] = 0.5
    df.loc[(df['gt'] <= 50000) & (df['gt'] > 15000) & (df['power'] == 7500), 'carbon_footprint_SO2'] = 0.57

    df.loc[(df['gt'] > 50000) & (df['power'] == 25000), 'carbon_footprint_NOx'] = 17
    df.loc[(df['gt'] > 50000) & (df['power'] == 25000), 'carbon_footprint_CO'] = 0.4
    df.loc[(df['gt'] > 50000) & (df['power'] == 25000), 'carbon_footprint_CH'] = 0.17
    df.loc[(df['gt'] > 50000) & (df['power'] == 25000), 'carbon_footprint_C'] = 0.1
    df.loc[(df['gt'] > 50000) & (df['power'] == 25000), 'carbon_footprint_SO2'] = 0.51

    # нахождение выбросов загрязняющих веществ для судов с режимом малого хода и маневрирования судов
    df.loc[(df['gt'] < 1000) & ((df['power'] == 150) | (df['power'] == 90)), 'carbon_footprint_NOx'] = 25
    df.loc[(df['gt'] < 1000) & ((df['power'] == 150) | (df['power'] == 90)), 'carbon_footprint_CO'] = 18
    df.loc[(df['gt'] < 1000) & ((df['power'] == 150) | (df['power'] == 90)), 'carbon_footprint_CH'] = 3.3
    df.loc[(df['gt'] < 1000) & ((df['power'] == 150) | (df['power'] == 90)), 'carbon_footprint_C'] = 1.6
    df.loc[(df['gt'] < 1000) & ((df['power'] == 150) | (df['power'] == 90)), 'carbon_footprint_SO2'] = 0.75

    df.loc[(df['gt'] <= 3000) & (df['gt'] >= 1000)
           & ((df['power'] == 310) | (df['power'] == 190)), 'carbon_footprint_NOx'] = 28
    df.loc[(df['gt'] <= 3000) & (df['gt'] >= 1000)
           & ((df['power'] == 310) | (df['power'] == 190)), 'carbon_footprint_CO'] = 11
    df.loc[(df['gt'] <= 3000) & (df['gt'] >= 1000)
           & ((df['power'] == 310) | (df['power'] == 190)), 'carbon_footprint_CH'] = 2.2
    df.loc[(df['gt'] <= 3000) & (df['gt'] >= 1000)
           & ((df['power'] == 310) | (df['power'] == 190)), 'carbon_footprint_C'] = 1.5
    df.loc[(df['gt'] <= 3000) & (df['gt'] >= 1000)
           & ((df['power'] == 310) | (df['power'] == 190)), 'carbon_footprint_SO2'] = 0.75

    df.loc[(df['gt'] <= 5000) & (df['gt'] > 3000)
           & ((df['power'] == 530) | (df['power'] == 320)), 'carbon_footprint_NOx'] = 28
    df.loc[(df['gt'] <= 5000) & (df['gt'] > 3000)
           & ((df['power'] == 530) | (df['power'] == 320)), 'carbon_footprint_CO'] = 11
    df.loc[(df['gt'] <= 5000) & (df['gt'] > 3000)
           & ((df['power'] == 530) | (df['power'] == 320)), 'carbon_footprint_CH'] = 2.2
    df.loc[(df['gt'] <= 5000) & (df['gt'] > 3000)
           & ((df['power'] == 530) | (df['power'] == 320)), 'carbon_footprint_C'] = 1.5
    df.loc[(df['gt'] <= 5000) & (df['gt'] > 3000)
           & ((df['power'] == 530) | (df['power'] == 320)), 'carbon_footprint_SO2'] = 0.69

    df.loc[(df['gt'] <= 15000) & (df['gt'] > 5000)
           & ((df['power'] == 1750) | (df['power'] == 1050)), 'carbon_footprint_NOx'] = 31
    df.loc[(df['gt'] <= 15000) & (df['gt'] > 5000)
           & ((df['power'] == 1750) | (df['power'] == 1050)), 'carbon_footprint_CO'] = 7
    df.loc[(df['gt'] <= 15000) & (df['gt'] > 5000)
           & ((df['power'] == 1750) | (df['power'] == 1050)), 'carbon_footprint_CH'] = 1
    df.loc[(df['gt'] <= 15000) & (df['gt'] > 5000)
           & ((df['power'] == 1750) | (df['power'] == 1050)), 'carbon_footprint_C'] = 0.8
    df.loc[(df['gt'] <= 15000) & (df['gt'] > 5000)
           & ((df['power'] == 1750) | (df['power'] == 1050)), 'carbon_footprint_SO2'] = 0.63

    df.loc[(df['gt'] <= 50000) & (df['gt'] > 15000)
           & ((df['power'] == 3750) | (df['power'] == 1500)), 'carbon_footprint_NOx'] = 33
    df.loc[(df['gt'] <= 50000) & (df['gt'] > 15000)
           & ((df['power'] == 3750) | (df['power'] == 1500)), 'carbon_footprint_CO'] = 2.3
    df.loc[(df['gt'] <= 50000) & (df['gt'] > 15000)
           & ((df['power'] == 3750) | (df['power'] == 1500)), 'carbon_footprint_CH'] = 0.6
    df.loc[(df['gt'] <= 50000) & (df['gt'] > 15000)
           & ((df['power'] == 3750) | (df['power'] == 1500)), 'carbon_footprint_C'] = 0.5
    df.loc[(df['gt'] <= 50000) & (df['gt'] > 15000)
           & ((df['power'] == 3750) | (df['power'] == 1500)), 'carbon_footprint_SO2'] = 0.57

    df.loc[(df['gt'] > 50000) & ((df['power'] == 12500) | (df['power'] == 5000)), 'carbon_footprint_NOx'] = 35
    df.loc[(df['gt'] > 50000) & ((df['power'] == 12500) | (df['power'] == 5000)), 'carbon_footprint_CO'] = 0.9
    df.loc[(df['gt'] > 50000) & ((df['power'] == 12500) | (df['power'] == 5000)), 'carbon_footprint_CH'] = 0.4
    df.loc[(df['gt'] > 50000) & ((df['power'] == 12500) | (df['power'] == 5000)), 'carbon_footprint_C'] = 0.1
    df.loc[(df['gt'] > 50000) & ((df['power'] == 12500) | (df['power'] == 5000)), 'carbon_footprint_SO2'] = 0.51

    # нахождение выбросов загрязняющих веществ на режиме стоянки судов со вспомогательными двигателями
    df.loc[(df['gt'] < 1000) & (df['power'] == 80), 'carbon_footprint_NOx'] = 11
    df.loc[(df['gt'] < 1000) & (df['power'] == 80), 'carbon_footprint_CO'] = 8
    df.loc[(df['gt'] < 1000) & (df['power'] == 80), 'carbon_footprint_CH'] = 1.5
    df.loc[(df['gt'] < 1000) & (df['power'] == 80), 'carbon_footprint_C'] = 1.1
    df.loc[(df['gt'] < 1000) & (df['power'] == 80), 'carbon_footprint_SO2'] = 0.75

    df.loc[(df['gt'] <= 3000) & (df['gt'] >= 1000) & (df['power'] == 150), 'carbon_footprint_NOx'] = 12
    df.loc[(df['gt'] <= 3000) & (df['gt'] >= 1000) & (df['power'] == 150), 'carbon_footprint_CO'] = 6
    df.loc[(df['gt'] <= 3000) & (df['gt'] >= 1000) & (df['power'] == 150), 'carbon_footprint_CH'] = 1.3
    df.loc[(df['gt'] <= 3000) & (df['gt'] >= 1000) & (df['power'] == 150), 'carbon_footprint_C'] = 1.1
    df.loc[(df['gt'] <= 3000) & (df['gt'] >= 1000) & (df['power'] == 150), 'carbon_footprint_SO2'] = 0.75

    df.loc[(df['gt'] <= 5000) & (df['gt'] > 3000) & (df['power'] == 300), 'carbon_footprint_NOx'] = 14
    df.loc[(df['gt'] <= 5000) & (df['gt'] > 3000) & (df['power'] == 300), 'carbon_footprint_CO'] = 5
    df.loc[(df['gt'] <= 5000) & (df['gt'] > 3000) & (df['power'] == 300), 'carbon_footprint_CH'] = 1.3
    df.loc[(df['gt'] <= 5000) & (df['gt'] > 3000) & (df['power'] == 300), 'carbon_footprint_C'] = 1.1
    df.loc[(df['gt'] <= 5000) & (df['gt'] > 3000) & (df['power'] == 300), 'carbon_footprint_SO2'] = 0.69

    df.loc[(df['gt'] <= 15000) & (df['gt'] > 5000) & (df['power'] == 500), 'carbon_footprint_NOx'] = 16
    df.loc[(df['gt'] <= 15000) & (df['gt'] > 5000) & (df['power'] == 500), 'carbon_footprint_CO'] = 4
    df.loc[(df['gt'] <= 15000) & (df['gt'] > 5000) & (df['power'] == 500), 'carbon_footprint_CH'] = 0.7
    df.loc[(df['gt'] <= 15000) & (df['gt'] > 5000) & (df['power'] == 500), 'carbon_footprint_C'] = 0.6
    df.loc[(df['gt'] <= 15000) & (df['gt'] > 5000) & (df['power'] == 500), 'carbon_footprint_SO2'] = 0.63

    df.loc[(df['gt'] <= 50000) & (df['gt'] > 15000) & (df['power'] == 700), 'carbon_footprint_NOx'] = 17
    df.loc[(df['gt'] <= 50000) & (df['gt'] > 15000) & (df['power'] == 700), 'carbon_footprint_CO'] = 3
    df.loc[(df['gt'] <= 50000) & (df['gt'] > 15000) & (df['power'] == 700), 'carbon_footprint_CH'] = 0.4
    df.loc[(df['gt'] <= 50000) & (df['gt'] > 15000) & (df['power'] == 700), 'carbon_footprint_C'] = 0.4
    df.loc[(df['gt'] <= 50000) & (df['gt'] > 15000) & (df['power'] == 700), 'carbon_footprint_SO2'] = 0.57

    df.loc[(df['gt'] > 50000) & (df['power'] == 3000), 'carbon_footprint_NOx'] = 17
    df.loc[(df['gt'] > 50000) & (df['power'] == 3000), 'carbon_footprint_CO'] = 1.5
    df.loc[(df['gt'] > 50000) & (df['power'] == 3000), 'carbon_footprint_CH'] = 0.25
    df.loc[(df['gt'] > 50000) & (df['power'] == 3000), 'carbon_footprint_C'] = 0.1
    df.loc[(df['gt'] > 50000) & (df['power'] == 3000), 'carbon_footprint_SO2'] = 0.51


    df['carbon_footprint'] = df['carbon_footprint_CO'] + df['carbon_footprint_C'] + df[
        'carbon_footprint_CH'] + df['carbon_footprint_SO2'] + df['carbon_footprint_NOx']

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

    epoch_time = datetime.datetime.fromtimestamp(1683749137)
    time_formatted = epoch_time.strftime('%Y-%m-%d %H:%M')
    print(time_formatted)

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

    # Отображаем карту
    fig.show()



    print("График построен")


except Exception as exc:
    print(exc)
finally:
    if conn:
        conn.close()
        print('Соединение прекращено')