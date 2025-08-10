from dash import Dash, html, dcc, callback, Output, Input, dash_table, State, callback_context
import dash_bootstrap_components as dbc
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

## Fix time zones to avoid bad filtering
df_scores['date'] = pd.to_datetime(df_scores['date'], errors='coerce').dt.tz_localize('UTC')
df_events['date'] = pd.to_datetime(df_events['date'], errors='coerce').dt.tz_localize('UTC')

## Find gaps in events so we can exclude them in the future
dt_obs = df_scores['date'].dt.normalize()
dt_all = pd.date_range(start=dt_obs.min(), end=dt_obs.max(), freq='D', tz='UTC')
dt_obs_set = set(dt_obs)
dt_breaks = [d for d in dt_all if d not in dt_obs_set]
# dt_breaks = [d for d in dt_all if d not in dt_obs.values]
dt_breaks = pd.to_datetime(dt_breaks, utc=True)

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
app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])

## Set up App layout
app.layout = html.Div([
    html.H1('THE NEEDLE DASHBOARD', id='header', style={'cursor': 'pointer'})
    ,dbc.Modal(
        [
            dbc.ModalHeader("THE NEEDLE DASHBOARD"),
            dbc.ModalBody(
            dcc.Markdown('''
                <p>Welcome to The Needle dashboard. This is a project tracking the 
                <a href="https://washingtoncitypaper.com/article/759589/reintroducing-the-needle/" target="_blank" rel="noopener noreferrer">
                Washington City Paper quality of life index</a>.</p>

                *What can the tool do?*\n
                Please click around to find out! The main graph tracks The Needle rating over time. 
                By clicking on one of the waterfalls you can zoom in and see the events from that day that make up The Needle rating.

                <p><em>This is a volunteer project created by Andrew Held. To learn more visit the project's 
                <a href="https://github.com/Aheld823/the_needle" target="_blank" rel="noopener noreferrer">GitHub</a>.</em></p>
            ''', dangerously_allow_html=True))
            ,dbc.ModalFooter(
                dbc.Button("Close", id="close-popup", className="dash-button", n_clicks=0)
            ),
        ],
        id="popup-modal",
        size='lg',
        is_open=True, 
        backdrop=True, 
        keyboard=True,  
    )
    ,html.Div(id='needle-rating-box')
    ,html.Div([html.Button("Reset View", id="reset-button", n_clicks=0, className='dash-button')
    ], style={
        'display': 'flex',
        'justifyContent': 'flex-start',
        'padding': '10px'}
    , id='reset-button-container'
    , className="reset-button-container"
    )
    ,dcc.Graph(id = 'waterfall-graph')
    ,html.Div([
        html.Div(id='slider-lock-indicator', style={'textAlign':'left','marginBottom': '10px'}),
        dcc.RangeSlider(
            id='date-slider'
            ,min=int(dt_all[0].timestamp())
            ,max=int(dt_all[-1].timestamp())
            ,value=[int(dt_all[0].timestamp()), int(dt_all[-1].timestamp())]
            ,marks=marks
            ,className='date-slider'
        )
    ]
    , id='slider-container'
    ,className='slider-wrapper')  
    ,html.Center([
        html.Button("← Previous", id="prev-day", n_clicks=0, className='dash-button', disabled=False)
        ,html.Button("Next →", id="next-day", n_clicks=0, className='dash-button', disabled=False)
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
    ,dcc.Store(id='popup-visible', data=True)
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
# Callback to control modal visibility
@app.callback(
    Output("popup-modal", "is_open"),
    Input("close-popup", "n_clicks"),
    Input("header", "n_clicks"),
    State("popup-modal", "is_open"),
    prevent_initial_call=True
)
def toggle_modal(close_clicks, header_clicks, is_open):
    ctx = callback_context

    if not ctx.triggered:
        raise PreventUpdate

    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if trigger_id == "close-popup":
        return False
    elif trigger_id == "header":
        return True

    return is_open


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
    start_date = pd.to_datetime(datetime.datetime.fromtimestamp(start_ts, datetime.UTC))
    end_date = pd.to_datetime(datetime.datetime.fromtimestamp(end_ts, datetime.UTC))
    
    # Filter on zoom
    if relayoutData and 'xaxis.range[0]' in relayoutData and 'xaxis.range[1]' in relayoutData:
        zoom_start = pd.to_datetime(relayoutData['xaxis.range[0]'], utc=True).normalize()
        zoom_end = pd.to_datetime(relayoutData['xaxis.range[1]'], utc=True).normalize()
        df_filtered = df_scores[df_scores['date'].between(zoom_start, zoom_end)]
    else:
        df_filtered = df_scores[df_scores['date'].between(start_date, end_date)]

    # If in detail mode, filter down to clicked date
    if mode == 'detail' and clickData:
        clicked_date = pd.to_datetime(clickData['points'][0]['x'], utc=True).normalize()
        clicked_date_str = clicked_date.strftime('%m/%d/%y')
        df_filtered = df_filtered[df_filtered['date'] == clicked_date]
        if not df_filtered.empty:
            current_rating = df_filtered.sort_values('date', ascending=False)['needle_rating'].iloc[0]
            return html.Span([html.Strong(f"NEEDLE RATING ON {clicked_date_str}: "),str(current_rating)])
        else:
            return html.Span([html.Strong(f"NO RATING AVAILABLE FOR {clicked_date_str}")])

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
    start_date = pd.to_datetime(start_ts, unit='s', utc=True)
    end_date = pd.to_datetime(end_ts, unit='s', utc=True)
    
    # Toggle to detail mode
    if mode == 'detail' and clickData:
        clicked_date = pd.to_datetime(clickData['points'][0]['x'], utc=True).normalize()
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
        margin={'t':30,'l':0,'b':0,'r':0},
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
        zoom_start = pd.to_datetime(relayoutData['xaxis.range[0]'], utc=True).normalize()
        zoom_end = pd.to_datetime(relayoutData['xaxis.range[1]'], utc=True).normalize()
        df_filtered = df_scores[df_scores['date'].between(zoom_start, zoom_end)]
        df_filtered['date'] = df_filtered['date'].dt.tz_localize(None)
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
    margin={'t':30,'l':0,'b':0,'r':0},
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

# Controls range slider
@app.callback(
    Output('date-slider', 'value'),
    Output('date-slider', 'disabled'),
    Output('slider-lock-indicator', 'children'),
    Input('relayout-store', 'data'),
    Input('reset-button', 'n_clicks'),
    prevent_initial_call=True
)
def sync_slider_with_zoom_or_reset(relayoutData, n_clicks):
    ctx = callback_context

    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if trigger_id == 'reset-button':
        return [int(dt_all[0].timestamp()), int(dt_all[-1].timestamp())], False, ''

    if relayoutData and 'xaxis.range[0]' in relayoutData and 'xaxis.range[1]' in relayoutData:
        zoom_start = pd.to_datetime(relayoutData['xaxis.range[0]'])
        zoom_end = pd.to_datetime(relayoutData['xaxis.range[1]'])
        return [int(zoom_start.timestamp()), int(zoom_end.timestamp())], True, 'Click Reset to Unlock Slider'

    elif relayoutData and relayoutData.get('xaxis.autorange') == True:
        return [int(dt_all[0].timestamp()), int(dt_all[-1].timestamp())], False, ''
    
    else:
        return [int(dt_all[0].timestamp()), int(dt_all.max().timestamp())], False, ''
        # return [int(dt_all[0].timestamp()), int(dt_all[-1].timestamp())], False, ''

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
        # dates = list(dt_obs_set)
        dates = sorted(dt_obs_set, reverse=True)
        current = pd.to_datetime(stored_click['points'][0]['x']).normalize().tz_localize('UTC')
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

@app.callback(
    Output('prev-day', 'disabled'),
    Output('next-day', 'disabled'),
    Input('click-store', 'data'),
    State('chart-mode', 'data'),
    prevent_initial_call=True
)
def update_nav_button_states(click_data, mode):
    if mode != 'detail' or not click_data or 'points' not in click_data:
        raise PreventUpdate

    current_date = pd.to_datetime(click_data['points'][0]['x']).normalize().tz_localize('UTC')
    # dates = list(dt_obs_set)
    dates = sorted(dt_obs_set, reverse=True)
    idx = dates.index(current_date)

    disable_prev = idx >= len(dates) - 1  
    disable_next = idx <= 0               

    return disable_prev, disable_next

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
    State('chart-mode', 'data'),
    Input('relayout-store', 'data')
)
def update_table(page_current, page_size, date_range, clickData, mode, relayoutData):    
    start_ts, end_ts = date_range
    start_date = pd.to_datetime(start_ts, unit='s', utc=True)
    end_date = pd.to_datetime(end_ts, unit='s', utc=True)
    df_filtered = df_events.copy()

    ### If reset then default to range slider filter
    if relayoutData and relayoutData.get('xaxis.autorange') == True and mode != 'detail':
        df_filtered = df_events[df_events['date'].between(start_date, end_date)]

    # If there is a zoom then filter on that
    elif relayoutData and 'xaxis.range[0]' in relayoutData and 'xaxis.range[1]' in relayoutData:
        zoom_start = pd.to_datetime(relayoutData['xaxis.range[0]'], utc=True).normalize()
        zoom_end = pd.to_datetime(relayoutData['xaxis.range[1]'], utc=True).normalize()
        df_filtered = df_events[df_events['date'].between(zoom_start, zoom_end)]
        if clickData and 'points' in clickData:
            clicked_date = pd.to_datetime(clickData['points'][0]['x'], utc=True).normalize()
            df_filtered = df_events[df_events['date'] == clicked_date]

    # If there is a click then filter to that
    elif clickData and 'points' in clickData:
        clicked_date = pd.to_datetime(clickData['points'][0]['x'], utc=True).normalize()
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
