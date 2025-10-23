from flask import Blueprint, request, jsonify, Response, redirect
from flask_jwt_extended import (
    create_access_token, create_refresh_token, 
    jwt_required, get_jwt_identity, get_jwt,
    set_access_cookies, set_refresh_cookies, unset_jwt_cookies
)
from utils.jwt_utils import add_to_blacklist
from models import user_manager
import time
import os

auth_bp = Blueprint('auth', __name__, template_folder=os.path.dirname(os.path.abspath(__file__)) + '/../../insightroom-frontend/pages')

@auth_bp.route('/register', methods=['POST'])
def register() -> Response:
    """Регистрация нового пользователя"""
    try:
        data = request.json
        
        # Проверяем обязательные поля
        required_fields = ['username', 'email', 'password', 'login', 'tel']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Поле {field} обязательно'}), 400
        
        username = data['username']
        email = data['email']
        password = data['password']
        login = data['login']
        phone_number = data['tel']
        print(username, email, password, login, phone_number)
        # Регистрируем пользователя
        ans = user_manager.user_manager.register_user(username, email, password, login, phone_number)

        success, result = ans
        if success and result is str:
            user_data = result
            access_token = create_access_token(
                identity=user_data.user_id,
                additional_claims={
                    'verified': user_data.verified
                }
            )
            refresh_token = create_refresh_token(identity=user_data.user_id)
            print(f"REG: {login}", access_token, refresh_token, sep='\n')

            response = redirect('/')
            set_access_cookies(response, access_token)
            set_refresh_cookies(response, refresh_token)
            return response
        else:
            return jsonify({'error': result}), 401
            
    except Exception as e:
        print(f'ERROR: `{e}` in /register')
        return jsonify({'error': f'Ошибка сервера: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login() -> Response:
    """Аутентификация пользователя"""
    try:
        login = request.json.get('login', None)
        email = request.json.get('email', None)
        phone = request.json.get('phone', None)
        password = request.json.get('password', None)
        print(login, email, phone, password)

        if not (login or email or phone) or not password:
            return jsonify({'error': 'Логин и пароль обязательны'}), 400
        
        if email:
            user = user_manager.user_manager.get_user_by_email(email)
            login = user_manager.user_manager.get_auth(user.user_id).login
        elif phone:
            user = user_manager.user_manager.get_user_by_phone(phone)
            login = user_manager.user_manager.get_auth(user.user_id).login

        success, result = user_manager.user_manager.authenticate_user(login, password)
        if success:
            user_data = result
            access_token = create_access_token(
                identity=str(user_data.user_id)
            )
            refresh_token = create_refresh_token(identity=str(user_data.user_id))
            print(f"LOG IN: {login}", access_token, refresh_token, sep='\n')

            response = jsonify({
                'message': 'Login successful',
                'access_expires_in': 900,  
                'refresh_expires_in': 604800
            })
            set_access_cookies(response, access_token)
            set_refresh_cookies(response, refresh_token)
            return response
        else:
            print(result)
            return jsonify({'error': result}), 401
            
    except Exception as e:
        print(f'ERROR {e} in /login POST')
        return jsonify({'error': f'Ошибка сервера: {str(e)}'}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh() -> Response:
    """Обновление access token"""
    current_user = get_jwt_identity()
    new_access_token = create_access_token(
        identity=current_user,
        additional_claims={'verified': user_manager.user_manager.get_user(current_user).verified}
    )
    response = jsonify({'msg': 'Token refreshed'})
    set_access_cookies(response, new_access_token)
    return response

@auth_bp.route('/protected-data')
@jwt_required()
def protected_data() -> Response:
    """Защищенные данные"""
    current_user = get_jwt_identity()
    print("!!!!!!!!!!", current_user)
    return jsonify({
        'message': 'Это защищенные данные!',
        'user': current_user,
        'data': ['Секретная информация 1', 'Секретная информация 2']
    })

@auth_bp.route('/logout', methods=['POST'])
def logout() -> Response:
    """Выход из системы"""
    access_token = request.cookies.get('access_token_cookie')
    refresh_token = request.cookies.get('refresh_token_cookie')
    print(access_token, refresh_token, sep='\n')
    add_to_blacklist(access_token)
    add_to_blacklist(refresh_token)
    response = jsonify({'message': 'Logged out successfully'})
    unset_jwt_cookies(response)
    return response