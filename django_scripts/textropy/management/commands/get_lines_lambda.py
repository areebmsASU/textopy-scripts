from django.core.management.base import BaseCommand
from textropy.models import Book, Line

from django.db.models import Count, Subquery, OuterRef


class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def handle(self, *args, **options):

        # TODO add value related fitler

        print(
            Line.objects.filter(book__gutenberg_id=3300, rel_id__gte=0)
            .values("rel_id", "text")
            .order_by("rel_id")[:30]
            .query
        )
