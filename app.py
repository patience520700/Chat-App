from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = 'votre_cle_secrete_tres_securisee'  # Changez ceci en production

# Configuration of the database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'lovenett.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models of the database
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    gender = db.Column(db.String(10))
    country = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    birthdate = db.Column(db.DateTime)
    profile_picture = db.Column(db.String(200))
    bio = db.Column(db.Text)
    interests = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    messages_sent = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy=True)
    messages_received = db.relationship('Message', foreign_keys='Message.receiver_id', backref='receiver', lazy=True)
    profile_views = db.relationship('ProfileView', foreign_keys='ProfileView.viewed_id', backref='viewed_user', lazy=True)
    viewers = db.relationship('ProfileView', foreign_keys='ProfileView.viewer_id', backref='viewer', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    read = db.Column(db.Boolean, default=False)

class ProfileView(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    viewer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    viewed_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Décorateur pour les routes nécessitant une authentification
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Veuillez vous connecter pour accéder à cette page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes de l'application
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Connexion réussie!', 'success')
            return redirect(url_for('messages'))
        else:
            flash('Email ou mot de passe incorrect.', 'danger')
    
    return render_template('forms.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        gender = request.form.get('gender')
        country = request.form.get('country')
        phone = request.form.get('phone')
        birthdate_str = request.form.get('birthdate')
        
        # Vérifier si l'utilisateur existe déjà
        if User.query.filter_by(email=email).first():
            flash('Un compte avec cet email existe déjà.', 'danger')
            return redirect(url_for('register'))
        
        if User.query.filter_by(username=username).first():
            flash('Ce nom d\'utilisateur est déjà pris.', 'danger')
            return redirect(url_for('register'))
        
        # Convertir la date de naissance
        try:
            birthdate = datetime.strptime(birthdate_str, '%Y-%m-%d')
        except:
            birthdate = None
        
        # Créer un nouvel utilisateur
        new_user = User(
            username=username,
            email=email,
            gender=gender,
            country=country,
            phone=phone,
            birthdate=birthdate
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Compte créé avec succès! Vous pouvez maintenant vous connecter.', 'success')
        return redirect(url_for('login'))
    
    return render_template('forms.html')

@app.route('/dashboard')  # CORRIGÉ: Changé de '/index' à '/dashboard'
@login_required
def dashboard():
    user = User.query.get(session['user_id'])
    return render_template('dashboard.html', user=user)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        user.username = request.form.get('username', user.username)
        user.bio = request.form.get('bio', user.bio)
        user.interests = request.form.get('interests', user.interests)
        user.country = request.form.get('country', user.country)
        
        # Gérer la photo de profil si fournie
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename != '':
                # En production, il faudrait sécuriser ceci
                filename = f"user_{user.id}_{file.filename}"
                file.save(os.path.join('static', 'uploads', filename))
                user.profile_picture = filename
        
        db.session.commit()
        flash('Profil mis à jour avec succès!', 'success')
        return redirect(url_for('profile'))
    
    return render_template('profile.html', user=user)

@app.route('/messages')
@login_required
def messages():
    user_id = session['user_id']
    
    # Récupérer tous les messages de l'utilisateur
    sent_messages = Message.query.filter_by(sender_id=user_id).order_by(Message.timestamp.desc()).all()
    received_messages = Message.query.filter_by(receiver_id=user_id).order_by(Message.timestamp.desc()).all()
    
    # Combiner et trier tous les messages
    all_messages = sorted(
        sent_messages + received_messages, 
        key=lambda x: x.timestamp, 
        reverse=True
    )
    
    # Récupérer les utilisateurs avec qui l'utilisateur a conversé
    conversation_partners = set()
    for msg in all_messages:
        if msg.sender_id == user_id:
            conversation_partners.add(msg.receiver)
        else:
            conversation_partners.add(msg.sender)
    
    return render_template('messages.html', 
                         messages=all_messages, 
                         partners=conversation_partners)

@app.route('/send_message', methods=['POST'])
@login_required
def send_message():
    receiver_username = request.form.get('receiver')
    content = request.form.get('content')
    
    receiver = User.query.filter_by(username=receiver_username).first()
    
    if not receiver:
        flash('Utilisateur non trouvé.', 'danger')
        return redirect(url_for('messages'))
    
    if receiver.id == session['user_id']:
        flash('Vous ne pouvez pas vous envoyer un message à vous-même.', 'warning')
        return redirect(url_for('chat'))
    
    new_message = Message(
        content=content,
        sender_id=session['user_id'],
        receiver_id=receiver.id
    )
    
    db.session.add(new_message)
    db.session.commit()
    
    flash('Message envoyé!', 'success')
    return redirect(url_for('messages'))

@app.route('/users')
@login_required
def users():
    # Récupérer tous les utilisateurs sauf l'utilisateur actuel
    all_users = User.query.filter(User.id != session['user_id']).all()
    return render_template('users.html', users=all_users)

@app.route('/view_profile/<int:user_id>')
@login_required
def view_profile(user_id):
    viewed_user = User.query.get_or_404(user_id)
    
    # Enregistrer la consultation du profil
    if user_id != session['user_id']:
        profile_view = ProfileView(
            viewer_id=session['user_id'],
            viewed_id=user_id
        )
        db.session.add(profile_view)
        db.session.commit()
    
    return render_template('view_profile.html', user=viewed_user)

@app.route('/logout')
def logout():
    session.clear()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('index'))

# API pour les messages (pour une application plus dynamique)
@app.route('/api/messages/<int:partner_id>')
@login_required
def api_messages(partner_id):
    user_id = session['user_id']
    
    messages = Message.query.filter(
        ((Message.sender_id == user_id) & (Message.receiver_id == partner_id)) |
        ((Message.sender_id == partner_id) & (Message.receiver_id == user_id))
    ).order_by(Message.timestamp.asc()).all()
    
    # Marquer les messages comme lus
    for msg in messages:
        if msg.receiver_id == user_id and not msg.read:
            msg.read = True
    db.session.commit()
    
    return jsonify([{
        'id': msg.id,
        'content': msg.content,
        'timestamp': msg.timestamp.isoformat(),
        'sender_id': msg.sender_id,
        'receiver_id': msg.receiver_id,
        'is_sender': msg.sender_id == user_id
    } for msg in messages])

# Nouvelles routes pour les pages HTML supplémentaires
@app.route('/subscription')
def subscription():
    return render_template('subscription.html')

# @app.route('/chat')
# @login_required
# def chat():
#     return render_template('chat.html')

@app.route('/faq')
def faq():
    return render_template('FAQ.html')


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/share')
def share():
    return render_template('share.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/contact-us')
def contact_us():
    return render_template('contact-us.html')

@app.route('/success-stories')
def success_stories():
    return render_template('success-stories.html')

@app.route('/shares-story')  # CORRIGÉ: Nom de fonction cohérent
def shares_story():
    return render_template('shares-story.html')

@app.route('/privacy')  # AJOUTÉ: Route manquante pour privacy
def privacy():
    return render_template('privacy.html')

@app.route('/forms')  # AJOUTÉ: Route manquante pour terms
def forms():
    return render_template('forms.html')

@app.route('/advert')
@login_required
def advert():
    return render_template('advert.html')

@app.route('/article1')
def article1():
    return render_template('article1.html')

# Initialisation de la base de données
@app.before_request
def create_tables():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)