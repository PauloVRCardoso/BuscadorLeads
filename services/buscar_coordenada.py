import requests
from services.empresas import buscar_empresas
from services.categorias import CATEGORIAS
from services.enriquecimento import enriquecer_empresas
from services.tratamento import tratar_empresas
from services.detalhes_empresa import buscar_detalhes

def buscar_coordenadas(endereco):

    url = "https://nominatim.openstreetmap.org/search"

    try:
        parametros = {
            "q": endereco,
            "format": "json",
            "limit": 1
        }

        headers = {
            "User-Agent": "BuscadorLeads/1.0"
        }

        response = requests.get(
            url,
            params=parametros,
            headers=headers,
            timeout=10
        )

        response.raise_for_status()
    except requests.exceptions.RequestException as erro:
        print (f"Erro ao consultar a latitude e longitude: {erro}")
        return None, None

    dados = response.json()

    if not dados:
        return None, None

    latitude = float(dados[0]["lat"])
    longitude = float(dados[0]["lon"])

    return latitude, longitude