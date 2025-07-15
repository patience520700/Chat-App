import requests

def envoyer_utilisateur():
    url = "http://localhost:5000/signup"
    utilisateur = {
        "nom": "Raymond",
        "age": 30,
        "sexe": "homme"
    }

    reponse = requests.post(url, json=utilisateur)

    if reponse.status_code == 200:
        print("✅ Utilisateur enregistré avec succès.")
    else:
        print("❌ Erreur :", reponse.json())

envoyer_utilisateur()