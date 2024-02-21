import datetime
from dataclasses import dataclass
from datetime import time
from typing import List


@dataclass
class Passenger:
    open_id: str = None



class Train:
    def __init__(self, poll_time: str, launch_time: str, reminder_time: str, clear_time: str, train_id: str, destination: str) -> None:
        self.poll_time: time = datetime.datetime.strptime(poll_time, '%H:%M').time()
        self.launch_time: time = datetime.datetime.strptime(launch_time, '%H:%M').time()
        self.reminder_time: time = datetime.datetime.strptime(reminder_time, '%H:%M').time()
        self.clear_time: time = datetime.datetime.strptime(clear_time, '%H:%M').time()
        self.train_id: str = train_id
        self.passengers: List[Passenger] = []
        self.destination: str = destination
        self.init_poll_published = False

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
        raise NotImplementedError

    def update_passenger(self, passenger: Passenger) -> None:
        """
        This method will be called to update the passengers list
        :return:
        """
        self.passengers.append(passenger)
        # update message
        raise NotImplementedError

    def remove_passenger(self, passenger: Passenger) -> None:
        """
        This method will be called to remove the passenger from the list
        :return:
        """
        self.passengers.remove(passenger)
        # update message
        raise NotImplementedError

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
        raise NotImplementedError

    def launch_notification(self) -> None:
        """
        This method will be called when the train reaches the launch time to notify the group members
        :return:
        """
        raise NotImplementedError

    def clear_passengers(self) -> None:
        """
        This method will be called to clear the passengers list
        :return:
        """
        self.passengers = []

    def clear_train(self) -> None:
        """
        This method will be called to clear the train
        :return:
        """
        self.clear_passengers()
        self.init_poll_published = False




@dataclass
class Running:
    train: Train = None

