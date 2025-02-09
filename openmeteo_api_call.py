import openmeteo_requests
import requests_cache
import pandas as pd
from numpy import ones, round
from retry_requests import retry
from settings import start_time

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://archive-api.open-meteo.com/v1/archive"
params = {
    "latitude": 54.9044,
    "longitude": 52.3154,
    "start_date": f'{start_time[0:10]}',  # "2022-11-22"
    "end_date": f'{start_time[0:10]}',  # "2022-11-23"
    "hourly": ["temperature_2m", "relative_humidity_2m", "precipitation", "rain", "snowfall", "weather_code",
               "surface_pressure", "cloud_cover", "cloud_cover_low", "cloud_cover_mid", "cloud_cover_high",
               "wind_speed_10m", "wind_speed_100m", "wind_direction_10m", "wind_direction_100m", "is_day"],
    "wind_speed_unit": "ms",
    "timezone": "Europe/Moscow"
}
responses = openmeteo.weather_api(url, params=params)

# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]
print(f"Coordinates {response.Latitude()}°E {response.Longitude()}°N")
print(f"Elevation {response.Elevation()} m asl")
print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

# Process hourly data. The order of variables needs to be the same as requested.
hourly = response.Hourly()
hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
hourly_relative_humidity_2m = hourly.Variables(1).ValuesAsNumpy()
hourly_precipitation = hourly.Variables(2).ValuesAsNumpy()
hourly_rain = hourly.Variables(3).ValuesAsNumpy()
hourly_snowfall = hourly.Variables(4).ValuesAsNumpy()
hourly_weather_code = hourly.Variables(5).ValuesAsNumpy()
hourly_surface_pressure = hourly.Variables(6).ValuesAsNumpy()
hourly_cloud_cover = hourly.Variables(7).ValuesAsNumpy()
hourly_cloud_cover_low = hourly.Variables(8).ValuesAsNumpy()
hourly_cloud_cover_mid = hourly.Variables(9).ValuesAsNumpy()
hourly_cloud_cover_high = hourly.Variables(10).ValuesAsNumpy()
hourly_wind_speed_10m = hourly.Variables(11).ValuesAsNumpy()
hourly_wind_speed_100m = hourly.Variables(12).ValuesAsNumpy()
hourly_wind_direction_10m = hourly.Variables(13).ValuesAsNumpy()
hourly_wind_direction_100m = hourly.Variables(14).ValuesAsNumpy()
hourly_is_day = hourly.Variables(15).ValuesAsNumpy()

hourly_data = {"date": pd.date_range(
    start=pd.to_datetime(hourly.Time(), unit="s"),
    end=pd.to_datetime(hourly.TimeEnd(), unit="s"),
    freq=pd.Timedelta(seconds=hourly.Interval()),
    inclusive="left"
)}
hourly_data["temperature_2m"] = hourly_temperature_2m
hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m
hourly_data["precipitation"] = hourly_precipitation
hourly_data["rain"] = hourly_rain
hourly_data["snowfall"] = hourly_snowfall
hourly_data["weather_code"] = hourly_weather_code
hourly_data["surface_pressure"] = hourly_surface_pressure
hourly_data["cloud_cover"] = hourly_cloud_cover
hourly_data["cloud_cover_low"] = hourly_cloud_cover_low
hourly_data["cloud_cover_mid"] = hourly_cloud_cover_mid
hourly_data["cloud_cover_high"] = hourly_cloud_cover_high
hourly_data["wind_speed_10m"] = hourly_wind_speed_10m
hourly_data["wind_speed_100m"] = hourly_wind_speed_100m
hourly_data["wind_direction_10m"] = hourly_wind_direction_10m
hourly_data["wind_direction_100m"] = hourly_wind_direction_100m
hourly_data["is_day"] = hourly_is_day

# hourly_dataframe = pd.DataFrame(data=hourly_data)
# print(hourly_dataframe)

# print('RH: ', hourly_relative_humidity_2m)
print('is day: ', hourly_is_day)
print('precipitation, hrly:', hourly_precipitation)
# print(hourly_cloud_cover)
# print(hourly_wind_speed_10m)

hourly_is_day = [1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1.]


