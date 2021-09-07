from dotenv import load_dotenv
import os
import requests
import json
from functools import reduce
import operator
import geopandas as gpd
import folium
import pandas as pd
from pymongo import MongoClient
from pymongo import GEOSPHERE

def foursq(venue,coords):
    """
    Esta funcion hace una llamada a la api de foursquare y devuelve un json con los datos de la busqueda de locales.
    inputs: venue: local a buscar (str)
            coords: latitud y longitud en donde se quiere realizar la búsqueda (list)
    outputs: json con los datos de los locales
    """
    load_dotenv()
    client_id = os.getenv("token1")
    client_secret = os.getenv("token2")
    url_query = 'https://api.foursquare.com/v2/venues/explore'
    parametros = {
    "client_id": client_id,
    "client_secret": client_secret,
    "v": "20180323",
    "ll": f"{coords[0]}, {coords[1]}",
    "query": f"{venue}",
    "limit": 200,
    "radius": 10000
    }
    resp = requests.get(url_query, params = parametros).json()
    return resp

def getFromDict(diccionario, mapa):
    """
    Esta funcion obtiene el value de un nested dictionary a partir de una ruta dada.
    inputs: diccionario: (dict)
            mapa: keys a seguir hasta llegar al valor deseado (list)
    outputs: valor dentro de la ultima key especificada
    """
    return reduce(operator.getitem,mapa,diccionario)

def type_point(lista):
    """
    Esta funcion convierte un par de coordenadas a tipo point.
    inputs: lista: latitud y longitud (list)
    outputs: coordenadas tipo point (dict)
    """
    return {"type": "Point", 
            "coordinates": lista }

def save_info(name,lista):
    """
    Esta funcion guarda todos los locales en un archivo tipo json en el ordenador.
    inputs: name: nombre del fichero (str)
            lista: lista de dicionarios con la info de los locales (list of dictionaries)
    outputs: none
    """
    with open(f'{name}.json', 'w') as f:
        json.dump(lista, f)

def datamatico(venue,coords):
    """
    Esta funcion guarda todos los locales en un archivo tipo json en el ordenador.
    inputs: venue: local a buscar (str)
            coords: latitud y longitud a partir de donde buscar (list)
    outputs: geodataframe
    """
    resp = foursq(venue,coords)
    data = resp["response"]["groups"][0]["items"]
    mapa_nombre = ["venue", "name"]
    mapa_latitud = ["venue", "location", "lat"]
    mapa_longitud = ["venue", "location", "lng"]
    lista = []
    for dic in data:
        paralista= {}
        paralista["type"]= f"{venue}"
        paralista[f"name.{venue}"]= getFromDict(dic,mapa_nombre)
        paralista["latitud"]= getFromDict(dic,mapa_latitud)
        paralista["longitud"]= getFromDict(dic,mapa_longitud)
        paralista["location"]=  type_point([paralista["longitud"],paralista["latitud"]])
        lista.append(paralista)
    save_info(venue,lista)
    info_pd = pd.DataFrame(lista)
    info_gpd = gpd.GeoDataFrame(info_pd, geometry = gpd.points_from_xy(info_pd.longitud, info_pd.latitud))
    return info_gpd
    
        
def distancia(colect, coords, venue):
    """
    Esta funcion calcula la distancia media de los 3 valores más cercanos y la minima del tipo de local a buscar, con los datos almacenados en mongodb.
    inputs: venue: local a buscar (str)
            coords: latitud y longitud a partir de donde buscar (list)
            colect: coleccion dentro de la base de datos (str)
    outputs: diccionario con la media y la minima distancia
    """
    client = MongoClient("localhost:27017")
    db = client.get_database("new_office")
    colec = db.get_collection(f"{colect}")
    query = [{
        '$geoNear': {'near': [coords[1],coords[0]],
            'distanceField': 'distancia(km)',
            'maxDistance': 10000,
            'query': {'type': {'$regex': f'(?i){venue}'}},
            'distanceMultiplier': 6371.008,
            #'includeLocs': "dist.location",
            'spherical': True,
            }
        }]
    geoloc = colec.aggregate(query)
    df = pd.DataFrame(geoloc)
    media = df.sort_values('distancia(km)').head(3).mean()['distancia(km)']
    mini = df['distancia(km)'].min()
    return {'media':media,'minima':mini}

def add_layer(nombre,colorin,mapa,df):
    """
    Esta funcion añade una capa al mapa de folium con los datos de un dataframe.
    inputs: nombre: nombre de la capa (str)
            colorin: color de los marcadores (str)
            mapa: mapa de folium
            df: dataframe
    outputs: None
    """
    layer = folium.FeatureGroup(name=f'{nombre}')
    for i, row in df.iterrows():
        layer.add_child(
            folium.Circle(
            radius=50,
            location=[row["latitud"], row["longitud"]],
            tooltip=f"<b>{nombre}: <br></b>"+row[f"name.{nombre}"],
            color=f"{colorin}",
            fill=True
            )
        )
    layer.add_to(mapa)

def get_distinct(colect):
    """
    Esta funcion obtiene todos los tipos distintos dentro de una colección.
    inputs: colect: colección de donde se quiere obtener los tipos unicos (str)
    outputs: lista con los distintos tipos unicos
    """
    client = MongoClient("localhost:27017")
    db = client.get_database("new_office")
    colec = db.get_collection(f"{colect}")
    return colec.distinct('type')
    
def puntajilizador(colect,coord):
    """
    Esta funcion pondera la distancia y la importancia de cada tipo de local.
    inputs: colect: colección a ponderar (str)
            coords: latitud y longitud a partir de donde calcular (list)
    outputs: puntaje (float)
    """
    try:
        dic = {}
        for venue in get_distinct(colect):
            dic.update({venue:distancia(colect,coord,venue)['media']})
        puntos = (10-(dic['Starbucks']*1))+(30-(dic['Vegan restaurant']*3))+(10-(dic['Daycare']*1))+(10-(dic['Basketball arena']*1))+(40-(dic['Bar']*4))
        return puntos
    except:
        print('No cumple con las condiciones mínimas')

def mapamatico(coords,nombre):
    """
    Esta funcion regresa un mapa en folium con los restaurantes veganos, los starbucks, las guarderias, los estadios de basketball y los bares marcados en un radio de 10 km. Tambien guara el mapa en el ordenador
    inputs:  coords: latitud y longitud a partir de donde calcular (list)
             nombre: nombre para guardar el mapa (str)
    outputs: mapa de folium
    """
    vegano = datamatico("Vegan restaurant",coords)
    starbucks = datamatico("Starbucks",coords)
    guarderia = datamatico("Daycare",coords)
    basketball = datamatico("Basketball arena",coords)
    bar = datamatico("Bar",coords)
    mapa = folium.Map(location=coords, zoom_start=12)
    add_layer('Vegan restaurant','blue',mapa,vegano)
    add_layer('Starbucks','red',mapa,starbucks)
    add_layer('Daycare','green',mapa,guarderia)
    add_layer('Basketball arena','purple',mapa,basketball)
    add_layer('Bar','black',mapa,bar)
    centro = folium.FeatureGroup(name='Centro')
    centro.add_child(folium.Marker(location = coords, tooltip="Centro")).add_to(mapa)
    folium.LayerControl(collapsed=False).add_to(mapa)
    mapa.save(f'{nombre}')
    return mapa