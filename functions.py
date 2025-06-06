from pydantic_ai import Agent, RunContext
from pydantic import BaseModel
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider
import pandas as pd
import json
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from sklearn.neighbors import BallTree

class Flora(BaseModel):
    name: str
    description: str
    img: str

APIKEY = json.load(open("./config.json"))["GEMINI_API_KEY"]
model = GeminiModel('gemini-1.5-flash', provider=GoogleGLAProvider(api_key=APIKEY))

agent = Agent(
    model,
    output_type = list[Flora],
    instructions = 'Eres un experto en Flora Chilena. Tu tarea es ayudar a los usuarios a encontrar información sobre flora chilena, dado un punto geográfico, incluye nombre científico, una descripción chistosa con estilo tinder y descripciones detalladas de las plantas.',
    )
@agent.tool
def get_nearest_flora(ctx: RunContext ,lat: float, lng: float) -> list[str]:
    """
    Obtiene la flora más cercana a las coordenadas dadas.
    
    Args:
        lat (float): Latitud del punto geográfico.
        lng (float): Longitud del punto geográfico.
        
    Returns:
        list[str]: Lista de de plantas con nombre científico cercanos al punto dado.
    """
    df = pd.read_csv("./data/NativePlants.csv")
    coords = np.radians(df[["decimalLatitude", "decimalLongitude"]])
    punto = np.radians([[lat, lng]])
    tree = BallTree(coords, metric='haversine')
    distancias, indices = tree.query(punto, k=200)
    nearest_plants = df.iloc[indices[0]].copy()

    nearest_plants["dist_km"] = distancias[0] * 6371  # Radio Tierra en km
    especies_cercanas = (
        nearest_plants
        .sort_values("dist_km")
        .drop_duplicates(subset=["species"])
        .head(10)
    )

    print(especies_cercanas)
    return especies_cercanas["species"].tolist()

@agent.tool
def get_flora_info(ctx: RunContext, species: list) -> dict:
    """
    Obtiene información detallada sobre una especie de planta.
    
    Args:
        species (list[str]): Nombre científico de las plantas.
        
    Returns:
        dict: Objeto con nombre y descripción de la planta.
    """
    df = pd.read_csv('./data/RasgosCL_aggregatedspp.csv')
    df = df[df['accepted_species'].isin(species)]
    if df.empty:
        return {}
    else:
        df = df.to_dict()
        return df

@agent.tool
def get_img_url(ctx: RunContext,prospect: str) -> str:
    """ Obtiene la URL de la imagen de una especie a partir de su página en el herbario digital.
    Args:
        prospect (str): prospecto de la especie.
    Returns:
        str: URL de la imagen de la especie, o None si no se encuentra.
    """
    prospect = prospect.replace(" ", "+")
    url_busqueda = f"https://www.herbariodigital.cl/catalog/?search={prospect}&select_category=species&send=Search"
    try:
        response = requests.get(url_busqueda)
        response.raise_for_status()  # Raise an exception for bad status codes
        soup = BeautifulSoup(response.text, 'html.parser')
        img_tag = soup.find_all('a', class_='text-dark', )
        for img in img_tag:
            if img and img.get('href'):
                img_url = img.get('href')
                if img_url.startswith('/catalog/details/'):
                    img_url = 'https://www.herbariodigital.cl' + img_url

        response = requests.get(img_url)
        response.raise_for_status()  # Raise an exception for bad status codes
        soup = BeautifulSoup(response.text, 'html.parser')
        img_tag = soup.find_all('img', {'data-target': '#galleryCarousel'})
        for img in img_tag:
            if img and img.get('src'):
                img_url = img.get('src')
                if img_url.startswith('https://images.herbariodigital.cl/gallery/'):
                    return img_url
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None