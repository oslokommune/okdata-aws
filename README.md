# okdata-aws

Collection of helpers for working with AWS.

## Logging for Lambda

Based on [Structlog](https://www.structlog.org/).

Structured and enriched logging for AWS Lambda functions.

### TL;DR:

 - Decorate handler with `logging_wrapper`
 - Encrich logs with key/value pairs using `log_add`
 - Time functions with `log_duration`
 - Log exceptions with `log_exception`

### Usage

Wrap your lambda handler with `logging_wrapper`. Badabing badabom, you're good
to go!

You can set the service name using the `logging.init` method, or configure it
using the `SERVICE_NAME` environment variable.

```python
from okdata.aws import logging
from okdata.aws.logging import logging_wrapper

logging.init("my_fantastic_lambda")

@logging_wrapper
def handler(event, context):
    if error:
        return {
            "statusCode": 500,
            "body": "Automatically logs bodies from error responses even!",
        }
```

#### Encriching logs

By automagic logs will be enriched with git revisions, cold start y/n call
duration and much more, but to add even more magic you can use `log_add` and
`log_duration`.

```python
from okdata.aws.logging import logging_wrapper, log_add, log_duration

@logging_wrapper
def handler(event, context):
    log_add(dataset=event["dataset"], foo=context["foo"])
    log_duration(
        lambda: slow_thinger(event["dataset"]),
        "my_slow_thinger"
    )
    ... and so on

def slow_thinger():
    sleep(9999999999999999)
```

#### Exceptions

Struct log can extract exception info if we log the exception to the special
[`exc_info`](https://www.structlog.org/en/stable/api.html#structlog.processors.format_exc_info)
key.

For convenience we catch and log uncaught exceptions using this already.

If you need to process an exception you can use `log_exception` to log it to the
`exc_info` key.

```python
from okdata.aws.logging import logging_wrapper, log_exception

@logging_wrapper
def handler(event, context):
    try:
        thing()
    except MyException as e:
        log_exception(e)
        return { ... }
```


## Status wrapper

The status wrapper logs details about a Lambda function execution and sends it
to the status API.

The first component that touches the data (typically on upload) sets a "trace
ID", which is then inherited by the following processing steps. This allows the
status API to track what has happened to the data, from upload through the
various processing steps until the data is ready for consumption.

For pipeline components, the status wrapper picks up the trace ID from the
Lambda event automatically.

The status wrapper expects the `SERVICE_NAME` of the Lambda component to be set
in an environment variable, along with `GIT_REV` and `GIT_BRANCH`.

### Usage

Tag the Lambda handler function with `@status_wrapper`.

The handler function should set the `domain` and `domain_id` values using the
`status_add` method:

```python
from okdata.aws.status import status_wrapper, status_add

@status_wrapper
def my_lambda_handler(event, context):
    status_add(domain="dataset", domain_id=f"{dataset_id}/{version}")

    # Regular handler logic here ...

    # The handler can also add a body object containing component-specific information
    status_body = {
        "input": "/tmp/file.txt",
        "output": "/tmp/file.csv",
        "transformation": "text-to-csv",
    }
    status_add(status_body=status_body)
```

By default, this will send a status event with event status `OK` and trace
status `CONTINUE`, meaning that the data pipeline is still running. If the
handler function fails, e.g. throws an exception, it will send event status
`FAILED` and trace status `FINISHED`, in addition to the failure details
(exception).
