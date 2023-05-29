import plotly.express as px
import pandas as pd
import sqlite3
import datetime

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

filename = r"A:\Files\Diploma\AIS_10_01_2021.db"
token = open("key.mapbox_token").read()

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

        wind_changes.updating_dataframe_with_new_latlon(df)

        return df


    # Карта судов и углеродного следа
    data_to_empty_df = {
        'longitude': 0,
        'latitude': 0,
    }

    frames = []
    all_results = pd.DataFrame()
    cache_df = pd.DataFrame(columns=['key', 'data'])

    app.layout = html.Div([
        dcc.Store(id='data_store', data=None),
        html.H1("-------------------------  КАРТА УГЛЕРОДНОГО СЛЕДА   -------------------------"),
        html.Div([
            html.Label("Даты выборки:", className='data-viborki'),
            dcc.DatePickerRange(
                id='date-picker',
                min_date_allowed=datetime.date(2015, 1, 1),
                max_date_allowed=datetime.date(2023, 12, 31),
                start_date=datetime.date(2021, 11, 14),
                end_date=datetime.date(2021, 11, 19),
                clearable=False
            ),
            html.Button("Построить карту", id='submit', ),
        ], className='date-picker',
        ),
        dcc.Graph(id='map_display', figure={
            'layout': {
                'plot_bgcolor': '#D2B48C',
                'paper_bgcolor': '#D2B48C',
            }}, style={'height': 700}),

        html.Div([
            html.H1("--------------------------- КРАТКИЙ ОБЗОР ДАННЫХ    ---------------------------"),

            html.Div([html.H2("Cоотношение записей по дням", className='database-review-head'),
                      dcc.Graph(id='percentage_days', figure={
                          'layout': {
                              'plot_bgcolor': '#D2B48C',
                              'paper_bgcolor': '#D2B48C',
                          }}, className='database-review-body'), ],
                     className='database-review'),
            html.Div([html.H2("Общее число полученных записей", className='database-review-head'),
                      html.Div(html.Div(id='total_number_of_records'), className='database-review-body-records',)],
                     className='database-review-records'),
            html.Div([html.H2("Cоотношение записей по кораблям", className='database-review-head'),
                      dcc.Graph(id='percentage_mmsi', figure={
                          'layout': {
                              'plot_bgcolor': '#D2B48C',
                              'paper_bgcolor': '#D2B48C',
                          }}, className='database-review-body'), ],
                     className='database-review'),
        ]),

        html.H1("----------------------- АНАЛИЗ УГЛЕРОДНОГО СЛЕДА    -----------------------"),
        html.Div([
            html.Button("Построить графики", id='submit-graphs', className='creator'),
        ], className='date-picker',
        ),
        dcc.Graph(id='bar_chart', figure={
            'layout': {
                'plot_bgcolor': '#D2B48C',
                'paper_bgcolor': '#D2B48C',
            }}),
        dcc.Graph(id='comparison_chart', figure={
            'layout': {
                'plot_bgcolor': '#D2B48C',
                'paper_bgcolor': '#D2B48C',
            }})
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
                return df.to_json(date_format='iso', orient='split')
            else:
                return data
        else:
            df = getting_data(startdate, enddate)
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
        Input('submit', 'n_clicks'),
        Input('data_store', 'data')
    )
    def update_map_display(n, data):
        if data is None:
            raise dash.exceptions.PreventUpdate

        df = pd.read_json(data, orient='split')

        global all_results

        empty_df = pd.DataFrame([data_to_empty_df])

        fig = px.scatter_mapbox(empty_df,
                                lon=empty_df['longitude'],
                                lat=empty_df['latitude'],
                                zoom=5,
                                )

        map_building.adding_additional_traces(df, fig)
        all_results = map_building.adding_traces_on_frames(df, pd, frames, datetime, all_results)
        map_building.adding_sliders_and_frames(fig, frames)

        figure = map_building.map_display(fig, token)

        print("График построен")
        return figure


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
        State('data_store', 'data')
    )
    def update_bar_chart(n, data):
        if data is None:
            raise dash.exceptions.PreventUpdate

        df = pd.read_json(data, orient='split')

        fig = cf_statistic_bar.bar_display(pd, all_results, datetime, px)

        return fig


    # График сравнения количества углеродного судна в зависимости от судна
    @app.callback(
        Output('comparison_chart', 'figure'),
        Input('submit-graphs', 'n_clicks'),
        State('data_store', 'data')
    )
    def update_comparison_chart(n, data):
        if data is None:
            raise dash.exceptions.PreventUpdate

        df = pd.read_json(data, orient='split')

        fig = cf_comparison_chart.chart_display(all_results)
        return fig


    if __name__ == '__main__':
        app.run_server(debug=True)

except Exception as exc:
    print(exc)
