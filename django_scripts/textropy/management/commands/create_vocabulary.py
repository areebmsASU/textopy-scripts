from collections import defaultdict

from django.core.management.base import BaseCommand

from textropy.models import Book, Vocabulary


class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def handle(self, *args, **options):
        book_count = defaultdict(int)
        total_count = defaultdict(int)
        for book in Book.objects.filter(skipped=False).order_by("id"):
            for token, count in book.text_lemma_counts.items():
                book_count[token] += 1
                total_count[token] += count

        print(sum(total_count.values()))

        for token, b_count in list(book_count.items()):
            if b_count <= 10:
                book_count.pop(token)
                total_count.pop(token)
            elif len(token) < 3:
                book_count.pop(token)
                total_count.pop(token)

        vocabulary = []
        for token, count in sorted(
            total_count.items(), key=lambda x: x[1], reverse=True
        )[:5000]:
            vocabulary.append(token)

        print(sum(sorted(total_count.values(), reverse=True)[:1000]))

        mean_repr = []
        for book in Book.objects.filter(skipped=False).order_by("id"):
            total_count = 0
            vocab_count = 0
            for token, count in book.text_lemma_counts.items():
                total_count += count
                if token in vocabulary:
                    vocab_count += count
            mean_repr.append(vocab_count / total_count)
            print(
                book.gutenberg_id,
                vocab_count,
                total_count,
                round(vocab_count / total_count, 3),
            )

        print(sum(mean_repr) / len(mean_repr))

        Vocabulary.objects.create(words=vocabulary)
