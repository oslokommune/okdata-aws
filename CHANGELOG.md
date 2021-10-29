## ?.?.?

* Replace the asynchronous logging wrapper with a method to register
  FastAPI logging middleware.

  ```python
  from okdata.aws.logging import add_fastapi_logging

  app = FastAPI()
  add_fastapi_logging(app)
  ```

## 0.4.1

* HTTP errors from the status API is no longer propagated to users of
  `@status_wrapper`; the errors are logged instead.

## 0.4.0

* An asynchronous variant of the logging wrapper is now available:

  ```python
  @logging_wrapper("my-service", async_wrapper=True)
  async def handler(event, context):
      return await foo()
  ```

## 0.3.3

* The minimum required version of `okdata-sdk` has been raised to 0.8.1 to
  support Keycloak v12.

## 0.3.2

* Fix bug in validator `ensure_format_of_error`.

## 0.3.1

* The field `errors` has been added to `StatusData`.

## 0.3.0

* The `okdata` namespace package now uses the old-style `pkg_resources`
  declaration instead of being an implicit namespace package.

* The status wrapper no longer throws an exception when receiving an HTTP error
  response from the status API, but logs it instead.

## 0.2.0

* Added `status_wrapper` and `status_add` from common-python under
  `okdata.aws.status`.

## 0.1.0

* Initial release based on the old `common-python` project.
