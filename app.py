
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from datetime import date
import dash
import dash_html_components as html
import flask

import base64
import pandas as pd
#from scipy import stats
import numpy as np

import dash_daq as daq
#from datetime import datetime
#import datetime as dt

import dash


df = pd.read_csv("create_tte_data/NDVI_series.csv")
df['date'] = pd.to_datetime(df['date'])

df['date_ordinal'] = pd.to_datetime(df['date']).apply(lambda date: date.toordinal())
list_of_fields = df['field_ID'].astype(int).unique().tolist()

pred_df = pd.read_csv("create_tte_data/Prophet_NDVI_preds.csv")
pred_df['ds'] = pd.to_datetime(pred_df['ds'])

yield_df = pd.read_csv("create_tte_data/field_sizes.csv")



def get_last_harvest(field_nr):
    
    mydata = df[df['field_ID']==field_nr][['date', 'NDVI']]
    mydata = mydata.rename(columns={'date': 'ds', 'NDVI': 'y'})
    # Import prediction dataframe
    pred_prophet = pred_df[pred_df['field_ID']==field_nr]

    # Get last day of real data
    max_date = mydata['ds'].max()
    
    # Get predictions if we are in negative, get dataset +half a year later 
    if mydata[mydata['ds']==max_date]['y'].tolist()[0]<=0:
        pred_prophet_future = pred_prophet[pred_prophet['ds']>(max_date+pd.DateOffset(days=200))] 
    else:
         pred_prophet_future = pred_prophet[pred_prophet['ds']>(max_date)]  
    # Get the first time when NDVI turns negative in the future = Harvested
    next_harvest_time = pred_prophet_future[pred_prophet_future['yhat']<=0][['ds', 'yhat']]['ds'].min()

    return next_harvest_time, pred_prophet



external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)    
server = app.server # the Flask app

app.layout = html.Div([
        
        html.Div([ html.Div([html.H1('Single field monitor'), 
                   html.Label('Select a field:'),
                         dcc.Dropdown(
                            id='field_id_dropdown',
                                options=[{'label': i, 'value': i} for i in list_of_fields],
                                         value=1,
                                  ) 
                          ],style={'width': '45%',  'display': 'inline-block', 'vertical-align': 'middle'},  
                            ), 
                 ]),
    
    

       html.Div([   
                 html.Div([
            html.Img(id='image')
               ],style={'width': '30%',  'display': 'inline-block', 'vertical-align': 'left'},
               ), 

           html.Div([                          
                            dcc.Graph(id='veg_index_graph'),
                            ], style={'width': '55%',  'display': 'inline-block', 'vertical-align': 'right'},  
                        ),
    
                   ],           
                 className="column"
                 ),

       html.Div([
                html.Div('x', style={'black': 'blue', 'fontSize': 30},  id='my-div-element_tte'),
                html.Div('x', style={'black': 'blue', 'fontSize': 30},  id='my-div-element_date'),
                html.Div('x', style={'black': 'blue', 'fontSize': 30},  id='my-div-element_yield'),

                 ], style={'marginBottom': 50, 'marginTop': 25})
             ])
    
######################### Callbacks ######################################3333


@app.callback(
    Output('my-div-element_tte', 'children'),
    [Input('field_id_dropdown', 'value')])
def callback_days(xaxis_column_name):
        
    next_harvest_time, pred_prophet = get_last_harvest(xaxis_column_name)
    
    last_date_dataset = pd.to_datetime(df[df['field_ID'] == xaxis_column_name]['date'].max())
    print('last date of dataset', last_date_dataset)
    
    return 'Time till next harvest: %s' %(next_harvest_time-last_date_dataset).days + ' days' 


@app.callback(
    Output('my-div-element_date', 'children'),
    [Input('field_id_dropdown', 'value')])
def callback_days(xaxis_column_name):
        
    next_harvest_time, pred_prophet = get_last_harvest(xaxis_column_name)    
    print('Next harvest', next_harvest_time)  
    return f'Next harvest date: {next_harvest_time}'

#############################################################################################33
@app.callback(
    Output('my-div-element_yield', 'children'),
    [Input('field_id_dropdown', 'value')])
def callback_days(xaxis_column_name):
        
    field_size = yield_df[yield_df['field_ID']==xaxis_column_name]['hectares'].tolist()[0]
    field_yield = yield_df[yield_df['field_ID']==xaxis_column_name]['yield_tonnes'].tolist()[0]
    return 'The field is %.3f'%field_size+' hectares, with a %.3f'%field_yield+' tonnes expected yield'

#############################################################################################33


@app.callback(
     Output('veg_index_graph', 'figure'),
    [Input('field_id_dropdown', 'value')])
def update_graph(xaxis_column_name):

    mydata = df[df['field_ID']==xaxis_column_name][['date', 'NDVI']]
    mydata = mydata.rename(columns={'date': 'ds', 'NDVI': 'y'})

    next_harvest_time, pred_prophet = get_last_harvest(xaxis_column_name)
    harv_time_line_x = [next_harvest_time, next_harvest_time]
    harv_time_line_y = [-0.2, 0.4]
    
    return {
        'data': [go.Scatter(
            x=mydata['ds'],
            y=mydata['y'],            
            mode='markers',
            name='Sentinel-2 Data',
            marker={
                'size': 15,
                'opacity': 0.5,
                'color':'black', 
                'line': {'width': 0.5, 'color': 'white'}
                     }
                      ),         
               go.Scatter(
                    x=pred_prophet['ds'], 
                    y=pred_prophet['yhat'],       
                    mode='lines',
                    name='Forecast',
                    marker={
                        'color':'red',
                        'size': 15,
                        'opacity': 0.5,
                        'line': {'width': 2, 'color': 'white'}
                        }
                          ),
                 
                go.Scatter(
                    x=harv_time_line_x, 
                    y=harv_time_line_y,       
                    mode='lines',
                    name='Next Harvest',
                    marker={
                        'color':'black',
                        'size': 15,
                        'opacity': 0.8,
                        'line': {'width': 1, 'color': 'white'}
                        }
                          )
                 
                 
                ],
        
        'layout': go.Layout(
            xaxis={'title': 'Date'}, 
            yaxis={'title': 'Vegetation Index (NDVI)'}, #, 'range': [20, 90]},
            hovermode='closest'
        )
    }


@app.callback(
    dash.dependencies.Output('image', 'src'),
    [dash.dependencies.Input('field_id_dropdown', 'value')])
def update_image_src(value):
    image_filename = f'field_highlights/hlght_{value}.png'  # replace with your own image
    encoded_image = base64.b64encode(open(image_filename, 'rb').read())

    return 'data:image/png;base64,{}'.format(encoded_image.decode())

    
if __name__ == '__main__':
    app.run_server(debug=True)


    