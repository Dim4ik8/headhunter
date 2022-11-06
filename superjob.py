import requests

from dotenv import load_dotenv

load_dotenv()
url = 'https://api.superjob.ru/2.0/vacancies/'

secret_key = os.getenv('SUPERJOB_KEY')
headers = {'X-Api-App-Id': secret_key}
params = {'keyword': 'доктор'}

response = requests.get(url, headers=headers, params=params)
j = response.json()
for i in j['objects']:
    print(i['profession'], ',', i['town']['title'])