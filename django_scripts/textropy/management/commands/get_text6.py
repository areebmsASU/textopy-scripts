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
        # TODO: Some books need to be deleted manually.

        for book in Book.objects.exclude(raw_text=None):
            lines = book.raw_text.split("\r\n")
            for i in range(len(lines)):
                if lines[i]:
                    book.lines.create(text=lines[i], rel_id=i)
