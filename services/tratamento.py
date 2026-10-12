import pandas as pd

def tratar_empresas(empresas):
    registros = []

    for empresa in empresas:
        registro = {
            "ID": empresa.get("id"),

            "Empresa": empresa.get(
                "displayName", {}
            ).get("text", "Não informado"),

            "Endereço": empresa.get(
                "formattedAddress",
                "Não informado"
            ),

            "Telefone": empresa.get(
                "nationalPhoneNumber",
                "Não informado"
            ),

            "Site": empresa.get(
                "websiteUri",
                "Não informado"
            )
        }

        registros.append(registro)

    df = pd.DataFrame(registros)

    return df