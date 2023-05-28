import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
import sqlite3
import datetime

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

import gross_tonnage
import map_building
import power
import carbon_footprint
import wind_changes
import cf_statistic_bar
import cf_comparison_chart
import correlation_plot

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
           "Vessels.shipType, "
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

    combined_fig = go.Figure()

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

    df['closest_match'] = df.apply(wind_changes.find_closest_match, args=(df_wind,), axis=1)
    df = df.merge(df_wind[['Wind Direction', 'Wind Speed']], left_on='closest_match',
                      right_index=True, suffixes=('', '_closest'))
    print(df.head())

    #print(df[["longitude", "latitude", "new_latitude", "new_longitude"]])

    wind_changes.updating_dataframe_with_new_latlon(df)

# Построение карты углеродного следа и судов
    map_building.adding_additional_traces(df, fig)
    all_results = map_building.adding_traces_on_frames(df, pd, frames, datetime, all_results)
    map_building.adding_sliders_and_frames(fig, frames)


    app = dash.Dash(__name__)

    app.layout = html.Div([
        dcc.Graph(id='map_display', style={'height': 600}),
        dcc.Graph(id='bar_chart'),
        dcc.Graph(id='pie_chart')
    ])


    @app.callback(
        Output('map_display', 'figure'),
        Input('map_display', 'id')
    )
    def update_map_display(id):
        figure = map_building.map_display(fig, token)
        return figure


# Гистограмма углеродного следа по дням
    @app.callback(
        Output('bar_chart', 'figure'),
        Input('bar_chart', 'id')
    )
    def update_bar_chart(id):
        fig = cf_statistic_bar.bar_display(pd, all_results, datetime, px)
        return fig


# График сравнения количества углеродного судна в зависимости от судна
    @app.callback(
        Output('comparison_chart', 'figure'),
        Input('comparison_chart', 'id')
    )
    def update_comparison_chart(id):
        fig = cf_comparison_chart.chart_display(all_results)
        return fig


    if __name__ == '__main__':
        app.run_server(debug=True)

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