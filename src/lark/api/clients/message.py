import json
from typing import List, Dict, Union

from furl import furl

from src.lark.api import MESSAGE_URI
from src.lark.api.clients.auth import AuthenticationApiClient
from src.lark.utils.dtypes import MessageType, ReceiveIdType


class MessageApiClient(AuthenticationApiClient):
    # ============= SEND ============= #
    @staticmethod
    def _build_send_objects(
            urls: Union[furl, List[furl]],
            bodies: List[Dict[str, any]],
            params: Union[None, Dict[str, any]] = None,
    ) -> List[Dict[str, Union[str, Dict[str, str]]]]:
        objects = []
        if not isinstance(urls, list):
            urls = [urls] * len(bodies)

        for url, body in zip(urls, bodies):
            if params:
                for param_key, param_value in params.items():
                    url.args[param_key] = param_value

            objects.append({
                "url": url,
                "body": body
            })
        return objects

    def _send(self, receive_id_type: ReceiveIdType, receive_id, msg_type: MessageType, content):
        responses = self.bulk_send(receive_id_type, [receive_id], msg_type, content)
        assert len(responses) == 1
        return responses[0]

    def _send_open_id(self, open_id, msg_type: MessageType, content):
        return self._send(ReceiveIdType.OPEN_ID, open_id, msg_type, content)

    def send_text(self, receive_id_type, receive_id, message):
        return self._send(receive_id_type, receive_id, MessageType.TEXT, json.dumps({"text": message}))

    def send_text_with_open_id(self, open_id, message):
        return self._send_open_id(open_id, MessageType.TEXT, json.dumps({"text": message}))

    def send_card(self, receive_id_type, receive_id, card_content: Dict[str, str]):
        return self._send(receive_id_type, receive_id, MessageType.INTERACTIVE, card_content)

    def send_card_with_open_id(self, open_id, card_content: Dict[str, str]):
        return self._send_open_id(open_id, MessageType.INTERACTIVE, card_content)

    # ************* BULK SEND ************* #
    def bulk_send(self, receive_id_type: ReceiveIdType, receive_ids, msg_type: MessageType, content):
        send_objects = self._build_send_objects(
            urls=self._lark_host / MESSAGE_URI,
            params={
                "receive_id_type": receive_id_type.value
            },
            bodies=[{
                "receive_id": receive_id,
                "msg_type": msg_type.value,
                "content": content
            } for receive_id in receive_ids]
        )
        send_objects = [{
            **send_object,
            "headers": self._get_auth_headers()
        } for send_object in send_objects]

        return self._bulk_post_request(send_objects)

    def bulk_send_with_open_ids(self, open_ids, msg_type: MessageType, content):
        return self.bulk_send(ReceiveIdType.OPEN_ID, open_ids, msg_type, content)

    def bulk_send_text(self, receive_id_type, receive_ids, message):
        return self.bulk_send(receive_id_type, receive_ids, MessageType.TEXT, {"text": message})

    def bulk_send_text_with_open_ids(self, open_ids, message):
        return self.bulk_send_with_open_ids(open_ids, MessageType.TEXT, {"text": message})

    def bulk_send_card(self, receive_id_type, receive_ids, card_content: Dict[str, str]):
        return self.bulk_send(receive_id_type, receive_ids, MessageType.INTERACTIVE, card_content)

    def bulk_send_card_with_open_ids(self, open_ids, card_content: Dict[str, str]):
        return self.bulk_send_with_open_ids(open_ids, MessageType.INTERACTIVE, card_content)

    # ============= BUZZ ============= #
    def buzz_message_with_open_id(self, message_id, user_ids):
        responses = self.bulk_buzz_message_with_open_ids([message_id], user_ids)
        assert len(responses) == 1
        return responses[0]

    def bulk_buzz_message_with_open_ids(self, message_ids, user_ids):
        buzz_objects = self._build_send_objects(
            urls=[
                self._lark_host / MESSAGE_URI / message_id / "urgent_app"
                for message_id in message_ids
            ],
            params={
                "user_id_type": ReceiveIdType.OPEN_ID.value
            },
            bodies=[{
                "user_id_list": [user_id]
            } for user_id in user_ids]
        )
        buzz_objects = [{
            **send_object,
            "headers": self._get_auth_headers()
        } for send_object in buzz_objects]

        return self._bulk_patch_request(buzz_objects)

    # ============= UPDATE ============= #
    def update_message(self, message_id, content):
        responses = self.bulk_update_message([message_id], content)
        assert len(responses) == 1
        return responses[0]

    def bulk_update_message(self, message_ids, content):
        update_objects = self._build_send_objects(
            urls=[
                self._lark_host / MESSAGE_URI / message_id
                for message_id in message_ids
            ],
            bodies=[{
                "content": content
            } for message_id in message_ids]
        )
        update_objects = [{
            **send_object,
            "headers": self._get_auth_headers()
        } for send_object in update_objects]
        return self._bulk_patch_request(update_objects)
