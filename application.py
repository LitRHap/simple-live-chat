import os
from flask import Flask, session, render_template, request, redirect, url_for, flash, Markup, jsonify
from flask_session import Session
from flask_socketio import SocketIO, emit



app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
Session(app)
socketio = SocketIO(app)

messages = []

# Configure session to use filesystem. Hamel: BOILERPLATE.
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

users = []

@app.route("/", methods=["POST", "GET"])
def index():

    #if a session already exists, just go to the 
    if 'display_name' in session:
        return redirect(url_for('chat'))
    # check if display name already exists before dropping into chat.
    if request.method == "POST":
        display_name = request.form.get("displayname")
        if display_name in users:
            flash(Markup(f'<p>Name <span style="font-weight:bold">{display_name}</span> already exists.  Please choose another name.</p>'))
        else:
            users.append(display_name)
            session['display_name'] = display_name
            return redirect(url_for('chat'))

    return render_template('index.html')


@app.route("/chat", methods=["GET"])
def chat():
    if 'display_name' not in session:
        flash('You must set a display name first!')
        return redirect(url_for('index'))    
    name = session['display_name']
    return render_template('chat.html', displayname=name)

@app.route("/logout")
def logout():
    session.pop('display_name', None)
    return redirect(url_for('index'))

@socketio.on("message")
def message(data):
    # keep the messages around!
    messages.append(data)
    emit("get-message", data, broadcast=True)

@socketio.on("page-loaded")
def page_loaded(data):
    # keep the messages around!
    if not messages:
        pass
    else:
        for message in messages[:50]:
            emit("get-message", message)

@app.route("/api")
def api():
    return jsonify(messages)

@app.route("/clear-data")
def clear_data():
    messages = []
    socketio.emit("burn", broadcast=True)
    return 'Data cleared from cache!'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=os.getenv('PORT'))