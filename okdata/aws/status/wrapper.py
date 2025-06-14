import logging
import os
import time
from functools import wraps

from requests.exceptions import HTTPError

from .model import (
    StatusData,
    StatusMeta,
    TraceEventStatus,
    TraceStatus,
)
from .sdk import Status

_status_logger = None


def status_wrapper(sdk_config=None):
    def _status_wrapper(handler):
        @wraps(handler)
        def wrapper(event, context):
            global _status_logger

            _status_logger = Status(
                _status_from_lambda_context(event, context), sdk_config
            )
            _status_logger.add(operation=handler.__name__)

            start_time = time.perf_counter_ns()
            try:
                response = handler(event, context)
                return response
            except Exception as e:
                _status_logger.add(exception=e)
                _status_logger.add(trace_event_status=TraceEventStatus.FAILED)
                _status_logger.add(trace_status=TraceStatus.FINISHED)
                raise e
            finally:
                end_time = time.perf_counter_ns()
                duration_ms = (end_time - start_time) / 1000000.0
                _status_logger.add(duration=duration_ms)
                try:
                    _status_logger.done()
                except HTTPError as e:
                    logging.exception(f"Error response from status API: {e}")
                _status_logger = None

        return wrapper

    return _status_wrapper


def status_add(**kwargs):
    if _status_logger:
        _status_logger.add(**kwargs)


def _status_from_lambda_context(event, context):
    request_context = event.get("requestContext") or {}
    authorizer = request_context.get("authorizer") or {}

    return StatusData.parse_obj(
        {
            "trace_id": event.get("execution_name"),
            "user": authorizer.get("principalId"),
            "component": os.getenv("SERVICE_NAME"),
            "meta": StatusMeta(
                function_name=getattr(context, "function_name", None),
                function_version=getattr(context, "function_version", None),
                function_stage=request_context.get("stage"),
                function_api_id=request_context.get("apiId"),
                git_rev=os.getenv("GIT_REV"),
                git_branch=os.getenv("GIT_BRANCH"),
            ),
        }
    )
