from dash import dcc, html
from assets import charts
import logging
# import dash_bootstrap_components as dbc
import dash_dangerously_set_inner_html
import dash_bootstrap_components as dbc

def layout(app, df, districts, parameters, names):

    layout = html.Div([
        # left half of the web page
        html.Div([
            html.Div([html.Img(src=app.get_asset_url('logo.png'), height='21 px', width='auto')],
                     className='col-2', style={'align-items': 'center', 'padding-top': '1%', 'height': 'auto'}),
            html.Div(dash_dangerously_set_inner_html.DangerouslySetInnerHTML(
                """
                <h2>Airbnb Benchmark Price Prediction</h2>
                This project aims at predicting Airbnb host charging prices of a potential new listing across Vienna.
                There is <a href="http://insideairbnb.com/get-the-data/", target="_blank">public information</a> available
                about roughly 12,000 Airbnb listings and their hosts.<br/>
                <br/>
                A machine learning pipline has been established, where OSM features are used for price modelling. These features include
                the count of restaurants, bars, cafes, subway station tourist destinations etc. within a walking distance.  
                However, this model ist just a case study how OpenStreetMap features can be used together with other property types,
                such as accommodation capacity and other property features.<br/>
                <br/>
                The data has been pre-processed and is available <a href="https://github.com/AReburg/Airbnb-Price-Prediction/", target="_blank">
                here</a>. All the data manipulation and the modelling steps
                are described in this 
                <a href="https://github.com/AReburg/Airbnb-Price-Prediction/blob/main/nb/Airbnb-Analysis.html", target="_blank">jupyter notebook</a>.
                <br/><br/>""")),
            html.A(href="https://github.com/AReburg/", target="_blank", children=[html.Img(
                        alt="My Github", src=app.get_asset_url('githublogo.png'), height='18 px', width='auto')]),
            ], className='four columns div-user-controls'),

        # right half of the web page
        html.Div([
            html.Br(),
            # Tabs - Method 2
            dcc.Tabs([
                dcc.Tab(label='Amenities',
                        children=[
                            dcc.Graph(id='text_lat_long', config={'displayModeBar': False}),]),
                dcc.Tab(label='Listings', children=[dcc.Graph(figure=charts.heatmap_airbnb_listings(df, districts, mode='dffline'),
                                                              config={'displayModeBar': False})]),
                dcc.Tab(label='Prices', children=[dcc.Graph(figure=charts.heatmap_airbnb_prices(df, districts, mode='dffline'),
                                                            config={'displayModeBar': False})]),
                ]),
            html.Br(),
            html.Br(),
            html.Div(
                children=[dcc.Input(id="input_text", type="text", placeholder="Enter an address (Vienna only) for price estimation.", debounce=True,
                                    style={'width': '45%', 'padding': '5px'})],
            ),
            html.Br(),
            html.Div(id="tokenized_text"),
            html.Div(dash_dangerously_set_inner_html.DangerouslySetInnerHTML(
                """ The chart below depicts the number of amenities found within 500 m around the geolocation:""")),
            dcc.Graph(id='result-histogram', config={'displayModeBar': False}),
        ], className='eight columns div-for-charts bg-grey')
    ])
    return layout

