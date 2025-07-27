from flask import Flask, request, jsonify
import requests
import os

API_KEY = os.environ.get("API_KEY")
BASE_URL = "https://api.sellauth.com/v1"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

app = Flask(__name__)

def get_product(product_id):
    url = f"{BASE_URL}/products/{product_id}"
    response = requests.get(url, headers=headers)
    return response.json()

def update_product_serials(product_id, new_serials):
    url = f"{BASE_URL}/products/{product_id}"
    payload = {"serials": new_serials}
    return requests.patch(url, headers=headers, json=payload).json()

def remove_serial(product_id, delivered_serial):
    product = get_product(product_id)
    current_serials = product.get("serials", [])
    updated_serials = [s for s in current_serials if s != delivered_serial]

    if len(updated_serials) < len(current_serials):
        update_product_serials(product_id, updated_serials)
        print(f"✅ Serial '{delivered_serial}' rimosso dal prodotto '{product_id}'")
    else:
        print("⚠️ Serial non trovato o già rimosso.")

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        print("📩 Headers:", dict(request.headers))
        print("📩 Raw body:", request.data.decode("utf-8"))

        if not request.is_json:
            return jsonify({"status": "error", "message": "Contenuto non JSON"}), 400

        data = request.get_json()
        print("📩 JSON ricevuto:", data)

        product_id = data.get("product_id")
        delivered_serial = data.get("serial")

        print("🔎 product_id:", product_id)
        print("🔎 serial:", delivered_serial)

        if product_id and delivered_serial:
            remove_serial(product_id, delivered_serial)
            return jsonify({"status": "ok", "message": "Serial rimosso"}), 200
        else:
            print("⚠️ Dati mancanti nel payload JSON:", data)
            return jsonify({"status": "error", "message": "Dati mancanti"}), 400
    except Exception as e:
        print("❌ Errore parsing JSON:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/", methods=["GET"])
def index():
    return "✅ Server attivo. Webhook pronto su /webhook"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
