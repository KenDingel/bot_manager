from flask import render_template, request, redirect, url_for, session, jsonify
from app.main import bp
from app.utils import (
    get_bot_stats, get_system_stats, start_bot, stop_bot, restart_bot, 
    add_schedule, delete_schedule, get_schedules
)
from config import Config

# Web routes
@bp.route('/')
def index():
    if 'authenticated' not in session:
        return redirect(url_for('main.login'))
    return render_template('dashboard.html', bots=Config.BOTS)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['token'] == Config.AUTH_TOKEN:
            session['authenticated'] = True
            return redirect(url_for('main.index'))
        else:
            return "Invalid token", 401
    return render_template('login.html')

@bp.route('/logout')
def logout():
    session.pop('authenticated', None)
    return redirect(url_for('main.login'))

@bp.route('/scheduler')
def scheduler():
    if 'authenticated' not in session:
        return redirect(url_for('main.login'))
    schedules = get_schedules()
    return render_template('scheduler.html', bots=Config.BOTS, schedules=schedules)

# API routes
@bp.route('/api/bot_stats/<bot_name>')
def api_bot_stats(bot_name):
    if 'authenticated' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    try:
        return jsonify(get_bot_stats(bot_name))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/api/system_stats')
def api_system_stats():
    if 'authenticated' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    try:
        return jsonify(get_system_stats())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/api/start_bot/<bot_name>')
def api_start_bot(bot_name):
    if 'authenticated' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    try:
        result = start_bot(bot_name)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/api/stop_bot/<bot_name>')
def api_stop_bot(bot_name):
    if 'authenticated' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    try:
        result = stop_bot(bot_name)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/api/restart_bot/<bot_name>')
def api_restart_bot(bot_name):
    if 'authenticated' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    try:
        result = restart_bot(bot_name)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/api/add_schedule', methods=['POST'])
def api_add_schedule():
    if 'authenticated' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    try:
        data = request.json
        result = add_schedule(data['bot_name'], data['schedule_type'], data['value'])
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/api/delete_schedule/<bot_name>', methods=['DELETE'])
def api_delete_schedule(bot_name):
    if 'authenticated' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    try:
        result = delete_schedule(bot_name)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/api/schedules')
def api_get_schedules():
    if 'authenticated' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    try:
        schedules = get_schedules()
        return jsonify(schedules)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Error handlers
@bp.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@bp.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500