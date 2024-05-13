from flask import Flask, render_template
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

def generate_transaction():
    while True:
        transaction = {
            "user_id": fake.unique.random_int(min=1, max=1000),
            "product_id": fake.unique.random_int(min=1, max=100),
            "amount": round(random.uniform(5.0, 500.0), 2),
            "timestamp": str(fake.date_time_this_year())
        }
        socketio.emit('newdata', {'data': json.dumps(transaction)}, namespace='/test')
        time.sleep(random.uniform(0.5, 2.0))

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect', namespace='/test')
def test_connect():
    app.logger.info("Client connected")

if __name__ == '__main__':
    threading.Thread(target=generate_transaction).start()
    socketio.run(app, debug=True)
