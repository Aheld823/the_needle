from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os

app = Dash(__name__)

app.layout = html.Div([
    html.H4('The Needle Dashboard')
    ,dcc.Checklist(
        id = 'toggle-rangeslider'
        ,options=[{'label':'include Rangeslider'
                   ,'value':'slider'}]
                   ,value = ['slider']
    )
    ,dcc.Graph(id = 'graph'),
])

@app.callback(
    Output("graph", "figure")
    ,Input("toggle-rangeslider", "value")
)

def display_candlestick(value):
    # df_events = pd.read_csv('../input/events.csv')
    df_scores = pd.read_csv('input/scores.csv')
    
    # Date conversation (can probably get rid of eventually)
    df_scores['date'] = pd.to_datetime(df_scores['date'], utc=True)
    df_scores['date'] = df_scores['date'].dt.tz_localize(None)
    df_scores = df_scores.astype({'article_id': 'object'
                                , 'date': 'datetime64[ns]'
                                ,'net_score': int
                                ,'needle_rating':int
                                ,'url':'object'})

    # Create base start point and setting colors 
    df_scores['base'] = df_scores[['needle_rating_previous', 'needle_rating']].min(axis=1)
    df_scores['color'] = df_scores['net_score'].apply(
        lambda x: 'green' if x > 0 else 'red' if x < 0 else 'gray'
    )
    # Give fake volume to cases where the needle doesn't change
    zero_mask = df_scores['net_score'] == 0
    df_scores.loc[zero_mask, 'net_score'] = 1.0
    df_scores.loc[zero_mask, 'base'] = df_scores.loc[zero_mask, 'base'] - 1

    # Date conversation (can probably get rid of eventually)
    df_scores['date'] = pd.to_datetime(df_scores['date'], utc=True)
    df_scores['date'] = df_scores['date'].dt.tz_localize(None)
    df_scores = df_scores.astype({'article_id': 'object'
                                , 'date': 'datetime64[ns]'
                                ,'net_score': int
                                ,'needle_rating':int
                                ,'url':'object'})
    ### 
    
    # Find gaps in events
    dt_obs = df_scores['date'].dt.normalize()
    dt_all = pd.date_range(start=dt_obs.min(), end=dt_obs.max(), freq='D')
    dt_breaks = [d for d in dt_all if d not in dt_obs.values]
    dt_breaks = pd.to_datetime(dt_breaks)

    # Create bar chart
    fig = go.Figure(data = [go.Bar(
        x = df_scores['date']          
        ,y = df_scores['net_score']
        ,base = df_scores['base']       
        ,marker_color = df_scores['color']
        # ,width = 0.5

    )])

    fig.update_layout(
    title = "Open–Close Bar Chart",
    yaxis_title = "Price",
    xaxis_title = "Date",
    bargap = 0
    )
    
    # Remove gaps between events
    fig.update_xaxes(rangebreaks=[dict(values=dt_breaks)])


#     df_scores['high'] = df_scores[['needle_rating_previous', 'needle_rating']].max(axis=1)
#     df_scores['low'] = df_scores[['needle_rating_previous', 'needle_rating']].min(axis=1)




#     # Date conversation (can probably get rid of eventually)
#     df_scores['date'] = pd.to_datetime(df_scores['date'], utc=True)
#     df_scores['date'] = df_scores['date'].dt.tz_localize(None)
#     df_scores = df_scores.astype({'article_id': 'object'
#                                 , 'date': 'datetime64[ns]'
#                                 ,'net_score': int
#                                 ,'needle_rating':int
#                                 ,'url':'object'})
    
#     # Find gaps in events
#     dt_obs = df_scores['date'].dt.normalize()
#     dt_all = pd.date_range(start=dt_obs.min(), end=dt_obs.max(), freq='D')
#     dt_breaks = [d for d in dt_all if d not in dt_obs.values]
#     dt_breaks = pd.to_datetime(dt_breaks)

#     df_scores['hover'] = (
#     'Date: ' + df_scores['date'].astype(str) + '<br>' +
#     'Open: ' + df_scores['needle_rating_previous'].astype(str) + '<br>' +
#     'Close: ' + df_scores['needle_rating'].astype(str) + '<br>' +
#     'Net Score: ' + df_scores['net_score'].astype(str)
# )

#     # Build candlestick
#     fig = go.Figure(go.Candlestick(
#         x = df_scores['date']
#         ,open = df_scores['needle_rating_previous']
#         ,high = df_scores['high']
#         ,low = df_scores['low']
#         ,close = df_scores['needle_rating']
#         ,text=df_scores['hover']
#         ,hoverinfo='text'
#     ))
    
#     fig.update_layout(
#         xaxis_rangeslider_visible='slider' in value
#     )

#     # Remove gaps between events
#     fig.update_xaxes(rangebreaks=[dict(values=dt_breaks)])

    return fig

app.run(debug=True)
