from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from extensions import login_manager
from models.user import User, Admin
from database import db, get_id

auth_bp = Blueprint('auth', __name__)

@login_manager.user_loader
def load_user(user_id):
    if user_id.startswith('admin_'):
        admin_id = int(user_id.replace('admin_', ''))
        admin = next((a for a in db['admins'] if a['id'] == admin_id), None)
        if admin:
            return Admin(id=admin['id'], username=admin['username'])
    else:
        uid = int(user_id)
        user = next((u for u in db['users'] if u['id'] == uid), None)
        if user:
            return User(id=user['id'], name=user['name'], email=user['email'], phone=user['phone'])
    return None

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    phone = data.get('phone')
    
    if not all([name, email, password]):
        return jsonify({'success': False, 'message': 'Missing fields'}), 400

    if any(u['email'] == email for u in db['users']):
        return jsonify({'success': False, 'message': 'Email already registered'}), 400
        
    hashed_password = generate_password_hash(password)
    new_user = {
        'id': get_id('users'),
        'name': name,
        'email': email,
        'password': hashed_password,
        'phone': phone
    }
    db['users'].append(new_user)
    
    return jsonify({'success': True, 'message': 'Registration successful'})

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'success': False, 'message': 'Missing credentials'}), 400

    admin = next((a for a in db['admins'] if a['username'] == email), None)
    if admin and (admin['password'] == password or check_password_hash(admin['password'], password)):
        user_obj = Admin(id=admin['id'], username=admin['username'])
        login_user(user_obj)
        return jsonify({'success': True, 'role': 'admin', 'redirect_url': '/admin/dashboard.html'})
    
    user = next((u for u in db['users'] if u['email'] == email), None)
    if user and check_password_hash(user['password'], password):
        user_obj = User(id=user['id'], name=user['name'], email=user['email'], phone=user['phone'])
        login_user(user_obj)
        return jsonify({'success': True, 'role': 'user', 'redirect_url': '/user/dashboard.html'})
        
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@auth_bp.route('/logout', methods=['POST', 'GET'])
@login_required
def logout():
    logout_user()
    return jsonify({'success': True})

@auth_bp.route('/me', methods=['GET'])
@login_required
def get_me():
    return jsonify({
        'success': True,
        'user': {
            'name': getattr(current_user, 'name', getattr(current_user, 'username', 'Unknown')),
            'email': getattr(current_user, 'email', getattr(current_user, 'username', '')),
            'role': current_user.role
        }
    })
