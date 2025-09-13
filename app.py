from flask import Flask, render_template
import subprocess
import signal
import os

app = Flask(__name__)

process = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_python')
def start_python():
    global process
    if process is None or process.poll() is not None:
        process = subprocess.Popen(['python', 'gesture_control.py'])
        return "Python script started!"
    else:
        return "Python script is already running."

@app.route('/stop_python')
def stop_python():
    global process
    if process is not None and process.poll() is None: 
        os.kill(process.pid, signal.SIGTERM)
        process = None
        return "Python script stopped!"
    else:
        return "Python script is not running."

if __name__ == '__main__':
    app.run(debug=True)