import json
import os
from time import sleep

from okdata.aws.logging import hide_suffix, log_duration, log_dynamodb, logging_wrapper

empty_event = {}
empty_context = None


def empty_handler(event, context):
    return {}


def ok_handler(event, context):
    return {"statusCode": 200, "body": "OK"}


def user_error_handler(event, context):
    return {"statusCode": 400, "body": "Bad Request"}


def server_error_handler(event, context):
    return {"statusCode": 500, "body": "Internal Server Error"}


def throwing_handler(event, context):
    raise Exception("fail!")


def timed_operation(raise_exception=False):
    sleep(0.01)
    if raise_exception:
        raise Exception("fail!")
    else:
        return 201


def timing_handler(event, context):
    result = log_duration(timed_operation, "my_timer")
    return {"statusCode": result}


def throwing_timing_handler(event, context):
    log_duration(lambda: timed_operation(raise_exception=True), "my_timer")


def non_rest_handler(event, context):
    return None


class RequestContext:
    def __init__(
        self, function_name, function_version, aws_request_id, memory_limit_in_mb
    ):
        self.function_name = function_name
        self.function_version = function_version
        self.aws_request_id = aws_request_id
        self.memory_limit_in_mb = memory_limit_in_mb


def test_log_service_name_from_env(capsys):
    os.environ["SERVICE_NAME"] = "my_other_service"

    wrapper = logging_wrapper(empty_handler)
    wrapper(empty_event, empty_context)

    log = json.loads(capsys.readouterr().out)

    assert log["service_name"] == "my_other_service"
    assert log["handler_method"] == "empty_handler"
    assert log["function_name"] == ""


def test_log_empty_event_and_context(capsys):
    decorator = logging_wrapper(service_name="my_service")
    wrapper = decorator(empty_handler)
    wrapper(empty_event, empty_context)

    log = json.loads(capsys.readouterr().out)

    assert log["service_name"] == "my_service"
    assert log["handler_method"] == "empty_handler"
    assert log["function_name"] == ""


def test_log_none_headers(capsys):
    decorator = logging_wrapper(service_name="my_service")
    wrapper = decorator(empty_handler)
    wrapper({"headers": None}, empty_context)


def test_legacy_wrapper(capsys):
    decorator = logging_wrapper("my_old_service")
    wrapper = decorator(empty_handler)
    wrapper(empty_event, empty_context)

    log = json.loads(capsys.readouterr().out)

    assert log["service_name"] == "my_old_service"
    assert log["handler_method"] == "empty_handler"
    assert log["function_name"] == ""


def test_handler_name(capsys):
    wrapper = logging_wrapper(empty_handler)

    assert wrapper.__name__ == empty_handler.__name__


def test_log_event_data(capsys):
    wrapper = logging_wrapper(empty_handler)
    event = {
        "path": "my_path",
        "pathParameters": {"my_path_param": "my_value"},
        "requestContext": {
            "accountId": "1234567890",
            "stage": "my_stage",
            "apiId": "my_api_id",
            "domainName": "my_domain",
            "identity": {"sourceIp": "1.2.3.4"},
        },
        "resource": "my_resource",
        "httpMethod": "my_method",
        "queryStringParameters": {
            "my_query_param": "my_query_value",
            "token": "secret-stuff",
            "secretToken": "secret-stuff",
        },
    }
    wrapper(event, empty_context)

    log = json.loads(capsys.readouterr().out)

    assert log["function_stage"] == "my_stage"
    assert log["function_api_id"] == "my_api_id"
    assert log["aws_account_id"] == "1234567890"
    assert log["source_ip"] == "1.2.3.x"
    assert log["request_domain_name"] == "my_domain"
    assert log["request_resource"] == "my_resource"
    assert log["request_path"] == "my_path"
    assert log["request_method"] == "my_method"
    assert log["request_path_parameters"] == {"my_path_param": "my_value"}
    assert log["request_query_string_parameters"] == {
        "my_query_param": "my_query_value"
    }
    assert event["queryStringParameters"] == {
        "my_query_param": "my_query_value",
        "token": "secret-stuff",
        "secretToken": "secret-stuff",
    }


def test_log_headers(capsys):
    wrapper = logging_wrapper(empty_handler)

    event = {"headers": {"X-Amzn-Trace-Id": "my-trace-id"}}
    wrapper(event, empty_context)

    log = json.loads(capsys.readouterr().out)

    assert log["aws_trace_id"] == "my-trace-id"


