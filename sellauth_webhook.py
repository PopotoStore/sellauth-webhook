from flask import Flask, request, jsonify
import requests
import os

# --- CONFIGURAZIONE ---
API_KEY = os.environ.get("API_KEY")  # ✅ Variabile ambiente sicura
BASE_URL = "https://api.sellauth.com/v1"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

app = Flask(__name__)

# 🔍 Recupera dettagli prodotto
def get_product(product_id):
    url = f"{BASE_URL}/products/{product_id}"
    response = requests.get(url, headers=headers)
    return response.json()

# 🔁 Aggiorna seriali disponibili
def update_product_serials(product_id, new_serials):
    url = f"{BASE_URL}/products/{product_id}"
    payload = {"serials": new_serials}
    return requests.patch(url, headers=headers, json=payload).json()

# ❌ Rimuove seriale venduto
def remove_serial(product_id, delivered_serial):
    product = get_product(product_id)
    current_serials = product.get("serials", [])

    print(f"📦 Seriali attuali per il prodotto {product_id}: {current_serials}")
    updated_serials = [s for s in current_serials if s != delivered_serial]

    if len(updated_serials) < len(current_serials):
        update_product_serials(product_id, updated_serials)
        print(f"✅ Serial **'{delivered_serial}'** rimosso da prodotto **'{product_id}'**")
        print(f"🔢 Seriali rimanenti: {updated_serials}")
    else:
        print(f"⚠️ Serial '{delivered_serial}' NON trovato in {product_id} o già rimosso.")

# 📬 Webhook endpoint
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        print("📩 Webhook ricevuto:", data)

        product_id = data.get("product_id")
        delivered_serial = data.get("serial")

        print("🔎 product_id:", product_id)
        print("🔎 serial:", delivered_serial)

        if product_id and delivered_serial:
            remove_serial(product_id, delivered_serial)
            return jsonify({"status": "ok", "message": "Serial rimosso"}), 200
        else:
            print("⚠️ Dati mancanti nel payload:", data)
            return jsonify({"status": "error", "message": "Dati mancanti"}), 400
    except Exception as e:
        print("❌ Errore nel webhook:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500

# 🌐 Test ping
@app.route("/", methods=["GET"])
def index():
    return "✅ Server attivo. Webhook pronto su /webhook"

# 🚀 Entry point per Render
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
