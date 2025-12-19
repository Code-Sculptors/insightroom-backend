from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import request
import logging
from datetime import datetime
from .routes import save_message_to_file, save_whiteboard_data, DataBase # Импортируем новую функцию

socketio = None
active_connections = {}

def init_socketio(socketio_instance):
    global socketio
    socketio = socketio_instance
    register_handlers()

def register_handlers():
    @socketio.on('connect')
    def handle_connect():
        logging.info(f"Клиент подключился: {request.sid}")

    @socketio.on('disconnect')
    def handle_disconnect():
        for room_url, users in list(active_connections.items()):
            if request.sid in users:
                user_info = users.pop(request.sid)
                emit('user-left', {
                    'userId': request.sid,
                    'userName': user_info.get('name', 'Участник')
                }, room=room_url, include_self=False)
                if not users: active_connections.pop(room_url, None)
                break

    @socketio.on('join-room')
    def handle_join_room(data):
        room_url = data.get('roomUrl')
        user_name = data.get('userName', 'Участник')
        if not room_url: return
        
        join_room(room_url)
        if room_url not in active_connections: active_connections[room_url] = {}
        active_connections[room_url][request.sid] = {'name': user_name, 'id': request.sid, 'room_url': room_url}
        
        users_in_room = list(active_connections[room_url].values())
        emit('room-users', {'users': users_in_room, 'yourId': request.sid}, room=request.sid)
        emit('user-joined', {'userId': request.sid, 'userName': user_name}, room=room_url, include_self=False)

    @socketio.on('toggle-whiteboard')
    def handle_whiteboard(data):
        emit('whiteboard-updated', {'state': data.get('state')}, room=data.get('roomUrl'))

    # === НОВОЕ: Обработка рисования ===
    @socketio.on('whiteboard-draw')
    def handle_whiteboard_draw(data):
        room_url = data.get('roomUrl')
        elements = data.get('elements')
        
        if room_url and elements:
            # 1. Сохраняем на сервере
            try:
                room_id = DataBase.get_room_id_by_url(room_url)
                room = DataBase.get_room(room_id)
                if room:
                    board_filename = room.message_file.replace('.txt', '_board.json')
                    if not board_filename.endswith('.json'): board_filename += '_board.json'
                    path = f"data/messages/{board_filename}"
                    save_whiteboard_data(path, elements)
            except Exception as e:
                logging.error(f"Error saving board: {e}")

            # 2. Рассылаем всем, КРОМЕ отправителя
            # (отправитель уже видит свои изменения)
            emit('whiteboard-draw-update', {
                'elements': elements
            }, room=room_url, include_self=False)

    @socketio.on('toggle-media')
    def handle_media_toggle(data):
        emit('media-toggled', {'userId': request.sid, 'type': data.get('type'), 'enabled': data.get('enabled')}, room=data.get('roomUrl'), include_self=False)

    @socketio.on('webrtc-offer')
    def handle_webrtc_offer(data):
        emit('webrtc-offer', {'offer': data.get('offer'), 'from': request.sid}, room=data.get('to'))

    @socketio.on('webrtc-answer')
    def handle_webrtc_answer(data):
        emit('webrtc-answer', {'answer': data.get('answer'), 'from': request.sid}, room=data.get('to'))

    @socketio.on('ice-candidate')
    def handle_ice_candidate(data):
        emit('ice-candidate', {'candidate': data.get('candidate'), 'from': request.sid}, room=data.get('to'))

    @socketio.on('chat-message')
    def handle_chat_message(data):
        room_url = data.get('roomUrl')
        text = data.get('text')
        sender_name = "Участник"
        if room_url in active_connections and request.sid in active_connections[room_url]:
            sender_name = active_connections[room_url][request.sid]['name']
        
        if room_url and text:
            try:
                room_id = DataBase.get_room_id_by_url(room_url)
                room = DataBase.get_room(room_id)
                chat_file_path = f'data/messages/{room.message_file}'
                save_message_to_file(chat_file_path, sender_name, text)
            except: pass

            now = datetime.now()
            emit('new-chat-message', {
                'sender': sender_name, 'text': text, 'userId': request.sid,
                'time': now.strftime("%H:%M"), 'date': now.strftime("%d.%m.%Y")
            }, room=room_url, include_self=False)