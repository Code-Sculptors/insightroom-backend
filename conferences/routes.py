import os
import json
import re
from datetime import datetime
from flask import render_template, request, jsonify
from . import conferences_bp
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.rooms_manager import rooms_manager
from data.main import DataBase

# === Логика чата (оставляем как было) ===
def get_last_date_from_file(file_path):
    if not os.path.exists(file_path): return None
    last_date = None
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('[') and line.endswith(']'):
                    last_date = line[1:-1]
    except: pass
    return last_date

def save_message_to_file(file_path, sender_name, message):
    try:
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        now = datetime.now()
        current_date_str = now.strftime("%d.%m.%Y")
        current_time_str = now.strftime("%H:%M")
        last_date = get_last_date_from_file(file_path)
        
        with open(file_path, 'a', encoding='utf-8') as f:
            if last_date != current_date_str:
                f.write(f'\n[{current_date_str}]\n')
            clean_message = message.replace('\\', '\\\\').replace('"', '\\"')
            line = f'{current_time_str} {sender_name}: "{clean_message}"\n'
            f.write(line)
    except Exception as e:
        print(f"Ошибка записи чата: {e}")

def load_chat_history(file_path):
    messages = []
    if not file_path or not os.path.exists(file_path): return messages
    current_date = None
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line: continue
                if line.startswith('[') and line.endswith(']'):
                    current_date = line[1:-1]
                    continue
                try:
                    time_part, rest = line.split(' ', 1)
                    if ':' in rest:
                        sender_part, content_part = rest.split(':', 1)
                        sender = sender_part.strip()
                        raw_text = content_part.strip()
                        if raw_text.startswith('"') and raw_text.endswith('"'):
                            text = raw_text[1:-1].replace('\\"', '"').replace('\\\\', '\\')
                            messages.append({'sender': sender, 'text': text, 'time': time_part, 'date': current_date})
                except ValueError: continue
    except Exception as e: print(f"Ошибка чтения чата: {e}")
    return messages

# === НОВАЯ ЛОГИКА: Доска (Whiteboard) ===
def save_whiteboard_data(file_path, elements_json):
    """Сохраняет состояние доски в JSON файл"""
    try:
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(json.dumps(elements_json))
    except Exception as e:
        print(f"Ошибка сохранения доски: {e}")

def load_whiteboard_data(file_path):
    """Загружает состояние доски"""
    if not file_path or not os.path.exists(file_path):
        return [] # Пустая доска
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = f.read()
            if not data: return []
            return json.loads(data)
    except Exception as e:
        print(f"Ошибка чтения доски: {e}")
        return []

@conferences_bp.route('/conference/<room_url>')
@jwt_required(optional=True)
def conference_room(room_url):
    try:
        user_id = get_jwt_identity()
        user_name = "Участник"
        room_name = f"Комната {room_url}"
        chat_history = []
        whiteboard_data = [] # Данные доски
        
        room_id = DataBase.get_room_id_by_url(room_url)
        if room_id:
            room = DataBase.get_room(room_id)
            room_info = DataBase.get_room_info(room_id)
            if room and room_info:
                # Чат
                chat_file_path = f"data/messages/{room.message_file}"
                chat_history = load_chat_history(chat_file_path)
                
                # Доска (сохраняем рядом с сообщениями, но с расширением .json)
                # Если message_file = "chat_123.txt", доска будет "chat_123_board.json"
                board_filename = room.message_file.replace('.txt', '_board.json')
                if not board_filename.endswith('.json'): board_filename += '_board.json'
                
                whiteboard_file_path = f"data/messages/{board_filename}"
                whiteboard_data = load_whiteboard_data(whiteboard_file_path)
                
                room_name = room_info.room_name

        if user_id:
            user = DataBase.get_user(user_id)
            user_name = user.username if user else "Участник"
            try: DataBase.add_user_and_room(user_id, room_id)
            except: pass
        
        return render_template('conference.html', 
                             room_url=room_url,
                             room_name=room_name,
                             user_name=user_name,
                             chat_history=chat_history,
                             whiteboard_data=whiteboard_data) # Передаем данные доски
                             
    except Exception as e:
        return f"Ошибка загрузки конференции: {str(e)}", 500

@conferences_bp.route('/api/validate-room/<room_url>')
def validate_room(room_url):
    try:
        return jsonify({'exists': True, 'room_url': room_url})
    except Exception as e:
        return jsonify({'exists': False, 'error': str(e)}), 500