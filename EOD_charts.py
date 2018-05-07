'''
This script produces EOD graphs from Yahoo adjusted close prices

No adjustment for closing prices is needed.

This script has RadioItems that can select type of graphs to be shown

The graphs plotted are Price-Volume graphs (Main graph on top)

Choices:
RSI, Swing, Ichimokucloud, Bollinger bands.
'''

from get_yahoo import download_quotes

import pandas as pd
import numpy as np
import re
import requests
from datetime import timedelta

import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Output, Input

import plotly
import plotly.tools as tls

from subprocess import run, PIPE
from io import StringIO


colist = requests.get('https://www.nseindia.com/content/equities/EQUITY_L.csv').text
colist = pd.read_csv(StringIO(colist))
colist = list(colist.SYMBOL)

app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div([
            html.Div([html.B('Stock to plot :  ')],style={'padding':10}),
            html.Div([dcc.Dropdown(id = 'stock_input',
                                   options = [ {'label':i,'value':i} for i in colist] ,
                                   value = 'INFY')
                    ],style = {'width': '40%','margin': 2})
            ], style = {'display':'flex'}),
    dcc.Graph(id = 'price_volume'),
    dcc.RadioItems(id = 'selector',
                   options=[{'label':'Bollinger Bands','value':1},
                            {'label':'Swing','value':2},
                            {'label':'RSI','value':3},
                            {'label':'Ichimoku Cloud','value':4}
                            ], value=4, labelStyle = {'display': 'inline-block', 'padding-left':'10%'}),
    dcc.Graph(id = 'graph2'),
    html.Div(id = 'store', style = {'display': 'none'})
    ])



# The hidden div to store our stock dataframe in JSON format
# for sharing between callbacks.
@app.callback(
              Output('store', 'children'),
              [Input('stock_input', 'value')]
              )
def cache(stock):
    # The '.NS' is for NSE stocks, for other exchange stocks just input the correct extension ,
    # that is available from Yahoo Finance.
    df = download_quotes(stock+'.NS', write_to_file = False)
    df = df.dropna()
    df = df.reset_index(drop = True)
    return df.to_json(date_format = 'iso', orient = 'split')



# Main graph (the top one)
@app.callback(
              Output('price_volume', 'figure'),
              [Input('store', 'children')]
             )
def graph(json_data):
    df = pd.read_json(json_data, orient = 'split')
    df['20 DMA'] = df['Adj Close'].rolling(window= 20).mean()
    df['50 DMA'] = df['Adj Close'].rolling(window= 50).mean()
    df['100 DMA'] = df['Adj Close'].rolling(window=100).mean()
    df['200 DMA'] = df['Adj Close'].rolling(window=200).mean()
    
    # to determine the monitor's height, width for graph's dimension
    output = run(['xrandr'], stdout=PIPE).stdout.decode()
    result = re.search(r'current (\d+) x (\d+)', output)
    width, height = map(int, result.groups()) if result else (800, 600)
    
    fig = tls.make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.09)
    
    fig.append_trace({'x' : df.DateTime, 'y' : df['Adj Close'], 'type':'scatter', 'name':'Price'}, 1,1)
    fig.append_trace({'x' : df.DateTime, 'y' : df['20 DMA'], 'type':'scatter', 'name':'20 DMA'}, 1,1)
    fig.append_trace({'x' : df.DateTime, 'y' : df['50 DMA'], 'type':'scatter', 'name':'50 DMA'}, 1,1)
    fig.append_trace({'x' : df.DateTime, 'y' : df['100 DMA'], 'type':'scatter', 'name':'100 DMA'}, 1,1)
    fig.append_trace({'x' : df.DateTime, 'y' : df['200 DMA'], 'type':'scatter', 'name':'200 DMA'}, 1,1)
    fig.append_trace({'x' : df.DateTime, 'y' : df.Volume, 'type':'bar', 'name':'Volume'}, 2,1)
    
    if height<800: # for laptops.
        fig['layout'].update(height=600, legend = dict(font=dict(size=22)))
        
    if 1000<height<1500: # for 1080p monitors
        fig['layout'].update(height=800, legend = dict(font=dict(size=22)))
        
    if 1600<height: # for 4k TV
        fig['layout'].update(height=1000, legend = dict(font=dict(size=22)))
        
    fig['layout']['yaxis1'].update(tickfont=dict(size= 15), title= 'Price', titlefont=dict(size=18))
    fig['layout']['yaxis2'].update(tickfont=dict(size= 15), title= 'Volume', titlefont=dict(size=18))
    fig['layout']['xaxis1'].update(tickfont=dict(size= 20), tickformat='%Y-%b-%d')

    return fig


# The choice graphs (The graph below the main one)
@app.callback(
        Output('graph2', 'figure'),
        [Input('store', 'children'),
         Input('selector', 'value')])
