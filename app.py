import os
import time
from os.path import join, dirname

import flask
import requests
from dotenv import load_dotenv
from flask import Flask
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash, generate_password_hash

from flask_apscheduler import APScheduler

from src.train import Train, Running, Passenger

app = Flask(__name__)
scheduler = APScheduler()
auth = HTTPBasicAuth()

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

lunch_train = Train('11:30', '11:50', '14:00', 'lunch')
dinner_train = Train('17:00', '17:20', '20:00', 'dinner')
running = Running(lunch_train)


@scheduler.task('cron', id='poll_lunch_train',
                hour=lunch_train.poll_time.hour,
                minute=lunch_train.poll_time.minute)
def poll_lunch_train():
    lunch_train.onboarding_notification()


@scheduler.task('cron', id='remind_lunch_train',
                hour=lunch_train.poll_time.hour,
                minute=lunch_train.poll_time.minute)
def poll_lunch_train():
    lunch_train.onboarding_notification()

@scheduler.task('cron', id='launch_lunch_train',
                hour=lunch_train.launch_time.hour,
                minute=lunch_train.launch_time.minute)
def launch_lunch_train():
    lunch_train.launch_notification()


@scheduler.task('cron', id='clear_lunch_train',
                hour=lunch_train.clear_time.hour,
                minute=lunch_train.clear_time.minute)
def clear_lunch_train():
    lunch_train.clear_train()
    running.train = dinner_train




@app.route("/poll", methods=['GET', 'POST'])
def issue_poll(request):
    launch_time = time.strptime(request.json['launch_time'], '%H:%M')
    destination = request.json['destination']
    clear_time = launch_time + 30

    running.train.launch_time = launch_time
    running.train.clear_time = clear_time
    running.train.destination = destination
    running.train.onboarding_notification()


@app.route("/passenger", methods=['GET', 'POST', 'DELETE'])
def update_passenger(request):
    user_id = request.json['user_id']
    if request.method == 'POST':
        running.train.update_passenger(Passenger(user_id))
    elif request.method == 'DELETE':
        running.train.remove_passenger(Passenger(user_id))
    else:
        return json


scheduler.init_app(app)
scheduler.start()

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))

    app.run(debug=True, host='0.0.0.0', port=port)
