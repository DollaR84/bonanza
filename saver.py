import csv

from config import Config

from schemas import Product


class CSVSaver:

    def __init__(self, config: Config):
        self.cfg = config

    def save(self, products: list[Product]):
        titles = products[0].dict().keys()

        with open('out.csv', 'w') as file_csv:
            writer = csv.writer(file_csv)
            writer.writerow(titles)
            for product in products:
                writer.writerow(product.dict().values())
