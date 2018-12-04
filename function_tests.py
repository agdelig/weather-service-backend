import unittest, iso8601, pytz
from datetime import datetime, timedelta
from weather.endpoints.forecast.routes import parse_date
from weather.endpoints.common.custom_exceptions import DateException


class ForecastFunctionTests(unittest.TestCase):

    def test_date_parsing(self):
        checked_date = pytz.utc.localize(datetime.utcnow() + timedelta(hours=1))
        url = f'http://www.domain/something/?at={checked_date}'
        parsed_date = parse_date(url)

        self.assertEqual(parsed_date, checked_date)

    def test_date_in_the_past(self):
        checked_date = pytz.utc.localize(datetime.utcnow() + timedelta(days=-1))
        url = f'http://www.domain/something/?at={checked_date}'
        parsed_date = 5

        with self.assertRaises(DateException):parse_date(url)

    def test_date_6_days_ahead(self):
        checked_date = pytz.utc.localize(datetime.utcnow() + timedelta(days=6))
        url = f'http://www.domain/something/?at={checked_date}'
        parsed_date = 5

        with self.assertRaises(DateException):parse_date(url)

    def test_invalid_date_string(self):
        invalid_date_string = 'nuisance'
        url = f'http://www.domain/something/?at={invalid_date_string}'
        parsed_date = 5

        with self.assertRaises(DateException):parse_date(url)


if __name__ == '__main__':
    unittest.main()

