from weather import create_app
import unittest


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


if __name__ =='__main__':
    unittest.main()

