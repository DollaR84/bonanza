import asyncio
import random
import uuid

from aiohttp import ClientSession

from bs4 import BeautifulSoup

from config import Config

from fake_useragent import UserAgent

from schemas import Category, Product, ProductDetails


class Parser:

    def __init__(self, config: Config):
        self.cfg = config
        self.ua = UserAgent()

        self.url = 'https://www.bonanza.com'
        self.results: list[Product] = []
        random.seed()

    @property
    def headers(self) -> dict:
        return {
            "Origin": self.url,
            "User-Agent": self.ua.random,
        }

    async def sleep(self):
        timeout = random.random() + self.cfg.default_sleep_timeout
        await asyncio.sleep(timeout)

    async def run(self):
        async with ClientSession(headers=self.headers) as session:
            categories = await self.get_categories(session)

            for category in categories[:self.cfg.categories_count]:
                await self.parse_products(session, category.url)

        return self.results

    async def fetch(self, session: ClientSession, url: str):
        data = ""
        async with session.get(url) as response:
            data = await response.text()
            await self.sleep()

        return data

    async def get_categories(self, session: ClientSession) -> list[Category]:
        data = await self.fetch(session, self.url)
        if not data:
            raise ValueError(f"Error get categories from url: {self.url}")

        bs = BeautifulSoup(data, "html.parser")
        return [
            Category(name=category.text.strip(), url=category.get("href"))
            for category in bs.find_all('a', {"class": "link_to_search"})
        ]

    async def parse_product_details(self, session: ClientSession, product_url: str):
        data = await self.fetch(session, product_url)
        bs = BeautifulSoup(data, 'html.parser')

        image = bs.find("div", {"class": "item_image_container"}).find("img").get("src")
        description_block = bs.find('div', class_="plain_text_description loading")
        description_url = ''.join([self.url, description_block.get("data-url")])
        description = await self.fetch(session, description_url)

        color, size = None, None
        info = bs.find('table', {'class': 'extended_info_table'})
        for row in info.find_all('tr', {'class': 'extended_info_row'}):
            if 'color' in row.find('th').text.lower():
                color = row.find('td').text.strip()
            if 'size' in row.find('th').text.lower():
                size = row.find('td').text.strip()

        return ProductDetails(
            image=image,
            description=description,
            color=color,
            size=size,
        )

    async def parse_products(self, session: ClientSession, url: str):
        data = await self.fetch(session, url)
        if not data:
            raise ValueError(f"Error get data from url: {url}")

        bs = BeautifulSoup(data, "html.parser")
        for product in bs.find_all("div", {"class": "search_result_item"})[:self.cfg.products_count]:
            product_id = product.get("id").replace("item-", "")
            title_block = product.find("div", {"class": "item_title"}).find("a")
            title = title_block.text.strip()
            product_url = title_block.get("href")
            product_url = "".join([self.url, product_url])
            price = product.find("div", {"class": "item_price_and_icons"})

            details = await self.parse_product_details(session, product_url)

            self.results.append(Product(
                id=str(int(uuid.uuid4())),
                product_id=product_id,
                title=title,
                url=product_url,
                price=".".join([
                    price.find("span", {"class": "money-whole"}).text,
                    price.find("span", {"class": "money-decimal"}).text
                ]),
                **details.dict(),
            ))
