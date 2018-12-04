from weather import create_app
from datetime import datetime, timedelta
import unittest, pytz


class RouteTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app().test_client()

    def test_ping_200(self):
        rv = self.app.get('/ping')
        print(rv)
        assert rv.status == '200 OK'

    def test_forecast_Leeds_200(self):
        rv = self.app.get('/forecast/Leeds/')
        print(rv)
        assert rv.status == '200 OK'

    def test_forecast_InvalidCityName_404(self):
        rv = self.app.get('/forecast/InvalidCityName/')
        print(rv)
        assert rv.status_code == 404

    def test_forecast_date_in_the_past_400(self):
        rv = self.app.get('/forecast/Leeds/?at=2018-10-04T12:17:40+0000')
        print(rv)
        assert rv.status_code == 400

    def test_forecast_date_6_days_in_the_future_400(self):
        future_day = pytz.utc.localize(datetime.utcnow()) + timedelta(days=6)

        rv = self.app.get(f'/forecast/Leeds/?at={future_day.isoformat()}')
        print(rv)
        assert rv.status_code == 400

    def test_forecast_unparsable_date_400(self):
        rv = self.app.get('/forecast/Leeds/?at=unparsable')
        print(rv)
        assert rv.status_code == 400

    def test_forecast_valid_date_200(self):
        future_day = pytz.utc.localize(datetime.utcnow()) + timedelta(days=3)

        rv = self.app.get(f'/forecast/Leeds/?at={future_day.isoformat()}')
        print(rv)
        assert rv.status_code == 200


if __name__ =='__main__':
    unittest.main()

