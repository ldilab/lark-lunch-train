import ast
import json
import os
from datetime import datetime, timedelta
from os.path import join, dirname

import pytz
from apscheduler.executors.pool import ProcessPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask import request
from flask_apscheduler import APScheduler
from flask_httpauth import HTTPBasicAuth

from src import rail
from src.keyword import detect
from src.lark.api.client import LarkClient
from src.lark.message.templates import ONBOARD_MESSAGE, CANCEL_MESSAGE
from src.lark.utils.decrypt import AESCipher
from src.train import Train, Passenger

# Set your desired timezone
desired_timezone = "Asia/Seoul"  # Change this to your desired timezone
local_tz = pytz.timezone(desired_timezone)
utc_tz = pytz.timezone("UTC")
# Set a default timezone (e.g., New York)

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
OPEN_ID = os.getenv("OPEN_ID")

POLL_TIME_AFTER_SECONDS = int(os.getenv("POLL_TIME_AFTER_SECONDS"))
REMINDER_TIME_BEFORE_MINUTES = int(os.getenv("REMINDER_TIME_BEFORE_MINUTES"))
CLEAR_TIME_AFTER_MINUTES = int(os.getenv("CLEAR_TIME_AFTER_MINUTES"))

message_api_client = LarkClient(app_id=APP_ID, app_secret=APP_SECRET, lark_host=LARK_HOST, logger=app.logger)


@app.context_processor
def inject_timezone():
    return {'datetime': datetime.now(local_tz)}


@scheduler.task('interval', id='check jobs', minutes=15)
def my_job():
    app.logger.error("Checking jobs")
    for job in scheduler.get_jobs():
        app.logger.error(job)


@app.route("/", methods=['POST'])
def main():
    dict_data = json.loads(request.data)
    encrypt_target = dict_data.get("encrypt")
    cipher = AESCipher(ENCRYPT_KEY)
    challenge = cipher.decrypt_string(encrypt_target)
    response = ast.literal_eval(challenge)
    app.logger.error(response)
    event = response.get("event", {})
    sender = event.get("sender", {})
    sender_id = sender.get("sender_id", {}).get("open_id", "")
    sender_name = message_api_client.get_user_info(sender_id).get("name", "")

    message = event.get("message", {})
    content_str = message.get("content", "")

    if content_str:
        content_dict = ast.literal_eval(content_str)
        keyword = detect(content_dict["text"])
        app.logger.error(f"Keyword: {keyword}")
        if len(keyword) == 2:
            _place, _time = keyword
            app.logger.error(f"Place: {_place}, Time: {_time}")
            return issue_train(_place, _time, Passenger(sender_id, sender_name))
        else:
            message_api_client.send_text_with_open_id(
                sender_id,
                message=keyword
            )
    app.logger.error("others")

    return jsonify(response)


def issue_train(p, t, issuer: Passenger):
    if rail.is_rail_full():
        message_api_client.send_text_with_open_id(
            issuer.open_id,
            message=f"There is a train already running. "
                    f"(Train: [to] {rail.train.destination} [at] {rail.train.launch_time.strftime('%H:%M')})"
        )
        return "Too many trains running", 400
    t_dt = datetime.strptime(t, '%H:%M')
    now_dt = datetime.now(tz=local_tz)
    launch_time_dt = local_tz.localize(datetime(now_dt.year, now_dt.month, now_dt.day, t_dt.hour, t_dt.minute))

    poll_time_dt = now_dt + timedelta(seconds=POLL_TIME_AFTER_SECONDS)
    reminder_time_dt = launch_time_dt - timedelta(minutes=REMINDER_TIME_BEFORE_MINUTES)
    clear_time_dt = launch_time_dt + timedelta(minutes=CLEAR_TIME_AFTER_MINUTES)

    launch_time = launch_time_dt.strftime('%H:%M')
    poll_time = poll_time_dt.strftime('%H:%M')
    reminder_time = reminder_time_dt.strftime('%H:%M')
    clear_time = clear_time_dt.strftime('%H:%M')

    destination = p

    train = Train(
        poll_time, launch_time, reminder_time, clear_time, GROUP_ID, destination, app.logger, message_api_client,
        issuer
    )
    rail.launch_train(train)
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

    return "Train issued", 200


@app.route("/card", methods=['POST'])
def update_passenger():
    dict_data = json.loads(request.data)
    app.logger.error(dict_data)
    if dict_data.get("challenge"):
        return jsonify({
            "challenge": dict_data.get("challenge")
        })

    app.logger.error(dict_data)
    user_id = request.json['open_id']
    action = request.json['action'].get('value', {}).get("state", "")
    user_info = message_api_client.get_user_info(user_id)
    name = user_info.get('name', "")
    user = Passenger(user_id, name)
    app.logger.error(f"User: {user.user_name}, user_id: {user.open_id}, action: {action}")

    msg_ids = rail.train.msg_ids.values()

    if action in ["on", "off"]:
        updated_status = rail.train.update_passengers(action=action, passenger=user)
        if not updated_status and action == "on":
            message_api_client.send_text_with_open_id(
                user.open_id,
                message="You are already on the train"
            )
            return "Invalid action", 400
        elif not updated_status and action == "off":
            message_api_client.send_text_with_open_id(
                user.open_id,
                message="You are not on the train"
            )
            return "Invalid action", 400

        msg = ONBOARD_MESSAGE(
            issuer=rail.train.issuer.user_name,
            place=rail.train.destination,
            time=rail.train.launch_time.strftime('%H:%M'),
            user_names=[passenger.user_name for passenger in rail.train.passengers], is_str=False
        )

    elif action == "cancel":
        if user.open_id != rail.train.issuer.open_id:
            message_api_client.send_text_with_open_id(
                user.open_id,
                message="Only the issuer can cancel the train"
            )
            return "Invalid action", 400

        msg = CANCEL_MESSAGE(
            place=rail.train.destination,
            time=rail.train.launch_time.strftime('%H:%M'),
            is_str=False
        )
        rail.train.clear_train()
    else:
        return "Invalid action", 400

    app.logger.error(msg)

    responses = message_api_client.bulk_update_message(
        msg_ids,
        json.dumps(msg)
    )
    app.logger.error(responses)

    return jsonify(msg)


scheduler.init_app(app)
scheduler.start()

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))

    app.run(debug=True, host='0.0.0.0', port=port)
