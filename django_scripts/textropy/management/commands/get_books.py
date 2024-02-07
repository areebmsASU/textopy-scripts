from django.utils import timezone
from collections import defaultdict
from time import sleep

import requests as r
from bs4 import BeautifulSoup

from django.core.management.base import BaseCommand
from entropy.models import Book

BASE_URL = "https://gutenberg.org"
MAX_BOOK_IDS_PER_PAGE = 25


def get_books(base_url):
    page_book_ids = []
    num_book_ids = -1
    while num_book_ids == -1 or (
        len(page_book_ids) != num_book_ids
        and len(page_book_ids) % MAX_BOOK_IDS_PER_PAGE == 0
    ):
        sleep(1)
        num_book_ids = len(page_book_ids)
        book_list_page = r.get(base_url + f"?start_index={num_book_ids+1}")
        for link in BeautifulSoup(book_list_page.text, "html.parser").find_all("a"):
            if (
                "ebooks" in link.get("href", "")
                and link["href"].split("/")[2].isdigit()
                and link["href"].split("/")[2] not in page_book_ids
            ):
                Book.objects.get_or_create(gutenberg_id=link["href"].split("/")[2])
                page_book_ids.append(link["href"].split("/")[2])
    return page_book_ids


def get_raw_metadata(book):
    metadata = defaultdict(list)
    for tr in (
        BeautifulSoup(r.get(book.metadata_url).content, "html.parser")
        .find("table", class_="bibrec")
        .find_all("tr")
    ):
        key = tr.find("th")
        if key is not None:
            value = tr.find("td")
            a = value.find("a")
            href = a["href"] if a else None
            key = key.text.lower().replace(" ", "-").replace(".", "").replace("-", "_")
            metadata[key].append([_ for _ in tr.find("td").text.split("\n") if _][0])
            if href:
                metadata[key + "_link"].append(href)

    book.raw_metadata = dict(metadata)
    book.metadata_retrieved_date = timezone.now()

    book.title = book.raw_metadata["title"][0]
    book.author = " & ".join(book.raw_metadata.get("author", []))
    book.subject = "; ".join(book.raw_metadata.get("subject", []))
    book.save(
        update_fields=[
            "raw_metadata",
            "metadata_retrieved_date",
            "title",
            "author",
            "subject",
        ]
    )
    return book.raw_metadata


class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def handle(self, *args, **options):
        # Economics URL was scraped to get all of the gutenberg book_ids.
        subject_book_ids = get_books(f"{BASE_URL}/ebooks/subject/1301")
        sleep(1)
        for book in Book.objects.filter(raw_metadata__isnull=True):
            raw_metadata = get_raw_metadata(book)
            sleep(1)
            author_links = set()
            for link in raw_metadata.get("author_link", []):
                author_links.add(link)

            for link in author_links:
                author_book_ids = get_books(BASE_URL + link)
                sleep(1)

        for book in Book.objects.filter(raw_metadata__isnull=True):
            raw_metadata = get_raw_metadata(book)
            sleep(1)
