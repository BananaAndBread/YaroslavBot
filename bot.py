import datetime
import time

import telebot
import requests
import re

bot = telebot.TeleBot('1163625212:AAFdbQgw0kWOvVxf5IWg16ibu92oeUiLCsA')

# Yandex API is used: https://yandex.ru/dev/weather/doc/dg/concepts/forecast-test-docpage/. Active for 30 days only.
# These are the required translations to Russian. Every translated key of daytime object (which is contained in
# "parts") is added to the bot response. For example, to add cloudness info from API, is is required to add {
# "cloudness": YOUR TRANSLATOIN}
translation_dict = {
    "temp_min": "Минимальная температура",
    "temp_max": "Максимальная температура",
    "temp_avg": "Средняя температура",
    "feels_like": "Чувствуется как",
    'clear': 'ясно',
    'partly-cloudy': 'малооблачно',
    'cloudy': 'облачно с прояснениями',
    'overcast': 'пасмурно',
    'drizzle': 'морось',
    'light-rain': 'небольшой дождь',
    'rain': 'дождь',
    'moderate-rain': 'умеренно сильный дождь',
    'heavy-rain': 'сильный дождь',
    'continuous-heavy-rain': 'длительный сильный дождь',
    'showers': 'ливень',
    'wet-snow': 'дождь со снегом',
    'light-snow': 'небольшой снег',
    'snow': 'снег',
    'snow-showers': 'снегопад',
    'hail': 'град',
    'thunderstorm': 'гроза',
    'thunderstorm-with-rain': 'дождь с грозой',
    'thunderstorm-with-hail': 'гроза с градом',
    'wind_speed': 'Скорость ветра (в м/с)',
    'condition': 'Условия',
    'night': "Прогноз на ночь",
    'morning': "Прогноз на утро",
    'day': 'Прогноз на день',
    'evening': "Прогноз на вечер",
    'pressure_mm': 'Давление (в мм рт. ст.)'
}


@bot.message_handler(commands=['start'])
def start_message(message):
    keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True)
    keyboard1.row('Получить прогноз погоды!')
    bot.send_message(message.chat.id, 'Чего тебе надобно, старче?', reply_markup=keyboard1)


@bot.message_handler(content_types=['text'])
def send_text(message):
    if message.text == 'Получить прогноз погоды!':
        answer = 'Я могу получить прогноз погоды на следующие 7 дней'
        # Output of next 7 days in the keyboard
        keyboard2 = telebot.types.ReplyKeyboardMarkup(False, False)
        next_seven_days = get_next_seven_days()
        keyboard2.add(*next_seven_days)
        bot.send_message(message.chat.id, answer, reply_markup=keyboard2)
    if re.findall("^\d{4}-\d{2}-\d{2}$", message.text):
        # If we got something like a day, try find it
        next_seven_days = get_next_seven_days()
        if message.text not in next_seven_days:
            bot.send_message(message.chat.id, "Я не знаю прогноз на такой день(")
        else:
            forecast = get_weather_forecast(message.text)
            bot.send_message(message.chat.id, forecast)


def get_weather_forecast(date):
    """
    :param date: Date in UTC format
    :return: The forecast output string for the bot
    """
    # Make request to Yandex
    headers = {'X-Yandex-API-Key': '9694cc45-c4f1-4a54-8f4e-f6f3d01abcf4'}
    response = requests.get(f'https://api.weather.yandex.ru/v2/forecast?\
 lat=57.6261 \
 & lon=39.8845\
 & [lang=ru_RU]\
 & [limit=7]\
 & [hours=true]\
 & [extra=true]', headers=headers).json()

    # Get forecasts
    forecasts = response['forecasts']
    for forecast in forecasts:
        if forecast['date'] == date:
            parsed_forecast = parse_forecast(forecast)
            return parsed_forecast
    return "Я не знаю прогноз на этот день ((("


def get_next_seven_days():
    """
    :return: List of next 7 days ( including current day)
    """
    today = datetime.date.today()
    next_seven_days = []
    for i in range(7):
        tomorrow_utc = today + datetime.timedelta(days=i)
        next_seven_days.append(str(tomorrow_utc))
    return next_seven_days


def parse_forecast(forecast):
    """
    :param forecast: forecast got from API
    :return: The forecast output string for the bot
    """
    daytimes_forecast = {}
    for daytime in forecast['parts']:
        if daytime in translation_dict:
            daytime_forecast = forecast['parts'][daytime]
            parsed = parse_daytime_forecast(daytime_forecast)
            daytimes_forecast[translation_dict[daytime]] = parsed

    daytimes_forecast = beautify_dict_output(daytimes_forecast)
    final_output = ""
    for string in daytimes_forecast:
        final_output = final_output + string
    return final_output


def beautify_dict_output(some_dict):
    """
    Make dictionary more readable for a human
    :param some_dict:  Some dictionary
    :return:  A list of tabulated strings
    """
    return beautify_dict_output_impl(some_dict, 0)


def beautify_dict_output_impl(some_dict, num_of_tab):
    tab = "   "
    strings = []
    if type(some_dict) != dict:
        return [str(some_dict)]
    for key in some_dict:
        current_string = "\n" + tab * num_of_tab + key + ": "
        values = beautify_dict_output_impl(some_dict[key], num_of_tab + 1)
        strings.append(current_string)
        for value in values:
            strings.append(value)
    return strings


def parse_daytime_forecast(daytime):
    """
    :param daytime: Daytime dictionary from 'parts' from API
    :return: Dictionary with keys, which are possible to translate and translated values
    """
    daytime_forecast = {}
    for key in daytime.keys():
        if key in translation_dict.keys():
            translated_key = translation_dict[key]
            value = daytime[key]
            if value in translation_dict.keys():
                value = translation_dict[value]
            daytime_forecast[translated_key] = value
    return daytime_forecast

while True:
    try:
        print("Start working")
        bot.polling()
        break
    except telebot.apihelper.ApiException as e:
        # Here we can write something to log this exception
        bot.stop_polling()
        time.sleep(3)

