from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Dictionary to store user data (email and associated name)
users = {
    'levi@gmail.com': 'Levi',
    'eve@gmail.com': 'Eve'
}

# List to store active users
active_users = []


@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))

    user_email = session['user']
    user_name = users.get(user_email, user_email.split('@')[0])  # Use email as name if not found
    return render_template('index.html', notes=session['notes'], logged_in_user=user_name, active_users=active_users)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        if email in users:
            session['user'] = email
            session['login_time'] = datetime.now()  # Store login time in session
            session['notes'] = ""
            active_users.append(email)
            return redirect(url_for('index'))
        else:
            error_message = 'Invalid email. Please try again.'

    return render_template('login.html', error_message=error_message if 'error_message' in locals() else None)


@app.route('/logout')
def logout():
    email = session.pop('user', None)
    session.pop('login_time', None)  # Remove login time from session on logout
    session.pop('notes', None)
    if email in active_users:
        active_users.remove(email)
    return redirect(url_for('login'))


@app.route('/delete', methods=['POST'])
def delete_notes():
    session['notes'] = ""
    emit('update_notes', {'notes': session['notes']}, broadcast=True)
    return redirect(url_for('index'))


@socketio.on('update_notes_request')
def handle_update_notes(data):
    session['notes'] = data['notes']
    emit('update_notes', {'notes': session['notes']}, broadcast=True)


@socketio.on('connect')
def handle_connect():
    if 'user' in session:
        email = session['user']
        if email not in active_users:
            active_users.append(email)
        emit_active_users()


@socketio.on('disconnect')
def handle_disconnect():
    if 'user' in session:
        email = session['user']
        if email in active_users:
            active_users.remove(email)
        emit_active_users()


def emit_active_users():
    socketio.emit('active_users_update', {'active_users': active_users}, broadcast=True)


if __name__ == '__main__':
    socketio.run(app, debug=True)
