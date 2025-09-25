from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from functools import wraps
from sqlalchemy import text  # Add this import

# Application Configuration
app = Flask(__name__)
app.secret_key = '935ac244f2b1c36b990a0569c8cfd6d8d7ad33e5feec29f40b04442aa031c489'  # Change this in production

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Lovenett123@localhost/chat_app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Extensions Initialization
db = SQLAlchemy(app)

# =============================================================================
# DATABASE MODELS
# =============================================================================

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
    
    # Relationships
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

# =============================================================================
# DECORATORS AND UTILITY FUNCTIONS
# =============================================================================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('forms'))
        return f(*args, **kwargs)
    return decorated_function

def initialize_database():
    """Initialize the database tables"""
    with app.app_context():
        db.create_all()
        print("✅ Database tables created successfully!")

def test_database_connection():
    """Test database connection"""
    try:
        with app.app_context():
            # Use text() to wrap SQL expression
            db.session.execute(text('SELECT 1'))
            print("✅ Database connection successful!")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

# =============================================================================
# AUTHENTICATION ROUTES
# =============================================================================

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/forms')
def forms():
    """Login/Registration page"""
    return render_template('forms.html')

@app.route('/login', methods=['POST'])
def login():
    """User login"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Incorrect email or password.', 'danger')
            return redirect(url_for('forms'))

@app.route('/register', methods=['POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm-password')
        gender = request.form.get('gender')
        country = request.form.get('country')
        phone = request.form.get('phone')
        birthdate_str = request.form.get('birthdate')
        
        # Password validation
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('forms'))
        
        # Check for existing user
        if User.query.filter_by(email=email).first():
            flash('An account with this email already exists.', 'danger')
            return redirect(url_for('forms'))
        
        if User.query.filter_by(username=username).first():
            flash('This username is already taken.', 'danger')
            return redirect(url_for('forms'))
        
        # Convert birthdate
        try:
            birthdate = datetime.strptime(birthdate_str, '%Y-%m-%d') if birthdate_str else None
        except ValueError:
            birthdate = None
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            gender=gender,
            country=country,
            phone=phone,
            birthdate=birthdate,
            profile_picture=f'https://ui-avatars.com/api/?name={username}&background=0062cc&color=fff'
        )
        new_user.set_password(password)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully! You can now log in.', 'success')
            return redirect(url_for('forms'))
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Please try again.', 'danger')
            return redirect(url_for('forms'))

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('forms'))

# =============================================================================
# MAIN APPLICATION ROUTES (REQUIRES AUTHENTICATION)
# =============================================================================

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    user = User.query.get(session['user_id'])
    return render_template('dashboard.html', user=user)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile management"""
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        # Update profile information
        user.username = request.form.get('username', user.username)
        user.bio = request.form.get('bio', user.bio)
        user.interests = request.form.get('interests', user.interests)
        user.country = request.form.get('country', user.country)
        
        # Handle profile picture upload
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename != '':
                filename = f"user_{user.id}_{file.filename}"
                file.save(os.path.join('static', 'uploads', filename))
                user.profile_picture = filename
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    
    return render_template('profile.html', user=user)

@app.route('/chat')
@login_required
def chat():
    """Main chat page"""
    return render_template('chat.html')



# =============================================================================
# REAL-TIME CHAT ROUTES (ADD THIS SECTION)
# =============================================================================

@app.route('/api/chat/messages/<int:partner_id>')
@login_required
def api_chat_messages(partner_id):
    """API: Get messages for real-time chat interface"""
    user_id = session['user_id']
    
    # Verify partner exists
    partner = User.query.get(partner_id)
    if not partner:
        return jsonify({'error': 'User not found'}), 404
    
    # Get messages between current user and partner
    messages = Message.query.filter(
        ((Message.sender_id == user_id) & (Message.receiver_id == partner_id)) |
        ((Message.sender_id == partner_id) & (Message.receiver_id == user_id))
    ).order_by(Message.timestamp.asc()).all()
    
    # Mark received messages as read
    for msg in messages:
        if msg.receiver_id == user_id and not msg.read:
            msg.read = True
    
    db.session.commit()
    
    # Format response
    messages_data = []
    for msg in messages:
        messages_data.append({
            'id': msg.id,
            'content': msg.content,
            'timestamp': msg.timestamp.isoformat(),
            'sender_id': msg.sender_id,
            'sender_name': msg.sender.username,
            'receiver_id': msg.receiver_id,
            'is_sender': msg.sender_id == user_id,
            'read': msg.read
        })
    
    return jsonify(messages_data)

@app.route('/api/chat/conversations')
@login_required
def api_chat_conversations():
    """API: Get list of conversations for chat sidebar"""
    user_id = session['user_id']
    
    # Get users you've had conversations with
    sent_to = db.session.query(Message.receiver_id).filter(Message.sender_id == user_id).distinct()
    received_from = db.session.query(Message.sender_id).filter(Message.receiver_id == user_id).distinct()
    
    partner_ids = set([id for (id,) in sent_to] + [id for (id,) in received_from])
    
    conversations = []
    for partner_id in partner_ids:
        if partner_id == user_id:
            continue
            
        partner = User.query.get(partner_id)
        if not partner:
            continue
        
        # Get last message
        last_message = Message.query.filter(
            ((Message.sender_id == user_id) & (Message.receiver_id == partner_id)) |
            ((Message.sender_id == partner_id) & (Message.receiver_id == user_id))
        ).order_by(Message.timestamp.desc()).first()
        
        # Count unread messages
        unread_count = Message.query.filter(
            Message.sender_id == partner_id,
            Message.receiver_id == user_id,
            Message.read == False
        ).count()
        
        conversations.append({
            'partner_id': partner.id,
            'partner_name': partner.username,
            'last_message': last_message.content if last_message else '',
            'last_message_time': last_message.timestamp.isoformat() if last_message else '',
            'unread_count': unread_count,
            'profile_picture': partner.profile_picture
        })
    
    # Sort by last message time
    conversations.sort(key=lambda x: x['last_message_time'], reverse=True)
    
    return jsonify(conversations)
