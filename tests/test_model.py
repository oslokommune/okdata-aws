import pytest
from pydantic.error_wrappers import ValidationError

from okdata.aws.status.model import StatusData

OK_ERROR = {"message": {"nb": "Det er et problem", "en": "There is a problem"}}


class TestStatusData:
    def test_errors_entry_valid(self):

        params = {"errors": [OK_ERROR, OK_ERROR]}
        result = StatusData(**params)
        assert isinstance(result, StatusData)
        assert result.errors[0] == OK_ERROR

    def test_errors_entry_not_dict(self):

        params = {"errors": [OK_ERROR, "This is string, not a dict."]}
        with pytest.raises(ValidationError):
            StatusData(**params)

    def test_errors_entry_no_message(self):

        params = {"errors": [OK_ERROR, {"Bad key": {}}]}
        with pytest.raises(ValueError):
            StatusData(**params)

    def test_errors_entry_no_nb(self):

        params = {"errors": [OK_ERROR, {"message": {"Bad key": "foo", "en": "bar"}}]}
        with pytest.raises(ValueError):
            StatusData(**params)
