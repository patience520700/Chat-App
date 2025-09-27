from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from functools import wraps
from sqlalchemy import text

# Application Configuration
app = Flask(__name__)
app.secret_key = '935ac244f2b1c36b990a0569c8cfd6d8d7ad33e5feec29f40b04442aa031c489'

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
    password_hash = db.Column(db.String(255), nullable=False)
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
        """Hash and set the password"""
        if password:
            self.password_hash = generate_password_hash(password)
            print(f"DEBUG: Password hash created for {self.username}")
        else:
            raise ValueError("Password cannot be empty")

    def check_password(self, password):
        """Check if the password is correct"""
        if not self.password_hash or not password:
            print("DEBUG: No password hash or no password provided")
            return False
        
        result = check_password_hash(self.password_hash, password)
        print(f"DEBUG: Password check for {self.username} - Result: {result}")
        return result

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
            db.session.execute(text('SELECT 1'))
            print("✅ Database connection successful!")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def check_database_schema():
    """Check if database schema matches models"""
    try:
        with app.app_context():
            users_count = User.query.count()
            print(f"✅ Users table accessible. Records: {users_count}")
            
            if users_count > 0:
                test_user = User.query.first()
                print(f"✅ User model test: {test_user.username}")
            
            return True
    except Exception as e:
        print(f"❌ Database schema issue: {e}")
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

@app.route('/register', methods=['POST'])
def register():
    """User registration with enhanced validation and debugging"""
    if request.method == 'POST':
        try:
            print("=== REGISTRATION STARTED ===")
            print(f"Form data received: {dict(request.form)}")
            
            # Get form data with defaults
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm-password', '')
            gender = request.form.get('gender', '')
            country = request.form.get('country', '')
            phone = request.form.get('phone', '').strip()
            birthdate_str = request.form.get('birthdate', '')
            
            print(f"Username: {username}, Email: {email}, Password length: {len(password)}")
            
            # Basic validation
            if not all([username, email, password, confirm_password]):
                flash('Please fill in all required fields.', 'danger')
                print("Missing required fields")
                return redirect(url_for('forms'))
            
            if password != confirm_password:
                flash('Passwords do not match.', 'danger')
                print("Passwords don't match")
                return redirect(url_for('forms'))
            
            # Check for existing user
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash('An account with this email already exists.', 'danger')
                print("Email already exists")
                return redirect(url_for('forms'))
            
            existing_username = User.query.filter_by(username=username).first()
            if existing_username:
                flash('This username is already taken.', 'danger')
                print("Username already taken")
                return redirect(url_for('forms'))
            
            # Create new user
            new_user = User(
                username=username,
                email=email,
                gender=gender,
                country=country,
                phone=phone,
                profile_picture=f'https://ui-avatars.com/api/?name={username}&background=0062cc&color=fff&size=128'
            )
            
            # Handle birthdate
            if birthdate_str:
                try:
                    birthdate = datetime.strptime(birthdate_str, '%Y-%m-%d')
                    new_user.birthdate = birthdate
                except ValueError:
                    print("Invalid birthdate format")
            
            # Set password
            new_user.set_password(password)
            print("Password hashed successfully")
            
            # Save to database
            db.session.add(new_user)
            db.session.commit()
            print(f"User created successfully with ID: {new_user.id}")
            
            # Auto-login after registration
            session['user_id'] = new_user.id
            session['username'] = new_user.username
            session['email'] = new_user.email
            
            flash('Account created successfully! Welcome to Lovenett!', 'success')
            print("Registration successful, redirecting to chat")
            return redirect(url_for('chat'))
            
        except Exception as e:
            db.session.rollback()
            print(f"REGISTRATION ERROR: {str(e)}")
            flash('Registration failed due to a system error. Please try again.', 'danger')
            return redirect(url_for('forms'))

@app.route('/login', methods=['POST'])
def login():
    """User login with enhanced debugging"""
    if request.method == 'POST':
        try:
            print("=== LOGIN ATTEMPT ===")
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            
            print(f"Login attempt - Email: {email}, Password length: {len(password)}")
            
            if not email or not password:
                flash('Please enter both email and password.', 'danger')
                print("Missing email or password")
                return redirect(url_for('forms'))
            
            user = User.query.filter_by(email=email).first()
            
            if user:
                print(f"User found: {user.username}")
                print(f"Stored password hash: {user.password_hash[:50]}...")
                
                # Debug password check
                password_match = user.check_password(password)
                print(f"Password match: {password_match}")
                
                if password_match:
                    session['user_id'] = user.id
                    session['username'] = user.username
                    session['email'] = user.email
                    
                    print(f"Login successful for user: {user.username}")
                    flash(f'Welcome back, {user.username}!', 'success')
                    return redirect(url_for('chat'))
                else:
                    print("Password incorrect")
            else:
                print("User not found")
            
            flash('Invalid email or password. Please try again.', 'danger')
            return redirect(url_for('forms'))
            
        except Exception as e:
            print(f"LOGIN ERROR: {str(e)}")
            flash('Login failed due to a system error. Please try again.', 'danger')
            return redirect(url_for('forms'))

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('forms'))