def weather_class(is_day, cloudness, windspeed):
    weatherclass = 0
    if windspeed < 2.:
        if is_day == 1 and cloudness <= 25.:
            weatherclass = 1.
        elif is_day == 1 and cloudness > 25 and cloudness <= 50.:
            weatherclass = 2.
        elif is_day == 1 and cloudness > 50 and cloudness <= 75.:
            weatherclass = 2.
        elif is_day == 1 and cloudness > 75.:
            weatherclass = 4.
        elif is_day == 0 and cloudness < 50.:
            weatherclass = 6.
        elif is_day == 0 and cloudness >= 50.:
            weatherclass = 6.
    elif windspeed < 3. and windspeed >= 2.:
        if is_day == 1 and cloudness <= 25.:
            weatherclass = 2.
        elif is_day == 1 and cloudness > 25 and cloudness <= 50.:
            weatherclass = 2.
        elif is_day == 1 and cloudness > 50 and cloudness <= 75.:
            weatherclass = 3.
        elif is_day == 1 and cloudness > 75.:
            weatherclass = 4.
        elif is_day == 0 and cloudness < 50.:
            weatherclass = 5.
        elif is_day == 0 and cloudness >= 50.:
            weatherclass = 5.
    elif windspeed < 5. and windspeed >= 3:
        if is_day == 1 and cloudness <= 25.:
            weatherclass = 2.
        elif is_day == 1 and cloudness > 25 and cloudness <= 50.:
            weatherclass = 3.
        elif is_day == 1 and cloudness > 50 and cloudness <= 75.:
            weatherclass = 3.
        elif is_day == 1 and cloudness > 75.:
            weatherclass = 4.
        elif is_day == 0 and cloudness < 50.:
            weatherclass = 4.
        elif is_day == 0 and cloudness >= 50.:
            weatherclass = 5.
    elif windspeed < 6. and windspeed >= 5.:
        if is_day == 1 and cloudness <= 25.:
            weatherclass = 3.
        elif is_day == 1 and cloudness > 25 and cloudness <= 50.:
            weatherclass = 4.
        elif is_day == 1 and cloudness > 50 and cloudness <= 75.:
            weatherclass = 4.
        elif is_day == 1 and cloudness > 75.:
            weatherclass = 4.
        elif is_day == 0 and cloudness < 50.:
            weatherclass = 4.
        elif is_day == 0 and cloudness >= 50.:
            weatherclass = 4.
    elif windspeed > 6.:
        if is_day == 1 and cloudness <= 25.:
            weatherclass = 3.
        elif is_day == 1 and cloudness > 25 and cloudness <= 50.:
            weatherclass = 4.
        elif is_day == 1 and cloudness > 50 and cloudness <= 75.:
            weatherclass = 4.
        elif is_day == 1 and cloudness > 75.:
            weatherclass = 4.
        elif is_day == 0 and cloudness < 50.:
            weatherclass = 4.
        elif is_day == 0 and cloudness >= 50.:
            weatherclass = 4.
    return weatherclass


# print('len  is day',len(hourly_is_day))

humidify = []
for i in range(len(hourly_precipitation)):
    if hourly_precipitation[i] > 0:
        humidify.append(2)
    else:
        humidify.append(1)

print(humidify)

# Переименовали переменную `weatherclass` в `stability_classes`
stability_classes = ones((3 * len(hourly_is_day), 1))

for i in range(len(hourly_is_day)):
    stability_classes[i * 3] = weather_class(
        float(hourly_is_day[i]),
        float(hourly_cloud_cover[i]),
        float(hourly_wind_speed_10m[i])
    )
    stability_classes[i + 1] = stability_classes[i]
    stability_classes[i + 2] = stability_classes[i]

RH = round(hourly_relative_humidity_2m, 2)
# print('RH:', RH)
# print(stability_classes)


# print(len(weatherclass))


def get_weather_for_single_point(time):
    """
    Возвращает класс стабильности атмосферы и влажность для указанной временной точки.
    """
    response = openmeteo.weather_api(url, params=params)[0]
    hourly = response.Hourly()

    time_index = list(pd.date_range(
        start=pd.to_datetime(hourly.Time(), unit="s"),
        periods=len(hourly.Variables(0).ValuesAsNumpy()),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        inclusive="left"
    )).index(pd.to_datetime(time))

    if time_index is None:
        raise ValueError("Не удалось найти данные для указанной временной точки.")

    humidity = hourly.Variables(1).ValuesAsNumpy()[time_index]  # Relative humidity
    wind_speed = hourly.Variables(11).ValuesAsNumpy()[time_index]  # Wind speed
    cloud_cover = hourly.Variables(7).ValuesAsNumpy()[time_index]  # Cloud cover
    is_day = hourly.Variables(15).ValuesAsNumpy()[time_index]  # Day or night

    # Убедитесь, что функция weather_class вызывается корректно
    stability_class = weather_class(is_day, cloud_cover, wind_speed)

    return stability_class, humidity

# тестовый запуск функции
# stability_class, humidity = get_weather_for_single_point(start_time[0:10])
# print(stability_class, humidity)
