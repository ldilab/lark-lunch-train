import os
import time
from datetime import datetime, timedelta
from os.path import join, dirname

import flask
import requests
from dotenv import load_dotenv
from flask import Flask
from flask import request
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash, generate_password_hash

from flask_apscheduler import APScheduler

from src.train import Train, Running, Passenger

app = Flask(__name__)
scheduler = APScheduler()
auth = HTTPBasicAuth()

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
GROUP_ID = os.environ.get("GROUP_ID")

running = []
jobs = []


@app.route("/", methods=['POST'])
def main():
    challenge = request.args.get('CHALLENGE')
    for k, v in request.json.items():
        app.logger.debug(f"{k}: {v}")

    if challenge:
        return challenge
    else:
        return "Hello World"


@app.route("/train", methods=['GET', 'POST'])
def issue_train():
    if len(running) > 5:
        return "Too many trains running", 400

    launch_time_dt = datetime.strptime(request.json['launch_time'], '%H:%M')
    poll_time_dt = datetime.now() + timedelta(minutes=1)
    reminder_time_dt = launch_time_dt - timedelta(minutes=5)
    clear_time_dt = launch_time_dt + timedelta(minutes=30)

    launch_time = launch_time_dt.strftime('%H:%M')
    poll_time = poll_time_dt.strftime('%H:%M')
    reminder_time = reminder_time_dt.strftime('%H:%M')
    clear_time = clear_time_dt.strftime('%H:%M')

    destination = request.json['destination']

    train = Train(launch_time, poll_time, reminder_time, clear_time, GROUP_ID, destination)
    running.append(train)
    job = scheduler.add_job(
        id=f"{len(running)}_poll_start",
        func=train.onboarding_notification,
        trigger='cron',
        hour=poll_time_dt.hour,
        minute=poll_time_dt.minute,
    )

    scheduler.add_job(
        id=f"{len(running)}_reminder",
        func=train.reminder_notification,
        trigger='cron',
        hour=reminder_time_dt.hour,
        minute=reminder_time_dt.minute,
    )
    scheduler.add_job(
        id=f"{len(running)}_clear",
        func=train.clear_train,
        trigger='cron',
        hour=clear_time_dt.hour,
        minute=clear_time_dt.minute,
    )


@app.route("/passenger", methods=['GET', 'POST', 'DELETE'])
def update_passenger():
    user_id = request.json['user_id']
    if request.method == 'POST':
        running.train.update_passenger(Passenger(user_id))
    elif request.method == 'DELETE':
        running.train.remove_passenger(Passenger(user_id))


scheduler.init_app(app)
scheduler.start()

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))

    app.run(debug=True, host='0.0.0.0', port=port)
