from django.core.management.base import BaseCommand
from textropy.models import Word, Lemma
import spacy
from django.db.models import F
from django.db.models.functions import Length


nlp = spacy.load("en_core_web_sm")


class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def handle(self, *args, **options):

        for lemma in Lemma.objects.filter(
            text__in=Word.objects.exclude(text=F("lemma__text")).values_list(
                "text", flat=True
            )
        ).order_by("-id"):
            related_lemmas = list(
                Lemma.objects.filter(
                    id__in=Word.objects.filter(text=lemma.text).values_list(
                        "lemma__id", flat=True
                    )
                )
                .annotate(len=Length("text"))
                .order_by("len")
            )

            if len(related_lemmas) == 1:
                continue

            if (
                len(set([len(related_lemma.text) for related_lemma in related_lemmas]))
                == 1
            ):
                word_count = {}
                for related_lemma in related_lemmas:
                    word_count[related_lemma.text] = len(
                        set(related_lemma.words.values_list("text", flat=True))
                        - set([related_lemma.text])
                    )

                if len(set(word_count.values())) == 1:
                    continue

                related_lemmas.sort(
                    key=lambda related_lemma: word_count[related_lemma.text],
                    reverse=True,
                )

            for related_lemma in related_lemmas[1:]:
                for word_text in related_lemma.words.values_list("text", flat=True):
                    related_lemmas[0].words.get_or_create(text=word_text)

            smallest_lemma_words = set(
                related_lemmas[0].words.all().values_list("text", flat=True)
            )
            print(lemma.id, [related_lemma.text for related_lemma in related_lemmas])

            for related_lemma in related_lemmas[1:]:
                is_subset = set(
                    related_lemma.words.all().values_list("text", flat=True)
                ).issubset(smallest_lemma_words)

                if is_subset:
                    related_lemma.delete()
