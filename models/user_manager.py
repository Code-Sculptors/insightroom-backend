import re
import hashlib
if __name__ == '__main__':
    from ..data.main import *
    from ..utils import ini_utils
else:
    from data.main import *
    from utils import ini_utils


class UserManager:
    '''Класс для работы с пользователями через БД'''
    def __init__(self):
        pass
    
    def hash_password(self, password: str) -> str:
        """Хеширование пароля"""
        # Используем простое хеширование для демонстрации
        # В реальном приложении используйте bcrypt или аналоги
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Проверка пароля"""
        return self.hash_password(password) == hashed_password
    
    def validate_username(self, username: str) -> tuple[bool, str]:
        """Валидация имени пользователя"""
        if len(username) < 3 or len(username) > 30:
            return False, "Имя пользователя должно быть от 3 до 30 символов"
        return True, "OK"
    
    def validate_password(self, password: str) -> tuple[bool, str]:
        """Валидация пароля"""
        if len(password) < 6:
            return False, "Пароль должен содержать минимум 6 символов"
        
        return True, "OK"
    
    def validate_email(self, email: str) -> tuple[bool, str]:
        """Валидация email"""
        # Простая проверка формата email
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            return False, "Некорректный формат email"
        
        # Проверка уникальности email
        for user in DataBase.get_all_users():
            if user.email == email:
                return False, "Email уже используется"
        
        return True, "OK"
    
    def validate_login(self, login: str) -> tuple[bool, str]:
        """Валидация логина"""
        login_regex = r'^[a-zA-Z0-9._%+-]'
        if not re.match(login_regex, login):
            return False, "Логин исользует запрещенные символы"
        
        for auth in DataBase.get_all_auth():
            if auth.login == login:
                return False, "Логин уже используется"
        return True, "OK"
    
    def register_user(self, username: str, email: str, password: str, login: str, phone: str) -> tuple[bool, (str | User)]:
        """Регистрация нового пользователя
        Args:
            username (str): имя пользователя
            email (str): почта пользователя
            password (str): пароль пользователя
            login (str): логин пользователя
        Returns:
            (True, User): в случае успеха
            (False, str): при провале"""
        # Валидация данных
        valid, message = self.validate_username(username)
        if not valid:
            return False, message
        
        valid, message = self.validate_email(email)
        if not valid:
            return False, message
        
        valid, message = self.validate_password(password)
        if not valid:
            return False, message
        
        valid, message = self.validate_login(login)
        if not valid:
            return False, message
        
        # Добавление пользователя
        try:
            new_auth = Auth(login=login, hash=self.hash_password(password))
            new_user = User(username=username, 
                            email=email,  
                            settings_file=f'user_{login}.ini', 
                            phone=phone)
            print(new_auth, new_user, sep='\n')
            user_id = DataBase.add_auth(new_auth)
            new_user.user_id = user_id
            print(new_user)
            DataBase.add_user(new_user)
            ini_utils.create_user_setting_file(f'user_{login}')
            return True, new_user
        except DataBaseException as ex:
            print(f'DataBaseException: `{ex}` in user_manager.register_user()')
            return False, "Ошибка при работе с БД"
        except Exception as ex:
            print(f'ERROR: `{ex}` in user_manager.register_user()')
            return False, "Непредвиденная ошибка"
    
    def authenticate_user(self, login: str, password: str) -> tuple[bool, User | str]:
        """Аутентификация пользователя
        Args:
            login (str): логин пользователя
            password (str): пароль пользователя
        Returns:
            (bool, User | str): успешна ли регистраци, в случае успеха - объект User, иначе информация об ошибке"""
        for auth in DataBase.get_all_auth():
            if auth.login == login:
                if not self.verify_password(password, auth.hash):
                    return False, "Неверный пароль"
                else:
                    try:
                        user = DataBase.get_user(auth.user_id)
                        return True, user
                    except DataBaseException as ex:
                        return False, "Ошибка при поиске пользователе в БД"
                    except Exception as ex:
                        print(f'ERROR: {ex} in user_manager.authenticate_user()')
                        return False, "Непредвиденная ошибка"
        return False, "Пользователь не найден"
    
    def get_user(user_id: int) -> User | None:
        '''Оболочка для DataBase.get_user'''
        try:
            return DataBase.get_user(user_id)
        except DataBaseException as ex:
            return None
        
    def get_user_by_phone(user_phone: str) -> User | None:
        '''Оболочка для DataBase.get_user_by_phone'''
        try:
            return DataBase.get_user_by_phone(user_phone)
        except DataBaseException as ex:
            return None
        
    def get_user_by_email(user_email: str) -> User | None:
        '''Оболочка для DataBase.get_user_by_email'''
        try:
            return DataBase.get_user_by_email(user_email)
        except DataBaseException as ex:
            return None
        

DataBase.setup_db_connection(dbname='my_pi_db', host='10.147.19.249', user='db_api_user', password='QpKwDx2bnFSNaSpm0J72Dfw0')

user_manager = UserManager()