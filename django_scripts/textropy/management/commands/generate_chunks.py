from django.core.management.base import BaseCommand
from django.db import transaction

from textropy.models import Book, Chunk


class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def handle(self, *args, **options):
        # Economics URL was scraped to get all of the gutenberg book_ids.
        BULK_SIZE = 600
        for book in Book.objects.filter(skipped=False).order_by("id"):
            lines = book.raw_text.split("\r\n")
            with transaction.atomic():  # PROBABLY IN THE WRONG PLACE
                for i in range(0, len(lines), BULK_SIZE):
                    print(book.gutenberg_id, book.title, i, len(lines))
                    line_set = lines[i : i + BULK_SIZE]
                    for j in range(len(line_set)):
                        if lines[i + j]:
                            book.lines.get_or_create(text=lines[i + j], rel_id=(i + j))
                        if (i + j) % Chunk.CHUNK_SIZE == 0:
                            book.chunks.get_or_create(
                                text=" ".join(
                                    map(
                                        lambda s: s.strip(),
                                        lines[(i + j) : (i + j) + Chunk.CHUNK_SIZE],
                                    )
                                ),
                                rel_id=int((i + j) // Chunk.CHUNK_SIZE),
                            )
