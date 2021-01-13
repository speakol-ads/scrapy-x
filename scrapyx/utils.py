import importlib
import inspect
import os
import threading
from typing import Callable

import scrapy
import scrapydo
from fastapi import FastAPI
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from uvicorn import Config, Server


def thread(fn: Callable, params: set) -> threading.Thread:
    t = threading.Thread(
        target=fn,
        daemon=True,
        args=params,
    )

    t.start()

    return t


def threads(count: int, fn: Callable, params: set) -> list:
    threads = []

    for _ in range(count):
        threads.append(thread(fn, params))

    return threads


def discover_spiders(settings: Settings) -> dict:
    """
    tries to discover the available spiders via the provided project settings
    """

    spiders = {}

    def is_spider(obj):
        return inspect.isclass(obj) and issubclass(obj, scrapy.Spider)

    for spiders_module in settings.get("SPIDER_MODULES"):
        parent_mod = importlib.import_module(spiders_module)
        for filename in os.listdir(os.path.dirname(parent_mod.__file__)):
            if not filename.startswith("_"):
                mod_name = filename.split('.')[0]
                mod = importlib.import_module(
                    spiders_module + '.' + mod_name
                )
                for _, v in inspect.getmembers(mod, is_spider):
                    spiders[v.name] = v

    return spiders


def crawl(spider: scrapy.Spider, settings: scrapy.settings.Settings, args: dict) -> scrapy.crawler.Crawler:
    crawler = scrapydo.run_spider(
        spider,
        settings=settings,
        return_crawler=True,
        capture_items=True,
        **args
    )

    return crawler
