from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Admin
import jwt
import datetime
import os

auth_bp = Blueprint('auth', __name__)

SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key')

@auth_bp.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    confirm_password = data.get('confirm_password')

    if not all([name, email, password, confirm_password]):
        return jsonify({'error': 'All fields are required'}), 400

    if password != confirm_password:
        return jsonify({'error': 'Passwords do not match'}), 400

    if len(password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters'}), 400

    if Admin.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 400

    hashed = generate_password_hash(password)
    admin = Admin(name=name, email=email, password_hash=hashed)
    db.session.add(admin)
    db.session.commit()

    return jsonify({'message': 'Account created successfully'}), 201

@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    admin = Admin.query.filter_by(email=email).first()
    if not admin or not check_password_hash(admin.password_hash, password):
        return jsonify({'error': 'Invalid email or password'}), 401

    token = jwt.encode({
        'admin_id': admin.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)  # long session
    }, SECRET_KEY, algorithm='HS256')

    return jsonify({'token': token, 'admin': {'id': admin.id, 'name': admin.name, 'email': admin.email}}), 200

@auth_bp.route('/api/forgot', methods=['POST'])
def forgot():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({'error': 'Email is required'}), 400

    # Always return success, regardless of existence
    reset_token = jwt.encode({
        'email': email,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }, SECRET_KEY, algorithm='HS256')

    return jsonify({'message': 'Reset link sent to your email', 'reset_token': reset_token}), 200