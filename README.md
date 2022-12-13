## Airbnb Price Modelling
#### Business analytics of Vienna's Airbnb listings and price modelling using geospatial OpenStreetMap features

<img src="img/vienna-grid.png" alt="OSM Data Vienna, Austria" width="400"/>

### 1. Introduction
This project aims at predicting benchmark charging prices of a new host, based on existing airbnb listings across Vienna.
There is public information available about roughly 12,000 airbnb listings and their hosts.

A machine learning pipline has been established, where OpenStreetMap has been used for feature generation. These features include
the location of amenities such as shops, bars, restaurants, tourist destinations etc., and are used for price modelling.

The project includes a web app that displays some statistics as well as an interface for benchmark price 
prediction, based on the geolocation of a new listing. The visualization is implemented as a 
plotly Dash app which is on deploy on Aszure and accessible [here](https://airbnb-price-prediction.azurewebsites.net/).<br><br>

<img src="img/app-dashboard.png" alt="Screenshot of the app dashboard" width="650"/>


### 2. File Structure

`app.py` main dash app <br>
`requirements.txt` python modules that will be installed for the web application at build. <br>
`/assets` this directory is to serve the CSS files and images for the app. `charts.py` is used for generating the figures. <br>
`layout.py` defines the html web layout, `callbacks.py` handles all the callbacks and `data_wrangling.py` is used
for all the data queries and date manipulation. <br>
`/data` contains the raw input `tar.gz files` from [insideairbnb](http://insideairbnb.com/get-the-data.html).<br>
`/data/geojson/vienna.geojson` geojson file with the geospatial data of [Viennas neighbourhoods](tbd).<br>
`/data/osm/` contains all the OSM feature pre-saved as `.csv` files for a better app performance <br>
`/model/` has the model (generated in the notebook) as a `Pickle file` <br>
`/nb/airbnb_vienna.ipynb` [jupyter](https://github.com/AReburg/Airbnb-Price-Prediction/blob/main/nb/Airbnb-Analysis.ipynb) notebook used for data exploration, feature extraction etc. and the analysis outcome <br>
`runtime.txt` tells (the Gunicorn HTTP server) which python version to use (only needed for Heroku deployment)<br>
`Procfile` defines what type of process is going to run (Gunicorn web process) and the Python app entrypoint
(only needed for a deployment on Heroku) <br>
`.gitignore`<br>

<img src="img/wordcloud-vienna.png" alt="Wordcloud Vienna, Austria" width="650"/>

### 3. Installation

#### Getting Started

- Change the current directory to the location where you want to clone the repository and run:

`$ git clone https://github.com/AReburg/Airbnb-Price-Prediction.git`
- Make sure that the app is running on the local webserver before deployment.
Setup your virtualenv (or don't) and ensure you have all the modules installed before running the app. 


#### Requirements
Install the modules from the `requirements.txt` with pip3 or conda from a terminal in the project root folder:

`pip install -r requirements.txt` <br>
`conda install --file requirements.txt` (Anaconda)
<br>


#### Jupyter Notebook
Executing the notebook is tested on *anaconda distribution 6.4.12.*  with 
*python 3.9.13*. Since the notebook is *>100 mb* without the cleared outputs it is converted to html and
can be viewed [here](https://github.com/AReburg/Airbnb-Price-Prediction/blob/main/nb/Airbnb-Analysis.html).

### 4. Usage

#### Local Web Application
- Run the app from your IDE direct, or from the terminal in the projects root directory: `python app.py`

- It should be accessible on the browser `http://127.0.0.1:8050/`

- Open the app in the browser and start playing around


### 5. Results
The main findings will be published in a Medium post. Feel free to contact me if you have any questions or suggestions.
To view the rendered geospatial charts of the Jupyter notebook go to [nbviewer](https://nbviewer.org/github/AReburg/Airbnb-Price-Prediction/blob/main/nb/Airbnb-Analysis.ipynb) and copy the 
notebooks link.


### 6. Conclusion
OpenStreetMap could be a powerful tool for feature generation. With OSM it is possible to determine
how many restaurants, bars, cafes, shops etc. there are within a given radius.
The number of amenities based on the geolocation can be used for price modelling. In the XGBoost model, 
some OSM features are important drivers for prices in Vienna.

### Copyright and Licencing
This project is licensed under the terms of the MIT license

### Authors, Acknowledgements



