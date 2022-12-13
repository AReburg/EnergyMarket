import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import json
from pathlib import Path
import geojson
from time import time
import plotly.io as pio
import shapely.ops
import shapely.geometry
import geopandas as gpd
from shapely.geometry import Point

cwd = Path().resolve()
token = open(os.path.join(Path(cwd), 'assets', '.mapbox_token')).read()


def save_figure(fig, name):
    t0 = time()
    with open(f"{name}.json", "w") as outfile:
        outfile.write(fig)
    print(time() - t0)


def aggregate_data(df, group='', agge='', rename=''):
    """ function to group, aggregate and rename the dataframe """
    df = df.groupby([group]).agg(agge)
    df.columns = df.columns.droplevel(0)
    df.columns = rename
    df.reset_index(drop=True, inplace=True)
    return df


def add_trace(fig, amenities, symbol, name="tbd", size=5):
    fig.add_traces(go.Scattermapbox(mode = "markers",
    lon = amenities.long.tolist(), lat = amenities.lat.tolist(), hoverinfo='skip',
    marker = {'size': size, 'symbol': symbol},
    showlegend=False, name=name))


def heatmap_airbnb_amenities(parameters, names, districts, point={"lat": 48.210033, "lon": 16.363449},
                             zoom=10, show=True, mode='offline',
                             center={"lat": 48.210033, "lon": 16.363449}):
    """ """
    t0 = time()
    if mode == 'offline':
        with open('airbnb_amenities.json', 'r') as f:
            fig = pio.from_json(f.read())
            print("figure import file took: ", time() - t0)
            return fig
    fig = go.Figure(go.Scattermapbox(
        mode="markers",
        lon=parameters[0].long.tolist(), lat=parameters[0].lat.tolist(),
        marker={'size': 5, 'symbol': "restaurant"}, hoverinfo='skip', showlegend=False
    ))
    # ['restaurant', 'cafe', 'bar', 'station', 'biergarten', 'fast_food', 'pub', 'nightclub', 'theatre',
    #              'university', 'attraction']
    add_trace(fig, parameters[1], symbol="cafe", name="cafe", size=4)
    add_trace(fig, parameters[2], symbol="alcohol-shop", name="cafe", size=4)
    add_trace(fig, parameters[3], symbol="bus", name="subway", size=7)
    add_trace(fig, parameters[-1], symbol="grocery", name="supermarket", size=2)

    # add location spot
    if show:
        pts = {"lat": point['latitude'].item(), "lon": point['longitude'].item()}
        location = gpd.GeoDataFrame({'address': 'Location',
                                     'geometry': [Point(point['longitude'].item(), point['latitude'].item())]},
                                    crs='EPSG:4326')

        fig.add_traces(go.Scattermapbox(lat=[pts['lat']], lon=[pts['lon']], mode='markers', marker_size=8,
                                        opacity=0.8, showlegend=True, marker_color="red", name="Location"))
        radius_in_meter = 500
        radius = location.to_crs(epsg=7855).buffer(radius_in_meter).to_crs(epsg=4326)

        ls = shapely.geometry.LineString(shapely.ops.unary_union(radius).exterior.coords)
        lats, lons = ls.coords.xy

        fig.add_trace(go.Scattermapbox(
            mode="lines",
            lon=list(lats),
            lat=list(lons),
            name=f"{radius_in_meter} m radius",
            hoverinfo='skip',
            marker={'size': 15, 'color': 'red', 'opacity': 0.2}))


    fig.update_layout(mapbox_style="light", mapbox_accesstoken=token, mapbox_zoom=zoom,
                      mapbox_center=center)
    fig.update_layout(font=dict(family="Helvetica"), legend={"title": "Select category:"})
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)')

    print("figure ammenities builg took: ", time() - t0)
    save_figure(fig.to_json(), 'airbnb_amenities')
    return fig


def heatmap_airbnb_prices(df, districts, mode='offline'):
    """
    returns heatmap with all the airbnbn listings
    """
    t0 = time()
    if mode == 'offline':
        with open('airbnb_prices.json', 'r') as f:
            fig = pio.from_json(f.read())
            print("figure import file took: ", time() - t0)
            return fig

    k = aggregate_data(df, 'neighbourhood', {'neighbourhood': ['first'], 'price': ['median']}, \
                       rename=['district', 'median'])
    k['median'] = k['median'].astype('category')
    k.sort_values(by='median', ascending=False, inplace=True)
    dfz = k.groupby(['median']).agg({'median': ['first']})
    dfz.columns = dfz.columns.droplevel(0)
    dfz.columns = ['price']
    dfz.reset_index(drop=True, inplace=True)
    dfz.sort_values(by='price', ascending=False, inplace=True)
    dfz = dfz['price'].tolist()
    dicts = {}
    farbe = px.colors.cyclical.IceFire[0:len(dfz)]
    for i, j in zip(dfz, farbe):
        dicts[i] = f'{i} $'
    cols = k['median'].map(dicts)

    fig = px.choropleth_mapbox(k, geojson=districts, locations=k['district'], featureidkey="properties.name",
                               color=cols,
                               color_discrete_sequence=farbe,
                               labels={'median': 'price per night'},
                               mapbox_style="open-street-map", zoom=10, center={"lat": 48.210033, "lon": 16.363449},
                               opacity=0.60)
    fig.add_scattermapbox(
        lat=df['latitude'].tolist(),
        lon=df['longitude'].tolist(),
        mode='markers',
        showlegend=False,
        marker_size=3,
        marker_color='#F3F5F6',
        opacity=0.3,
        hoverinfo='skip'
    )
    fig.update_layout(mapbox_style="light", mapbox_accesstoken=token)
    fig.update_layout(legend={"title": "price per night"})
    fig.update_layout(font=dict(family="Helvetica"))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    print("figure took: ", time() - t0)
    save_figure(fig.to_json(), 'airbnb_prices')
    return fig


