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
