from django.core.management.base import BaseCommand
from unidecode import unidecode
from textropy.models import Book, Lemma
from collections import defaultdict
import spacy
from django.db import transaction


nlp = spacy.load("en_core_web_sm")


class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def handle(self, *args, **options):
        for book in Book.objects.filter(skipped=False).order_by("-id"):
            print(book.gutenberg_id, book.title)
            words_by_lemma = defaultdict(set)
            for chunk in book.chunks.all():
                for token in nlp(
                    unidecode(
                        " ".join([token for token in chunk.text.split() if token])
                    )
                ):
                    if token.is_alpha and not token.is_stop:
                        words_by_lemma[token.lemma_.lower()].add(token.lower_)

            for lemma, word_list in words_by_lemma.items():
                with transaction.atomic():
                    lemma_obj = Lemma.objects.get_or_create(text=lemma)[0]
                    for word in word_list:
                        lemma_obj.words.get_or_create(text=word)
