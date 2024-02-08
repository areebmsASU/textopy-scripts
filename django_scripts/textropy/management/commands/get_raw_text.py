from time import sleep

from django.core.management.base import BaseCommand

from textropy.models import Subject, Book, Author


class Command(BaseCommand):
    help = "Economics URL was scraped to get all of the gutenberg book_ids."

    def handle(self, *args, **options):
        econ, created = Subject.objects.get_or_create(
            label="Economics", gutenberg_id=1301
        )
        if created:
            econ.get_books()

        for book in Book.objects.all():
            new = book.get_raw_metadata(force_refresh=False)
            if new:
                book.add_authors()
                book.add_subjects()
                sleep(1)

        Book.objects.get(gutenberg_id=38194).skip("DUPLICATE")

        for book in econ.books.filter(skipped=False):
            print(book.gutenberg_id, book.title)
            if book.authors.count() == 0:
                book.skip("NO_AUTHOR")
            elif "English" not in book.raw_metadata["language"]:
                book.skip("LANG")
            elif book.raw_metadata["category"] != ["Text"]:
                book.skip("FORMAT")
            book.get_raw_text()

        print(econ.books.filter(skipped=False).count())
