from dash import Dash, html, dcc, callback, Output, Input, dash_table, State, callback_context
import plotly.express as px
import plotly.graph_objects as go
from dash.exceptions import PreventUpdate
import pandas as pd
import os
import datetime as datetime

# Initial data wrangling for the app
df_events = pd.read_excel('input/events.xlsx')
df_scores = pd.read_excel('input/scores.xlsx')

## Create base start point and setting colors 
df_scores.loc[df_scores['article_id']==1, 'needle_rating_previous'] = 70.0
df_scores['base'] = df_scores[['needle_rating_previous', 'needle_rating']].min(axis=1)

df_scores['color'] = df_scores['net_score'].apply(
    lambda x: '#b8e6bf' if x > 0 else '#d63678' if x < 0 else '#949494'
)

## Create y variable such that those with net_score == 0 show up on the chart
df_scores['y'] = df_scores['net_score']
zero_mask = df_scores['net_score'] == 0
df_scores.loc[zero_mask, 'y'] = 1.0

## Find gaps in events so we can exclude them in the future
dt_obs = df_scores['date'].dt.normalize()
dt_all = pd.date_range(start=dt_obs.min(), end=dt_obs.max(), freq='D')
dt_breaks = [d for d in dt_all if d not in dt_obs.values]
dt_breaks = pd.to_datetime(dt_breaks)

marks = {
    int(d.timestamp()): d.strftime('%m/%d/%y')
    for i, d in enumerate(dt_all)
    if i % 7 == 0 or d == dt_all[-1] or d == dt_all[0]  # every 10th + first/last
}

## Creates text for table
df_events['title_desc'] = (
    '**' + df_events['title'] + '** \n\n' + df_events['description']
)
df_events['links'] = (
    '**[Link](' + df_events['url'] +')**'
)
df_events['color'] = df_events['score'].apply(
    lambda x: '#b8e6bf' if x > 0 else '#d63678' if x < 0 else '#949494'
)

# Initiate App
app = Dash(__name__, suppress_callback_exceptions=True)

## Set up App layout
app.layout = html.Div([
    html.H1('THE NEEDLE DASHBOARD')
    ,html.Div(id='needle-rating-box')
    ,html.Div([html.Button("Reset View", id="reset-button", n_clicks=0, className='dash-button')
    ], style={
        'display': 'flex',
        'justifyContent': 'flex-end',
        'padding': '10px'}
    , id='reset-button-container'
    , className="reset-button-container"
    )
    ,dcc.Graph(id = 'waterfall-graph')
    ,html.Div([
        dcc.RangeSlider(
            id='date-slider'
            ,min=int(dt_all[0].timestamp())
            ,max=int(dt_all[-1].timestamp())
            ,value=[int(dt_all[0].timestamp()), int(dt_all[-1].timestamp())]
            ,marks=marks
            ,className='date-slider'
        )
    ], style={'margin-bottom': '10px'}
    , id='slider-container'
    ,className='slider-wrapper')  
    ,html.Center([
        html.Button("← Previous", id="prev-day", n_clicks=0, className='dash-button')
        ,html.Button("Next →", id="next-day", n_clicks=0, className='dash-button')
    ]
    , id='detail-nav-buttons'
    , className='detail-nav-buttons-container'
    )  
    ,html.Div([dash_table.DataTable(
    id='events-table'
    ,columns=[
        {"name": "Date", "id": "date_str"}
        ,{"name": "Article ID", "id": "article_id"}
        ,{"name": "Event ID", "id": "event_id"}
        ,{"name": "Details", "id": "title_desc", "type": "text", "presentation": "markdown"}
        ,{"name": "Score", "id":"score"}
        ,{"name": "Links", "id": "links", "type": "text", "presentation": "markdown"}
    ]
    ,style_cell_conditional=[
    {'if': {'column_id': 'date_str'}, 'width': '50px'},
    {'if': {'column_id': 'article_id'}, 'width': '75px'},
    {'if': {'column_id': 'event_id'}, 'width': '75px'},
    {'if': {'column_id': 'score'}, 'width': '50px'},
    {'if': {'column_id': 'links'}, 'width': '50px'},
    ]
    ,page_current = 0
    ,page_size = 5
    ,page_action = 'custom'
    ,data=df_events.to_dict('records')
    ,style_cell={
        'border':'none'
        ,'borderBottom': '1px solid #cccccc'
        ,'fontFamily': "Noto Sans, Helvetic, sans-serif"
        ,'frontSize': '10px'
        ,'whiteSpace': 'normal'
        ,'height': 'auto'
        ,'textAlign': 'left'
        ,'backgroundColor': '#ffffff'
        }
    ,style_header={
        'borderBottom': '2px solid #333333'
        ,'fontFamily': 'Helvetica, sans-serif'
        ,'fontSize': '15px'
        ,'fontWeight': '600'
        ,'textAlign': 'left'
        ,'backgroundColor': '#ffffff'}
    )
    ]
    )
    ,dcc.Store(id='click-store', data=None)
    ,dcc.Store(id='relayout-store', data={})
    ,dcc.Store(id='chart-mode', data='main')
    ,html.Br()
    ,html.Br()
    ,html.Br()
], style={
    'marginLeft': '10%',
    'marginRight': '10%',
    'padding': '10px',
    'backgroundColor': '#ffffff'
})


