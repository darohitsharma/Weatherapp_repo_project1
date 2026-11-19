"""Current-weather lookup. No network request occurs on import or GET."""
import os
from flask import Flask, render_template, request
import requests

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 8192
ENDPOINT = 'https://api.openweathermap.org/data/2.5/weather'
UNITS = {'metric': '°C', 'imperial': '°F', 'standard': 'K'}


def page(error=None, weather=None, status=200, city='', units='metric'):
    return render_template('index.html', error=error, weather=weather,
                           city=city, units=units), status


@app.route('/')
@app.route('/weatherapp', methods=['GET', 'POST'])
def weather():
    if request.method == 'GET':
        return page()
    city = request.form.get('city', '').strip()
    units = request.form.get('units', 'metric')
    if not city or len(city) > 100 or any(ord(c) < 32 for c in city):
        return page('Enter a city name, optionally followed by a country code. Maximum 100 characters.', status=400)
    if units not in UNITS:
        return page('Choose a supported unit system.', status=400, city=city)
    key = os.environ.get('OPENWEATHER_API_KEY', '').strip()
    if not key:
        return page('Weather service is not configured. The server owner must set a local API key.', status=503, city=city, units=units)
    try:
        response = requests.get(ENDPOINT, params={'q': city, 'appid': key, 'units': units}, timeout=8)
        if response.status_code == 404:
            return page('City not found. Try adding a country code.', status=404, city=city, units=units)
        if response.status_code == 429:
            return page('Weather service limit reached. Try again later.', status=503, city=city, units=units)
        if response.status_code != 200:
            return page('Weather provider could not complete the request.', status=502, city=city, units=units)
        data = response.json()
        result = {'name': str(data.get('name', city)),
                  'country': str(data.get('sys', {}).get('country', '')),
                  'temperature': data['main']['temp'], 'unit': UNITS[units],
                  'description': str(data['weather'][0]['description'])}
    except (requests.RequestException, ValueError, KeyError, IndexError, TypeError):
        # Request exceptions can include the URL and key. Never show or log them here.
        return page('Weather service is unavailable or returned an unexpected response.', status=502, city=city, units=units)
    return page(weather=result, city=city, units=units)


@app.after_request
def private_response(response):
    response.headers['Cache-Control'] = 'no-store'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5002, debug=False)
