import asyncio

from config import Config

from parser import Parser

from saver import CSVSaver


async def main():
    config = Config()
    parser = Parser(config)
    products = await parser.run()
    saver = CSVSaver(config)
    saver.save(products)


if "__main__" == __name__:
    asyncio.run(main())
