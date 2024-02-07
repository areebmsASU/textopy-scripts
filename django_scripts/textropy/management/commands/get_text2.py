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
        ["NO AUTHOR"]
        for author in Author.objects.all():
            print(author.name, author.books.all().count())
            for book in author.books.all():
                for i in range(len(book.raw_metadata["subject"])):
                    subject, _ = Subject.objects.get_or_create(
                        label=book.raw_metadata["subject"][i],
                        gutenberg_id=book.raw_metadata["subject_link"][i].split("/")[
                            -1
                        ],
                    )
                    book.subjects.add(subject)
