from dash import Dash, html, dcc, callback, Output, Input, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os
import datetime as datetime

df_events = pd.read_csv('input/events.csv')
df_scores = pd.read_csv('input/scores.csv')

# Date conversation (can probably get rid of eventually)
df_scores['date'] = pd.to_datetime(df_scores['date'], utc=True)
df_scores['date'] = df_scores['date'].dt.tz_localize(None)
df_scores = df_scores.astype({'article_id': 'object'
                            ,'date': 'datetime64[ns]'
                            ,'net_score': int
                            ,'needle_rating':int
                            ,'url':'object'})
df_scores['date'] = df_scores['date'].dt.normalize()

df_events['date'] = pd.to_datetime(df_events['date'], utc=True)
df_events['date'] = df_events['date'].dt.tz_localize(None)
df_events = df_events.astype({'article_id': 'object'
                            ,'date': 'datetime64[ns]'
                            ,'event_id':'object'
                            ,'title':'object'
                            ,'description':'object'
                            ,'score': int
                            ,'url':'object'})
df_events['date'] = df_events['date'].dt.normalize()
df_events['date_str'] = df_events['date'].dt.strftime('%m/%d/%y') 
### 

# Create base start point and setting colors 
df_scores['base'] = df_scores[['needle_rating_previous', 'needle_rating']].min(axis=1)
df_scores['color'] = df_scores['net_score'].apply(
    lambda x: 'green' if x > 0 else 'red' if x < 0 else 'gray'
)

# Give fake volume to cases where the needle doesn't change
zero_mask = df_scores['net_score'] == 0
df_scores.loc[zero_mask, 'net_score'] = 1.0
df_scores.loc[zero_mask, 'base'] = df_scores.loc[zero_mask, 'base'] - 1

# Find gaps in events
dt_obs = df_scores['date'].dt.normalize()
dt_all = pd.date_range(start=dt_obs.min(), end=dt_obs.max(), freq='D')
dt_breaks = [d for d in dt_all if d not in dt_obs.values]
dt_breaks = pd.to_datetime(dt_breaks)

marks = {
    int(d.timestamp()): d.strftime('%m/%d/%y')
    for i, d in enumerate(dt_all)
    if i % 7 == 0 or d == dt_all[-1] or d == dt_all[0]  # every 10th + first/last
}

# Creates text for table
df_events['title_desc'] = (
    '**' + df_events['title'] + '** \n\n' + df_events['description']
)
df_events['links'] = (
    '**[Link](' + df_events['url'] +')**'
)

app = Dash(__name__, suppress_callback_exceptions=True)

app.layout = html.Div([
    html.H4('The Needle Dashboard')
    ,dcc.RangeSlider(
        id = 'date-slider'
        ,min = int(dt_all[0].timestamp())
        ,max = int(dt_all[-1].timestamp())
        ,value = [int(dt_all[0].timestamp()), int(dt_all[-1].timestamp())]
        ,marks = marks
    )
    ,dcc.Graph(id = 'waterfall-graph')
    ,dcc.Store(id='click-store', data=None)
    ,dash_table.DataTable(
    id='events-table'
    ,columns=[
        {"name": "Date", "id": "date_str"}
        ,{"name": "Article ID", "id": "article_id"}
        ,{"name": "Event ID", "id": "event_id"}
        ,{"name": "Details", "id": "title_desc", "type": "text", "presentation": "markdown"}
        ,{"name": "Score", "id":"score"}
        ,{"name": "Links", "id": "links", "type": "text", "presentation": "markdown"}
    ]
    ,page_current = 0
    ,page_size = 5
    ,page_action = 'custom'
    ,data=df_events.to_dict('records')
    ,style_cell={'whiteSpace': 'normal', 'height': 'auto'}
    )
    # ,html.Div(id='page-counter', style={'marginTop': '10px'})
    ,html.Br()
    ,html.Br()
    ,html.Br()
    ,html.Br()
    ,html.Br()
])


