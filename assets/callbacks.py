from pathlib import Path
import logging
from opencensus.ext.azure.log_exporter import AzureLogHandler
import xgboost as xgb
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input
cwd = Path().resolve()
from assets.data_wrangling import DataManipulation
from assets import charts
from dash import dcc, html

data = DataManipulation()

logger = logging.getLogger(__name__)
logger.addHandler(AzureLogHandler(
    connection_string='InstrumentationKey=d989e5c0-698b-4b3e-a645-18ac1f273b59'))


def register_callbacks(app, df, model, region, districts, parameters, names):

    @app.callback(
        [Output('tokenized_text', 'children'), Output('result-histogram', 'figure'),
         Output('text_lat_long', 'figure')],
        Input("input_text", "value"))
    def update_categories(input_text):
        """ use model to predict benchmark price for input address
        e.g. # Universitätsring 2, 1010 Wien
        Fleischmarkt 20, Wien
        important: https://stackoverflow.com/questions/69964486/plotly-dash-how-to-prevent-figure-from-appearing-when-no-dropdown-value-is-sele
        """
        if input_text == '' or input_text is None:
            return [html.P(" "),
                    charts.get_bar_chart(None),
                    charts.heatmap_airbnb_amenities(parameters, names, districts, show=False, mode='online')]

        else:
            logger.exception(f'input text: {input_text}')
            dfi = data.parse_input(input_text)
            try:
                dfi[['longitude', 'latitude']] = dfi.apply(lambda x: data.get_lat_long(x['geometry']), axis=1)
            except:
                return [html.P("Address could not be found."),
                        charts.get_bar_chart(None),
                        charts.heatmap_airbnb_amenities(parameters, names, districts, show=False, mode='online')]

            if not data.check_if_coord_in_poly(region, dfi['longitude'].item(), dfi['latitude'].item()):
                return [html.P("Not a valid address in Vienna, Austria. Try again."),
                        charts.get_bar_chart(None),
                        charts.heatmap_airbnb_amenities(parameters, names, districts, show=False, mode='online')]

            else:
                try:
                    X_pred = data.predict_price(dfi, parameters, names)
                    preds = round(float(model.predict(X_pred)), 2)
                    return [html.P(f"Point({dfi['longitude'].item()}, {dfi['latitude'].item()}) "
                                   f"results in a {preds} $ benchmark price."),
                            charts.get_bar_chart(X_pred),
                            charts.heatmap_airbnb_amenities(parameters, names, districts, dfi, show=True,
                                  zoom=14, center={"lat": dfi['latitude'].item(), "lon": dfi['longitude'].item()},
                                                            mode='online')]

                except Exception as e:
                    print(f'X_pred exception: {e}')
                    return [html.P("Error in price prediction."), charts.get_bar_chart(None),
                            charts.heatmap_airbnb_amenities(parameters, names, districts, show=False, mode='online')]

