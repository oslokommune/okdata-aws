from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from json import dumps, JSONEncoder
from typing import Dict, Optional, List


class TraceStatus(str, Enum):
    STARTED = "STARTED"
    CONTINUE = "CONTINUE"
    FINISHED = "FINISHED"


class TraceEventStatus(str, Enum):
    OK = "OK"
    FAILED = "FAILED"


class StatusJSONEncoder(JSONEncoder):
    def default(self, obj, *args, **kwargs):
        if isinstance(obj, Exception):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class BaseModel:
    def dict(self, exclude_none=False):
        if exclude_none:
            return asdict(
                self,
                dict_factory=lambda d: {k: v for (k, v) in d if v is not None},
            )
        return asdict(self)

    def json(self, exclude_none=False, **kwargs):
        return dumps(
            self.dict(exclude_none=exclude_none),
            cls=StatusJSONEncoder,
            **kwargs,
        )

    @classmethod
    def parse_obj(cls, obj):
        return cls(**obj)


@dataclass
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
@dataclass
class StatusData(BaseModel):
    trace_id: Optional[str] = None  # TODO: Generate here as default?
    # trace_event_id: UUID = None  # = Field(default_factory=uuid4)
    domain: str = "N/A"  # TODO: Temporary default (required)
    domain_id: Optional[str] = None
    start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    end_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
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

    def __setattr__(self, name, value):
        # Validate and ensure format of errors
        if name == "errors" and value is not None:
            if not isinstance(value, list):
                raise TypeError("`errors` must be provided as a list.")

            for error in value:
                if not isinstance(error, dict):
                    raise TypeError(f"{error} is not a dict.")
                if "message" not in error:
                    raise ValueError("Missing key 'message'.")
                if not isinstance(error["message"], dict):
                    raise TypeError("error['message'] is not a dict.")
                if "nb" not in error["message"]:
                    raise ValueError("Missing key 'nb' in error['message'].")

        super().__setattr__(name, value)
