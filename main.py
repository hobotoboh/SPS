import plotly.express as px
import pandas as pd
import sqlite3
import datetime

import gross_tonnage
import map_building
import power
import carbon_footprint
import cf_statistic_bar
import wind_changes

filename = r"A:\Files\Diploma\AIS_10_01_2021.db"
token = open("key.mapbox_token").read()

try:
    # получение данных из БД
    conn = sqlite3.connect(filename)

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
    df['time'] = df['time'].divide(10000)
    df['time'] = df['time'].round(0)
    df['time'] = df['time'].multiply(10)

    df_wind = pd.read_csv('output.csv')

    # Карта судов и углеродного следа
    data_to_empty_df = {
        'longitude': 0,
        'latitude': 0,
    }
    frames = []
    empty_df = pd.DataFrame([data_to_empty_df])

    fig = px.scatter_mapbox(empty_df,
                            lon=empty_df['longitude'],
                            lat=empty_df['latitude'],
                            zoom=5,
                            )

    all_results = pd.DataFrame()

# Расчет валовой вместимости и мощности судов
    gross_tonnage.calculation(df)
    power.finding_power(df)

# Расчет углеродного следа
    carbon_footprint.carbon_footprint_parameters(df)
    carbon_footprint.cf_Sea_Canal(df)
    carbon_footprint.cf_low_speed_and_maneuvering(df)
    carbon_footprint.cf_mooring(df)
    carbon_footprint.cf_calculation(df)

# Определение ближайшей точки с информацией по ветру
    """epoch_time = datetime.datetime.fromtimestamp(time)
    time_formatted = epoch_time.strftime('%Y-%m-%d %H:%M')"""
    df['date'] = df['time'].apply(lambda x: datetime.datetime.fromtimestamp(x).strftime('%Y-%m-%d'))

    print(df.columns.tolist())
    print(df_wind.columns.tolist())

    df['closest_match'] = df.apply(wind_changes.find_closest_match, args=(df_wind,), axis=1)
    result = df.merge(df_wind, left_on='closest_match', right_index=True, suffixes=('', '_closest'))
    print(result)

# Построение карты углеродного следа и судов
    map_building.adding_additional_traces(df, fig)
    all_results = map_building.adding_traces_on_frames(df, pd, frames, datetime, all_results)
    map_building.adding_sliders_and_frames(fig, frames)
    map_building.map_display(fig, token)

# Гистограмма углеродного следа по дням
    cf_statistic_bar.bar_display(pd, all_results, datetime, px)


    # График углеродного следа
    #fig_graph

    print(df['time'].tail(1))




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