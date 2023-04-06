
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
# Press Ctrl+F8 to toggle the breakpoint.

# from tkinter import *
import plotly.express as px
import pandas as pd
import sqlite3

print('Получение данных...')
filename = r"A:\Files\Diploma\AIS_10_01_2021.db"
sql = (
    "SELECT ais.mmsi, ais.Longitude, ais.Latitude, Vessels.referencePointA "
    "FROM ais, Vessels "
    "WHERE ais.mmsi = Vessels.mmsi"
)

try:
    cnn = sqlite3.connect(filename)
    dataframe = pd.read_sql(sql, cnn)
    print(dataframe.head(20))
    figure = px.scatter_mapbox(dataframe,
                               lon=dataframe['Longitude'],
                               lan=dataframe['Latitude'],
                               zoom=5,
                               size=dataframe['referencePointA'],
                               width=900,
                               height=600,
                               title="AIS 2021")
    figure.update_layout(mapbox_style="open-street-map")
    figure.show()
    print("График построен")


except Exception as exc:
    print(exc)
finally:
    if cnn:
        cnn.close()
        print('Соединение прекращено')

# root = Tk()
# root.title("Автоматизированная система")
# root.geometry("1000x600+200+50")
# root.resizable(width=False, height=False)
#
# root.mainloop()
