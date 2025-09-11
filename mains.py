from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit, join_room, leave_room
from datetime import datetime
import os

# Initialisation de l'application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'votre_cle_secrete_tres_securisee'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lovenett.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialisation des extensions
db = SQLAlchemy(app)
socketio = SocketIO(app)

# Modèles de données
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    birthdate = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    profile_image = db.Column(db.String(200))
    bio = db.Column(db.Text)
    interests = db.Column(db.String(200))
    
    def __repr__(self):
        return f'<User {self.username}>'

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    read = db.Column(db.Boolean, default=False)
    
    sender = db.relationship('User', foreign_keys=[sender_id])
    receiver = db.relationship('User', foreign_keys=[receiver_id])

# Routes principales
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/forms')
def forms():
    return render_template('forms.html')

@app.route('/chat')
def chat():
    if 'user_id' not in session:
        return redirect(url_for('forms'))
    return render_template('chat.html')

@app.route('/subscription')
def subscription():
    return render_template('subscription.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')

# API Routes pour l'authentification
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Vérifier si l'utilisateur existe déjà
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'success': False, 'message': 'Email already exists'})
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'success': False, 'message': 'Username already exists'})
    
    # Créer un nouvel utilisateur
    new_user = User(
        username=data['username'],
        email=data['email'],
        password=data['password'],  # Note: devrait être hashé en production
        gender=data['gender'],
        country=data['country'],
        phone=data['phone'],
        birthdate=datetime.strptime(data['birthdate'], '%Y-%m-%d')
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Registration successful'})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    
    user = User.query.filter_by(email=data['email']).first()
    
    if user and user.password == data['password']:  # Note: utiliser hashing en production
        session['user_id'] = user.id
        session['username'] = user.username
        return jsonify({'success': True, 'message': 'Login successful'})
    
    return jsonify({'success': False, 'message': 'Invalid credentials'})

@app.route('/api/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# Gestion du chat en temps réel avec SocketIO
@socketio.on('connect')
def handle_connect():
    if 'user_id' in session:
        join_room(session['user_id'])
        emit('user_connected', {'user_id': session['user_id'], 'username': session['username']})

@socketio.on('send_message')
def handle_send_message(data):
    receiver_id = data['receiver_id']
    content = data['content']
    
    # Sauvegarder le message en base de données
    new_message = Message(
        sender_id=session['user_id'],
        receiver_id=receiver_id,
        content=content
    )
    
    db.session.add(new_message)
    db.session.commit()
    
    # Envoyer le message au destinataire
    emit('receive_message', {
        'sender_id': session['user_id'],
        'sender_name': session['username'],
        'content': content,
        'timestamp': datetime.utcnow().isoformat()
    }, room=receiver_id)

@socketio.on('disconnect')
def handle_disconnect():
    if 'user_id' in session:
        leave_room(session['user_id'])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True)