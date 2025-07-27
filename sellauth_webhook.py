from flask import Flask, request, jsonify
import requests
import os

# Configurazione API Key e base URL
API_KEY = os.environ.get("API_KEY")
BASE_URL = "https://api.sellauth.com/v1"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

app = Flask(__name__)

# Recupera il prodotto da SellAuth
def get_product(product_id):
    url = f"{BASE_URL}/products/{product_id}"
    response = requests.get(url, headers=headers)
    return response.json()

# Aggiorna la lista di seriali di un prodotto
def update_product_serials(product_id, new_serials):
    url = f"{BASE_URL}/products/{product_id}"
    payload = {"serials": new_serials}
    return requests.patch(url, headers=headers, json=payload).json()

# Rimuove un seriale dal prodotto
def remove_serial(product_id, delivered_serial):
    product = get_product(product_id)
    current_serials = product.get("serials", [])
    updated_serials = [s for s in current_serials if s != delivered_serial]

    if len(updated_serials) < len(current_serials):
        update_product_serials(product_id, updated_serials)
        print(f"✅ Serial '{delivered_serial}' rimosso dal prodotto '{product_id}'")
    else:
        print("⚠️ Serial non trovato o già rimosso.")

# Webhook principale
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        print("📩 Headers:", dict(request.headers))
        print("📩 Raw body:", request.data.decode("utf-8"))

        if not request.is_json:
            return jsonify({"status": "error", "message": "Contenuto non JSON"}), 400

        data = request.get_json()
        print("📩 JSON ricevuto:", data)

        # Esempio JSON:
        # {
        #   "type": "ShopInvoiceProcessed",
        #   "data": {
        #       "invoice_id": 5770767
        #   },
        #   "notifiable_id": 167934
        # }

        event_type = data.get("type")
        invoice_id = data.get("data", {}).get("invoice_id")
        notifiable_id = data.get("notifiable_id")

        print("🔎 Evento:", event_type)
        print("🔎 Invoice ID:", invoice_id)
        print("🔎 Notifiable ID:", notifiable_id)

        # ✅ Qui puoi aggiungere chiamate API per ottenere il serial e il product_id

        return jsonify({"status": "ok", "message": "Webhook ricevuto correttamente"}), 200

    except Exception as e:
        print("❌ Errore nel webhook:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500

# Per testare che il server sia attivo
@app.route("/", methods=["GET"])
def index():
    return "✅ Server attivo. Webhook pronto su /webhook"

# Avvio dell'app Flask
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
