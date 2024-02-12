from django.core.management.base import BaseCommand
from textropy.models import LemmaCount, Vocabulary, Entropy

from django.db import transaction

import numpy as np
from scipy.special import rel_entr


class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def handle(self, *args, **options):

        vocabulary_id = Vocabulary.objects.last().id
        completed_ids = Entropy.objects.values_list(
            "related_chunk_id", flat=True
        ).distinct()
        for related_chunk_id, related_chunk_counts in (
            LemmaCount.objects.exclude(counts__exact={})
            .exclude(chunk__in=completed_ids)
            .filter(vocabulary=vocabulary_id, chunk__book__skipped=False)
            .order_by("-id")
            .values_list("chunk", "counts")[2500:]
        ):

            words = list(related_chunk_counts)

            with transaction.atomic():

                for this_chunk_id, this_chunk_counts in (
                    LemmaCount.objects.exclude(counts__exact={})
                    .filter(
                        chunk__book__skipped=False,
                        vocabulary_id=vocabulary_id,
                        counts__has_any_keys=words,
                        chunk__book__gutenberg_id=3300,
                    )
                    .exclude(chunk_id=related_chunk_id)
                    .values_list("chunk", "counts")
                ):

                    print(
                        Entropy.objects.create(
                            chunk_id=int(this_chunk_id),
                            related_chunk_id=int(related_chunk_id),
                            vocabulary_id=vocabulary_id,
                            value=sum(
                                rel_entr(
                                    np.array(
                                        [
                                            this_chunk_counts.get(word, 0)
                                            for word in words
                                        ]
                                    ),
                                    np.array(
                                        [related_chunk_counts[word] for word in words]
                                    ),
                                )
                            ),
                        )
                    )
