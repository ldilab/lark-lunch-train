import logging
from typing import Dict, List

import requests
from furl import furl

from src.lark.api.exception import LarkException


class BaseApiClient(object):
    def __init__(self, app_id, app_secret, lark_host, logger):
        self._tenant_access_refresh_time = None
        self._app_id = app_id
        self._app_secret = app_secret
        self._lark_host = furl(lark_host)
        self._tenant_access_token = ""
        self.logger = logger

    def _post_request(
            self,
            url: str,
            headers: Dict[str, str],
            body: Dict[str, str],
    ):
        resp = requests.post(url, headers=headers, json=body)
        return self._check_error_response(resp)

    def _get_request(
            self,
            url: str,
            headers: Dict[str, str],
    ):
        response = requests.get(url, headers=headers)
        return self._check_error_response(response)

    def _bulk_post_request(
            self,
            request_targets: List[Dict[str, str]],
    ):
        responses = []
        for target in request_targets:
            if "url" not in target:
                raise ValueError("URL is required in request target")
            url = target.get("url")
            headers = target.get("headers", {})
            body = target.get("body", {})
            response = self._post_request(url, headers, body)
            responses.append(self._check_error_response(response))

        return responses

    @staticmethod
    def _check_error_response(resp):
        # check if the response contains error information
        if resp.status_code != 200:
            resp.raise_for_status()
        response_dict = resp.json()
        code = response_dict.get("code", -1)
        if code != 0:
            logging.error(response_dict)
            raise LarkException(code=code, msg=response_dict.get("msg"))
        return response_dict
