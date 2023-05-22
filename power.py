def finding_power(df):
    # нахождение мощности
    df['power'] = ''

    # мощность главных двигателей при режиме прохода по Морскому каналу
    df.loc[(df['gt'] < 1000)
           & (df['latitude'] < 60.01) & (df['longitude'] > 29.7838) & (df['sog'] > 1), 'power'] = 480
    df.loc[(df['gt'] <= 3000) & (df['gt'] >= 1000)
           & (df['latitude'] < 60.01) & (df['longitude'] > 29.7838) & (df['sog'] > 1), 'power'] = 1000
    df.loc[(df['gt'] <= 5000) & (df['gt'] > 3000)
           & (df['latitude'] < 60.01) & (df['longitude'] > 29.7838) & (df['sog'] > 1), 'power'] = 1700
    df.loc[(df['gt'] <= 15000) & (df['gt'] > 5000)
           & (df['latitude'] < 60.01) & (df['longitude'] > 29.7838) & (df['sog'] > 1), 'power'] = 3500
    df.loc[(df['gt'] <= 50000) & (df['gt'] > 15000)
           & (df['latitude'] < 60.01) & (df['longitude'] > 29.7838) & (df['sog'] > 1), 'power'] = 7500
    df.loc[(df['gt'] > 50000)
           & (df['latitude'] < 60.01) & (df['longitude'] > 29.7838) & (df['sog'] > 1), 'power'] = 25000

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