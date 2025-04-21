from flask import Flask, request, jsonify
import requests
import logging
from datetime import datetime
import os

HUBSPOT_TOKEN = os.getenv("HUBSPOT_TOKEN")

app = Flask(__name__)

# === CONFIGURAÇÃO DO LOG ===
logging.basicConfig(
    filename='webhook.log',
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def atualizar_lead_hubspot(hubspot_id, status, fase):
    url = f'https://api.hubapi.com/crm/v3/objects/contacts/{hubspot_id}'
    headers = {
        'Authorization': f'Bearer {HUBSPOT_TOKEN}',
        'Content-Type': 'application/json'
    }
    payload = {
        "properties": {
            "hs_lead_status": status,
            "lifecyclestage": fase
        }
    }

    logging.info(f"🔄 Enviando atualização para HubSpot: ID={hubspot_id}, status={status}, fase={fase}")
    response = requests.patch(url, headers=headers, json=payload)

    if response.status_code == 200:
        logging.info(f"✅ Lead {hubspot_id} atualizado com sucesso no HubSpot.")
        return True
    else:
        logging.error(f"❌ Falha ao atualizar lead {hubspot_id}: {response.status_code} - {response.text}")
        return False

@app.route('/webhook/classificar', methods=['POST'])
def classificar_lead():
    data = request.get_json()
    logging.info(f"📩 Requisição recebida: {data}")

    hubspot_id = data.get("hubspot_id")
    status = data.get("status", "Conectado")
    fase = data.get("fase", "Lead qualificado para venda")

    if not hubspot_id:
        logging.warning("⚠️ ID do lead não fornecido na requisição.")
        return jsonify({"error": "ID do lead não fornecido"}), 400

    atualizado = atualizar_lead_hubspot(hubspot_id, status, fase)

    if atualizado:
        return jsonify({"mensagem": "Lead atualizado com sucesso!"}), 200
    else:
        return jsonify({"erro": "Erro ao atualizar lead"}), 500

@app.route('/', methods=['GET'])
def home():
    return "🚀 Webhook FiqON-HubSpot ativo!", 200

if __name__ == '__main__':
    logging.info("🔧 Iniciando servidor Flask no webhook_receiver.py")
    app.run(host='0.0.0.0', port=5050)
