import json
import re
from copy import deepcopy
from unittest.mock import patch

import pytest
from freezegun import freeze_time
from okdata.sdk.config import Config

from okdata.aws.status.model import (
    StatusData,
    StatusMeta,
    TraceStatus,
    TraceEventStatus,
)
from okdata.aws.status.sdk import Status
from okdata.aws.status.wrapper import _status_from_lambda_context


utc_now = "2020-10-10T08:55:01+00:00"
trace_id = "my-trace-id"
mock_token_response = {
    "access_token": "access",
    "refresh_token": "refresh",
    "token_type": "bearer",
}
mock_status_data = {
    "trace_id": trace_id,
    "trace_status": "CONTINUE",
    "trace_event_status": "OK",
    "domain": "dataset",
    "domain_id": "my-dataset/1",
    "status_body": None,
    "user": "someuser",
    "component": "system32",
}
mock_status_response = {"trace_id": trace_id}


class MockLambdaContext:
    function_name = "my_lambda_function"
    function_version = 123


@pytest.fixture(scope="function")
def mock_openid(requests_mock):
    openid_matcher = re.compile("openid-connect")
    requests_mock.register_uri(
        "POST",
        openid_matcher,
        json=mock_token_response,
        status_code=200,
    )


@pytest.fixture(scope="function")
def mock_status_api(requests_mock):
    matcher = re.compile("mock-status-api")
    requests_mock.register_uri(
        "POST", matcher, json=mock_status_response, status_code=200
    )


class TestStatusClass:
    def test_status_data_from_trace_id(self):
        s = Status(trace_id)
        assert s.status_data.trace_id == trace_id

    def test_status_data_from_dict(self):
        s = Status(mock_status_data)
        assert s.status_data.trace_id == trace_id

    def test_status_data_from_object(self):
        status_data = StatusData.parse_obj(mock_status_data)
        s = Status(status_data)
        assert s.status_data.trace_id == trace_id

    def test_status_with_sdk_config(self):
        config = Config(config={"foo": "bar"})
        # Mock out the `Authenticate` class so that the SDK doesn't try to set
        # up authentication with a malformed config.
        with patch("okdata.sdk.sdk.Authenticate"):
            s = Status(trace_id, config)
        assert s._sdk.config.config == {"foo": "bar"}

    def test_status_data_from_lambda(self):
        lambda_context = MockLambdaContext()
        s = _status_from_lambda_context(
            event={
                "requestContext": {"authorizer": {"principalId": "someuser"}},
                "execution_name": trace_id,
            },
            context=lambda_context,
        )
        assert s.trace_id == trace_id
        assert s.meta.function_name == lambda_context.function_name
        assert s.user == "someuser"

    @freeze_time(utc_now)
    def test_status_done(self, requests_mock, mock_openid, mock_status_api):
        requests_mock.register_uri("POST", f"/status-api/status/{trace_id}", json={})
        s = Status(StatusData.parse_obj(mock_status_data))
        s.done()

        last_request = requests_mock.last_request
        assert last_request.method == "POST"
        assert last_request.url.endswith(f"/status/{trace_id}")

        payload = last_request.json()
        assert payload["trace_id"] == trace_id
        assert payload["start_time"] == utc_now
        assert payload["end_time"] == utc_now
        assert payload["domain"] == "dataset"
        assert payload["domain_id"] == "my-dataset/1"
        assert payload["user"] == "someuser"
        assert payload["component"] == "system32"
        assert payload["trace_status"] == TraceStatus.CONTINUE
        assert payload["trace_event_status"] == TraceEventStatus.OK

    def test_status_optional_fields(self):
        status_data = deepcopy(mock_status_data)
        status_data["domain_id"] = None
        status_data["user"] = None
        s = StatusData.parse_obj(status_data)
        assert s.domain_id is None
        assert s.user is None

        status_data.pop("domain_id")
        status_data.pop("user")
        s = StatusData.parse_obj(status_data)
        assert s.domain_id is None
        assert s.user is None

    def test_add_status_data_payload(self, mock_openid, mock_status_api):
        s = Status(mock_status_data)
        s.add(domain_id="my-domain-id")
        assert s.status_data.domain_id == "my-domain-id"

    @freeze_time(utc_now)
    def test_status_data_as_json(self, mock_openid, mock_status_api):
        s = Status(mock_status_data)
        s.add(
            domain_id="my-domain-id",
            exception=Exception("This did not work as expected"),
            user=None,
            meta=StatusMeta(function_name="foo-bar"),
        )
        assert json.loads(s.status_data.json(exclude_none=True)) == {
            "trace_id": "my-trace-id",
            "domain": "dataset",
            "domain_id": "my-domain-id",
            "start_time": utc_now,
            "end_time": utc_now,
            "trace_status": "CONTINUE",
            "trace_event_status": "OK",
            "component": "system32",
            "meta": {"function_name": "foo-bar"},
            "exception": "This did not work as expected",
        }
