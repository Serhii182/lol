import requests
from flask import Flask
from flask import request
from flask import jsonify
import flask_sslify


TOKEN = '473476617:AAHIPuR4TsSysfp2Fu1BCiQ3ZcZrPgw-XGE'
URL = "https://api.telegram.org/bot" + TOKEN + '/'
GOOGLE_API_KEY = 'AIzaSyBv_4QYPOu9uw11JGKQM64aNIpK2e6h98Q'

app = Flask(__name__)
sslify = flask_sslify.SSLify(app)


class Bot:

    photo = 'https://images.pexels.com/photos/207962/pexels-photo-207962.jpeg?w=940&h=650&auto=compress&cs=tinysrgb'
    audio_id_acdc = 'AwADAgADvQADOgABkUlc0jfkyY2oFwI'
    audio_id_cherry = 'AwADAgADFAEAAmG9mUl24CddHk7pvgI'
    video_id = 'CgADAgAD3AADOgABkUlaCGNdhoQKgI'
    last_update_id = None
    command = {
        'btc': 'bitcoin price',
        'weather': 'weather in your city',
        'google': 'www.google.com',
        'hi': 'hello buddy'
    }

    @staticmethod
    def get_updates():
        url = URL + 'getupdates'
        r = requests.get(url)
        return r.json()

    @staticmethod
    def send_message(chat_id, text=None):
        url = URL + 'sendmessage'
        answer = {'chat_id': chat_id, 'text': text}
        r = requests.post(url, json=answer)
        return r.json()

    @staticmethod
    def send_photo(chat_id, photo):
        url = URL + 'sendPhoto'
        answer = {'chat_id': chat_id, 'photo': photo}
        r = requests.post(url, answer)
        return r.json()

    @staticmethod
    def send_audio(chat_id, audio):
        url = URL + 'sendVoice'
        answer = {'chat_id': chat_id, 'voice': audio}
        r = requests.post(url, answer)
        return r.json()

    @staticmethod
    def send_video(chat_id, video):
        url = URL + 'sendVideo'
        answer = {'chat_id': chat_id, 'video': video}
        r = requests.post(url, answer)
        return r.json()


class YahooWeatherForecast:

    def get(self, city):
        url = f"https://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20weather." \
              f"forecast%20where%20woeid%20in%20(select%20woeid%20from%20geo.places(1)%20where%20text%" \
              f"3D%22{city}%22)%20and%20u%3D%22c%22&format=json&env=store%3A%2F%2Fdatatables." \
              f"org%2Falltableswithkeys"
        data = requests.get(url).json()
        try:
            day_data = data["query"]["results"]["channel"]["item"]["forecast"][1]['date']
            weather_data = data["query"]["results"]["channel"]["item"]["forecast"][1]['high']
            forecast = 'today is {} and {} 0C'.format(day_data, weather_data)
            return forecast
        except TypeError:
            print("Where are You ?")


class CityInfo:

    def __init__(self, weather_forecast=None):
        self._weather_forecast = weather_forecast or YahooWeatherForecast()

    def weather_forecast(self):
        return self._weather_forecast.get(self.get_where())

    def get_where(self):
        where = 'Netishin'
        self.city = where
        return self.city


def weather():
    city_info = CityInfo()
    forecast = city_info.weather_forecast()
    return str(forecast)


def get_btc():
    url = 'https://api.coinmarketcap.com/v1/ticker/'
    response = requests.get(url).json()
    price = response[0]['price_usd']
    return str(price) + ' usd'


# -------------------------------------------------------------------
CITIES = ['Netishyn']


def send_location(chat_id, lat, long):
    url = URL + 'sendLocation'
    answer = {'chat_id': chat_id, 'latitude': lat, 'longitude': long}
    r = requests.post(url, json=answer)
    return r.json()


def get_location(chat_id, loc):
    chat_id = chat_id
    city = loc
    location = 'https://maps.googleapis.com/maps/api/geocode/json?address={0}&key={1}'.format(city, GOOGLE_API_KEY)
    data = requests.get(location).json()
    coordinate = data['results'][0]['geometry']['location']
    lat = float(coordinate['lat'])
    lng = float(coordinate['lng'])
    send_location(chat_id, lat, lng)


def get():
    api = 'https://resources.finance.ua/ua/public/currency-cash.json'
    try:
        data = requests.get(api).json()
        organizations = data['organizations']
    except KeyError:
        return 'Вибачте, сервер тимчасово недоступний'
    price = {}
    for organization in organizations:
        title = organization['title']
        try:
            price[title] = float(organization['currencies']['EUR']['bid'])
        except KeyError:
            pass
    return str(sorted(price.items(), key=lambda x: x[1], reverse=True)[0])


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        r = request.get_json()
        chat_id = r['message']['chat']['id']
        text = r['message']['text']
        bot = Bot()
        if text == '/btc':
            bot.send_message(chat_id, get_btc())
        elif text == '/get':
            bot.send_message(chat_id, text=get())
        elif text == '/weather':
            bot.send_message(chat_id, weather())
        elif text == 'google':
            bot.send_message(chat_id, 'www.google.com')
        elif text == "hi":
            bot.send_message(chat_id, 'Привіт, Сергіє, що бажаєте дізнатися ?')
        elif text == '/help':
            bot.send_message(chat_id, bot.command)
        elif text == '/photo':
            bot.send_photo(chat_id, bot.photo)
        elif text == '/audio_acdc':
            bot.send_audio(chat_id, bot.audio_id_acdc)
        elif text == '/audio_cherry':
            bot.send_audio(chat_id, bot.audio_id_cherry)
        elif text == '/video':
            bot.send_video(chat_id, bot.video_id)
        elif text == '/loc':
            get_location(chat_id, CITIES)
        else:
            bot.send_message(chat_id, 'Що вам потрібно ?')
        return jsonify(r)
    return '<h1>hello buddy !</h1>'


if __name__ == '__main__':
    app.run()

