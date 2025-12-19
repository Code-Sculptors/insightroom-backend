from flask import render_template, request, jsonify
from . import conferences_bp
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.rooms_manager import rooms_manager
from data.main import DataBase

@conferences_bp.route('/conference/<room_url>')
@jwt_required(optional=True)
def conference_room(room_url):
    try:
        user_id = get_jwt_identity()
        user_name = "Участник"
        
        if user_id:
            user = DataBase.get_user(user_id)
            user_name = user.username if user else "Участник"
        
        return render_template('conference.html', 
                             room_url=room_url, 
                             user_name=user_name)
                             
    except Exception as e:
        return f"Ошибка загрузки конференции: {str(e)}", 500

@conferences_bp.route('/api/validate-room/<room_url>')
def validate_room(room_url):
    try:
        return jsonify({
            'exists': True,
            'room_url': room_url
        })
    except Exception as e:
        return jsonify({
            'exists': False,
            'error': str(e)
        }), 500