import os
import sys

def create_directory(path):
    """Create a directory if it doesn't exist at current path of this script."""
    path = os.path.join(os.path.dirname(__file__), path)
    os.makedirs(path, exist_ok=True)

def write_file(filepath, content):
    filepath = os.path.join(os.path.dirname(__file__), filepath)
    """Write content to a file, creating directories if needed."""
    directory = os.path.dirname(filepath)
    create_directory(directory)
    
    # Check if file exists
    if os.path.exists(filepath):
        print(f"Warning: File {filepath} already exists. Overwriting...")
    
    with open(filepath, 'w') as file:
        file.write(content)
    print(f"Created file: {filepath}")

def create_project_files():
    """Create all project files with their respective contents."""
    
    # Define file contents
    files = {
        "run.py": '''
from app import create_app, socketio

app = create_app()

if __name__ == '__main__':
    socketio.run(app, debug=True)
''',
        "app/__init__.py": '''
from flask import Flask
from flask_socketio import SocketIO
from config import Config

socketio = SocketIO()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    socketio.init_app(app)

    return app

from app import routes, events
''',
        "app/routes.py": '''
from flask import render_template, request, redirect, url_for, session
from app.main import bp
from app.utils import get_bot_stats, get_system_stats, start_bot, stop_bot, restart_bot, add_schedule
from config import Config

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
    return render_template('scheduler.html', bots=Config.BOTS, schedules={})  # You'll need to implement get_schedules()

@bp.route('/api/bot_stats/<bot_name>')
def api_bot_stats(bot_name):
    return get_bot_stats(bot_name)

@bp.route('/api/system_stats')
def api_system_stats():
    return get_system_stats()

@bp.route('/api/start_bot/<bot_name>')
def api_start_bot(bot_name):
    return start_bot(bot_name)

@bp.route('/api/stop_bot/<bot_name>')
def api_stop_bot(bot_name):
    return stop_bot(bot_name)

@bp.route('/api/restart_bot/<bot_name>')
def api_restart_bot(bot_name):
    return restart_bot(bot_name)

@bp.route('/api/add_schedule', methods=['POST'])
def api_add_schedule():
    data = request.json
    return add_schedule(data['bot_name'], data['schedule_type'], data['value'])
''',
        "app/events.py": '''
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
''',
        "app/utils.py": '''
import psutil
import random

def get_bot_stats(bot_name):
    # Placeholder: Replace with actual bot statistics gathering
    return {
        'status': random.choice(['online', 'offline']),
        'cpu': random.uniform(0, 100),
        'memory': random.uniform(0, 100),
        'uptime': random.randint(0, 86400)
    }

def get_system_stats():
    return {
        'cpu': psutil.cpu_percent(),
        'memory': psutil.virtual_memory().percent,
        'network_sent': psutil.net_io_counters().bytes_sent / 1024 / 1024,
        'network_recv': psutil.net_io_counters().bytes_recv / 1024 / 1024
    }

def start_bot(bot_name):
    # Placeholder: Replace with actual bot starting logic
    print(f"Starting bot: {bot_name}")
    return {'success': True}

def stop_bot(bot_name):
    # Placeholder: Replace with actual bot stopping logic
    print(f"Stopping bot: {bot_name}")
    return {'success': True}

def restart_bot(bot_name):
    # Placeholder: Replace with actual bot restarting logic
    print(f"Restarting bot: {bot_name}")
    return {'success': True}

def add_schedule(bot_name, schedule_type, value):
    # Placeholder: Replace with actual scheduling logic
    print(f"Adding schedule for {bot_name}: {schedule_type} - {value}")
    return {'success': True}
''',
        "config.py": '''
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    AUTH_TOKEN = os.environ.get('AUTH_TOKEN') or 'default-token'
    BOTS = ['bot1', 'bot2', 'bot3']  # Replace with your actual bot names
''',
        "app/main/__init__.py": '''
from flask import Blueprint

bp = Blueprint('main', __name__)

from app.main import routes
''',
        "app/main/routes.py": '''
# This file is intentionally left empty as the routes are defined in app/routes.py
''',
        "templates/base.html": '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Bot Management System{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='styles.css') }}">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <nav>
        <ul>
            <li><a href="{{ url_for('main.index') }}">Dashboard</a></li>
            <li><a href="{{ url_for('main.scheduler') }}">Scheduler</a></li>
            <li><a href="{{ url_for('main.logout') }}">Logout</a></li>
        </ul>
    </nav>
    <div class="container">
        {% block content %}{% endblock %}
    </div>
    {% block scripts %}{% endblock %}
</body>
</html>
''',
        "templates/dashboard.html": '''
{% extends "base.html" %}

{% block title %}Dashboard{% endblock %}

{% block content %}
    <h1>Bot Dashboard</h1>
    {% for bot_name in bots %}
        <div class="bot-card" id="bot-{{ bot_name }}">
            <h2>{{ bot_name }}</h2>
            <p>Status: <span id="status-{{ bot_name }}">Unknown</span></p>
            <p>CPU Usage: <span id="cpu-{{ bot_name }}">0</span>%</p>
            <p>Memory Usage: <span id="memory-{{ bot_name }}">0</span>%</p>
            <p>Uptime: <span id="uptime-{{ bot_name }}">0</span> seconds</p>
            <button onclick="startBot('{{ bot_name }}')">Start</button>
            <button onclick="stopBot('{{ bot_name }}')">Stop</button>
            <button onclick="restartBot('{{ bot_name }}')">Restart</button>
            <div class="stats">
                <canvas id="chart-{{ bot_name }}"></canvas>
            </div>
        </div>
    {% endfor %}
    <div class="system-stats">
        <h2>System Statistics</h2>
        <p>Network Sent: <span id="network-sent">0</span> MB</p>
        <p>Network Received: <span id="network-recv">0</span> MB</p>
        <div class="stats">
            <canvas id="chart-network"></canvas>
        </div>
    </div>
{% endblock %}

{% block scripts %}
<script>
    const socket = io();
    const charts = {};
    
    socket.on('connect', () => {
        console.log('Connected to server');
        {% for bot_name in bots %}
            socket.emit('request_update', { bot_name: '{{ bot_name }}' });
        {% endfor %}
    });

    socket.on('bot_update', (data) => {
        updateBotStats(data.bot_name, data.stats);
    });

    socket.on('system_update', (stats) => {
        updateSystemStats(stats);
    });

    function updateBotStats(botName, stats) {
        document.getElementById(`status-${botName}`).textContent = stats.status;
        document.getElementById(`cpu-${botName}`).textContent = stats.cpu.toFixed(2);
        document.getElementById(`memory-${botName}`).textContent = stats.memory.toFixed(2);
        document.getElementById(`uptime-${botName}`).textContent = stats.uptime;

        if (!charts[botName]) {
            const ctx = document.getElementById(`chart-${botName}`).getContext('2d');
            charts[botName] = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'CPU',
                        data: [],
                        borderColor: 'rgb(75, 192, 192)',
                        tension: 0.1
                    }, {
                        label: 'Memory',
                        data: [],
                        borderColor: 'rgb(255, 99, 132)',
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }

        const chart = charts[botName];
        chart.data.labels.push(new Date().toLocaleTimeString());
        chart.data.datasets[0].data.push(stats.cpu);
        chart.data.datasets[1].data.push(stats.memory);

        if (chart.data.labels.length > 60) {
            chart.data.labels.shift();
            chart.data.datasets[0].data.shift();
            chart.data.datasets[1].data.shift();
        }

        chart.update();
    }

    function updateSystemStats(stats) {
        document.getElementById('network-sent').textContent = stats.network_sent.toFixed(2);
        document.getElementById('network-recv').textContent = stats.network_recv.toFixed(2);

        if (!charts.network) {
            const ctx = document.getElementById('chart-network').getContext('2d');
            charts.network = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Sent',
                        data: [],
                        borderColor: 'rgb(75, 192, 192)',
                        tension: 0.1
                    }, {
                        label: 'Received',
                        data: [],
                        borderColor: 'rgb(255, 99, 132)',
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }

        const chart = charts.network;
        chart.data.labels.push(new Date().toLocaleTimeString());
        chart.data.datasets[0].data.push(stats.network_sent);
        chart.data.datasets[1].data.push(stats.network_recv);

        if (chart.data.labels.length > 60) {
            chart.data.labels.shift();
            chart.data.datasets[0].data.shift();
            chart.data.datasets[1].data.shift();
        }

        chart.update();
    }

    function startBot(botName) {
        fetch(`/api/start_bot/${botName}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    console.log(`Started bot ${botName}`);
                } else {
                    console.error(`Failed to start bot ${botName}`);
                }
            });
    }

    function stopBot(botName) {
        fetch(`/api/stop_bot/${botName}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    console.log(`Stopped bot ${botName}`);
                } else {
                    console.error(`Failed to stop bot ${botName}`);
                }
            });
    }

    function restartBot(botName) {
        fetch(`/api/restart_bot/${botName}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    console.log(`Restarted bot ${botName}`);
                } else {
                    console.error(`Failed to restart bot ${botName}`);
                }
            });
    }
</script>
{% endblock %}
''',
        "templates/login.html": '''
{% extends "base.html" %}

{% block title %}Login{% endblock %}

{% block content %}
    <h1>Login</h1>
    <form method="POST">
        <label for="token">Auth Token:</label>
        <input type="password" id="token" name="token" required>
        <button type="submit">Login</button>
    </form>
{% endblock %}
''',
        "templates/scheduler.html": '''
{% extends "base.html" %}

{% block title %}Scheduler{% endblock %}

{% block content %}
    <h1>Bot Scheduler</h1>
    <form id="schedule-form">
        <label for="bot-select">Select Bot:</label>
        <select id="bot-select" required>
            {% for bot_name in bots %}
                <option value="{{ bot_name }}">{{ bot_name }}</option>
            {% endfor %}
        </select>

        <label for="schedule-type">Schedule Type:</label>
        <select id="schedule-type" required>
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
            <option value="interval">Interval (hours)</option>
        </select>

        <label for="schedule-value">Value:</label>
        <input type="text" id="schedule-value" required>

        <button type="submit">Add Schedule</button>
    </form>

    <h2>Current Schedules</h2>
    <ul id="schedule-list">
        {% for bot_name, schedule in schedules.items() %}
            <li>{{ bot_name }}: {{ schedule }}</li>
        {% endfor %}
    </ul>
{% endblock %}

{% block scripts %}
<script>
    document.getElementById('schedule-form').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const botName = document.getElementById('bot-select').value;
        const scheduleType = document.getElementById('schedule-type').value;
        const scheduleValue = document.getElementById('schedule-value').value;

        fetch('/api/add_schedule', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                bot_name: botName,
                schedule_type: scheduleType,
                value: scheduleValue
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Schedule added successfully');
                location.reload();
            } else {
                alert('Failed to add schedule');
            }
        });
    });
</script>
{% endblock %}
''',
        "static/styles.css": '''
body {
    font-family: Arial, sans-serif;
    line-height: 1.6;
    margin: 0;
    padding: 0;
}

.container {
    width: 80%;
    margin: auto;
    overflow: hidden;
    padding: 0 20px;
}

nav {
    background: #333;
    color: #fff;
    padding: 10px 0;
}

nav ul {
    padding: 0;
    list-style: none;
}

nav li {
    display: inline;
    padding: 0 20px;
}

nav a {
    color: #fff;
    text-decoration: none;
}

.bot-card {
    background: #f4f4f4;
    padding: 20px;
    margin-bottom: 20px;
    border-radius: 5px;
}

.bot-card h2 {
    margin-top: 0;
}

.bot-card button {
    margin-right: 10px;
}

.stats {
    margin-top: 20px;
}

canvas {
    max-width: 100%;
    height: 200px;
}

form {
    background: #f4f4f4;
    padding: 20px;
    margin-bottom: 20px;
}

form label {
    display: block;
    margin-bottom: 5px;
}

form input, form select {
    width: 100%;
    padding: 8px;
    margin-bottom: 10px;
}

form button {
    display: block;
    width: 100%;
    padding: 10px;
    background: #333;
    color: #fff;
    border: none;
    cursor: pointer;
}

form button:hover {
    background: #555;
}
''',
        "requirements.txt": '''
Flask==2.0.1
Flask-SocketIO==5.1.1
python-dotenv==0.19.0
psutil==5.8.0
APScheduler==3.7.0
''',
        "config/.env.example": '''
SECRET_KEY=your-secret-key
AUTH_TOKEN=your-auth-token
''',
        "app/templates/base.html": '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Bot Management System{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='styles.css') }}">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <nav>
        <ul>
            <li><a href="{{ url_for('main.index') }}">Dashboard</a></li>
            <li><a href="{{ url_for('main.scheduler') }}">Scheduler</a></li>
            <li><a href="{{ url_for('main.logout') }}">Logout</a></li>
        </ul>
    </nav>
    <div class="container">
        {% block content %}{% endblock %}
    </div>
    {% block scripts %}{% endblock %}
</body>
</html>
''',
        "app/templates/dashboard.html": '''
{% extends "base.html" %}

{% block title %}Dashboard{% endblock %}

{% block content %}
    <h1>Bot Dashboard</h1>
    {% for bot_name in bots %}
        <div class="bot-card" id="bot-{{ bot_name }}">
            <h2>{{ bot_name }}</h2>
            <p>Status: <span id="status-{{ bot_name }}">Unknown</span></p>
            <p>CPU Usage: <span id="cpu-{{ bot_name }}">0</span>%</p>
            <p>Memory Usage: <span id="memory-{{ bot_name }}">0</span>%</p>
            <p>Uptime: <span id="uptime-{{ bot_name }}">0</span> seconds</p>
            <button onclick="startBot('{{ bot_name }}')">Start</button>
            <button onclick="stopBot('{{ bot_name }}')">Stop</button>
            <button onclick="restartBot('{{ bot_name }}')">Restart</button>
            <div class="stats">
                <canvas id="chart-{{ bot_name }}"></canvas>
            </div>
        </div>
    {% endfor %}
    <div class="system-stats">
        <h2>System Statistics</h2>
        <p>Network Sent: <span id="network-sent">0</span> MB</p>
        <p>Network Received: <span id="network-recv">0</span> MB</p>
        <div class="stats">
            <canvas id="chart-network"></canvas>
        </div>
    </div>
{% endblock %}

{% block scripts %}
<script>
    // ... (keep the JavaScript code)
</script>
{% endblock %}
''',
        "app/templates/login.html": '''
{% extends "base.html" %}

{% block title %}Login{% endblock %}

{% block content %}
    <h1>Login</h1>
    <form method="POST">
        <label for="token">Auth Token:</label>
        <input type="password" id="token" name="token" required>
        <button type="submit">Login</button>
    </form>
{% endblock %}
''',
        "app/templates/scheduler.html": '''
{% extends "base.html" %}

{% block title %}Scheduler{% endblock %}

{% block content %}
    <h1>Bot Scheduler</h1>
    <form id="schedule-form">
        <label for="bot-select">Select Bot:</label>
        <select id="bot-select" required>
            {% for bot_name in bots %}
                <option value="{{ bot_name }}">{{ bot_name }}</option>
            {% endfor %}
        </select>

        <label for="schedule-type">Schedule Type:</label>
        <select id="schedule-type" required>
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
            <option value="interval">Interval (hours)</option>
        </select>

        <label for="schedule-value">Value:</label>
        <input type="text" id="schedule-value" required>

        <button type="submit">Add Schedule</button>
    </form>

    <h2>Current Schedules</h2>
    <ul id="schedule-list">
        {% for bot_name, schedule in schedules.items() %}
            <li>{{ bot_name }}: {{ schedule }}</li>
        {% endfor %}
    </ul>
{% endblock %}

{% block scripts %}
<script>
    // ... (keep the JavaScript code)
</script>
{% endblock %}
'''
    }

    for filepath, content in files.items():
        write_file(filepath, content.strip())

    print("All files have been created successfully.")

if __name__ == "__main__":
    create_project_files()