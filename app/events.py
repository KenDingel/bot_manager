from flask_socketio import emit
from app import socketio
from app.utils import get_bot_stats, get_system_stats

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('request_update')
def handle_request_update(data):
    bot_name = data['bot_name']
    bot_stats = get_bot_stats(bot_name)
    system_stats = get_system_stats()
    emit('bot_update', {'bot_name': bot_name, 'stats': bot_stats})
    emit('system_update', system_stats)