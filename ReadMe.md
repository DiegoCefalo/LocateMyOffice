# The office
![stonks](https://github.com/DiegoCefalo/company_location/blob/main/img/stonks.jpg)
    En este repositorio se encuentra un estudio sobre los posibles lugares para crear una nueva oficina para una empresa. Se comenzó escogiendo 3 localizaciones urbanas con una gran variedad de productos y servicios a facil disoposicion. Los Ángeles, Londres y Madrid. Luego mediante llamadas a la API de foursquare obtuvimos la localización de todos los locales de interés para el bienestar de la compañia y de sus empleados (Starbucks, restaurantes veganos, guarderías, bares y estadios de baloncesto). Después, la data con la localización y los nombres de los locales fue procesada para ser visualmente entendible mediante mapas marcados con cada uno. Finalmente a cada lugar se le dio una ponderación basada en la importancia de cada tipo de local para los intereses de la compañía y la media entre los tres locales mas cercanos de cada tipo.
Los mapas al ser interactivos, no se pueden apreciar bien en las imágenes, se recomienda leer el "limpiecito.ipynb"

## Los Ángeles
![LA](https://github.com/DiegoCefalo/company_location/blob/main/img/los_angeles.png)
Puntuación : 92.55
## Londres
![Londres](https://github.com/DiegoCefalo/company_location/blob/main/img/londres.png)
Puntuación : 92.76
## Madrid
![Madrid](https://github.com/DiegoCefalo/company_location/blob/main/img/madrid.png)
Puntuación : 94.90
## Puntaje final
![barras](https://github.com/DiegoCefalo/company_location/blob/main/img/histograma.jpg)

    En resumen, Madrid ganó. Fin
## Documentación de módulos utilizados
 * [Pandas](https://pandas.pydata.org/docs/)
 * [Numpy](https://numpy.org/doc/stable/)
 * [Plotly](https://plotly.com/python/)
 * [Seaborn](https://seaborn.pydata.org/)
 * [Matplotlib](https://matplotlib.org/stable/index.html)
 * [Dotenv](https://www.npmjs.com/package/dotenv)
 * [Os](https://docs.python.org/3/library/os.html)
 * [Json](https://docs.python.org/3/library/json.html)
 * [Requests](https://docs.python-requests.org/en/master/)
 * [Geopandas](https://geopandas.org/)
 * [Pymongo](https://pymongo.readthedocs.io/en/stable/)
 * [Operators](https://docs.python.org/3/library/operator.html)
 * [Functools](https://docs.python.org/3/library/functools.html)