def gr2(json_data,graphtype):
    
    df = pd.read_json(json_data, orient='split')
    df['20 DMA'] = df['Adj Close'].rolling(window=20).mean()
    df['UpperBand'] = df['20 DMA']+(df['Adj Close'].rolling(window=20).std()*2)
    df['LowerBand'] = df['20 DMA']-(df['Adj Close'].rolling(window=20).std()*2)
    

    if graphtype==1: # Bollinger bands indicator
        traces1 = []
        
        traces1.append(plotly.graph_objs.Scatter(x = df.DateTime, y = df['Adj Close'], 
                                                  name = 'Close',mode = 'lines'))
        traces1.append(plotly.graph_objs.Scatter(x = df.DateTime, y = df.UpperBand,
                                                  fill = None,line = dict(color='rgb(143, 19, 13)'), name = 'UB',mode = 'lines'))
        traces1.append(plotly.graph_objs.Scatter(x = df.DateTime, y = df.LowerBand,
                                                  fill = 'tonexty',line = dict(color='rgb(143, 19, 13)'),name = 'LB',mode = 'lines'))
                                                  
                                                  
        layout1 = plotly.graph_objs.Layout(title = 'Bollinger Band',titlefont=dict(size=25),
                                       yaxis = dict(title='Price',tickfont=dict(size=20),titlefont=dict(size=18)),
                                       xaxis = dict(tickfont=dict(size=20), showspikes=True,tickformat='%Y-%b-%d'),
                                       margin=dict(r=10))
                                       
        return {'data': traces1, 'layout':layout1}
     
    elif graphtype==2: # Swing level indicator
        
        # This indicator is got from http://www.vfmdirect.com/kplswing/index.html
        # The souce code for this - http://www.vfmdirect.com/kplswing/kpl_swing.afl
        # 
        # In simple words this is a break-out trading strategy.
        
        res=df['High'].rolling(window= 20).max()
        sup=df['Low'].rolling(window= 20).min()

        avd = np.where(df['Adj Close'] > res.shift(1), 1,np.where(df['Adj Close']<sup.shift(1),-1,0))
        df1=pd.concat([res,sup],axis=1)
        df1['s']=avd
        
        df['swing']=np.nan
        df['swing']=np.where(df1.s ==1 ,df1.Low, np.where(df1.s == -1 ,df1.High, df['swing'].fillna(method='ffill')))
        df.swing=df['swing'].fillna(method='ffill')
        
        
        traces2=[]
        traces2.append(plotly.graph_objs.Scatter(x = df.DateTime, y = df['Adj Close'], name = 'Close',mode = 'lines'))
        traces2.append(plotly.graph_objs.Scatter(x = df.DateTime, y = df.swing, name = 'Swing',mode = 'lines'))
        
        layout2 = plotly.graph_objs.Layout(title = 'Swing levels')
        
        return {'data': traces2, 'layout':layout2}
     
    elif graphtype==3: # RSI
        traces3 = []
        window_length = 14
 
        close = df['Adj Close']
        delta = close.diff()
        delta = delta[1:] 
 
        up, down = delta.copy(), delta.copy()
        up[up < 0] = 0
        down[down > 0] = 0
 
         # Calculate the RSI based on EWMA
 #        roll_up1 = pd.stats.moments.ewma(up, window_length)
 #        roll_down1 = pd.stats.moments.ewma(down.abs(), window_length)
 #        RS1 = roll_up1 / roll_down1
 #        RSI1 = 100.0 - (100.0 / (1.0 + RS1))
 
         # Calculate the RSI based on SMA
        roll_up2 = up.rolling(window= window_length).mean()
        roll_down2 = down.abs().rolling(window= window_length).mean()
        RS2 = roll_up2 / roll_down2
        RSI2 = 100.0 - (100.0 / (1.0 + RS2))
         
        traces3.append(plotly.graph_objs.Scatter(x = df.DateTime, y = RSI2, name = 'RSI',mode = 'lines'))
        
        layout3 = plotly.graph_objs.Layout(title = 'RSI')
        
        return {'data': traces3,'layout':layout3}
     
     
    elif graphtype==4 : # ichimoku cloud
        
        high_9 = df['High'].rolling(window= 9).max()
        low_9 = df['Low'].rolling(window= 9).min()
        df['tenkan_sen'] = (high_9 + low_9) /2
        
        high_26 = df['High'].rolling(window= 26).max()
        low_26 = df['Low'].rolling(window= 26).min()
        df['kijun_sen'] = (high_26 + low_26) /2
        
        last_index=df.iloc[-1:].index[0]
        last_date=df['DateTime'].iloc[-1].date()
        for i in range(26):
            df.loc[last_index+1+i,'DateTime']=last_date+timedelta(days=i)
            
        df['senkou_span_a'] = ((df['tenkan_sen'] + df['kijun_sen']) / 2).shift(26)
        
        high_52 = df['High'].rolling(window= 52).max()
        low_52 = df['Low'].rolling(window= 52).min()
        df['senkou_span_b'] = ((high_52 + low_52) /2).shift(26)
        
        df['chikou_span'] = df['Adj Close'].shift(-22)
        
        
        traces4=[]
        traces4.append(plotly.graph_objs.Scatter(x = df.DateTime, y = df['Adj Close'],  name = 'Close',mode = 'lines'))
        traces4.append(plotly.graph_objs.Scatter(x = df.DateTime, y = df['tenkan_sen'], name = 'tenkan_sen',mode = 'lines'))
        traces4.append(plotly.graph_objs.Scatter(x = df.DateTime, y = df['kijun_sen'],  name = 'kijun_sen',mode = 'lines'))
        traces4.append(plotly.graph_objs.Scatter(x = df.DateTime, y = df['senkou_span_a'],fill = 'none', name = 'senkou_span_a',mode = 'lines'))
        traces4.append(plotly.graph_objs.Scatter(x = df.DateTime, y = df['senkou_span_b'],fill = 'tonexty' ,name = 'senkou_span_b',mode = 'lines'))
        traces4.append(plotly.graph_objs.Scatter(x = df.DateTime, y = df['chikou_span'],name = 'chikou_span',mode = 'lines'))
        
        layout4 = plotly.graph_objs.Layout(title = 'Ichimoku Cloud')
        
        return {'data': traces4,'layout':layout4}

if __name__ == '__main__':
    app.run_server(debug=True)
