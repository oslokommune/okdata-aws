from enum import Enum
from typing import Dict, Optional, List
from datetime import datetime, timezone
from pydantic import BaseModel, Field, validator


class TraceStatus(str, Enum):
    STARTED = "STARTED"
    CONTINUE = "CONTINUE"
    FINISHED = "FINISHED"


class TraceEventStatus(str, Enum):
    OK = "OK"
    FAILED = "FAILED"


class StatusMeta(BaseModel):
    function_name: Optional[str] = None
    function_version: Optional[str] = None
    function_stage: Optional[str] = None
    function_api_id: Optional[str] = None
    git_rev: Optional[str] = None
    git_branch: Optional[str] = None


# TODO: Rework optional vs required and defaults when currents users are updated
# and if to be used as a basis for the status api. Both trace_id (for new traces)
# and trace_event_id are currently generated in status-api.
class StatusData(BaseModel):
    trace_id: Optional[str] = None  # TODO: Generate here as default?
    # trace_event_id: UUID = None  # = Field(default_factory=uuid4)
    domain: str = "N/A"  # TODO: Temporary default (required)
    domain_id: Optional[str] = None
    start_time: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), str=datetime.isoformat
    )
    end_time: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), str=datetime.isoformat
    )
    trace_status: TraceStatus = TraceStatus.CONTINUE
    trace_event_status: TraceEventStatus = TraceEventStatus.OK
    user: Optional[str] = None
    component: str = "N/A"  # TODO: Temporary default (required)
    operation: Optional[str] = None
    status_body: Optional[Dict] = None
    meta: Optional[StatusMeta] = None
    s3_path: Optional[str] = None
    duration: Optional[int] = None
    exception: Optional[str] = None
    errors: Optional[List] = None

    class Config:
        validate_assignment = True

    @validator("exception", pre=True)
    def ensure_exception_data_is_string(cls, v):
        if isinstance(v, Exception):
            return str(v)
        return v

    @validator("errors", each_item=True)
    def ensure_format_of_errors(cls, v):

        if not isinstance(v, dict):
            raise TypeError(f"{v} is not a dict.")
        if "message" not in v:
            raise ValueError("Missing key 'message'.")
        if not isinstance(v["message"], dict):
            raise TypeError("error['message'] is not a dict.")
        if "nb" not in v["message"]:
            raise ValueError("Missing key 'nb' in error['message'].")
        return v
