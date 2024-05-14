from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import threading
import time
import random
from faker import Faker
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
fake = Faker()

generator_thread = None

def generate_transaction():
    while True:
        transaction = {
            "user_id": fake.random_int(min=1, max=10000),
            "product_id": fake.random_int(min=1, max=1000),
            "amount": round(random.uniform(5.0, 500.0), 2),
            "timestamp": str(fake.date_time_this_year())
        }
        socketio.emit('newdata', {'data': json.dumps(transaction)}, namespace='/test')
        time.sleep(random.uniform(0.1, 0.5))
        if threading.current_thread().stopped():
            break

class StoppableThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('start_generate', namespace='/test')
def start_generate(message):
    global generator_thread
    if generator_thread is None or not generator_thread.is_alive():
        generator_thread = StoppableThread(target=generate_transaction)
        generator_thread.start()
    emit('response', {'data': 'Started Generating'})

@socketio.on('stop_generate', namespace='/test')
def stop_generate(message):
    global generator_thread
    if generator_thread is not None:
        generator_thread.stop()
    emit('response', {'data': 'Stopped Generating'})

if __name__ == '__main__':
    socketio.run(app, debug=True)
