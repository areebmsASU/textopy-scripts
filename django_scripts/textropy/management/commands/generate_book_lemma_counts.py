from collections import defaultdict, Counter

from django.core.management.base import BaseCommand

from textropy.models import Book, Word
from unidecode import unidecode

from string import punctuation

from django.utils import timezone


class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def handle(self, *args, **options):
        lemma_map = {
            word: lemma
            for word, lemma in Word.objects.values_list("text", "lemma__text")
        }

        trans = str.maketrans(punctuation, " " * len(punctuation))
        for book in Book.objects.filter(skipped=False).order_by("id"):
            book.text_lemma_counts = dict(
                Counter(
                    [
                        lemma_map[word]
                        for line in book.raw_text.split("\r\n")
                        for word in unidecode(line).translate(trans).lower().split()
                        if word and lemma_map.get(word)
                    ]
                )
            )
            book.text_lemma_count_date = timezone.now()
            book.save(update_fields=["text_lemma_counts", "text_lemma_count_date"])
