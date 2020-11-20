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