## Callbacks 
### Show/hide buttons and slider depending on mode
@app.callback(
    Output('slider-container', 'style')
    ,Output('detail-nav-buttons', 'style')
    ,Input('chart-mode', 'data')
)
def toggle_detail_controls(mode):
    if mode == 'detail':
        # hide slider, show nav buttons
        return {'display': 'none'}, {'display': 'block', 'marginTop':'10px'}
    # main mode: show slider, hide buttons
    return {'display': 'block'}, {'display': 'none'}


### Determine value for needle-rating-box
@app.callback(
    Output('needle-rating-box', 'children')
    ,Input('date-slider', 'value')
    ,Input('relayout-store', 'data')
    ,Input('chart-mode', 'data')
    ,Input('click-store', 'data')
)
def update_rating_text(date_range, relayoutData, mode, clickData):
    start_ts, end_ts = date_range
    start_date = pd.to_datetime(datetime.datetime.fromtimestamp(start_ts))
    end_date = pd.to_datetime(datetime.datetime.fromtimestamp(end_ts))
    
    # Filter on zoom
    if relayoutData and 'xaxis.range[0]' in relayoutData and 'xaxis.range[1]' in relayoutData:
        zoom_start = pd.to_datetime(relayoutData['xaxis.range[0]']).normalize()
        zoom_end = pd.to_datetime(relayoutData['xaxis.range[1]']).normalize()
        df_filtered = df_scores[df_scores['date'].between(zoom_start, zoom_end)]
    else:
        df_filtered = df_scores[df_scores['date'].between(start_date, end_date)]

    # If in detail mode, filter down to clicked date
    if mode == 'detail' and clickData:
        clicked_date = pd.to_datetime(clickData['points'][0]['x']).normalize()
        clicked_date_str = clicked_date.strftime('%m/%d/%y')
        df_filtered = df_filtered[df_filtered['date'] == clicked_date]
        if not df_filtered.empty:
            current_rating = df_filtered.sort_values('date', ascending=False)['needle_rating'].iloc[0]
            return html.Span([html.Strong(f"NEEDLE RATING ON {clicked_date_str}: "),str(current_rating)])
        else:
            return html.Span([html.Strong("NO RATING AVAILABLE FOR "),str(clicked_date_str)])

    # Find latest available rating (sorted by date descending)
    if not df_filtered.empty:
        latest_rating = df_filtered.sort_values('date', ascending=False)['needle_rating'].iloc[0]
        return html.Span([html.Strong("CURRRENT NEEDLE RATING: "),str(latest_rating)])
    else:
        return html.Span([html.Strong("NO RATING AVILABLE FOR CURRENT FILTER")])


