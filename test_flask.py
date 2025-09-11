from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return 'Flask fonctionne !'

if __name__ == '__main__':
    print("✓ Flask est installé correctement")
    print("Lancez le serveur avec: flask run")