def heatmap_airbnb_listings(df, districts, mode='offline'):
    """
    returns heatmap with all the airbnbn listings
    https://plotly.com/python/builtin-colorscales/
    interesting: https://stackoverflow.com/questions/71104827/plotly-express-choropleth-map-custom-color-continuous-scale
    """
    if mode == 'offline':
        with open('airbnb_listings.json', 'r') as f:
            fig = pio.from_json(f.read())
            return fig
    agg = df.groupby('neighbourhood').agg(nr_listings = ('id', 'count')).reset_index().sort_values('nr_listings', ascending=False)
    agg['ratio'] = 100 * agg['nr_listings'] / agg['nr_listings'].sum()
    agg['nr_listings'] = agg['nr_listings'].astype('category')
    agg.sort_values(by='nr_listings', ascending = False, inplace=True)
    fig = px.choropleth_mapbox(agg, geojson=districts, locations=agg['neighbourhood'], featureidkey="properties.name",
                               color_discrete_sequence=px.colors.cyclical.IceFire, #px.colors.sequential.Plasma_r, #px.colors.qualitative.Dark24,
                               color=agg['nr_listings'],
                               #color=agg['ratio'],
                               labels={'nr_listings':'Nr. of listings'},
        mapbox_style="open-street-map", zoom=10, center = {"lat": 48.210033, "lon": 16.363449}, opacity=0.30)
    neighbourhood = agg['neighbourhood'].tolist()
    nr = agg['nr_listings'].tolist()
    for i,trace in enumerate (fig.data):
        trace.update(name=f'{nr[i]} / {neighbourhood[i]}')
    #fig.for_each_trace(lambda t: t.update(name = newnames[t.name]))
    fig.update_layout(mapbox_style="light", mapbox_accesstoken=token)
    fig.update_layout(font=dict(family="Helvetica"))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    save_figure(fig.to_json(), 'airbnb_listings')
    return fig


def get_bar_chart(dfx):
    """ returns bar chart with number of amenities within the given radius """
    try:
        night_colors = ['rgb(56, 75, 126)', 'rgb(18, 36, 37)', 'rgb(34, 53, 101)']

        # return empty bar chart for no input
        if dfx is None:
            d = {'restaurant': 0, 'cafe': 0, 'bar': 0, 'station': 0, 'biergarten': 0, 'fast_food': 0, 'pub': 0,
                 'nightclub': 0, 'theatre': 0, 'university': 0}
            df = pd.DataFrame(data=d, index=[0])
            df1_transposed = df.T

        # generates the horizontal bar chart with the categories
        else:
            df1_transposed = dfx.T
        df1_transposed.rename({0: 'value'}, inplace=True, axis=1)
        df1_transposed['feature'] = df1_transposed.index
        fig = px.bar(df1_transposed, x='value', y='feature', orientation='h')
        fig.update_layout(hovermode=False)
        # fig.update_layout(xaxis={'visible': False, 'showticklabels': True},
        #                  yaxis={'visible': False, 'showticklabels': True})
        fig.update_yaxes(title='', visible=True, showticklabels=True)
        fig.update_xaxes(title='', visible=True, showticklabels=True)
        fig.update_yaxes(tickfont=dict(size= 10, family='Helvetica', color='#9c9c9c'),
                         title_font_color='#9c9c9c',
                         ticks='outside', showline=True, gridwidth=1, gridcolor='#4c4c4c')
        fig.update_layout(font_family="Helvetica")
        if dfx is None:
            fig.update_xaxes(range=[0, 10])
        fig.update_traces(marker_color=night_colors[0], marker_line_color='#9c9c9c', opacity=0.7)
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        fig.update_layout(autosize=True,height=300,margin_pad=0)
        fig.update_layout(margin={"r":0,"t":20,"l":0,"b":0})
        fig.update_yaxes(fixedrange=True)
        fig.update_xaxes(fixedrange=True)
        return fig

    except Exception as e:
        fig = go.Figure(go.Scatter(x=[0], y=[0]))
        fig.update_layout(template=None)
        fig.update_xaxes(showgrid=False, showticklabels=False, zeroline=False)
        fig.update_yaxes(showgrid=False, showticklabels=False, zeroline=False)
        return fig


def blank_fig():
    """ returns a black fig without any content """
    fig = go.Figure(go.Scatter(x=[], y=[]))
    fig.update_layout(template=None)
    fig.update_xaxes(showgrid=False, showticklabels=False, zeroline=False)
    fig.update_yaxes(showgrid=False, showticklabels=False, zeroline=False)
    return fig