### Display/filter waterfall-graph, toggle to detail mode
@app.callback(
    Output("waterfall-graph", "figure"),
    Input("date-slider", "value"),
    Input('relayout-store', 'data'),
    Input("chart-mode", "data"),
    Input("click-store", "data")
)
def update_chart(date_range, relayoutData, mode, clickData):
    start_ts, end_ts = date_range
    start_date = pd.to_datetime(datetime.datetime.fromtimestamp(start_ts))
    end_date = pd.to_datetime(datetime.datetime.fromtimestamp(end_ts))
    
    # Toggle to detail mode
    if mode == 'detail' and clickData:
        clicked_date = pd.to_datetime(clickData['points'][0]['x']).normalize()
        df_filtered = df_events[df_events['date'] == clicked_date]

        fig = go.Figure(data = [go.Bar(
        x = df_filtered['event_id']          
        ,y = df_filtered['score']
        ,base = 0      
        ,marker_color = df_filtered['color']
        ,customdata = df_filtered[['title']]
        ,name =''
        ,hovertemplate = 
                "<b>Title:</b> %{customdata[0]}<br>"
                +"<b>Event:</b> %{x}<br>" 
                +"<b>Score:</b> %{y}<br>"
        )])
        fig.update_layout(
        bargap = 0,
        plot_bgcolor =  '#ffffff',
        paper_bgcolor = '#ffffff',
        yaxis=dict(
            title="Needle Score",
            showgrid=True,
            gridcolor='#e0e0e0'  
        ),
        xaxis=dict(
            title="Event",
            showgrid=True,
            gridcolor='#e0e0e0'
        ))
        return fig

    # Filter on zoom
    if relayoutData and 'xaxis.range[0]' in relayoutData and 'xaxis.range[1]' in relayoutData:
        zoom_start = pd.to_datetime(relayoutData['xaxis.range[0]']).normalize()
        zoom_end = pd.to_datetime(relayoutData['xaxis.range[1]']).normalize()
        df_filtered = df_scores[df_scores['date'].between(zoom_start, zoom_end)]
    else:
        df_filtered = df_scores[df_scores['date'].between(start_date, end_date)]
    
    # Build figure
    fig = go.Figure(data = [go.Bar(
        x = df_filtered['date']          
        ,y = df_filtered['y']
        ,base = df_filtered['needle_rating_previous']       
        ,marker_color = df_filtered['color']
        ,customdata = df_filtered[['needle_rating_previous','needle_rating','net_score']]
        ,hovertemplate = 
                "<b>Date:</b> %{x}<br>" 
                +"<b>Previous Score:</b> %{customdata[0]}<br>"
                +"<b>New Score:</b> %{customdata[1]}<br>"
                +"<b>Net Change:</b> %{customdata[2]}<extra></extra>"
    )])
    fig.update_layout(
    yaxis_title = "Needle Score",
    xaxis_title = "Date",
    bargap = 0,
    plot_bgcolor =  '#ffffff',
    paper_bgcolor = '#ffffff',
    yaxis=dict(
        title="Needle Score",
        showgrid=True,
        gridcolor='#e0e0e0'  
    ),
    xaxis=dict(
        title="Date",
        showgrid=True,
        gridcolor='#e0e0e0'
    ))
    fig.update_xaxes(rangebreaks=[dict(values=dt_breaks)])

    return fig


