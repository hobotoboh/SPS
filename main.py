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
           "referencePointD "
           "FROM location ")
    df = pd.read_sql(sql, conn)

    print(df.head(15))

    fig = px.scatter_mapbox(df,
                            lon=df['longitude'],
                            lat=df['latitude'],
                            zoom=5,
                            size=df['referencePointA']/10,
                            size_max=8,
                            color=df['mmsi'],
                            width=1200,
                            height=600,
                            title='AIS',
                            hover_name=df['mmsi'],
                            )

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