def test_log_context(capsys):
    wrapper = logging_wrapper(empty_handler)

    context = RequestContext(
        function_name="my_function",
        function_version="my_function_version",
        aws_request_id="my_request_id",
        memory_limit_in_mb=1024,
    )
    wrapper(empty_event, context)

    log = json.loads(capsys.readouterr().out)

    assert log["function_name"] == "my_function"
    assert log["function_version"] == "my_function_version"
    assert log["aws_request_id"] == "my_request_id"
    assert log["memory_limit_in_mb"] == 1024


def test_log_authenticated(capsys):
    event = {"requestContext": {"authorizer": {"principalId": "abc123456"}}}
    wrapper = logging_wrapper(ok_handler)
    wrapper(event, empty_context)

    log = json.loads(capsys.readouterr().out)

    assert log["principal_id"] == "abc123xxx"
    assert log["logged_in"] is True


def test_log_unauthenticated(capsys):
    wrapper = logging_wrapper(ok_handler)
    wrapper(empty_event, empty_context)

    log = json.loads(capsys.readouterr().out)

    assert log["logged_in"] is False


def test_log_response_ok(capsys):
    wrapper = logging_wrapper(ok_handler)
    wrapper(empty_event, empty_context)

    log = json.loads(capsys.readouterr().out)

    assert log["response_status_code"] == 200
    assert "response_body" not in log
    assert log["level"] == "info"


def test_log_user_error(capsys):
    wrapper = logging_wrapper(user_error_handler)
    wrapper(empty_event, empty_context)

    log = json.loads(capsys.readouterr().out)

    assert log["response_status_code"] == 400
    assert log["response_body"] == "Bad Request"
    assert log["level"] == "info"


def test_log_server_error(capsys):
    wrapper = logging_wrapper(server_error_handler)
    wrapper(empty_event, empty_context)

    log = json.loads(capsys.readouterr().out)

    assert log["response_status_code"] == 500
    assert log["response_body"] == "Internal Server Error"
    assert log["level"] == "error"


def test_log_exception(capsys):
    wrapper = logging_wrapper(throwing_handler)
    try:
        wrapper(empty_event, empty_context)
        assert False
    except Exception:
        pass

    log = json.loads(capsys.readouterr().out)

    assert log["level"] == "error"
    assert "Exception: fail!" in log["exception"]


def test_log_duration(capsys):
    wrapper = logging_wrapper(timing_handler)
    wrapper(empty_event, empty_context)

    log = json.loads(capsys.readouterr().out)

    assert log["my_timer"] > 10.0
    assert log["response_status_code"] == 201


def test_log_duration_exception(capsys):
    wrapper = logging_wrapper(throwing_timing_handler)
    try:
        wrapper(empty_event, empty_context)
        assert False
    except Exception:
        pass

    log = json.loads(capsys.readouterr().out)

    assert log["my_timer"] > 10.0
    assert log["level"] == "error"
    assert "Exception: fail!" in log["exception"]


def test_log_non_rest_response(capsys):
    wrapper = logging_wrapper(non_rest_handler)
    wrapper(empty_event, empty_context)

    log = json.loads(capsys.readouterr().out)

    assert log["level"] == "info"


def test_hide_suffix():
    username = "jon-blund"

    assert hide_suffix(username) == "jon-blxxx"
    assert hide_suffix(username, 5) == "jon-xxxxx"
    assert hide_suffix(username, 20) == "xxxxxxxxx"


def dynamodb_handler(event, context):
    dynamodb_response = {"ResponseMetadata": {"HTTPStatusCode": 200}}
    if "Count" in event:
        dynamodb_response["Count"] = event["Count"]

    log_dynamodb(lambda: dynamodb_response)


def test_log_dynamodb(capsys):
    wrapper = logging_wrapper(dynamodb_handler)
    wrapper(empty_event, empty_context)

    log = json.loads(capsys.readouterr().out)

    assert "dynamodb_duration_ms" in log
    assert log["dynamodb_status_code"] == 200


def test_log_dynamodb_item_count(capsys):
    event = {"Count": 123}
    wrapper = logging_wrapper(dynamodb_handler)
    wrapper(event, empty_context)

    log = json.loads(capsys.readouterr().out)

    assert log["dynamodb_item_count"] == 123
