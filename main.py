import datetime
import pandas
import argparse
from http.server import HTTPServer, SimpleHTTPRequestHandler

from jinja2 import Environment, FileSystemLoader, select_autoescape


def get_year_word(number):
    if number % 10 == 1 and number % 100 != 11:
        return 'год'
    elif number % 10 in [2, 3, 4] and number % 100 not in [12, 13, 14]:
        return 'года'
    else:
        return 'лет'


def main():
    parser = argparse.ArgumentParser(
        description='Генерирование страницы сайта с подгрузкой информации из xlsx-файла',
    )
    parser.add_argument(
        '--path',
        '-p',
        type=str,
        nargs='?',
        default='products.xlsx',
        help='Путь к excel-файлу',
    )
    args = parser.parse_args()
    path = args.path

    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')

    date_of_creation = datetime.datetime(year=1920,month=1,day=1)
    now = datetime.datetime.now()
    age = now.year - date_of_creation.year
    declension = get_year_word(age)
    age_text = f'Уже {age} {declension} с вами'

    excel_data = pandas.read_excel(
        path,
        na_values=None,
        keep_default_na=False,
    )

    grouped_products = {}
    for category, group in excel_data.groupby('Категория'):
        grouped_products[category] = group.to_dict('records')

    rendered_page = template.render(assortment=grouped_products, year=age_text)

    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)

    server = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
    server.serve_forever()


if __name__ == '__main__':
    main()