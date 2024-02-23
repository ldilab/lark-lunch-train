import ast
import json
import os
import time
from datetime import datetime, timedelta
from os.path import join, dirname
from typing import Tuple

import flask
import pytz
import requests
import tzlocal
from apscheduler.executors.pool import ProcessPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask import request
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash, generate_password_hash

from flask_apscheduler import APScheduler

from src import running
from src.keyword import detect
from src.train import Train, Running, Passenger
from src.utils.api import MessageApiClient
from src.utils.decrypt import AESCipher
from src.utils.event import EventManager, UrlVerificationEvent, MessageReceiveEvent


# Set your desired timezone
desired_timezone = "Asia/Seoul"  # Change this to your desired timezone
local_tz = pytz.timezone(desired_timezone)
utc_tz = pytz.timezone("UTC")
# Set a default timezone (e.g., New York)
tz = tzlocal.get_localzone()

app = Flask(__name__)

executors = {
    'default': {'type': 'threadpool', 'max_workers': 20},
    'processpool': ProcessPoolExecutor(max_workers=5)
}
job_defaults = {
    'coalesce': False,
    'max_instances': 3
}
scheduler = APScheduler(
    scheduler=BackgroundScheduler(executors=executors, job_defaults=job_defaults, timezone=desired_timezone),
    app=app
)

auth = HTTPBasicAuth()

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
GROUP_ID = os.getenv("GROUP_ID")



# load from env
APP_ID = os.getenv("APP_ID")
APP_SECRET = os.getenv("APP_SECRET")
VERIFICATION_TOKEN = os.getenv("VERIFICATION_TOKEN")
ENCRYPT_KEY = os.getenv("ENCRYPT_KEY")
LARK_HOST = os.getenv("LARK_HOST")


@app.context_processor
def inject_timezone():
    return {'datetime': datetime.now(local_tz)}


@app.route("/", methods=['POST'])
def main():
    dict_data = json.loads(request.data)
    encrypt_target = dict_data.get("encrypt")
    cipher = AESCipher(ENCRYPT_KEY)
    challenge = cipher.decrypt_string(encrypt_target)
    response = ast.literal_eval(challenge)
    event = response.get("event", {})
    message = event.get("message", {})
    content_str = message.get("content", "")

    if content_str:
        content_dict = ast.literal_eval(content_str)
        keyword = detect(content_dict["text"])
        app.logger.error(f"Keyword: {keyword}")
        if keyword:
            _place, _time = keyword
            app.logger.error(f"Place: {_place}, Time: {_time}")
            return issue_train(_place, _time)
    app.logger.error("others")

    return jsonify(response)


def issue_train(p, t):
    if len(running) > 0:
        return "Too many trains running", 400
    t_dt = datetime.strptime(t, '%H:%M')
    now_dt = datetime.now(tz=local_tz)
    launch_time_dt = datetime(now_dt.year, now_dt.month, now_dt.day, t_dt.hour, t_dt.minute, tzinfo=local_tz)

    poll_time_dt = now_dt + timedelta(seconds=10)
    reminder_time_dt = launch_time_dt - timedelta(minutes=1)
    clear_time_dt = launch_time_dt + timedelta(minutes=1)

    launch_time = launch_time_dt.strftime('%H:%M')
    poll_time = poll_time_dt.strftime('%H:%M')
    reminder_time = reminder_time_dt.strftime('%H:%M')
    clear_time = clear_time_dt.strftime('%H:%M')

    destination = p

    train = Train(launch_time, poll_time, reminder_time, clear_time, GROUP_ID, destination)
    train.logger = app.logger
    scheduler.add_job(
        id=f"poll_start",
        func=train.onboarding_notification,
        trigger='date',
        run_date=poll_time_dt,
    )
    app.logger.error("poll time: " + str(poll_time_dt))
    scheduler.add_job(
        id=f"reminder",
        func=train.reminder_notification,
        trigger='date',
        run_date=reminder_time_dt,
    )
    app.logger.error("reminder time: " + str(reminder_time_dt))
    scheduler.add_job(
        id=f"clear",
        func=train.clear_train,
        trigger='date',
        run_date=clear_time_dt,
    )
    app.logger.error("clear time: " + str(clear_time_dt))

    for job in scheduler.get_jobs():
        app.logger.error(job)
        app.logger.error(job.next_run_time)

    return "Train issued", 200


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
