import logging
from typing import Dict, List, Union

import grequests
from furl import furl

from src.lark.api.exception import LarkException


class BaseApiClient:
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
        return self._bulk_post_request([{
            "url": url,
            "headers": headers,
            "body": body
        }])[0]

    def _patch_request(
            self,
            url: str,
            headers: Dict[str, str],
            body: Dict[str, str],
    ):
        return self._bulk_patch_request([{
            "url": url,
            "headers": headers,
            "body": body
        }])[0]

    def _get_request(
            self,
            url: str,
            headers: Dict[str, str],
    ):
        request_object = grequests.get(url, headers=headers)
        response = grequests.map([request_object])[0]
        self.logger.error("GET request response: %s", response.json())

        return self._check_error_response(response)

    def _bulk_post_request(
            self,
            request_targets: List[Dict[str, Union[str, Dict[str, str]]]],
    ):
        request_objects = [
            grequests.post(target["url"], headers=target["headers"], json=target["body"])
            for target in request_targets
        ]
        responses = grequests.map(request_objects)
        self.logger.error("POST request responses: %s", responses)

        error_checked_responses = [
            self._check_error_response(response)
            for response in responses
        ]
        return error_checked_responses

    def _bulk_patch_request(
            self,
            request_targets: List[Dict[str, Union[str, Dict[str, str]]]],
    ):
        request_objects = [
            grequests.patch(target["url"], headers=target["headers"], json=target["body"])
            for target in request_targets
        ]
        responses = grequests.map(request_objects)
        self.logger.error("PATCH request responses: %s", responses)

        error_checked_responses = [
            self._check_error_response(response)
            for response in responses
        ]
        return error_checked_responses

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
