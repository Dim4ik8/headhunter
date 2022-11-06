import requests
import os

from dotenv import load_dotenv

load_dotenv()
url = 'https://api.superjob.ru/2.0/vacancies/'

def predict_rub_salary_for_superJob(vacancy):
    if (vacancy['payment_from'] or vacancy['payment_to']) and vacancy['currency'] == "rub":
        if vacancy['payment_from'] and vacancy['payment_to']:
            return (int(vacancy['payment_from']) + int(vacancy['payment_to'])) / 2
        if vacancy['payment_from']:
            return int(vacancy['payment_from']) * 1.2
        if vacancy['payment_to']:
            return int(vacancy['payment_to']) * 0.8
    else:
        return None

secret_key = os.getenv('SUPERJOB_KEY')
headers = {'X-Api-App-Id': secret_key}
params = {'keyword': 'программист'}

response = requests.get(url, headers=headers, params=params)
j = response.json()
for i in j['objects']:
    print(i['profession'], ',', i['town']['title'], i['payment_from'], i['payment_to'], i['currency'], '=====', predict_rub_salary_for_superJob(i))