# =============================================================================
# MESSAGING ROUTES
# =============================================================================

@app.route('/messages')
@login_required
def messages():
    """Messages page (classic version)"""
    user_id = session['user_id']
    
    # Get user messages
    sent_messages = Message.query.filter_by(sender_id=user_id).order_by(Message.timestamp.desc()).all()
    received_messages = Message.query.filter_by(receiver_id=user_id).order_by(Message.timestamp.desc()).all()
    
    # Combine and sort messages
    all_messages = sorted(
        sent_messages + received_messages, 
        key=lambda x: x.timestamp, 
        reverse=True
    )
    
    # Get conversation partners
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
    """Send message (classic version)"""
    receiver_username = request.form.get('receiver')
    content = request.form.get('content')
    
    receiver = User.query.filter_by(username=receiver_username).first()
    
    if not receiver:
        flash('User not found.', 'danger')
        return redirect(url_for('messages'))
    
    if receiver.id == session['user_id']:
        flash('You cannot send a message to yourself.', 'warning')
        return redirect(url_for('messages'))
    
    new_message = Message(
        content=content,
        sender_id=session['user_id'],
        receiver_id=receiver.id
    )
    
    db.session.add(new_message)
    db.session.commit()
    flash('Message sent!', 'success')
    return redirect(url_for('messages'))

# =============================================================================
# USER MANAGEMENT ROUTES
# =============================================================================

@app.route('/users')
@login_required
def users():
    """Users listing page"""
    all_users = User.query.filter(User.id != session['user_id']).all()
    return render_template('users.html', users=all_users)

@app.route('/view_profile/<int:user_id>')
@login_required
def view_profile(user_id):
    """View another user's profile"""
    viewed_user = User.query.get_or_404(user_id)
    
    # Record profile view
    if user_id != session['user_id']:
        profile_view = ProfileView(
            viewer_id=session['user_id'],
            viewed_id=user_id
        )
        db.session.add(profile_view)
        db.session.commit()
    
    return render_template('view_profile.html', user=viewed_user)

# =============================================================================
# API ROUTES (FOR AJAX/DYNAMIC FUNCTIONALITY)
# =============================================================================

@app.route('/api/chat-users')
@login_required
def api_chat_users():
    """API: Get users for chat"""
    users = User.query.filter(User.id != session['user_id']).all()
    users_data = []
    
    for user in users:
        users_data.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'gender': user.gender,
            'country': user.country,
            'phone': user.phone,
            'created_at': user.created_at.isoformat() if user.created_at else None
        })
    
    return jsonify(users_data)

@app.route('/api/send-message', methods=['POST'])
@login_required
def api_send_message():
    """API: Send message via AJAX"""
    try:
        data = request.get_json()
        receiver_id = data.get('receiver_id')
        content = data.get('content')
        
        if not receiver_id or not content:
            return jsonify({'error': 'Missing required fields'}), 400
        
        receiver = User.query.get(receiver_id)
        if not receiver:
            return jsonify({'error': 'User not found'}), 404
        
        new_message = Message(
            content=content,
            sender_id=session['user_id'],
            receiver_id=receiver_id
        )
        
        db.session.add(new_message)
        db.session.commit()
        return jsonify({'success': True, 'message_id': new_message.id})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/messages/<int:partner_id>')
@login_required
def api_messages(partner_id):
    """API: Get messages with a partner"""
    user_id = session['user_id']
    
    partner = User.query.get(partner_id)
    if not partner:
        return jsonify({'error': 'User not found'}), 404
    
    messages = Message.query.filter(
        ((Message.sender_id == user_id) & (Message.receiver_id == partner_id)) |
        ((Message.sender_id == partner_id) & (Message.receiver_id == user_id))
    ).order_by(Message.timestamp.asc()).all()
    
    # Mark messages as read
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

# =============================================================================
# STATIC/INFORMATIONAL PAGES ROUTES
# =============================================================================

@app.route('/subscription')
def subscription():
    return render_template('subscription.html')

@app.route('/faq')
def faq():
    return render_template('FAQ.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/share')
def share():
    return render_template('share.html')

@app.route('/contact-us')
def contact_us():
    return render_template('contact-us.html')

@app.route('/success-stories')
def success_stories():
    return render_template('success-stories.html')

@app.route('/shares-story')
def shares_story():
    return render_template('shares-story.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/advert')
@login_required
def advert():
    return render_template('advert.html')

@app.route('/article1')
def article1():
    return render_template('article1.html')

# =============================================================================
# ERROR HANDLERS
# =============================================================================

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

# =============================================================================
# MAIN APPLICATION ENTRY POINT
# =============================================================================

if __name__ == '__main__':
    # Database initialization
    initialize_database()
    
    # Test database connection
    if test_database_connection():
        print("🚀 Starting Lovenett application...")
        print("📱 Application URL: http://localhost:5000")
        print("🔐 Login URL: http://localhost:5000/forms")
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        print("❌ Cannot start application due to database connection issues.")
        print("💡 Please check:")
        print("   1. MySQL server is running")
        print("   2. Database 'chat_app' exists")
        print("   3. MySQL user 'root' has correct permissions")
        print("   4. Password 'Lovenett123' is correct")
        