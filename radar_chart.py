import plotly.graph_objects as go

def radar_display(df, ):

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=df['carbon_footprint'],
        theta=df['Wind Direction'],
        fill='toself'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True),
            angularaxis=dict(direction="clockwise"),),
        showlegend=False,
        plot_bgcolor='#D2B48C', paper_bgcolor='#D2B48C',
        title={
            'text': "Углеродный след при различных направлениях ветра",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        margin=dict(l=50)
    )

    fig.add_annotation(
        x=1,
        y=0.5,
        text="0 - север,<br>"
             "90 - восток,<br>"
             "180 - юг,<br>"
             "270 - запад",
        showarrow=False,
        font=dict(size=14)
    )

    return fig