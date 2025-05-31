import requests

api = "d1cd75a8bb9b14afc7b25af9fe33c5c0"
city = 'Kuwait'
url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api}&units=metric"

r = requests.get(url)

if r.status_code == 200:
    data = r.json()
    print("Temperature:", data["main"]["temp"], "°C")
else:
    print("API Error:", r.status_code)
    print("Response:", r.text)
