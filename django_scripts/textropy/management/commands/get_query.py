from django.utils import timezone
from collections import defaultdict
from time import sleep

import requests as r
from bs4 import BeautifulSoup

from django.core.management.base import BaseCommand
from entropy.models import Book, Author, Subject, Line

BASE_URL = "https://gutenberg.org"
MAX_BOOK_IDS_PER_PAGE = 25


class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def handle(self, *args, **options):
        # TODO: Some books need to be deleted manually.

        print(
            Line.objects.filter(book__gutenberg_id=3300, rel_id__gte=0)
            .values("rel_id", "text")
            .order_by("rel_id")[:30]
            .query
        )
