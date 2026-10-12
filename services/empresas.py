import requests
import os
from dotenv import load_dotenv

load_dotenv()

def buscar_empresas(latitude, longitude, raio_km, tipo_empresa):

    api_key = os.getenv("GOOGLE_MAPS_API_KEY")

    if not api_key:
        raise ValueError("Chave do Google Places nao configurada")

    url = "https://places.googleapis.com/v1/places:searchNearby"

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": (
            "places.id,"
            "places.displayName,"
            "places.formattedAddress"
        )
    }

    parametros = {
        "includedTypes": [tipo_empresa],
        "maxResultCount": 20,
        "locationRestriction":{
            "circle": {
                "center": {
                    "latitude": latitude,
                    "longitude": longitude
                },
                "radius": raio_km*1000
            }
        },
        "rankPreference": "DISTANCE",
        "languageCode": "pt-BR"
    }

    response = requests.post(
        url,
        headers=headers,
        json=parametros,
        timeout=30
    )

    response.raise_for_status()

    dados = response.json()

    return dados.get("places", [])