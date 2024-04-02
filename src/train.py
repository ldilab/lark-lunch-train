import datetime
import os
from dataclasses import dataclass
from datetime import time
from enum import Enum
from typing import List, Union

from src import rail
from src.lark.api.client import LarkClient
from src.lark.message.templates import ONBOARD_MESSAGE


@dataclass
class Passenger:
    open_id: str = None
    user_name: str = None


OPEN_ID = os.getenv("OPEN_ID")


class Train:
    def __init__(self, poll_time: str, launch_time: str, reminder_time: str, clear_time: str, train_id: str,
                 destination: str, logger, message_client: LarkClient, issuer: Passenger):
        self.logger = logger
        self.message_api_client = message_client
        self.poll_time: time = datetime.datetime.strptime(poll_time, '%H:%M').time()
        self.launch_time: time = datetime.datetime.strptime(launch_time, '%H:%M').time()
        self.reminder_time: time = datetime.datetime.strptime(reminder_time, '%H:%M').time()
        self.clear_time: time = datetime.datetime.strptime(clear_time, '%H:%M').time()
        self.train_id: str = train_id
        self.passengers: List[Passenger] = []
        self.destination: str = destination
        self.issuer = issuer
        self.passengers.append(issuer)
        self.msg_ids = {}

    def onboarding_notification(self) -> None:
        """
        This method will be called to issue the initial poll to group members
        :return:
        """
        onboard_msg = ONBOARD_MESSAGE(
            issuer=self.issuer.user_name,
            place=self.destination,
            time=self.launch_time.strftime('%H:%M'),
            user_names=[passenger.user_name for passenger in self.passengers], is_str=True
        )

        user_ids = self.message_api_client.get_department_user_ids()
        self.logger.error(f"onboarding to: \n-> {user_ids}")

        responses = self.message_api_client.bulk_send_card_with_open_ids(
            open_ids=user_ids,
            card_content=onboard_msg
        )
        msg_ids = [
            response.get("data", {}).get("message_id", "")
            for response in responses
        ]
        self.msg_ids = dict(zip(user_ids, msg_ids))
        self.logger.error(f"onboarding msgs:\n-> {self.msg_ids}")

    def update_passengers(self, action: str, passenger: Passenger) -> None:
        """
        This method will be called to update the passengers list
        :return:
        """
        if action == "on":
            self.add_passenger(passenger)
        elif action == "off":
            self.pop_passenger(passenger)

    def add_passenger(self, passenger: Passenger) -> None:
        if passenger.open_id in [p.open_id for p in self.passengers]:
            self.logger.error(f"[ALREADY IN] [Passenger {passenger.user_name}]")
            return

        self.passengers.append(passenger)
        self.logger.error(f"[ADDED] [Passenger {passenger.user_name}]")

    def pop_passenger(self, passenger: Passenger) -> None:
        """
        This method will be called to remove the passenger from the list
        :return:
        """
        if passenger.open_id not in [p.open_id for p in self.passengers]:
            self.logger.error(f"[NOT IN] [Passenger {passenger.user_name}]")
            return

        self.passengers.remove(passenger)
        self.logger.error(f"[REMOVED] [Passenger {passenger.user_name}]")

    def reminder_notification(self) -> None:
        """
        This method will be called to remind the group members about the train
        :return:
        """
        msg = f"(REMIND) Train {self.train_id} to {self.destination} will be launched at {self.launch_time}"
        self.logger.error(f"Reminder: {msg}")


        open_ids = [passenger.open_id for passenger in self.passengers]
        msg_ids = [self.msg_ids.get(open_id, "") for open_id in open_ids]
        self.message_api_client.bulk_buzz_message_with_open_ids(
            message_ids=msg_ids,
            user_ids=open_ids
        )

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
        rail.clear_rail(self.destination)

