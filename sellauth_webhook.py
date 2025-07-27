from flask import Flask, request, jsonify
import requests

from flask import Flask, request, jsonify
import requests
import os  # 🔐 Per leggere l'API_KEY in modo sicuro

# --- CONFIGURAZIONE ---
API_KEY = os.environ.get("API_KEY")  # ✅ Lettura da variabile ambiente
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
        print(f"✅ Serial {delivered_serial} rimosso dal prodotto {product_id}")
    else:
        print("⚠️ Serial non trovato o già rimosso.")

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("📩 Webhook ricevuto:", data)

    product_id = data.get("product_id")
    delivered_serial = data.get("serial")

    if product_id and delivered_serial:
        remove_serial(product_id, delivered_serial)
        return jsonify({"status": "ok", "message": "Serial rimosso"}), 200
    else:
        return jsonify({"status": "error", "message": "Dati mancanti"}), 400

@app.route("/", methods=["GET"])
def index():
    return "✅ Server attivo. Webhook pronto su /webhook"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
