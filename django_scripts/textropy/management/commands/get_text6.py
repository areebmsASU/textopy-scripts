from django.core.management.base import BaseCommand
from textropy.models import Chunk, LemmaCount

from django.db.models import Count

from scipy.special import kl_div

import numpy as np


class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def handle(self, *args, **options):
        pk = np.array([1 / 2, 1 / 2])
        qk = np.array([9 / 10, 1 / 10])

        pk = np.array([1 / 2])
        qk = np.array([1 / 10])

        print(kl_div(pk, qk))

        # TODO: Some books need to be deleted manually.

        cs = [
            (0, 28554094),
            (1, 3590007),
            (2, 373849),
            (3, 36322),
            (4, 4476),
            (5, 662),
            (6, 199),
            (7, 87),
            (8, 80),
            (15, 54),
            (11, 19),
            (10, 11),
            (9, 8),
            (12, 3),
            (13, 1),
        ]

        total = 0
        for s, c in sorted(cs):
            total += c

        for s, c in sorted(cs):
            print(s, 100 * c / total)

        exit()
        for chunk in (
            Chunk.objects.filter(book__skipped=False)
            .annotate(counts=Count("lemma_counts"))
            .order_by("id")
        ):
            if chunk.id % 1000 == 0:
                print(chunk.id, chunk.counts)
