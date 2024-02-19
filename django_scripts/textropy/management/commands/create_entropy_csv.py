import csv

from django.core.management.base import BaseCommand
from textropy.models import Entropy


class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def handle(self, *args, **options):
        with open("entropy.csv", "w", newline="") as output_file:
            qs = Entropy.objects.values(
                "chunk__book",
                "chunk",
                "related_chunk__book",
                "related_chunk",
                "vocabulary",
                "value",
            )
            num_ent = qs.count()

            keys = list(qs.first())

            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()

            i = 0
            for vals in qs.iterator():
                dict_writer.writerow(vals)
                i += 1
                print(i, "of", num_ent)