### Controls data storage and output
@app.callback(
    Output('click-store', 'data'),
    Output('chart-mode', 'data'),
    Input('waterfall-graph', 'clickData'),
    Input('prev-day', 'n_clicks'),
    Input('next-day', 'n_clicks'),
    Input('reset-button', 'n_clicks'),
    State('chart-mode', 'data'),
    State('click-store', 'data'),
    prevent_initial_call=True
)
def handle_all_interactions(clickData, prev_clicks, next_clicks, reset_clicks, mode, stored_click):
    triggered = callback_context.triggered[0]['prop_id']

    # Reset button trumps all
    if triggered == 'reset-button.n_clicks':
        return None, 'main'

    # Clicking on bar will trigger detailed mode
    if triggered == 'waterfall-graph.clickData':
        if mode == 'detail':
            raise PreventUpdate
        return clickData, 'detail'

    # Navigation within detailed mode
    if mode == 'detail' and stored_click and 'points' in stored_click:
        # build a list of all normalized dates
        dates = list(dt_obs)
        current = pd.to_datetime(stored_click['points'][0]['x']).normalize()
        idx = dates.index(current)

        if triggered == 'next-day.n_clicks':
            new_idx = max(0, idx - 1)
        elif triggered == 'prev-day.n_clicks':
            new_idx = min(len(dates) - 1, idx + 1)
        else:
            raise PreventUpdate

        new_date = dates[new_idx]
        new_click = {'points': [{'x': new_date.strftime('%Y-%m-%d')}]}
        return new_click, 'detail'

    raise PreventUpdate


### Controls storage of zoom information
@app.callback(
    Output('relayout-store','data'),
    Input('waterfall-graph','relayoutData'),
    Input('reset-button','n_clicks'),
    prevent_initial_call=True
)
def store_relay(relayoutData, n_clicks):
    triggered = callback_context.triggered[0]['prop_id']
    if triggered == 'reset-button.n_clicks':
        return {}
    return relayoutData


### Controls filtering of table
@app.callback(
    Output('events-table', 'data'),
    Output('events-table', 'page_count'),
    Input('events-table', "page_current"),
    Input('events-table', "page_size"),
    Input('date-slider', 'value'),
    Input('click-store', 'data'),
    Input('relayout-store', 'data')
)
def update_table(page_current, page_size, date_range, clickData, relayoutData):    
    start_ts, end_ts = date_range
    start_date = pd.to_datetime(datetime.datetime.fromtimestamp(start_ts))
    end_date = pd.to_datetime(datetime.datetime.fromtimestamp(end_ts))

    df_filtered = df_events.copy()

    ### If reset then default to range slider filter
    if relayoutData and relayoutData.get('xaxis.autorange') == True:
        df_filtered = df_events[df_events['date'].between(start_date, end_date)]

    # If there is a zoom then filter on that
    elif relayoutData and 'xaxis.range[0]' in relayoutData and 'xaxis.range[1]' in relayoutData:
        zoom_start = pd.to_datetime(relayoutData['xaxis.range[0]']).normalize()
        zoom_end = pd.to_datetime(relayoutData['xaxis.range[1]']).normalize()
        df_filtered = df_events[df_events['date'].between(zoom_start, zoom_end)]
        if clickData and 'points' in clickData:
            clicked_date = pd.to_datetime(clickData['points'][0]['x']).normalize()
            df_filtered = df_events[df_events['date'] == clicked_date]

    # If there is a click then filter to that
    elif clickData and 'points' in clickData:
        clicked_date = pd.to_datetime(clickData['points'][0]['x']).normalize()
        df_filtered = df_events[df_events['date'] == clicked_date]

    # Fallback: use slider range
    else:
        df_filtered = df_events[df_events['date'].between(start_date, end_date)]

    # Controls pagination display for the table
    total_records = len(df_filtered)
    total_pages = max(1, -(-total_records // page_size))  # ceiling division
    page_data = df_filtered.iloc[
        page_current * page_size : (page_current + 1) * page_size
    ].to_dict('records')

    page_text = f"Page {page_current + 1} of {total_pages}"

    return page_data, total_pages



if __name__ == "__main__":
    app.run(debug=True)