@app.route('/debug/users')
def debug_users():
    """Debug route to see all users in database"""
    users = User.query.all()
    result = "<h1>Users in Database:</h1><ul>"
    for user in users:
        result += f"""
        <li>
            <strong>ID:</strong> {user.id}<br>
            <strong>Username:</strong> {user.username}<br>
            <strong>Email:</strong> {user.email}<br>
            <strong>Password Hash:</strong> {user.password_hash[:50]}...<br>
            <strong>Created:</strong> {user.created_at}<br>
            <hr>
        </li>
        """
    result += "</ul>"
    return result

@app.route('/test/password')
def test_password():
    """Test password hashing"""
    test_password = "test123"
    user = User()
    user.set_password(test_password)
    
    return f"""
    <h1>Password Test</h1>
    <p>Original: {test_password}</p>
    <p>Hashed: {user.password_hash}</p>
    <p>Check correct: {user.check_password(test_password)}</p>
    <p>Check wrong: {user.check_password('wrong')}</p>
    """

@app.route('/test-users')
def test_users():
    """Test route to check registered users"""
    users = User.query.all()
    result = []
    for user in users:
        result.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'created_at': user.created_at
        })
    return jsonify(result)

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
        user.username = request.form.get('username', user.username)
        user.bio = request.form.get('bio', user.bio)
        user.interests = request.form.get('interests', user.interests)
        user.country = request.form.get('country', user.country)
        
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
    user = User.query.get(session['user_id'])
    return render_template('chat.html', user=user)

# =============================================================================
# REAL-TIME CHAT ROUTES
# =============================================================================

@app.route('/api/chat/messages/<int:partner_id>')
@login_required
def api_chat_messages(partner_id):
    """API: Get messages for real-time chat interface"""
    user_id = session['user_id']
    
    partner = User.query.get(partner_id)
    if not partner:
        return jsonify({'error': 'User not found'}), 404
    
    messages = Message.query.filter(
        ((Message.sender_id == user_id) & (Message.receiver_id == partner_id)) |
        ((Message.sender_id == partner_id) & (Message.receiver_id == user_id))
    ).order_by(Message.timestamp.asc()).all()
    
    for msg in messages:
        if msg.receiver_id == user_id and not msg.read:
            msg.read = True
    
    db.session.commit()
    
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
        
        last_message = Message.query.filter(
            ((Message.sender_id == user_id) & (Message.receiver_id == partner_id)) |
            ((Message.sender_id == partner_id) & (Message.receiver_id == user_id))
        ).order_by(Message.timestamp.desc()).first()
        
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
    
    sent_messages = Message.query.filter_by(sender_id=user_id).order_by(Message.timestamp.desc()).all()
    received_messages = Message.query.filter_by(receiver_id=user_id).order_by(Message.timestamp.desc()).all()
    
    all_messages = sorted(
        sent_messages + received_messages, 
        key=lambda x: x.timestamp, 
        reverse=True
    )
    
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

@app.route('/admin/db-info')
def admin_db_info():
    """Comprehensive database information"""
    try:
        with app.app_context():
            # Get table counts
            users_count = User.query.count()
            messages_count = Message.query.count()
            profile_views_count = ProfileView.query.count()
            
            # Get recent users
            recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
            
            result = f"""
            <h1>Database Information</h1>
            <p><strong>Users:</strong> {users_count}</p>
            <p><strong>Messages:</strong> {messages_count}</p>
            <p><strong>Profile Views:</strong> {profile_views_count}</p>
            
            <h2>Recent Users</h2>
            <ul>
            """
            
            for user in recent_users:
                result += f"""
                <li>
                    ID: {user.id} | 
                    Username: {user.username} | 
                    Email: {user.email} | 
                    Created: {user.created_at}
                </li>
                """
            
            result += "</ul>"
            return result
            
    except Exception as e:
        return f"<p>Error: {e}</p>"

@app.route('/admin/user/<int:user_id>')
def admin_user_detail(user_id):
    """View detailed user information"""
    user = User.query.get(user_id)
    if not user:
        return f"<p>User {user_id} not found</p>"
    
    return f"""
    <h1>User Details: {user.username}</h1>
    <p><strong>ID:</strong> {user.id}</p>
    <p><strong>Username:</strong> {user.username}</p>
    <p><strong>Email:</strong> {user.email}</p>
    <p><strong>Gender:</strong> {user.gender}</p>
    <p><strong>Country:</strong> {user.country}</p>
    <p><strong>Phone:</strong> {user.phone}</p>
    <p><strong>Birthdate:</strong> {user.birthdate}</p>
    <p><strong>Created:</strong> {user.created_at}</p>
    <p><strong>Password Hash:</strong> {user.password_hash[:50]}...</p>
    """

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

@app.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='images/favicon.jpg'))

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
    
    # Test database connection and schema
    if test_database_connection() and check_database_schema():
        print("🚀 Starting Lovenett application...")
        print("📱 Application URL: http://localhost:5000")
        print("🔐 Login URL: http://localhost:5000/forms")
        print("💾 Database: Connected successfully")
        
        # Display sample users for testing
        with app.app_context():
            users = User.query.all()
            if users:
                print(f"👥 Registered users: {len(users)}")
                for user in users[:3]:
                    print(f"   - {user.username} ({user.email})")
        
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        print("❌ Cannot start application due to database issues.")