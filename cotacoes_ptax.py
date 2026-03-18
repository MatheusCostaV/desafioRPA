import requests
import csv
from datetime import datetime, timedelta

ARQUIVO = "cotacoes.csv"  
moedas = ["USD", "EUR"]  # moedas que vamos buscar
registros = []  # lista para guardar os resultados

# percorre cada moeda
for moeda in moedas:
    # tenta buscar até
    #  7 dias para trás
    for i in range(7):
        data = (datetime.today() - timedelta(days=i)).strftime("%m-%d-%Y")

        # monta a URL dependendo da moeda
        if moeda == "USD":
            url = f"https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoDolarDia(dataCotacao=@dataCotacao)?@dataCotacao='{data}'&$format=json"
        else:
            url = f"https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoMoedaDia(moeda=@moeda,dataCotacao=@dataCotacao)?@moeda='{moeda}'&@dataCotacao='{data}'&$format=json"

        try:
            resposta = requests.get(url)  # faz a requisição
            valores = resposta.json().get("value", [])  # pega os dados

            # se encontrou dados
            if valores:
                ultima = valores[-1]  # pega o último valor

                # salva na lista
                registros.append({
                    "moeda": moeda,
                    "data": ultima["dataHoraCotacao"][:10],  # só a data
                    "compra": ultima["cotacaoCompra"],
                    "venda": ultima["cotacaoVenda"]
                })
                break  # para de tentar dias anteriores

        except:
            print(f"Erro ao buscar {moeda}")  # erro na requisição
            break

    else:
        # entra aqui se não encontrou em nenhum dia
        print(f"nenhuma cotacão encontrada para {moeda}")

# salva no CSV se tiver dados
if registros:
    with open(ARQUIVO, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["moeda", "data", "compra", "venda"], delimiter=";")
        writer.writeheader()
        writer.writerows(registros)

    print("arquivo criado")

    # mostra no terminal
    for r in registros:
        print(r)
else:
    print("nada encontrado.")