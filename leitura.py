import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import requests
import webbrowser  # Para abrir a URL no navegador

READER = SimpleMFRC522()

try:
    print("Aproxime o cartão RFID...")
    uid, _ = READER.read()  # O método read() retorna (uid, texto) se aplicável
    print(f"UID lido: {uid}")

    # Envia o UID para o servidor Flask para validação
    url_api = "http://<IP_DO_RASPBERRY>:5000/validar-cartao"  # Use o IP local ou hostname conforme sua rede
    response = requests.post(url_api, json={"uid": uid})
    
    if response.status_code == 200:
        # Se a resposta for 200, espera que retorne a URL da dashboard
        dados = response.json()
        dashboard_url = dados.get("dashboard_url")
        if dashboard_url:
            print("Cartão válido! Abrindo dashboard...")
            # Abre a URL no navegador (supondo que o Raspberry Pi esteja conectado a um display)
            webbrowser.open(dashboard_url)
        else:
            print("Erro: URL da dashboard não retornada.")
    else:
        # Exibe a mensagem de erro retornada pelo servidor
        print("Erro na validação do cartão:", response.json().get("error"))

finally:
    GPIO.cleanup()
