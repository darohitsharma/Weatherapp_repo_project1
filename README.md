# Current Weather, Flask Learning App

A small Flask application that requests current city weather from OpenWeather. It is **not a weather forecast**, alerting service or production deployment.

## Behavior

- GET renders a local city/unit form without making an external request.
- A valid POST requests current conditions with an eight-second timeout.
- City length and unit values are validated. Units are metric (Celsius), imperial (Fahrenheit) or standard (Kelvin).
- Provider errors, timeouts, unknown cities and malformed responses show bounded messages, not raw response bodies or connection details.
- The API key is configured on the server through `OPENWEATHER_API_KEY`, never entered in the browser form.
- Results are HTML-escaped, not stored by this code, and responses use `Cache-Control: no-store`.

The app does not save lookup history, but configured lookups send the city to OpenWeather. Server/provider infrastructure may have its own logs. Never place a secret in a city field, URL, commit or chat.

## Local setup

```sh
python -m venv .venv
# Activate for your operating system.
python -m pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5002`. Debug mode is off and the development server binds localhost. Without a key, GET still works and a submitted lookup shows a configuration message without contacting the provider.

If you already have an authorized OpenWeather account/key, set `OPENWEATHER_API_KEY` privately in the server environment. No account or key was created, used or tested in this cleanup. Do not assume a particular plan, quota, availability or price. Review the provider's current terms before enabling real traffic.

Official endpoint/parameter reference: [OpenWeather current weather documentation](https://openweathermap.org/current).

## Test without an API key

```sh
python -m unittest discover -s tests -v
```

Ten tests mock HTTP responses. They cover local GET, input validation, missing configuration, success, not-found, rate-limit, malformed response, timeout and escaping. No real provider requests are made. A rendered synthetic result was visually checked; it is not live weather evidence.

The existing requirements are unpinned. Flask/requests tests were run in an isolated local dependency directory during cleanup, not a locked production environment. No hosting/deployment is claimed.

## Security and deployment limits

- The API key stays server-side, but the provider receives it. Never echo request URLs or exception text into pages/logs.
- POST is not inherently secure without HTTPS. Do not expose the Flask development server publicly.
- A production service needs a reviewed deployment, HTTPS, secret storage, rate limiting/abuse controls, monitoring and provider quota policy. This learning app does not implement them.
- A city name is not exact user location, and current conditions can be stale or differ locally. Do not use this app for emergency decisions.
- Original repository/history are retained; no duplicate-looking weather repo was merged or deleted.
