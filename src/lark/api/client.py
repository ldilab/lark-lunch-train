from src.lark.api.clients.message import MessageApiClient
from src.lark.api.clients.user import UserApiClient


class LarkClient(
    MessageApiClient,
    UserApiClient
):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

