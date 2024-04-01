import json
from datetime import datetime
from typing import List, Dict

import requests

from src.lark.api import BATCH_MESSAGE_URI, MESSAGE_URI
from src.lark.api.clients.auth import AuthenticationApiClient
from src.lark.utils.dtypes import MessageType, ReceiveIdType


class MessageApiClient(AuthenticationApiClient):
    # ============= SEND ============= #
    def _send(self, receive_id_type: ReceiveIdType, receive_id, msg_type: MessageType, content):
        self._authorize_tenant_access_token()
        url = self._lark_host / MESSAGE_URI
        url.args["receive_id_type"] = receive_id_type.value
        self.logger.error(f"{url=}")
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.tenant_access_token,
        }
        self.logger.error(f"{headers=}")
        req_body = {
            "receive_id": receive_id,
            "content": json.dumps(content),
            "msg_type": msg_type.value,
        }
        self.logger.error(f"{req_body=}")
        return self._post_request(url, headers, req_body)

    def send_open_id(self, open_id, msg_type: MessageType, content):
        return self._send(ReceiveIdType.OPEN_ID, open_id, msg_type, content)

    def send_text(self, receive_id_type, receive_id, message):
        return self._send(receive_id_type, receive_id, MessageType.TEXT, {"text": message})

    def send_text_with_open_id(self, open_id, message):
        return self.send_open_id(open_id, MessageType.TEXT, {"text": message})

    def send_card(self, receive_id_type, receive_id, card_content: Dict[str, str]):
        return self._send(receive_id_type, receive_id, MessageType.INTERACTIVE, card_content)

    def send_card_with_open_id(self, open_id, card_content: Dict[str, str]):
        return self.send_open_id(open_id, MessageType.INTERACTIVE, card_content)

    # ************* BULK SEND ************* #
    def bulk_send(self, receive_id_type: ReceiveIdType, receive_ids, msg_type: MessageType, content):
        raise NotImplementedError

    def bulk_send_with_open_ids(self, open_ids, msg_type: MessageType, content):
        self.bulk_send(ReceiveIdType.OPEN_ID, open_ids, msg_type, content)

    def bulk_send_text(self, receive_id_type, receive_ids, message):
        self.bulk_send(receive_id_type, receive_ids, MessageType.TEXT, {"text": message})

    def bulk_send_text_with_open_ids(self, open_ids, message):
        self.bulk_send_with_open_ids(open_ids, MessageType.TEXT, {"text": message})

    def bulk_send_card(self, receive_id_type, receive_ids, card_content: Dict[str, str]):
        self.bulk_send(receive_id_type, receive_ids, MessageType.INTERACTIVE, card_content)

    def bulk_send_card_with_open_ids(self, open_ids, card_content: Dict[str, str]):
        self.bulk_send_with_open_ids(open_ids, MessageType.INTERACTIVE, card_content)

    # ============= BUZZ ============= #
    def buzz_message_with_open_id(self, message_id, user_ids):
        self._authorize_tenant_access_token()
        url = self._lark_host / MESSAGE_URI / message_id / "urgent_app"
        url.args["user_id_type"] = "open_id"
        self.logger.error(f"{url=}")

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.tenant_access_token,
        }
        self.logger.error(f"{headers=}")

        req_body = {
            "user_id_list": user_ids
        }
        self.logger.error(f"{req_body=}")

        resp = requests.patch(url=url, headers=headers, json=req_body)
        return self._check_error_response(resp)

    def bulk_buzz_message_with_open_ids(self, message_ids, user_ids):
        raise NotImplementedError

    # ============= UPDATE ============= #
    def update_message(self, message_id, content):
        self._authorize_tenant_access_token()
        url = f"{self._lark_host}{MESSAGE_URI}/{message_id}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.tenant_access_token,
        }
        req_body = {
            "content": content
        }
        resp = requests.patch(url, headers=headers, json=req_body)
        return self._check_error_response(resp)

    def bulk_update_message(self, message_ids, content):
        raise NotImplementedError