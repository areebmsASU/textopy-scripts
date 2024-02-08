from django.utils import timezone
from collections import Counter
from time import sleep

import requests as r
from bs4 import BeautifulSoup

from django.core.management.base import BaseCommand
from textropy.models import Book, Author

from stop_words import STOP_WORDS


class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def handle(self, *args, **options):
        # Economics URL was scraped to get all of the gutenberg book_ids.
        for book in Book.objects.exclude(raw_text=None):
            word_counts = Counter(book.raw_text.split())
            for stop_word in STOP_WORDS:
                del word_counts[stop_word]

            print(book.title, word_counts.most_common(10))
