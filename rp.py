from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from functools import wraps
import os
import psutil
import subprocess
import socket

app = Flask(__name__)
app.secret_key = '841wd485f49wfw41'  # Változtasd meg ezt egy biztonságos, véletlenszerű karakterlánccá

# Példa felhasználók (valódi alkalmazásban használj adatbázist és helyes jelszókezelést)
users = {
    "admin": "szabee",
    "user": "2011",
    "szabee": "2011"  # Hozzáadott új felhasználó
}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print(f"Session ellenőrzése: {session}")  # Debug print
        if 'username' not in session:
            print("Felhasználó nincs bejelentkezve, átirányítás a login oldalra")  # Debug print
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    print("Login függvény meghívva")  # Debug print
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(f"Bejelentkezési kísérlet: username={username}, password={password}")  # Debug print
        if username in users and users[username] == password:
            session['username'] = username
            print(f"Sikeres bejelentkezés: {username}")  # Debug print
            print("Átirányítás az indexre")  # Debug print
            return redirect(url_for('index'))
        else:
            error = 'Érvénytelen felhasználónév vagy jelszó'
            print(f"Sikertelen bejelentkezés: {username}")  # Debug print
    return render_template('login.html', error=error)

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    hostname = socket.gethostname()  # Ez platformfüggetlen
    username = session['username']
    return render_template('index.html', hostname=hostname, username=username)

@app.route('/system_info')
@login_required
def system_info():
    cpu_percent = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    return jsonify({
        'cpu': cpu_percent,
        'memory': {
            'total': memory.total,
            'available': memory.available,
            'percent': memory.percent
        },
        'disk': {
            'total': disk.total,
            'used': disk.used,
            'free': disk.free,
            'percent': disk.percent
        }
    })

@app.route('/execute_command', methods=['POST'])
@login_required
def execute_command():
    command = request.form['command']
    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
        return jsonify({'output': output})
    except subprocess.CalledProcessError as e:
        return jsonify({'error': str(e.output)})

@app.route('/storage_info')
@login_required
def storage_info():
    partitions = psutil.disk_partitions()
    disks = []
    for partition in partitions:
        usage = psutil.disk_usage(partition.mountpoint)
        disks.append({
            'device': partition.device,
            'mountpoint': partition.mountpoint,
            'fstype': partition.fstype,
            'total': usage.total,
            'used': usage.used,
            'free': usage.free,
            'percent': usage.percent
        })
    return jsonify(disks)

@app.route('/directory_contents')
@login_required
def directory_contents():
    path = request.args.get('path', '/')
    contents = []
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        is_dir = os.path.isdir(item_path)
        size = os.path.getsize(item_path) if not is_dir else 0
        contents.append({
            'name': item,
            'path': item_path,
            'is_dir': is_dir,
            'size': size
        })
    return jsonify(contents)

@app.route('/file_content')
@login_required
def file_content():
    path = request.args.get('path')
    try:
        with open(path, 'r') as file:
            content = file.read()
        return jsonify({'content': content})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.after_request
def after_request(response):
    print(f"Session tartalma: {session}")  # Debug print
    return response

@app.errorhandler(Exception)
def handle_exception(e):
    print(f"Hiba történt: {str(e)}")  # Ez kiírja a hibát a szerver konzoljára
    return "Hiba történt a szerveren", 500

if __name__ == '__main__':
    app.run(debug=True)