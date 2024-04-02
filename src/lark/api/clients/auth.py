from datetime import datetime, timedelta

from src.lark.api import TENANT_ACCESS_TOKEN_URI
from src.lark.api.clients.base import BaseApiClient


class AuthenticationApiClient(BaseApiClient):
    def _authorize_tenant_access_token(self):
        if (
                self._tenant_access_token
                and self._tenant_access_refresh_time is not None
                and datetime.now() < self._tenant_access_refresh_time
        ):
            self.logger.error(f"(NOT EXPIRED) tenant_access_token: {self._tenant_access_token}")
            return
        url = self._lark_host / TENANT_ACCESS_TOKEN_URI
        req_body = {"app_id": self._app_id, "app_secret": self._app_secret}
        response = self._post_request(
            url,
            headers={"Content-Type": "application/json"},
            body=req_body
        )
        self._check_error_response(response)
        self._tenant_access_token = response.json().get("tenant_access_token")
        self._tenant_access_token_expires = response.json().get("expire")
        self._tenant_access_refresh_time = datetime.now() + timedelta(seconds=self._tenant_access_token_expires - 5)
        self.logger.error(f"(RENEWED) tenant_access_token: {self._tenant_access_token}")

    def _get_auth_headers(self):
        self._authorize_tenant_access_token()
        return {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.tenant_access_token,
        }

    @property
    def tenant_access_token(self):
        return self._tenant_access_token
