# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
# Press Ctrl+F8 to toggle the breakpoint.

import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import folium
import sqlite3

print('Получение данных...')
filename = r"A:\Files\Diploma\AIS_10_01_2021.db"

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
           "sog "
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

    print(df.head(15))
    fig = px.scatter_mapbox(df,
                            lon=df['longitude'],
                            lat=df['latitude'],
                            zoom=5,
                            size=df['gt']/10,
                            size_max=8,
                            color=df['gt'],
                            width=1200,
                            height=600,
                            title='AIS',
                            hover_name=df['mmsi'],
                            )


    fig2 = px.scatter_mapbox(df,
                            lon=df['longitude'],
                            lat=df['latitude'],
                            size=df['referencePointA']*10,
                            color=df['mmsi'],
                            hover_name=df['mmsi'],
                            opacity= 0.5
                            )

    fig.add_trace(fig2.data[0])

    fig.update_layout(mapbox_style="open-street-map",
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
