from math import radians, cos, sin, asin, sqrt, atan2, degrees

def haversine_distance(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    km = 6371 * c
    return km

def find_closest_match(row, df_wind):
    min_distance = float('inf')
    closest_index = -1
    for index, coord in df_wind.iterrows():
        if row['date'] == coord['Date']:
            distance = haversine_distance(row['latitude'], row['longitude'], coord['Latitude'], coord['Longitude'])
            if distance < min_distance:
                min_distance = distance
                closest_index = index
    return closest_index


def updating_dataframe_with_new_latlon(df):
    wind_effect_constant = 10.000 # Adjust this value based on your requirements

    df['new_latitude'], df['new_longitude'] = zip(*df.apply(
        lambda row: new_coordinates(row['latitude'], row['longitude'],
                                    row['Wind Speed'], row['Wind Direction'],
                                    wind_effect_constant), axis=1))
def new_coordinates(lat, lon, wind_speed, wind_direction, wind_effect_constant):
    R = 6371e3  # Радиус Земли в метрах

    bearing = radians(wind_direction)
    distance = wind_speed * wind_effect_constant

    lat1 = radians(lat)
    lon1 = radians(lon)

    lat2 = asin(sin(lat1) * cos(distance / R) +
                     cos(lat1) * sin(distance / R) * cos(bearing))

    lon2 = lon1 + atan2(sin(bearing) * sin(distance / R) * cos(lat1),
                             cos(distance / R) - sin(lat1) * sin(lat2))

    lat2 = degrees(lat2)
    lon2 = degrees(lon2)

    return lat2, lon2

