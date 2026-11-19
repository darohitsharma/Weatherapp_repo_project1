import os
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import app
import requests


class WeatherTests(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_get_is_local(self):
        with patch('app.requests.get') as get:
            response = self.client.get('/')
            self.assertEqual(response.status_code, 200)
            self.assertNotIn(b'name="appid"', response.data)
            get.assert_not_called()

    def test_blank_city_denied(self):
        with patch('app.requests.get') as get:
            self.assertEqual(self.client.post('/weatherapp', data={'city': ''}).status_code, 400)
            get.assert_not_called()

    def test_units_allowlist(self):
        self.assertEqual(self.client.post('/weatherapp', data={'city': 'Example', 'units': 'other'}).status_code, 400)

    def test_missing_key_denied(self):
        with patch.dict(os.environ, {}, clear=True), patch('app.requests.get') as get:
            self.assertEqual(self.client.post('/weatherapp', data={'city': 'Example'}).status_code, 503)
            get.assert_not_called()

    def response(self, status=200, payload=None):
        response = Mock(status_code=status)
        response.json.return_value = payload or {'name': 'Example City', 'sys': {'country': 'XX'}, 'main': {'temp': 20}, 'weather': [{'description': 'invented clear conditions'}]}
        return response

    def post_with(self, response):
        with patch.dict(os.environ, {'OPENWEATHER_API_KEY': 'synthetic-test-key'}), patch('app.requests.get', return_value=response) as get:
            result = self.client.post('/weatherapp', data={'city': 'Example', 'units': 'metric'})
            self.assertEqual(get.call_args.kwargs['timeout'], 8)
            return result

    def test_mocked_success(self):
        response = self.post_with(self.response())
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Example City', response.data)
        self.assertNotIn(b'synthetic-test-key', response.data)

    def test_not_found(self):
        self.assertEqual(self.post_with(self.response(404)).status_code, 404)

    def test_rate_limit(self):
        self.assertEqual(self.post_with(self.response(429)).status_code, 503)

    def test_bad_json_shape(self):
        self.assertEqual(self.post_with(self.response(payload={'unexpected': True})).status_code, 502)

    def test_timeout_does_not_leak(self):
        with patch.dict(os.environ, {'OPENWEATHER_API_KEY': 'synthetic-test-key'}), patch('app.requests.get', side_effect=requests.Timeout('private URL omitted')):
            response = self.client.post('/weatherapp', data={'city': 'Example'})
            self.assertEqual(response.status_code, 502)
            self.assertNotIn(b'private URL', response.data)

    def test_html_escaping(self):
        payload = self.response().json.return_value
        payload['name'] = '<script>alert(1)</script>'
        response = self.post_with(self.response(payload=payload))
        self.assertNotIn(b'<script>alert(1)</script>', response.data)


if __name__ == '__main__':
    unittest.main()
