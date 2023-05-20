# функция добавления параметров углеродного следа
def carbon_footprint_parameters(df):
    df['carbon_footprint_NOx'] = ''
    df['carbon_footprint_CO'] = ''
    df['carbon_footprint_CH'] = ''
    df['carbon_footprint_C'] = ''
    df['carbon_footprint_SO2'] = ''
    df['carbon_footprint'] = ''

# нахождение выбросов загрязняющих веществ для судов с режимом прохода по Морскому каналу
def cf_Sea_Canal(df):
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
def cf_low_speed_and_maneuvering(df):
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
def cf_mooring(df):
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

def cf_calculation(df):
    df['carbon_footprint'] = df['carbon_footprint_CO'] + df['carbon_footprint_C'] + df[
        'carbon_footprint_CH'] + df['carbon_footprint_SO2'] + df['carbon_footprint_NOx']