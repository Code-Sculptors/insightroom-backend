import time
from datetime import datetime
if __name__ == '__main__':
    from ..data.main import *
    from ..utils import ini_utils
else:
    from data.main import *
    from utils import ini_utils

import hashlib

def generate_room_url_deterministic(room_id, room_name, prefix="ir"):
    """
    Генерирует уникальный URL для комнаты без случайной соли
    """
    # Данные для хэширования
    data = f"{room_id}:{room_name}:{int(time.time())}"
    
    # Создаем SHA256 хэш
    hash_object = hashlib.sha256(data.encode())
    hash_hex = hash_object.hexdigest()
    
    # Берем первые 8 символов хэша
    url_part = hash_hex[:8]
    
    # Создаем простую контрольную сумму
    checksum = hashlib.md5(url_part.encode()).hexdigest()[:2]
    
    # Формируем окончательный URL
    room_url = f"{prefix}-{url_part}-{checksum}"
    
    return room_url

def validate_room_url(url, room_id, room_name, prefix="ir"):
    """
    Проверяет, соответствует ли URL данной комнате
    """
    # Генерируем ожидаемый URL
    expected_url = generate_room_url_deterministic(room_id, room_name, prefix)
    
    # Сравниваем
    return url == expected_url

def check_activation_status(activation_time):
    target_time = datetime.fromisoformat(activation_time)
    return "Активно" if target_time <= datetime.now() else "Запланировано"

class Rooms_manager():
    def __init__(self):
        pass

    def create_room(self, user_id: int, room_name: str, description: str, activation_time: str | int) -> str:
        """Функция для создания комнаты и всего, что с ней связано
        Args:
            user_id (int): ID создателя комнаты,
            room_name (str): Название комнаты, 
            description (str): Описание комнаты, 
            activation_time (str): Время активации ["now" | timestamp], 
        Returns:
            URL (str): Ссылка на комнату"""
        if activation_time == 'now':
            activation_time = int(datetime.timestamp(datetime.now()))

        url = generate_room_url_deterministic(user_id, room_name)

        new_room = Room(activation_time=activation_time,
                        message_file=ini_utils.create_message_file(url),
                        settings_file=ini_utils.create_room_setting_file(url))
        new_room.room_id = DataBase.add_room(new_room)

        room_info = RoomInfo(room_id=new_room.room_id,
                             description=description,
                             room_name=room_name,
                             room_url=url)
        DataBase.add_room_info(room_info)

        DataBase.add_user_and_room(user_id, new_room.room_id)

        user_role = UserRole(new_room.room_id, user_id, 'Creator')
        DataBase.add_user_role(user_role)

        return url

    def get_user_rooms(self, user_id: int) -> list[dict]:
        rooms : list[dict] = DataBase.get_all_rooms_for_user(user_id)
        answer = []
        for room in rooms:
            temp = {
                'id': room['room_info']['room_url'],
                'title': room['room_info']['room_name'],
                'description': room['room_info']['description'],
                'status': check_activation_status(room['activation_time']),
                'date': room['activation_time'].split('T')[0],
                'time': room['activation_time'].split('T')[1][:-3]
            }
            answer.append(temp)
        return answer
    
    def get_created_rooms(self, user_id: int) -> list[dict]:
        rooms : list[dict] = DataBase.get_created_rooms_for_user(user_id)
        answer = []
        for room in rooms:
            temp = {
                'id': room['room_info']['room_url'],
                'title': room['room_info']['room_name'],
                'description': room['room_info']['description'],
                'status': check_activation_status(room['activation_time']),
                'date': room['activation_time'].split('T')[0],
                'time': room['activation_time'].split('T')[1][:-3]
            }
            answer.append(temp)
        return answer

    def refactor_room(self, room_id: int, room_name: str, description: str, activation_time: str | int):
        updated_room = Room(room_id=room_id, activation_time=activation_time)
        updated_room_info = RoomInfo(room_id=room_id, description=description, room_name=room_name)
        DataBase.update_room(updated_room)
        DataBase.update_room_info(updated_room_info)
        print(updated_room, updated_room_info)

    def get_room_id_by_url(self, room_url: str) -> int | None:
        return DataBase.get_room_id_by_url(room_url)
rooms_manager = Rooms_manager()