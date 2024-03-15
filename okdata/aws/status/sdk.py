import json
import logging
from datetime import datetime, timezone
from typing import Dict, Union

from okdata.sdk.status import Status as StatusSDK
from requests.exceptions import HTTPError, RetryError

from .model import StatusData

log = logging.getLogger()


class Status:
    def __init__(self, status_data: Union[StatusData, Dict, str]):
        if isinstance(status_data, str):
            # TODO: Remove in future - for backwards-compatibility:
            # Status-class used directly in state-machine-event only(?),
            # passes trace_id
            status_data = StatusData(trace_id=status_data)
        if isinstance(status_data, dict):
            status_data = StatusData.parse_obj(status_data)

        self.status_data = status_data
        self._sdk = StatusSDK()

    def _process_payload(self):
        if self.status_data.trace_id is None:
            log.warning(
                "dataplatform.status: status_data.trace_id is None, will not process payload"
            )
            return {}

        payload = json.loads(self.status_data.json(exclude_none=True))

        try:
            log.info(f"Sending payload to status API: {payload}")
            response = self._sdk.update_status(self.status_data.trace_id, payload)
            log.info(f"Response from status API: {response}")
            return response
        except (HTTPError, RetryError) as e:
            log.error(f"Status API error: {e}")
            return None

    def add(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self.status_data, key, value)

    def done(self):
        # TODO: Currently in use by state-machine-event. Mark internal ("_")
        # or remove once updated (DP-1259)?
        self.status_data.end_time = datetime.now(timezone.utc)
        return self._process_payload()
