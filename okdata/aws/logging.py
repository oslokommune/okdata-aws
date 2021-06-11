import os
import time
from copy import copy
from functools import wraps

import structlog

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ]
)

logger = structlog.get_logger()
_logger = None

COLD_START = True
SERVICE_NAME = None
ASYNC = False


def _init_logger(handler, event, context):
    global COLD_START
    global SERVICE_NAME
    global _logger

    headers = event.get("headers", {})
    headers = {k.lower(): v for k, v in headers.items()}

    request_context = event.get("requestContext", {})
    domain_name = request_context.get("domainName", None)
    if not domain_name:
        domain_name = headers.get("host", None)

    authorizer = request_context.get("authorizer", {})
    principal_id = authorizer.get("principalId", None)
    if principal_id:
        # Strip last characters of principal ID for privacy
        principal_id = principal_id[0:-3] + "xxx"

    identity = request_context.get("identity", {})
    source_ip = identity.get("sourceIp", None)
    if source_ip:
        # Strip final octet of IP address for privacy
        source_ip = ".".join(source_ip.split(".")[0:-1]) + ".x"

    _logger = logger.bind(
        service_name=SERVICE_NAME,
        handler_method=handler.__name__,
        function_name=getattr(context, "function_name", ""),
        function_version=getattr(context, "function_version", ""),
        function_stage=request_context.get("stage", ""),
        function_api_id=request_context.get("apiId", ""),
        git_rev=os.getenv("GIT_REV"),
        aws_account_id=request_context.get("accountId", ""),
        aws_request_id=getattr(context, "aws_request_id", ""),
        aws_trace_id=headers.get("x-amzn-trace-id", ""),
        memory_limit_in_mb=getattr(context, "memory_limit_in_mb", 0),
        logged_in=principal_id is not None,
        principal_id=principal_id,
        source_ip=source_ip,
        request_domain_name=domain_name,
        request_resource=event.get("resource", ""),
        request_path=event.get("path", ""),
        request_method=event.get("httpMethod", ""),
        request_path_parameters=event.get("pathParameters", {}),
        request_query_string_parameters=remove_secret_query_parameters(
            event.get("queryStringParameters", {})
        ),
        cold_start=COLD_START,
    )
    COLD_START = False


def _finalize(start_time):
    global _logger
    duration_ms = (time.perf_counter_ns() - start_time) / 1000000.0
    _logger.msg("", duration_ms=duration_ms)
    _logger = None


def _handle_response(response):
    global _logger

    if isinstance(response, dict) and "statusCode" in response:
        status_code = response["statusCode"]
        _logger = _logger.bind(
            response_status_code=status_code,
            level="info" if status_code < 500 else "error",
        )
        if status_code >= 400:
            _logger = _logger.bind(response_body=response.get("body", ""))
    else:
        _logger = _logger.bind(level="info")

    return response


def logging_wrapper(*args, **kwargs):
    global SERVICE_NAME
    global ASYNC

    if kwargs.get("async_wrapper"):
        ASYNC = True

    # Support @logging_wrapper(service_name="...")
    if "service_name" in kwargs:
        SERVICE_NAME = kwargs["service_name"]
        return logging_wrapper

    # Support @logging_wrapper("name")
    if len(args) == 1 and isinstance(args[0], str):
        SERVICE_NAME = args[0]
        return logging_wrapper

    # Fall back to looking up service name from environment variable
    if not SERVICE_NAME:
        SERVICE_NAME = os.getenv("SERVICE_NAME")
        if not SERVICE_NAME:
            raise ValueError(
                "Service name not configured, please set SERVICE_NAME environment variable."
            )

    if len(args) == 0:
        raise ValueError("Missing handler function argument")

    handler = args[0]

    @wraps(handler)
    def wrapper(event, context):
        global _logger
        _init_logger(handler, event, context)
        start_time = time.perf_counter_ns()
        try:
            return _handle_response(handler(event, context))
        except Exception as e:
            _logger = _logger.bind(exc_info=e, level="error")
            raise e
        finally:
            _finalize(start_time)

    @wraps(handler)
    async def async_wrapper(event, context):
        global _logger
        _init_logger(handler, event, context)
        start_time = time.perf_counter_ns()
        try:
            return _handle_response(await handler(event, context))
        except Exception as e:
            _logger = _logger.bind(exc_info=e, level="error")
            raise e
        finally:
            _finalize(start_time)

    return async_wrapper if ASYNC else wrapper


def log_dynamodb(f):
    start_time = time.perf_counter_ns()
    try:
        db_response = f()

        status_code = db_response["ResponseMetadata"]["HTTPStatusCode"]
        log_add(dynamodb_status_code=status_code)

        if "Count" in db_response:
            log_add(dynamodb_item_count=db_response["Count"])

        return db_response
    finally:
        duration_ms = (time.perf_counter_ns() - start_time) / 1000000.0
        log_add(dynamodb_duration_ms=duration_ms)


def log_duration(f, duration_field):
    start_time = time.perf_counter_ns()
    try:
        return f()
    finally:
        duration_ms = (time.perf_counter_ns() - start_time) / 1000000.0
        log_add(**{duration_field: duration_ms})


def log_add(**kwargs):
    global _logger

    if _logger:
        _logger = _logger.bind(**kwargs)


def log_exception(e):
    log_add(exc_info=e, level="error")


def hide_suffix(username, suffix_size=3):
    if suffix_size > len(username):
        return "x" * len(username)
    return username[:-suffix_size] + "x" * suffix_size


def remove_secret_query_parameters(query_parameters):
    if not query_parameters:
        return {}
    filtered_parameters = copy(query_parameters)
    for key in query_parameters.keys():
        if "token" in key.lower():
            del filtered_parameters[key]
    return filtered_parameters
