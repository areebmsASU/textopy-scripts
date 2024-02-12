from collections import Counter
from string import punctuation

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Count
from unidecode import unidecode


from textropy.models import Chunk, Word, Vocabulary


class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def handle(self, *args, **options):
        BULK_SIZE = 1000
        lemma_map = {
            word: lemma
            for word, lemma in Word.objects.values_list("text", "lemma__text")
        }

        vocabulary = Vocabulary.objects.last()
        trans = str.maketrans(punctuation, " " * len(punctuation))
        chunks = list(
            Chunk.objects.filter(book__skipped=False)
            .annotate(counts=Count("lemma_counts"))
            .filter(counts=0)
            .order_by("id")
        )
        num_chunks = len(chunks)
        for i in range(0, len(chunks), BULK_SIZE):
            with transaction.atomic():
                for chunk in chunks[i : i + BULK_SIZE]:
                    chunk.lemma_counts.create(
                        vocabulary=vocabulary,
                        counts=dict(
                            Counter(
                                [
                                    lemma_map[word]
                                    for line in chunk.text.split("\r\n")
                                    for word in unidecode(line)
                                    .translate(trans)
                                    .lower()
                                    .split()
                                    if word and lemma_map.get(word) in vocabulary.words
                                ]
                            )
                        ),
                    )
            print(i, "of", num_chunks)