# Callbacks
@app.callback(
    Output("waterfall-graph", "figure"),
    Input("date-slider", "value")
)
def update_chart(date_range):
    start_ts, end_ts = date_range
    start_date = pd.to_datetime(datetime.datetime.fromtimestamp(start_ts))
    end_date = pd.to_datetime(datetime.datetime.fromtimestamp(end_ts))
    
    df_filtered = df_scores[df_scores['date'].between(start_date, end_date)]
    
    # Create bar chart
    fig = go.Figure(data = [go.Bar(
        x = df_filtered['date']          
        ,y = df_filtered['net_score']
        ,base = df_filtered['base']       
        ,marker_color = df_filtered['color']
        ,customdata = df_filtered[['needle_rating']]
        ,hovertemplate = 
                "<b>Date:</b> %{x}<br>" 
                +"<b>Previous Score:</b> %{base}<br>"
                +"<b>New Score:</b> %{customdata[0]}<br>"
                +"<b>Net Change:</b> %{y}<extra></extra>"
        # ,width = 0.5
    )])
    fig.update_layout(
    # title = "Open–Close Bar Chart",
    yaxis_title = "Needle Score",
    xaxis_title = "Date",
    bargap = 0
    ,dragmode = 'zoom'
    # ,doubleclick = 'none'
    )
    
    # Remove gaps between events
    fig.update_xaxes(rangebreaks=[dict(values=dt_breaks)])
    # fig.show(config={'doubleClick': False})


    return fig

@app.callback(
    Output('reset-signal', 'data'),
    Input('waterfall-graph', 'relayoutData')
)
def detect_double_click(relayoutData):
    return relayoutData.get('xaxis.autorange') if relayoutData else False


@app.callback(
    Output('click-store', 'data'),
    Input('waterfall-graph', 'clickData'),
    Input('waterfall-graph', 'relayoutData')
)
def manage_click(clickData, relayoutData):
    if relayoutData and relayoutData.get('xaxis.autorange'):
        return None  # Clear selection on double click
    return clickData

@app.callback(
    Output('events-table', 'data'),
    Output('events-table', 'page_count'),
    Input('events-table', "page_current"),
    Input('events-table', "page_size"),
    Input('date-slider', 'value'),
    Input('click-store', 'data'),
    Input('waterfall-graph', 'relayoutData') 
)
def update_table(page_current, page_size, date_range, clickData, relayoutData):
    # df_filtered = df_events.copy()
    
    start_ts, end_ts = date_range
    start_date = pd.to_datetime(datetime.datetime.fromtimestamp(start_ts))
    end_date = pd.to_datetime(datetime.datetime.fromtimestamp(end_ts))

    df_filtered = df_events.copy()

    # Priority 1: Reset view on double-click
    if relayoutData and relayoutData.get('xaxis.autorange') == True:
        df_filtered = df_events[df_events['date'].between(start_date, end_date)]

    # Priority 2: Zoom selection via drag
    elif relayoutData and 'xaxis.range[0]' in relayoutData and 'xaxis.range[1]' in relayoutData:
        zoom_start = pd.to_datetime(relayoutData['xaxis.range[0]']).normalize()
        zoom_end = pd.to_datetime(relayoutData['xaxis.range[1]']).normalize()
        df_filtered = df_events[df_events['date'].between(zoom_start, zoom_end)]

    # Priority 3: Bar click
    elif clickData and 'points' in clickData:
        clicked_date = pd.to_datetime(clickData['points'][0]['x']).normalize()
        df_filtered = df_events[df_events['date'] == clicked_date]

    # Fallback: use slider range
    else:
        df_filtered = df_events[df_events['date'].between(start_date, end_date)]

    # Filter data based on slider if desired
    # start_ts, end_ts = date_range
    # start_date = pd.to_datetime(datetime.datetime.fromtimestamp(start_ts))
    # end_date = pd.to_datetime(datetime.datetime.fromtimestamp(end_ts))
    
    # df_filtered = df_events[df_events['date'].between(start_date, end_date)]

    # Pagination
    total_records = len(df_filtered)
    total_pages = max(1, -(-total_records // page_size))  # ceiling division
    page_data = df_filtered.iloc[
        page_current * page_size : (page_current + 1) * page_size
    ].to_dict('records')

    page_text = f"Page {page_current + 1} of {total_pages}"

    return page_data, total_pages

if __name__ == "__main__":
    app.run(debug=True)
    # app.run(debug=False)
    # app.server_run()
