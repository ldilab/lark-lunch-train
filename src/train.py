import datetime
import os
from dataclasses import dataclass
from datetime import time
from typing import List, Union

from src import running
from src.messages import ONBOARD_MESSAGE
from src.utils.api import MessageApiClient


@dataclass
class Passenger:
    open_id: str = None
    user_name: str = None


OPEN_ID = os.getenv("OPEN_ID")


class Train:
    def __init__(self, poll_time: str, launch_time: str, reminder_time: str, clear_time: str, train_id: str,
                 destination: str, logger, message_client: MessageApiClient, issuer: Passenger):
        self.logger = logger
        self.message_api_client = message_client
        self.poll_time: time = datetime.datetime.strptime(poll_time, '%H:%M').time()
        self.launch_time: time = datetime.datetime.strptime(launch_time, '%H:%M').time()
        self.reminder_time: time = datetime.datetime.strptime(reminder_time, '%H:%M').time()
        self.clear_time: time = datetime.datetime.strptime(clear_time, '%H:%M').time()
        self.train_id: str = train_id
        self.passengers: List[Passenger] = []
        self.destination: str = destination
        self.init_poll_published = False
        self.issuer = issuer
        self.msg_ids = {}

    def update_launch_time(self, poll_time: str) -> None:
        self.launch_time = datetime.datetime.strptime(poll_time, '%H:%M').time()

    def update_poll_time(self, poll_time: str) -> None:
        self.poll_time = datetime.datetime.strptime(poll_time, '%H:%M').time()

    def update_clear_time(self, poll_time: str) -> None:
        self.clear_time = datetime.datetime.strptime(poll_time, '%H:%M').time()

    def update_destination(self, destination: str) -> None:
        self.destination = destination

    def onboarding_notification(self) -> None:
        """
        This method will be called to issue the initial poll to group members
        :return:
        """
        self.init_poll_published = True
        msg = ONBOARD_MESSAGE(
            issuer=self.issuer.user_name,
            place=self.destination,
            time=self.launch_time.strftime('%H:%M'),
            user_names=[passenger.user_name for passenger in self.passengers], is_str=True
        )
        self.logger.error(msg)
        user_ids = self.message_api_client.get_department_users(str(os.getenv("DEPARTMENT_ID")))
        for user_id in user_ids:
            response = self.message_api_client.send(
                receive_id_type="open_id",
                receive_id=user_id,
                msg_type="interactive",
                content=msg
            )
            self.logger.error(response)
            msg_id = response.get("data", {}).get("message_id", "")
            self.logger.error("Msg id: " + msg_id)
            self.msg_ids[user_id] = msg_id

    def update_passenger(self, passenger: Passenger) -> None:
        """
        This method will be called to update the passengers list
        :return:
        """
        if passenger.open_id not in [p.open_id for p in self.passengers]:
            self.passengers.append(passenger)
            self.logger.error(f"Passenger {passenger.user_name} added to train {self.train_id}")
        else:
            self.logger.error(f"Passenger {passenger.user_name} already in train {self.train_id}")

    def remove_passenger(self, passenger: Passenger) -> None:
        """
        This method will be called to remove the passenger from the list
        :return:
        """
        if passenger.open_id in [p.open_id for p in self.passengers]:
            self.passengers.remove(passenger)
            self.logger.error(f"Passenger {passenger.user_name} removed from train {self.train_id}")
        else:
            self.logger.error(f"Passenger {passenger.user_name} not in train {self.train_id}")

    def boarded_notification(self) -> None:
        """
        This method will be called when new passenger boards the train to notify the group members
        :return:
        """
        raise NotImplementedError

    def reminder_notification(self) -> None:
        """
        This method will be called to remind the group members about the train
        :return:
        """
        msg = f"(REMIND) Train {self.train_id} to {self.destination} will be launched at {self.launch_time}"
        self.logger.error(f"Reminder: {msg}")
        for passenger in self.passengers:
            self.message_api_client.buzz_message(
                self.msg_ids.get(passenger.open_id, ""),
                [passenger.open_id]
            )

    def launch_notification(self) -> None:
        """
        This method will be called when the train reaches the launch time to notify the group members
        :return:
        """
        msg = f"(LAUNCH) Train {self.train_id} to {self.destination} has been launched"
        self.logger.error(f"Launch: {msg}")

    def clear_passengers(self) -> None:
        """
        This method will be called to clear the passengers list
        :return:
        """
        self.passengers = []
        self.msg_ids = {}

    def clear_train(self) -> None:
        """
        This method will be called to clear the train
        :return:
        """
        self.clear_passengers()
        self.init_poll_published = False
        # running.remove(self)
        running.pop()
        msg = f"(CLEAR) Train {self.train_id} to {self.destination} has been cleared"
        self.logger.error(f"Clear: {msg}")
        self.logger.error(f"clear {running=}")


@dataclass
class Running:
    train: Train = None
