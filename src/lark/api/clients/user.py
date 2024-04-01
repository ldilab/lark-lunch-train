import os
from typing import List

import requests

from src.lark.api.clients.auth import AuthenticationApiClient


class UserApiClient(AuthenticationApiClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filter_ids = os.getenv("FILTER_IDS", "").split(",")
        self.logger.error(f"Filter IDs: {self.filter_ids}")

    def get_department_user_ids(self, department_id: str):
        self._authorize_tenant_access_token()
        url = self._lark_host / "open-apis" / "contact" / "v3" / "department" / "user" / "list"
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.tenant_access_token,
        }
        req_body = {
            "department_id": department_id,
        }
        resp = self._post_request(
            url,
            headers=headers,
            body=req_body
        )
        department_user_ids = resp.json().get("data", {}).get("user_ids", [])

        if self.filter_ids:
            department_user_ids = [d for d in department_user_ids if d not in self.filter_ids]

        self.logger.error(f"Department User IDs: {department_user_ids}")
        return department_user_ids
    def get_user_info(self, open_id):
        self._authorize_tenant_access_token()
        url = self._lark_host / "open-apis" / "contact" / "v3" / "users" / open_id
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.tenant_access_token,
        }
        response = self._get_request(
            url,
            headers=headers
        )
        data = response.json().get("data", {}).get("user", {})
        return data
