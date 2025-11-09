from celery import shared_task
import requests


def get_exchange_rate():
    api_key = 'c03b35ab1e419bbbd3321e32'
    url = f'https://v6.exchangerate-api.com/v6/{api_key}/latest/RUB'

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()["conversion_rates"]

        myset = {}
        for key, value in data.items():
            myset[key] = round(1/value,2)
        return myset