from django.utils import timezone
from collections import defaultdict
from time import sleep

import requests as r
from bs4 import BeautifulSoup

from django.core.management.base import BaseCommand
from entropy.models import Book, Author, Subject

BASE_URL = "https://gutenberg.org"
MAX_BOOK_IDS_PER_PAGE = 25


def get_raw_text(book):
    book.raw_text = BeautifulSoup(r.get(book.raw_text_url).content, "html.parser").text
    book.save(update_fields=["raw_text"])


class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def handle(self, *args, **options):
        # Economics URL was scraped to get all of the gutenberg book_ids.
        print(Book.objects.filter(skipped=False).count())
        for author in Author.objects.all():
            print(author.name)
            for book in author.books.filter(skipped=False):
                get_raw_text(book)
                sleep(1)
