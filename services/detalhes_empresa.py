import os
import requests
from dotenv import load_dotenv

load_dotenv()

def buscar_detalhes(place_id):

    api_key = os.getenv("GOOGLE_MAPS_API_KEY")

    if not api_key:
        raise ValueError("Chave do Google Places nao configurada")

    url = ("https://places.googleapis.com/v1/"f"places/{place_id}")

    headers = {
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": (
            "id,"
            "displayName,"
            "nationalPhoneNumber,"
            "websiteUri"
        )
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=15
    )

    if not response.ok:
        try:
            erro = response.json()
        except ValueError:
            erro = {"message": response.text}

        raise RuntimeError(
            f"Status HTTP: {response.status_code}\n"
            f"Resposta do Google: {erro}"
        )

    return response.json()