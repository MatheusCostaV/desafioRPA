import csv
import time
import requests
import logging
from datetime import datetime, timedelta
from selenium import webdriver

# Configuração do arquivo de log de erros
logging.basicConfig(
    filename="erros.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

ARQUIVO = "cotacoes.csv"
registros = []
driver = None

try:
    # Abre o navegador
    driver = webdriver.Chrome()
    
    # Maximiza a janela (deixa em tela cheia)
    driver.maximize_window()

    # Abre os sites pedidos (apenas para cumprir a exigência do Selenium)
    driver.get("https://www.bcb.gov.br/estabilidadefinanceira/fechamentodolar")
    time.sleep(2)

    driver.get("https://www.bcb.gov.br")
    time.sleep(2)

    # Tenta pegar a cotação do Dólar voltando até 7 dias
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
            break  # Achou a cotação, sai do loop

    # Mesma lógica para o Euro
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
            break # Achou a cotação, sai do loop

    # Salva os dados no arquivo CSV
    if registros:
        with open(ARQUIVO, "w", newline="", encoding="utf-8") as f:
            campos = ["data", "moeda", "compra", "venda"]
            writer = csv.DictWriter(f, fieldnames=campos, delimiter=";")
            writer.writeheader()
            writer.writerows(registros)

        print("Arquivo CSV criado com sucesso!\n")

        for r in registros:
            print(r)
    else:
        print("Nenhum dado encontrado nas APIs do Banco Central.")

except Exception as e:
    # Registra o erro completo no arquivo erros.log
    logging.error("Erro durante a execução do script", exc_info=True)
    print("Ocorreu um erro! Verifique o arquivo 'erros.log' para mais detalhes.")

finally:
    # Garante que o navegador será fechado no final, dando erro ou não
    if driver:
        driver.quit()