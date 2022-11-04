import requests

def main():
    url = 'https://api.hh.ru/vacancies/'
    params = {'text': 'программист', 'per_page': '100', 'search_field': 'name', 'premium': True, 'area': '1',
              'date_from': '2022-10-04'}
    response = requests.get(url, params=params)
    response.raise_for_status()

    vacancies = response.json()
    print(vacancies)

if __name__ == '__main__':
    main()