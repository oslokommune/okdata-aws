## 5.0.0 - 2025-06-27

* Added support for Python 3.13.
* Dropped support for Python 3.8 which has reached end of life and Python 3.9
  which is very soon reaching end of life.
* Increased the okdata-sdk minimum version requirement to be able to upgrade
  away from the vulnerable urllib3 v1.x dependency.

## 4.1.0 - 2024-04-17

* Deprecated FastAPI `on_event` hooks have been replaced with a "lifespan"
  context manager for logging configuration. This requires `fastapi>=0.93`.
* Updated okdata-sdk version requirement to remove the vulnerable ecdsa
  dependency.

## 4.0.0 - 2024-03-21

* `okdata.aws.status.status_wrapper` now supports an optional argument for
  configuring the SDK instance used to call the status API.

  Current users must update their usage from:

  ```python
  @status_wrapper
  def foo():
      ...
  ```

  To:

  ```python
  @status_wrapper()
  def foo():
      ...
  ```

## 3.0.1 - 2024-03-21

* Status data exceptions are now accurately converted to strings when exported
  as JSON.

## 3.0.0 - 2024-03-18

* Refactored status data helpers to adopt standard dataclasses in place of
  Pydantic, preventing Pydantic from being included as a transitive dependency
  for projects utilizing these helpers.

## 2.2.0 - 2024-03-18

* `okdata.aws.status.sdk.Status` now accepts an additional optional
  parameter, `sdk_config`, which allows the underlying Status SDK to
  be configured.

## 2.1.0 - 2024-02-15

* New utility function `okdata.aws.ssm.get_secret` for retrieving secure strings
  from AWS SSM.
* Updated dependencies.

## 2.0.0 - 2023-11-17

* Added support for Python 3.10, 3.11, and 3.12.
* Dropped support for Python 3.7 which is being phased out by AWS. Python 3.8+
  is now required.
* Fixed a bug in the logging module when the event from AWS contains
  `{"headers": null}`.

## 1.0.1 - 2023-02-16

* Updated dependencies.

## 1.0.0 - 2021-10-29

* Replace the asynchronous logging wrapper with a method to register
  FastAPI logging middleware.

  ```python
  from okdata.aws.logging import add_fastapi_logging

  app = FastAPI()
  add_fastapi_logging(app)
  ```

## 0.4.1 - 2021-09-27

* HTTP errors from the status API is no longer propagated to users of
  `@status_wrapper`; the errors are logged instead.

## 0.4.0 - 2021-06-11

* An asynchronous variant of the logging wrapper is now available:

  ```python
  @logging_wrapper("my-service", async_wrapper=True)
  async def handler(event, context):
      return await foo()
  ```

## 0.3.3 - 2021-05-06

* The minimum required version of `okdata-sdk` has been raised to 0.8.1 to
  support Keycloak v12.

## 0.3.2 - 2021-02-04

* Fix bug in validator `ensure_format_of_error`.

## 0.3.1 - 2021-02-01

* The field `errors` has been added to `StatusData`.

## 0.3.0 - 2021-01-07

* The `okdata` namespace package now uses the old-style `pkg_resources`
  declaration instead of being an implicit namespace package.

* The status wrapper no longer throws an exception when receiving an HTTP error
  response from the status API, but logs it instead.

## 0.2.0 - 2020-11-30

* Added `status_wrapper` and `status_add` from common-python under
  `okdata.aws.status`.

## 0.1.0 - 2020-11-20

* Initial release based on the old `common-python` project.
