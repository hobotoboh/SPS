import plotly.express as px
import pandas as pd
import sqlite3
import datetime
import requests

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State

import gross_tonnage
import map_building
import power
import carbon_footprint
import wind_changes
import cf_statistic_bar
import cf_comparison_chart
import database_overview
import correlation_plot
import radar_chart

filename = r"A:\Files\Diploma\AIS_10_01_2021.db"
token = open("key.mapbox_token").read()

api_key = open("key.weather_token").read()
base_weather_url = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/"

try:
    app = dash.Dash(__name__)


    def getting_data(startdate, enddate):
        conn = sqlite3.connect(filename)

        startdate = datetime.datetime.strptime(startdate, "%Y-%m-%d")
        enddate = datetime.datetime.strptime(enddate, "%Y-%m-%d")

        enddate += datetime.timedelta(days=1, milliseconds=-1)

        startdate = int(startdate.timestamp()) * 1000
        enddate = int(enddate.timestamp()) * 1000

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
               "ais1.timestampExternal/1000 AS time "
               "FROM ais1, Vessels "
               "WHERE ais1.mmsi = Vessels.mmsi "
               "AND ais1.timestampExternal >= :startdate "
               "AND ais1.timestampExternal <= :enddate "
               "GROUP BY ais1.mmsi, strftime('%Y-%m-%d %H', datetime(ais1.timestampExternal/1000, 'unixepoch', "
           "'localtime'))"
               "LIMIT 3000")
        print('Получение данных БД...')

        df = pd.read_sql(sql, conn, params={"startdate": startdate, "enddate": enddate})
        df = df[(df.referencePointA != 0) & (df.referencePointB != 0) & (df.referencePointC != 0) & (
                    df.referencePointD != 0)]


        print('Получение данных погоды...')

        rows = []
        wind_coordinates = {
            'lat': [59.95, 60.44, 59.966, 59.6844, 59.4713, 60.02, 59.9, 59.65],
            'lon': [29.96, 27.8, 24.481, 27.8, 24.481, 27.64, 25.75, 23.73]
        }

        startdate = startdate // 1000
        enddate = enddate // 1000

        for i in range(len(wind_coordinates['lat'])):
            lat = wind_coordinates['lat'][i]
            lon = wind_coordinates['lon'][i]

            complete_url = base_weather_url + str(lat) + "," + str(lon) + "/" \
                           + str(int(startdate)) + "/" + str(int(enddate)) \
                           + "?key=" + api_key + "&include=days" + "&elements=datetime,winddir,windspeed"
            print(complete_url)
            res = requests.get(complete_url)

            weather_data = res.json()
            days_data = weather_data["days"]

            for day in days_data:
                date = day["datetime"]
                wind_direction = day["winddir"]
                wind_speed = day["windspeed"]
                row = [date, wind_direction, wind_speed, lat, lon]
                rows.append(row)

        df_wind = pd.DataFrame(rows, columns=['Date', 'Wind Direction', 'Wind Speed', 'Latitude', 'Longitude'])
        #df_wind = pd.read_csv('A:/Files/Diploma/output.csv')

        print('Проведение расчетов...')
        # Расчет валовой вместимости и мощности судов
        gross_tonnage.calculation(df)
        power.finding_power(df)

        # Расчет углеродного следа
        carbon_footprint.carbon_footprint_parameters(df)
        carbon_footprint.cf_Sea_Canal(df)
        carbon_footprint.cf_low_speed_and_maneuvering(df)
        carbon_footprint.cf_mooring(df)
        carbon_footprint.cf_calculation(df)

        print('Работа с данными по ветру...')
        # Определение ближайшей точки с информацией по ветру
        """epoch_time = datetime.datetime.fromtimestamp(time)
        time_formatted = epoch_time.strftime('%Y-%m-%d %H:%M')"""
        df['date'] = df['time'].apply(lambda x: datetime.datetime.fromtimestamp(x).strftime('%Y-%m-%d'))

        df['closest_match'] = df.apply(wind_changes.find_closest_match, args=(df_wind,), axis=1)
        df = df.merge(df_wind[['Wind Direction', 'Wind Speed']], left_on='closest_match',
                      right_index=True, suffixes=('', '_closest'))

        wind_changes.updating_dataframe_with_new_latlon(df)

        return df


    # Карта судов и углеродного следа
    data_to_empty_df = {
        'longitude': 0,
        'latitude': 0,
    }

    app.layout = html.Div([
        dcc.Store(id='data_store', data=None),
        dcc.Store(id='all_results_store'),

        html.H1("-------------------------  КАРТА УГЛЕРОДНОГО СЛЕДА   -------------------------"),
        html.Div([
            html.Label("Даты выборки:", className='data-viborki'),
            dcc.DatePickerRange(
                id='date-picker',
                min_date_allowed=datetime.date(2001, 1, 1),
                max_date_allowed=datetime.date(2030, 12, 31),
                start_date=datetime.date(2021, 11, 14),
                end_date=datetime.date(2021, 11, 19),
                clearable=False
            ),
            html.Button("Построить карту", id='submit', ),
        ], className='date-picker',
        ),
        dcc.Graph(id='map_display', figure={
            'layout': {
                'plot_bgcolor': '#FFDAB9',
                'paper_bgcolor': '#FFDAB9',
            }}, style={'height': 700}),

        html.Div([
            html.H1("--------------------------- КРАТКИЙ ОБЗОР ДАННЫХ    ---------------------------"),

            html.Div([html.H2("Cоотношение записей по дням", className='database-review-head'),
                      dcc.Graph(id='percentage_days', figure={
                          'layout': {
                              'plot_bgcolor': '#FFDAB9',
                              'paper_bgcolor': '#FFDAB9',
                          }}, className='database-review-body'), ],
                     className='database-review'),
            html.Div([html.H2("Общее число полученных записей", className='database-review-head'),
                      html.Div(html.Div(id='total_number_of_records'), className='database-review-body-records', )],
                     className='database-review-records'),
            html.Div([html.H2("Cоотношение записей по кораблям", className='database-review-head'),
                      dcc.Graph(id='percentage_mmsi', figure={
                          'layout': {
                              'plot_bgcolor': '#FFDAB9',
                              'paper_bgcolor': '#FFDAB9',
                          }}, className='database-review-body'), ],
                     className='database-review'),
        ]),

        html.H1("----------------------- АНАЛИЗ УГЛЕРОДНОГО СЛЕДА    -----------------------"),
        html.Div([
            html.Button("Построить графики", id='submit-graphs', className='creator'),
        ], className='date-picker',
        ),
        html.Div([
            dcc.Graph(id='bar_chart', figure={
                'layout': {
                    'plot_bgcolor': '#FFDAB9',
                    'paper_bgcolor': '#FFDAB9',
                }}, className='cf_bar_chart'),
            dcc.Graph(id='radar_chart', figure={
                'layout': {
                    'plot_bgcolor': '#FFDAB9',
                    'paper_bgcolor': '#FFDAB9',
                }}, className='cf_radar_chart')
        ], ),
        dcc.Graph(id='comparison_chart', figure={
            'layout': {
                'plot_bgcolor': '#FFDAB9',
                'paper_bgcolor': '#FFDAB9',
            }}),
        html.Div([dcc.Graph(id='correlation_gt_plot', figure={
            'layout': {
                'plot_bgcolor': '#FFDAB9',
                'paper_bgcolor': '#FFDAB9',
            }}, className='correlation-plots'),
                  dcc.Graph(id='correlation_power_plot', figure={
                      'layout': {
                          'plot_bgcolor': '#FFDAB9',
                          'paper_bgcolor': '#FFDAB9',
                      }}, className='correlation-plots'),
                  ], )
    ],
        style={'css': ['styles.css']})


    @app.callback(
        Output('data_store', 'data'),
        Input('submit', 'n_clicks'),
        State('date-picker', 'start_date'),
        State('date-picker', 'end_date'),
        State('data_store', 'data'))
    def update_data_store(n, startdate, enddate, data):
        if n is None:
            raise dash.exceptions.PreventUpdate

        if data is not None:
            current_df = pd.read_json(data, orient='split')

            current_df['date'] = pd.to_datetime(current_df['date'])
            start_date = pd.to_datetime(startdate)
            end_date = pd.to_datetime(enddate)

            if (current_df['date'].min() != start_date) or (current_df['date'].max() != end_date):
                del data
                df = getting_data(startdate, enddate)
                print("Все данные получены")
                return df.to_json(date_format='iso', orient='split')
            else:
                print("Данные не изменились")
                return data
        else:
            df = getting_data(startdate, enddate)
            print("Все данные получены")
            return df.to_json(date_format='iso', orient='split')


    @app.callback(
        Output('submit-graphs', 'n_clicks'),
        Input('submit-graphs', 'n_clicks'),
    )
    def update_plots(n_clicks, ):
        if n_clicks is None:
            raise dash.exceptions.PreventUpdate


    # Построение карты углеродного следа и судов
    @app.callback(
        Output('map_display', 'figure'),
        Output('all_results_store', 'data'),
        Input('submit', 'n_clicks'),
        Input('data_store', 'data'),
        State('date-picker', 'start_date'),
        State('date-picker', 'end_date'),
    )
    def update_map_display(n, data, startdate, enddate):
        if data is None:
            raise dash.exceptions.PreventUpdate

        df = pd.read_json(data, orient='split')

        all_results = pd.DataFrame()
        empty_df = pd.DataFrame([data_to_empty_df])
        fig = px.scatter_mapbox(empty_df,
                                lon=empty_df['longitude'],
                                lat=empty_df['latitude'],
                                zoom=5,
                                )

        frames = []

        map_building.adding_additional_traces(df, fig)
        all_results = map_building.adding_traces_on_frames(df, pd, frames, datetime, all_results)
        map_building.adding_sliders_and_frames(fig, frames)

        figure = map_building.map_display(fig, token)

        print("График построен")
        all_results_json = all_results.to_json(date_format='iso', orient='split')

        return figure, all_results_json


    @app.callback(
        Output('total_number_of_records', 'children'),
        Input('data_store', 'data'),
    )
    def update_total_number(data):
        if data is None:
            raise dash.exceptions.PreventUpdate

        df = pd.read_json(data, orient='split')

        total_records = df.shape[0]
        return total_records


    @app.callback(
        Output('percentage_days', 'figure'),
        Input('data_store', 'data')
    )
    def update_percentage_days_chart(data):
        if data is None:
            raise dash.exceptions.PreventUpdate

        df = pd.read_json(data, orient='split')
        fig = database_overview.percentage_days(px, df, pd)
        return fig


    @app.callback(
        Output('percentage_mmsi', 'figure'),
        Input('data_store', 'data')
    )
    def update_percentage_mmsi_chart(data):
        if data is None:
            raise dash.exceptions.PreventUpdate

        df = pd.read_json(data, orient='split')
        fig = database_overview.percentage_mmsi(px, df)
        return fig


    # Гистограмма углеродного следа по дням
    @app.callback(
        Output('bar_chart', 'figure'),
        Input('submit-graphs', 'n_clicks'),
        State('all_results_store', 'data'),
    )
    def update_bar_chart(n, data):
        if data is None:
            raise dash.exceptions.PreventUpdate

        all_results = pd.read_json(data, orient='split')

        fig = cf_statistic_bar.bar_display(pd, all_results, datetime, px)

        return fig


    # Углеродный след при различных направлениях ветра
    @app.callback(
        Output('radar_chart', 'figure'),
        Input('submit-graphs', 'n_clicks'),
        State('all_results_store', 'data'),
    )
    def update_radar_chart(n, data):
        if data is None:
            raise dash.exceptions.PreventUpdate

        df = pd.read_json(data, orient='split')

        fig = radar_chart.radar_display(df, )

        return fig


    # График сравнения количества углеродного судна в зависимости от судна
    @app.callback(
        Output('comparison_chart', 'figure'),
        Input('submit-graphs', 'n_clicks'),
        State('all_results_store', 'data'),
    )
    def update_comparison_chart(n, data):
        if data is None:
            raise dash.exceptions.PreventUpdate

        all_results = pd.read_json(data, orient='split')

        fig = cf_comparison_chart.chart_display(all_results)
        return fig


    # Корреляционные графики взаимосвязи между углеродным следом и мощностью/валовой вместимостью
    @app.callback(
        Output('correlation_gt_plot', 'figure'),
        Input('submit-graphs', 'n_clicks'),
        State('data_store', 'data')
    )
    def update_correlation_gt_plot(n, data):
        if data is None:
            raise dash.exceptions.PreventUpdate

        df = pd.read_json(data, orient='split')

        fig = correlation_plot.correlation_gt(pd, df)
        return fig


    @app.callback(
        Output('correlation_power_plot', 'figure'),
        Input('submit-graphs', 'n_clicks'),
        State('data_store', 'data')
    )
    def update_correlation_power_plot(n, data):
        if data is None:
            raise dash.exceptions.PreventUpdate

        df = pd.read_json(data, orient='split')

        fig = correlation_plot.correlation_power(pd, df)
        return fig


    if __name__ == '__main__':
        app.run_server(debug=False)

except Exception as exc:
    print(exc)
