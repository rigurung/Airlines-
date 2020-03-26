from flask import Flask
from flask import send_from_directory
import folium
import pandas as pd
import json
import csv
import os
from os import path

app = Flask("__name__")

with open("./data/data_f.json","r") as mf:
    data = json.loads(mf.read())

df = pd.DataFrame(data["states"])


# rename 17 columns to how they're assigned in the docs 
df.columns = ["icao24","callsign","origin_country","time_position","last_contact","longitude","latitude","paro_altitude","on_ground","velocity","true_track","vertical_rate","sensors","geo_altitude","squawk","spi","position_source"]
 #folium_map = folium.Map(location=[46.9540700, 142.7360300], zoom_start=14,tiles="Mapbox Bright")
folium_map = folium.Map(location=[46.9540700, 142.7360300], zoom_start=0)
points = df[["latitude", "longitude"]].dropna().head(100).values
for point in range(len(points)):
    folium.CircleMarker(points[point], popup=df["callsign"][point], fill = True, radius=0.5).add_to(folium_map)
    
folium_map.save("static/map.html")

@app.route('/')
def index():
    return send_from_directory(os.path.join(".", "static"), "index.html")
    

@app.route('/map')
def send_map():
    print(os.path.join(".", "static"))
    return send_from_directory(os.path.join(".", "static"), "map.html")
    
@app.route('/canvasOverlay')
def moving_marker():
    return send_from_directory(os.path.join(".", "static"), "CanvasOverlay.js")

@app.route("/mapData")
def send_map_data():
    df_airports = pd.read_csv("./data/airports.csv")
    df_route = pd.read_csv("./data/routes.csv")

    df_route["Source Airport ID"] = pd.to_numeric(df_route["Source Airport ID"], errors = "coerce").fillna(0).astype('int64')
    df_route["Destination Airport ID"] = pd.to_numeric(df_route["Destination Airport ID"], errors = "coerce").fillna(0).astype('int64')

    df_airports.set_index("Airport ID", inplace = True)
    #df_route.set_index("Source Airport ID")

    df_data = df_route.join(df_airports, on = "Source Airport ID")[["Latitude", "Longitude", "Source Airport ID", "Destination Airport ID"]].fillna(0).head(5000)
    df_data.rename(columns = {"Latitude": "Source Latitude", "Longitude": "Source Longitude"}, inplace = True)

    df_data.set_index("Destination Airport ID", inplace = True)

    df_data = df_airports.join(df_data, how = "inner")[["Latitude", "Longitude","Source Latitude","Source Longitude", ]].fillna(0).head(100)
    
    print(df_data.head(100))
    data = df_data.values.tolist()
    data.insert(0, list(df_data.columns))
    return str(data)

if __name__ == '__main__':
    app.run(debug=True)

