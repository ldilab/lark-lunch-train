import os

from src.lark.api.clients.auth import AuthenticationApiClient


class UserApiClient(AuthenticationApiClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filter_ids = os.getenv("FILTER_IDS", "").split(",")
        self.logger.error(f"Filter IDs: {self.filter_ids}")
        self.department_id = str(os.getenv("DEPARTMENT_ID"))

    def get_department_user_ids(self):
        url = self._lark_host / "open-apis" / "contact" / "v3" / "department" / "user" / "list"
        url.args["department_id"] = self.department_id
        resp = self._get_request(
            url,
            headers=self._get_auth_headers(),
        )
        department_user_ids = resp.get("data", {}).get("user_ids", [])

        if self.filter_ids:
            department_user_ids = [d for d in department_user_ids if d not in self.filter_ids]

        self.logger.error(f"Department User IDs: {department_user_ids}")
        return department_user_ids
    def get_user_info(self, open_id):
        url = self._lark_host / "open-apis" / "contact" / "v3" / "users" / open_id
        response = self._get_request(
            url,
            headers=self._get_auth_headers()
        )
        data = response.get("data", {}).get("user", {})
        return data
