@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        print("📩 Headers:", dict(request.headers))
        print("📩 Raw body:", request.data.decode("utf-8"))

        if not request.is_json:
            return jsonify({"status": "error", "message": "Contenuto non JSON"}), 400

        data = request.get_json()
        print("📩 JSON ricevuto:", data)

        # Stampiamo i dati specifici che arrivano da SellAuth
        event_type = data.get("type")
        invoice_id = data.get("data", {}).get("invoice_id")
        notifiable_id = data.get("notifiable_id")

        print("🔎 Evento:", event_type)
        print("🔎 Invoice ID:", invoice_id)
        print("🔎 Notifiable ID:", notifiable_id)

        return jsonify({"status": "ok", "message": "Ricevuto correttamente"}), 200

    except Exception as e:
        print("❌ Errore parsing JSON:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500

