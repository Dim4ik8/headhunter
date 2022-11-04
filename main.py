import requests
from pprint import pprint

def main():
    url = 'https://api.hh.ru/vacancies/'
    languages = ['Javascript', 'Java', 'Python', 'Ruby', 'PHP', 'C#', 'C', 'Go', 'Swift', 'Scala']

    statistics = {}
    for language in languages:
        params = {'text': f'программист {language}', 'per_page': '100', "search_field": "name", 'premium': True,
                  'area': '1'}

        response = requests.get(url, params=params)
        response.raise_for_status()

        vacancies = response.json()
        if int(vacancies['found']) > 100:
            statistics[language] = vacancies['found']

    pprint(statistics)


if __name__ == '__main__':
    main()