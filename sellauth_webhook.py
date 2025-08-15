from flask import Flask, request, jsonify
import requests
import os
import json

# Configurazione
API_KEY = os.environ.get("API_KEY")
BASE_URL = "https://api.sellauth.com/v1"

if not API_KEY:
    raise RuntimeError("⚠️ API_KEY non impostata nelle variabili d'ambiente")

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

app = Flask(__name__)

# Recupera il prodotto da SellAuth
def get_product(product_id):
    url = f"{BASE_URL}/products/{product_id}"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"❌ Errore recupero prodotto: {response.status_code} - {response.text}")
        return {}
    return response.json()

# Aggiorna la lista dei seriali nel prodotto
def update_product_serials(product_id, new_serials):
    url = f"{BASE_URL}/products/{product_id}"
    payload = {"serials": new_serials}
    response = requests.patch(url, headers=headers, json=payload)
    if response.status_code != 200:
        print(f"❌ Errore aggiornamento serials: {response.status_code} - {response.text}")
    return response.json()

# Rimuove il seriale dal prodotto
def remove_serial(product_id, delivered_serial):
    product = get_product(product_id)
    current_serials = product.get("serials", [])
    updated_serials = [s for s in current_serials if s != delivered_serial]

    if len(updated_serials) < len(current_serials):
        update_product_serials(product_id, updated_serials)
        print(f"✅ Serial '{delivered_serial}' rimosso dal prodotto '{product_id}'")
        return True
    else:
        print("⚠️ Serial non trovato o già rimosso.")
        return False

# Webhook handler
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        # Log degli header e body grezzo
        headers_received = dict(request.headers)
        raw_body = request.data.decode("utf-8", errors="ignore")

        print("📩 Headers ricevuti:", headers_received)
        print("📩 Body grezzo ricevuto:", raw_body)

        # Parsing JSON forzato anche se Content-Type non è corretto
        try:
            data = request.get_json(force=True)
            print("📩 JSON parsato (formattato):")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        except Exception as e:
            print("❌ Errore parsing JSON:", str(e))
            return jsonify({
                "status": "error",
                "message": "Body non è JSON valido",
                "headers": headers_received,
                "raw_body": raw_body
            }), 400

        # Estrai product_id e serial
        product_id = data.get("product_id")
        delivered_serial = data.get("serial")

        # Estratti alternativi in caso siano annidati
        if not product_id and "line_items" in data:
            product_id = data["line_items"][0].get("product_id")
        if not delivered_serial and "line_items" in data:
            delivered_serial = data["line_items"][0].get("serial")

        print("🔎 Estratto product_id:", product_id)
        print("🔎 Estratto serial:", delivered_serial)

        if product_id and delivered_serial:
            removed = remove_serial(product_id, delivered_serial)
            return jsonify({
                "status": "ok" if removed else "warning",
                "message": "Serial rimosso" if removed else "Serial non trovato",
                "order_details": {
                    "product_id": product_id,
                    "serial": delivered_serial
                },
                "full_payload": data
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "Dati mancanti",
                "full_payload": data
            }), 400

    except Exception as e:
        print("❌ Errore nel webhook:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500

# Pagina base
@app.route("/", methods=["GET"])
def index():
    return "✅ Server attivo. Webhook pronto su /webhook"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)




