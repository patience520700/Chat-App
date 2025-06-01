from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modèles de base de données
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

# Créer la base de données
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return render_template('chat.html')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            return jsonify({'success': True, 'username': user.username})
        
        return jsonify({'success': False, 'message': 'Invalid credentials'})
    
    return render_template('login.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if User.query.filter_by(email=email).first():
        return jsonify({'success': False, 'message': 'Email already exists'})
    
    hashed_password = generate_password_hash(password, method='sha256')
    new_user = User(username=username, email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/api/contacts')
def get_contacts():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    current_user_id = session['user_id']
    contacts = User.query.filter(User.id != current_user_id).all()
    
    contacts_data = []
    for contact in contacts:
        last_message = Message.query.filter(
            ((Message.sender_id == current_user_id) & (Message.recipient_id == contact.id)) |
            ((Message.sender_id == contact.id) & (Message.recipient_id == current_user_id))
        ).order_by(Message.timestamp.desc()).first()
        
        contacts_data.append({
            'id': contact.id,
            'name': contact.username,
            'lastMessage': last_message.content if last_message else '',
            'online': True,  # Vous devrez implémenter la logique réelle
            'lastSeen': 'Just now'
        })
    
    return jsonify(contacts_data)

@app.route('/api/messages/<int:contact_id>')
def get_messages(contact_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    current_user_id = session['user_id']
    messages = Message.query.filter(
        ((Message.sender_id == current_user_id) & (Message.recipient_id == contact_id)) |
        ((Message.sender_id == contact_id) & (Message.recipient_id == current_user_id))
    ).order_by(Message.timestamp.asc()).all()
    
    messages_data = [{
        'senderId': msg.sender_id,
        'content': msg.content,
        'timestamp': msg.timestamp.isoformat(),
        'type': 'sticker' if any(c in msg.content for c in ['❤️', '😊', '😂']) else 'text'
    } for msg in messages]
    
    return jsonify(messages_data)

@app.route('/api/send', methods=['POST'])
def send_message():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    recipient_id = data.get('recipient_id')
    content = data.get('content')
    
    new_message = Message(
        sender_id=session['user_id'],
        recipient_id=recipient_id,
        content=content
    )
    db.session.add(new_message)
    db.session.commit()
    
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True)