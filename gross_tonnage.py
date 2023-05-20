def calculation(df):
    # расчет валовой вместимости
    df['gt'] = df.apply(
        lambda row: ((row['referencePointA'] + row['referencePointB'])
                     * (row['referencePointC'] + row['referencePointD'])
                     * row['draught'] / 10) / 2,
        axis=1)