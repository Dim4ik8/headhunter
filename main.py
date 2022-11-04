import requests

def main():
    url = 'https://api.hh.ru/vacancies/'
    params = {'text': 'программист', 'per_page': '100', "search_field": "name"}
    response = requests.get(url, params=params)
    response.raise_for_status()

    vacancies = response.json()
    print(vacancies)

if __name__ == '__main__':
    main()