from django.utils import timezone
from collections import defaultdict
from time import sleep

import requests as r
from bs4 import BeautifulSoup

from django.core.management.base import BaseCommand
from entropy.models import Book, Author, Subject

BASE_URL = "https://gutenberg.org"
MAX_BOOK_IDS_PER_PAGE = 25


class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def handle(self, *args, **options):
        # Economics URL was scraped to get all of the gutenberg book_ids.
        for author in Author.objects.all():
            has_economics_books = 1301 in list(
                author.books.values_list("subjects__gutenberg_id", flat=True).distinct()
            )
            if not has_economics_books:
                for book in author.books.all():
                    book.skip("AUTHOR HAS NO ECONOMICS BOOK")
