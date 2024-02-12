from django.core.management.base import BaseCommand
from textropy.models import Book, Entropy

from django.db.models import Count, Subquery, OuterRef


class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def handle(self, *args, **options):

        # TODO add value related fitler
        # chunks_with_entropy = (
        #    Entropy.objects.filter(value__gt=0)
        #    .filter(chunk__book__id=OuterRef("id"))
        #    .values("chunk__book__id")
        #    .annotate(chunk_count=Count("chunk", distinct=True))
        #    .values("chunk_count")
        # )

        book_values_query = (
            Book.objects.filter(skipped=False)
            .order_by("gutenberg_id")
            # .annotate(chunk_count=Count("chunks")).filter(chunk_count__gt=0)
            # .annotate(related_chunk_count=Subquery(chunks_with_entropy))
            .values(
                "gutenberg_id",
                "title",
                "authors__name",
                "authors__life_span",
            )
            .query
        )
        print(book_values_query)
