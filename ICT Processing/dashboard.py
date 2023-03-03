import dash_leaflet as dl
from dash import Dash, html, Output, Input
from dash.exceptions import PreventUpdate
from dash_extensions.javascript import assign
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, dcc, Input, Output, State
from datetime import date
from dash.long_callback import DiskcacheLongCallbackManager
import time
# How to render geojson.
# Create example app.
import diskcache
cache = diskcache.Cache("./cache")
long_callback_manager = DiskcacheLongCallbackManager(cache)

app = Dash(__name__, long_callback_manager=long_callback_manager, external_stylesheets=[dbc.themes.BOOTSTRAP])

point_to_layer = assign("""function(feature, latlng, context){
    const p = feature.properties;
    if(p.type === 'circlemarker'){return L.circleMarker(latlng, radius=p._radius)}
    if(p.type === 'circle'){return L.circle(latlng, radius=p._mRadius)}
    return L.marker(latlng);
}""")

map1 = dl.Map(center=[17.81, -77.25], zoom=11, children=[
        dl.TileLayer(), dl.FeatureGroup([dl.EditControl(id="edit_control", draw=dict(circle=False, retangle=False, circlemarker=False, marker=False),)], id='fg'),
    ], style={'width': '100%', 'height': '60vh', 'margin': "auto", "display": "inline-block"}, id="map")
map2 =  dl.Map(center=[17.81, -77.25], zoom=11, children=[
        dl.TileLayer(), dl.GeoJSON(id="geojson", options=dict(pointToLayer=point_to_layer), zoomToBounds=True),
    ], style={'width': '80%', 'height': '60vh', 'margin': "auto", "display": "inline-block"}, id="mirror"),

preview_dropdown = dcc.Dropdown(
    [
        'Area of interest'
    ], placeholder="Select Preview Layer", id = 'aoi-dropdown'
)

date_picker = html.Div([
    dcc.DatePickerRange(
        id='my-date-picker-range',
        min_date_allowed=date(2015, 6, 27),
        initial_visible_month=date.today()),
    html.Div(id='output-container-date-picker-range'),
])

container_style = {'border':'1px solid', 'border-radius': 10, 'backgroundColor':'#FFFFFF', 'width': '80%', 'align' : 'center'}
control_panel = [
                    html.Br(),
                    dbc.Row(html.Div([html.H4('Select Polygon'), 
                            html.Div('No polygon selected!', id = 'polygon_selection'),],)),
                    html.Br(),
                    dbc.Row(html.Div([html.H4('Select Date Range'), 
                            html.Div(date_picker),],)),
                    html.Br(),
                    dbc.Row(html.Div([html.H4(id="paragraph_id", children=["Start processing below..."]), 
                            html.Div(dbc.Progress(id="progress_bar",value=0, style={"height": "30px"}))],
                            )),
                    html.Br(),
                    dbc.Row(html.Div([html.Button(id="button_id", children="Start"),
                        html.Button(id="cancel_button_id", children="Cancel"),])),
                    html.Br(),
                ]

app.layout = html.Div([
    dbc.Row(
        [
            dbc.Col(html.Div(html.H2('Options', style={'textAlign': 'center'})), width=3),
            dbc.Col(html.Div(html.H2('Select AOI', style={'textAlign': 'center'}))),
            dbc.Col(html.Div(html.H2('Preview', style={'textAlign': 'center'})))
        ]
    ),
    dbc.Row(
        [
            dbc.Col(html.Div(control_panel, style=container_style), width=3),
            dbc.Col(map1),
            dbc.Col(map2)
        ]
    ),
    dbc.Row(
        [
            dbc.Col(html.Div(), width=3),
            dbc.Col(html.Div()),
            dbc.Col(html.Div(preview_dropdown))
        ]
    ),
    dcc.Store(id='aoi'),
    dcc.Store(id='dates'),
    dcc.Store(id='labels')
])

@app.callback(
    Output('output-container-date-picker-range', 'children'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date'))
def update_output(start_date, end_date):
    string_prefix = ''
    if start_date is not None:
        start_date_object = date.fromisoformat(start_date)
        start_date_string = start_date_object.strftime('%B %d, %Y')
        string_prefix = string_prefix + 'Start Date: ' + start_date_string + ' | '
    if end_date is not None:
        end_date_object = date.fromisoformat(end_date)
        end_date_string = end_date_object.strftime('%B %d, %Y')
        string_prefix = string_prefix + 'End Date: ' + end_date_string
    return string_prefix

@app.long_callback(
    output=Output("paragraph_id", "children"),
    inputs=Input("button_id", "n_clicks"),
    state=State('aoi', 'data'),
    running=[
        (Output("button_id", "disabled"), True, False),
        (Output("cancel_button_id", "disabled"), False, True),
        (
            Output("paragraph_id", "style"),
            {"visibility": "hidden"},
            {"visibility": "visible"},
        ),
        (
            Output("progress_bar", "style"),
            {"visibility": "visible"},
            {"visibility": "hidden"},
        ),
    ],
    cancel=[Input("cancel_button_id", "n_clicks")],
    progress=[Output("progress_bar", "value"), Output("progress_bar", "max")],
)

def run_processing(set_progress, n_clicks, aoi):
    total = 10
    if n_clicks:
        if n_clicks > 0:
            for i in range(total):
                time.sleep(0.5)
                set_progress((str(i + 1), str(total)))
            print(aoi)
            return [f"Classification Finished!"]
        else:
            raise PreventUpdate
    else:
        raise PreventUpdate

# Copy data from the edit control to the geojson component.
@app.callback(Output("geojson", "data"), Output('aoi', 'data'), Output('polygon_selection', 'children'), Input("edit_control", "geojson"))
def mirror(x):
    if not x:
        raise PreventUpdate
    if x:
        if len(x['features']) > 0:
            x['features'] = [x['features'][-1]]
            return x, x, 'Polygon selected!'
        else:
            raise PreventUpdate

@app.callback(
    Output('testtest', 'children'),
    Input('aoi-dropdown', 'value')
)
def update_output(value):
    if value:
        print(value)
  

if __name__ == '__main__':
    app.run_server()