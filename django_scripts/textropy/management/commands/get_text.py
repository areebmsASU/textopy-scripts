from django.utils import timezone
from collections import defaultdict
from time import sleep

import requests as r
from bs4 import BeautifulSoup

from django.core.management.base import BaseCommand
from entropy.models import Book, Author

BASE_URL = "https://gutenberg.org"
MAX_BOOK_IDS_PER_PAGE = 25


class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def handle(self, *args, **options):
        # Economics URL was scraped to get all of the gutenberg book_ids.
        ["NO AUTHOR"]
        for book_vals in Book.objects.filter(skipped=False):
            if not book_vals.author:
                book_vals.skip("NO AUTHOR")
            elif "English" not in book_vals.raw_metadata["language"]:
                book_vals.skip("NOT ENGLISH")
            elif book_vals.raw_metadata["category"] != ["Text"]:
                book_vals.skip("NOT A TEXT")
            elif len(book_vals.author.split(" & ")) > 2:
                book_vals.skip("TOO MANY AUTHORS")

            for i in range(len(book_vals.raw_metadata["author"])):
                life_span = book_vals.raw_metadata["author"][i].split(", ")[-1]
                if "-" not in life_span:
                    continue
                name = book_vals.raw_metadata["author"][i].replace(", " + life_span, "")
                gutenberg_id = book_vals.raw_metadata["author_link"][i].split("/")[-1]
                author, _ = Author.objects.get_or_create(
                    name=name, gutenberg_id=gutenberg_id, life_span=life_span
                )
                book_vals.authors.add(author)
