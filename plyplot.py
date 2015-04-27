__author__ = 'itoledo'

import datetime as dt
from plotly.graph_objs import *
import plotly.plotly as py
import plotly.tools as tools


py.sign_in('itoledoc', 'vk43crr906')

def plot_delay(data):

    t1 = data.query('BB == "BB_1" and ANTENNA != REF_ANT')
    t2 = data.query('BB == "BB_2" and ANTENNA != REF_ANT')
    t3 = data.query('BB == "BB_3" and ANTENNA != REF_ANT')
    t4 = data.query('BB == "BB_4" and ANTENNA != REF_ANT')

    trace1 = Scatter(
        x=t1.apply(
            lambda r: dt.datetime.strftime(r['TIME'],
                                           '%Y-%m-%d %H:%M:%S.%s'),
            axis=1).values,
        y=t1['delay_X'].values,
        mode='markers',
        name='BB_1 Pol X',
        text=t1.ANTENNA.values,
        error_y=ErrorY(
            array=t1['error_X'].values
        )
    )

    trace2 = Scatter(
        x=t2.apply(
            lambda r: dt.datetime.strftime(r['TIME'],
                                           '%Y-%m-%d %H:%M:%S.%s'),
            axis=1).values,
        y=t2['delay_X'].values,
        mode='markers',
        name='BB_2 Pol X',
        text=t2.ANTENNA.values,
        error_y=ErrorY(
            array=t2['error_X'].values
        )
    )
    trace3 = Scatter(
        x=t3.apply(
            lambda r: dt.datetime.strftime(r['TIME'],
                                           '%Y-%m-%d %H:%M:%S.%s'),
                   axis=1).values,
        y=t3['delay_X'].values,
        mode='markers',
        name='BB_3 Pol X',
        text=t3.ANTENNA.values,
        error_y=ErrorY(
            array=t3['error_X'].values
        )
    )
    trace4 = Scatter(
        x=t4.apply(
            lambda r: dt.datetime.strftime(r['TIME'],
                                           '%Y-%m-%d %H:%M:%S.%s'),
            axis=1).values,
        y=t4['delay_X'].values,
        mode='markers',
        name='BB_4 Pol X',
        text=t4.ANTENNA.values,
        error_y=ErrorY(
            array=t4['error_X'].values
        )
    )

    trace1y = Scatter(
        x=t1.apply(
            lambda r: dt.datetime.strftime(r['TIME'],
                                           '%Y-%m-%d %H:%M:%S.%s'),
            axis=1).values,
        y=t1['delay_Y'].values,
        mode='markers',
        name='BB_1 Pol Y',
        text=t1.ANTENNA.values,
        error_y=ErrorY(
            array=t1['error_Y'].values
        )
    )

    trace2y = Scatter(
        x=t2.apply(
            lambda r: dt.datetime.strftime(r['TIME'],
                                           '%Y-%m-%d %H:%M:%S.%s'),
            axis=1).values,
        y=t2['delay_Y'].values,
        mode='markers',
        name='BB_2 Pol Y',
        text=t2.ANTENNA.values,
        error_y=ErrorY(
            array=t2['error_Y'].values
        )
    )
    trace3y = Scatter(
        x=t3.apply(
            lambda r: dt.datetime.strftime(r['TIME'],
                                           '%Y-%m-%d %H:%M:%S.%s'),
                   axis=1).values,
        y=t3['delay_Y'].values,
        mode='markers',
        name='BB_3 Pol Y',
        text=t3.ANTENNA.values,
        error_y=ErrorY(
            array=t3['error_Y'].values
        )
    )
    trace4y = Scatter(
        x=t4.apply(
            lambda r: dt.datetime.strftime(r['TIME'],
                                           '%Y-%m-%d %H:%M:%S.%s'),
            axis=1).values,
        y=t4['delay_Y'].values,
        mode='markers',
        name='BB_4 Pol Y',
        text=t4.ANTENNA.values,
        error_y=ErrorY(
            array=t4['error_Y'].values
        )
    )

    fig = tools.make_subplots(rows=2, shared_xaxes=True)
    fig.append_trace(trace1,1,1)
    fig.append_trace(trace2,1,1)
    fig.append_trace(trace3,1,1)
    fig.append_trace(trace4,1,1)
    fig.append_trace(trace1y,2,1)
    fig.append_trace(trace2y,2,1)
    fig.append_trace(trace3y,2,1)
    fig.append_trace(trace4y,2,1)


    fig['layout'] = {
        'hovermode': 'closest',
        'showlegend': True,
        'autosize': True,
        'height': 800,
        'xaxis1': {'anchor': 'y2', 'domain': [0.0, 1.0], 'type':'date',
                   'title': 'Time'},
        'yaxis1': {'anchor': 'free', 'domain': [0.575, 1.0], 'position': 0.0,
                   'type':'linear', 'title': 'Delay (Pol X)', 'zeroline': True},
        'yaxis2': {'anchor': 'x1', 'domain': [0.0, 0.425], 'type':'linear',
                   'title': 'Delay (Pol Y)', 'zeroline': True}}

    return fig