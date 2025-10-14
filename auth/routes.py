from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token, 
    jwt_required, get_jwt_identity, get_jwt
)
from utils.jwt_utils import add_to_blacklist
from models.user_manager import user_manager
import time
import os

auth_bp = Blueprint('auth', __name__, template_folder=os.path.dirname(os.path.abspath(__file__)) + '/../../insightroom-frontend/pages')

@auth_bp.route('/register', methods=['POST'])
def register():
    """Регистрация нового пользователя"""
    try:
        data = request.json
        
        # Проверяем обязательные поля
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Поле {field} обязательно'}), 400
        
        username = data['username']
        email = data['email']
        password = data['password']
        
        # Регистрируем пользователя
        success, message = user_manager.register_user(username, email, password)
        
        if success:
            return jsonify({
                'message': message,
                'user': {
                    'username': username,
                    'email': email
                }
            }), 201
        else:
            return jsonify({'error': message}), 400
            
    except Exception as e:
        return jsonify({'error': f'Ошибка сервера: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Аутентификация пользователя"""
    try:
        username = request.json.get('username')
        password = request.json.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Логин и пароль обязательны'}), 400
        
        # Аутентифицируем пользователя
        success, result = user_manager.authenticate_user(username, password)
        
        if success:
            user_data = result
            access_token = create_access_token(
                identity=username,
                additional_claims={'role': user_data['role']}
            )
            refresh_token = create_refresh_token(identity=username)
            print("LOG IN", access_token, refresh_token, sep='\n')
            return jsonify({
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': {
                    'username': username,
                    'email': user_data['email'],
                    'role': user_data['role']
                },
                'access_expires_in': 900,
                'refresh_expires_in': 604800
            }), 200
        else:
            return jsonify({'error': result}), 401
            
    except Exception as e:
        return jsonify({'error': f'Ошибка сервера: {str(e)}'}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Обновление access token"""
    current_user = get_jwt_identity()
    new_access_token = create_access_token(
        identity=current_user,
        additional_claims={'role': user_manager.get_user(current_user)['role']}
    )
    
    return jsonify({
        'access_token': new_access_token,
        'access_expires_in': 900
    })

@auth_bp.route('/protected-data')
@jwt_required()
def protected_data():
    """Защищенные данные"""
    current_user = get_jwt_identity()
    print("!!!!!!!!!!", current_user)
    return jsonify({
        'message': 'Это защищенные данные!',
        'user': current_user,
        'data': ['Секретная информация 1', 'Секретная информация 2']
    })

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Выход из системы"""
    access_token = request.headers.get('Authorization', '').replace('Bearer ', '')
    refresh_token = request.get_json().get('refresh_token')
    print(access_token, refresh_token, sep='\n')
    add_to_blacklist(access_token)
    add_to_blacklist(refresh_token)
    return jsonify({'message': 'Успешный выход'})

@auth_bp.route('/admin/users', methods=['GET'])
@jwt_required()
def get_all_users():
    """Получение списка всех пользователей (только для админа)"""
    try:
        # Проверяем права администратора
        current_user = get_jwt_identity()
        user_data = user_manager.get_user(current_user)
        
        if not user_data or user_data.get('role') != 'admin':
            return jsonify({'error': 'Требуются права администратора'}), 403
        
        users = user_manager.get_all_users()
        return jsonify({'users': users}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500