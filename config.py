from dataclasses import dataclass
import os


@dataclass
class Config:
    categories_count: int = 3
    products_count: int = 5
    default_sleep_timeout: float = 1.0
