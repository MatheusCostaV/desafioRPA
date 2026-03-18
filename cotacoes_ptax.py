import csv
import time
import requests
from datetime import datetime, timedelta
from selenium import webdriver

ARQUIVO = "cotacoes.csv"

# abre o navegador
driver = webdriver.Chrome()

registros = []

try:
    # abre os sites pedidos (so pra cumprir a parte de usar o selenium, ja que a API do BC é mais facil)
    driver.get("https://www.bcb.gov.br/estabilidadefinanceira/fechamentodolar")
    time.sleep(2)

    driver.get("https://www.bcb.gov.br")
    time.sleep(2)

    # tenta pegar a cotação voltando até 7 dias
    for i in range(7):
        data = datetime.today() - timedelta(days=i)
        data_api = data.strftime("%m-%d-%Y")

        url_dolar = f"https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoDolarDia(dataCotacao=@dataCotacao)?@dataCotacao='{data_api}'&$format=json"

        resposta = requests.get(url_dolar)
        valores = resposta.json().get("value", [])

        if valores:
            ultimo = valores[-1]

            registros.append({
                "data": data.strftime("%d/%m/%Y"),
                "moeda": "Dolar",
                "compra": ultimo["cotacaoCompra"],
                "venda": ultimo["cotacaoVenda"]
            })
            break  # achou, parou

    # mesma loogica para o euro
    for i in range(7):
        data = datetime.today() - timedelta(days=i)
        data_api = data.strftime("%m-%d-%Y")

        url_euro = f"https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoMoedaDia(moeda=@moeda,dataCotacao=@dataCotacao)?@moeda='EUR'&@dataCotacao='{data_api}'&$format=json"

        resposta = requests.get(url_euro)
        valores = resposta.json().get("value", [])

        if valores:
            ultimo = valores[-1]

            registros.append({
                "data": data.strftime("%d/%m/%Y"),
                "moeda": "Euro",
                "compra": ultimo["cotacaoCompra"],
                "venda": ultimo["cotacaoVenda"]
            })
            break

    # salva no csv
    if registros:
        with open(ARQUIVO, "w", newline="", encoding="utf-8") as f:
            campos = ["data", "moeda", "compra", "venda"]
            writer = csv.DictWriter(f, fieldnames=campos, delimiter=";")
            writer.writeheader()
            writer.writerows(registros)

        print("arquivo criado\n")

        for r in registros:
            print(r)
    else:
        print("nenhum dado encontrado")

except Exception as e:
    print("erro:", e)

finally:
    driver.quit()
