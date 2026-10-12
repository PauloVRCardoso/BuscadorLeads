from services.detalhes_empresa import buscar_detalhes

def enriquecer_empresas(empresas, limite=20):
    estatisticas = {
        "empresas_encontradas": len(empresas),
        "consulta_realizada": 0,
        "consulta_sucesso": 0,
        "consultas_falha": 0
    }

    for empresa in empresas[:limite]:
        place_id = empresa.get("id")

        if not place_id:
            continue

        estatisticas["consulta_realizada"] +=1

        try:
            
            detalhes = buscar_detalhes(place_id)

            empresa["nationalPhoneNumber"] = (
                detalhes.get("nationalPhoneNumber") or "Não informado"
            )

            empresa["websiteUri"] = (
                detalhes.get("websiteUri") or "Não informado"
            )

            estatisticas["consulta_sucesso"] += 1
        except Exception as erro:
            empresa["nationalPhoneNumber"] = (
                "Consulta não realizada"
            )

            empresa["websiteUri"] = (
                "Consulta não realziada"
            )

            estatisticas["consultas_falha"] += 1

            print(f"Erro ao consultar {place_id}: {erro}")

    return empresas, estatisticas