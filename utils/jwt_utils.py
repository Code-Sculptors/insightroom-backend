import os
import jwt
from flask_jwt_extended import JWTManager
from flask import current_app
import time
import datetime

jwt_manager = JWTManager()
# Черный список токенов (в production используйте Redis или БД)
def load_blacklist() -> set:
    '''Загружает черный список токенов в множество'''
    with open(os.path.dirname(os.path.abspath(__file__)) + '/../data/blacklist.txt', mode='r', encoding='utf-8') as file:
        blacklisted_tokens = set(map(str.rstrip, file.readlines()))
    return blacklisted_tokens

def add_to_blacklist(token: str) -> None:
    '''Добавляет токен в черны список'''
    global blacklisted_tokens
    if token and token != 'None':
        with open(os.path.dirname(os.path.abspath(__file__)) + '/../data/blacklist.txt', mode='a', encoding='utf-8') as blacklist:
            blacklist.write(token + '\n')
    blacklisted_tokens = load_blacklist()
    # print(f"BlacklistedTokens: {blacklisted_tokens}")

blacklisted_tokens = load_blacklist()

@jwt_manager.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload) -> bool:
    """Проверка, находится ли токен в черном списке"""
    jti = jwt_payload["jti"]
    return jti in blacklisted_tokens

@jwt_manager.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload) -> tuple[dict, int]:
    """Обработчик истечения access token"""
    return {
        'error': 'access_token_expired',
        'message': 'Access token истек. Используйте refresh token для получения нового.'
    }, 401

@jwt_manager.invalid_token_loader
def invalid_token_callback(error) -> tuple[dict, int]:
    """Обработчик невалидного токена"""
    return {
        'error': 'invalid_token',
        'message': 'Токен невалиден.'
    }, 401

@jwt_manager.unauthorized_loader
def missing_token_callback(error):
    """Обработчик отсутствия токена"""
    print("Error", "нет токена")
    return {
        'error': 'authorization_required',
        'message': 'Требуется аутентификация.'
    }, 401

def is_token_expired(token) -> tuple[bool, dict]:
    """
    Проверяет, просрочен ли JWT токен
    
    Args:
        token (str): JWT токен
        secret_key (str): Секретный ключ для проверки подписи
    
    Returns:
        bool: True если токен просрочен, False если валиден
        dict: Дополнительная информация об ошибке (если есть)
    """
    try:
        # Декодируем токен без проверки срока действия
        payload = jwt_manager.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'], options={'verify_exp': False})
        print('payload = ', payload)
        # Проверяем срок действия вручную
        current_time = time.time()
        exp_timestamp = payload.get('exp')
        
        if exp_timestamp is None:
            return True, {'error': 'Токен не содержит срока действия'}
        
        if current_time > exp_timestamp:
            return True, {'expired_at': datetime.fromtimestamp(exp_timestamp).isoformat()}
        else:
            return False, {'expires_at': datetime.fromtimestamp(exp_timestamp).isoformat()}
            
    except jwt.ExpiredSignatureError:
        return True, {'error': 'Токен просрочен'}
    except jwt.InvalidTokenError as e:
        return True, {'error': f'Невалидный токен: {str(e)}'}
    except Exception as e:
        return True, {'error': f'Ошибка при проверке токена: {str(e)}'}
    
def cleanup_expired_tokens() -> int:
    '''Очищает черный список от просроченных токенов'''
    global blacklisted_tokens
    valid_list = []
    count_invalid_tokens = 0
    with open(os.path.dirname(os.path.abspath(__file__)) + '/../data/blacklist.txt', mode='r', encoding='utf-8') as file:
        while token := file.readline().rstrip():
            expired, _ = is_token_expired(token)
            if not expired:
                valid_list.append(token)
            else:
                count_invalid_tokens += 1
    if count_invalid_tokens != 0:
        with open(os.path.dirname(os.path.abspath(__file__)) + '/../data/blacklist.txt', mode='w', encoding='utf-8') as file:
            file.writelines(map(lambda x: x+'\n', valid_list))
        blacklisted_tokens = load_blacklist()
    return count_invalid_tokens