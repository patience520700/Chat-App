from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore

# Initialiser Firebase
cred = credentials.Certificate("firebase_config.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Création du serveur Flask
app = Flask(__name__)
CORS(app)  # Autoriser les requêtes de l'extérieur

@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    nom = data.get("nom")
    age = data.get("age")
    sexe = data.get("sexe")

    if not nom or not age or not sexe:
        return jsonify({"error": "Champs manquants"}), 400

    utilisateur = {
        "nom": nom,
        "age": age,
        "sexe": sexe
    }

    db.collection("users").add(utilisateur)
    return jsonify({"message": "Utilisateur enregistré avec succès"}), 200

if __name__ == "_main_":
    app.run(port=5000)