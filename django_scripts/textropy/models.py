from collections import defaultdict
from time import sleep

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone


try:
    import requests as r
    from bs4 import BeautifulSoup
except ModuleNotFoundError:
    pass
BASE_URL = "https://gutenberg.org"


class BookList(models.Model):
    MAX_BOOK_IDS_PER_PAGE = 25
    gutenberg_id = models.IntegerField(unique=True, db_index=True)

    class Meta:
        abstract = True

    def get_books(self):
        page_book_ids = []
        num_book_ids = -1
        while num_book_ids == -1 or (
            len(page_book_ids) != num_book_ids
            and len(page_book_ids) % self.MAX_BOOK_IDS_PER_PAGE == 0
        ):
            sleep(1)
            num_book_ids = len(page_book_ids)
            book_list_page = r.get(
                self.book_list_url + f"?start_index={num_book_ids+1}"
            )
            for link in BeautifulSoup(book_list_page.text, "html.parser").find_all("a"):
                if (
                    "ebooks" in link.get("href", "")
                    and link["href"].split("/")[2].isdigit()
                    and link["href"].split("/")[2] not in page_book_ids
                ):
                    Book.objects.get_or_create(gutenberg_id=link["href"].split("/")[2])
                    page_book_ids.append(link["href"].split("/")[2])
        return page_book_ids


class Subject(BookList):
    label = models.TextField()

    @property
    def book_list_url(self):
        return f"{BASE_URL}/ebooks/subject/{self.gutenberg_id}/"


class Author(BookList):
    name = models.TextField()
    life_span = models.TextField()

    @property
    def book_list_url(self):
        return f"{BASE_URL}/ebooks/author/{self.gutenberg_id}/"


class Book(models.Model):
    SKIPPED_CHOICES = {
        "NO_AUTHOR": "Author Missing",
        "FORMAT": "Not a text",
        "LANG": "Not English",
        "DUPLICATE": "Already Exists",
    }

    gutenberg_id = models.IntegerField(unique=True, db_index=True)
    gutenberg_id_retrieved = models.DateTimeField(auto_now_add=True)

    text_retrieved_date = models.DateTimeField(null=True)
    metadata_retrieved_date = models.DateTimeField(null=True)
    raw_text = models.TextField(null=True)
    raw_metadata = models.JSONField(null=True)

    text_lemma_counts = models.JSONField(null=True)
    text_lemma_count_date = models.DateTimeField(null=True)

    title = models.TextField(null=True)
    authors = models.ManyToManyField(Author, related_name="books")
    subjects = models.ManyToManyField(Subject, related_name="books")

    skipped = models.BooleanField(default=False)
    skipped_reason = models.CharField(
        null=True, default=None, choices=SKIPPED_CHOICES, max_length=15
    )

    @property
    def metadata_url(self):
        return f"{BASE_URL}/ebooks/{self.gutenberg_id}/"

    @property
    def raw_text_url(self):
        return f"{BASE_URL}/cache/epub/{self.gutenberg_id}/pg{self.gutenberg_id}.txt"

    def skip(self, reason):
        self.skipped = True
        self.skipped_reason = reason
        self.save(update_fields=["skipped", "skipped_reason"])

    def get_raw_metadata(self, force_refresh=False):
        if self.raw_metadata and not force_refresh:
            return False

        metadata = defaultdict(list)
        for tr in (
            BeautifulSoup(r.get(self.metadata_url).content, "html.parser")
            .find("table", class_="bibrec")
            .find_all("tr")
        ):
            key = tr.find("th")
            if key is not None:
                value = tr.find("td")
                a = value.find("a")
                href = a["href"] if a else None
                key = (
                    key.text.lower()
                    .replace(" ", "-")
                    .replace(".", "")
                    .replace("-", "_")
                )
                for line in tr.find("td").get_text(separator="\n").split("\n"):
                    if line:
                        metadata[key].append(line)
                if href:
                    metadata[key + "_link"].append(href)

        self.raw_metadata = dict(metadata)
        self.metadata_retrieved_date = timezone.now()
        self.title = self.raw_metadata["title"][0].strip()

        update_fields = ["raw_metadata", "metadata_retrieved_date", "title"]
        if self.skipped:
            self.skipped = False
            self.skipped_reason = None
            update_fields.extend(["skipped", "skipped_reason"])

        self.save(update_fields=update_fields)
        return True

    def add_authors(self):
        authors = self.raw_metadata.get("author", [])
        for i in range(len(authors)):
            life_span = authors[i].split(", ")[-1]
            if "-" not in life_span:
                continue
            name = authors[i].replace(", " + life_span, "")
            gutenberg_id = self.raw_metadata["author_link"][i].split("/")[-1]
            author, _ = Author.objects.get_or_create(
                name=name, gutenberg_id=gutenberg_id, life_span=life_span
            )
            self.authors.add(author)

    def add_subjects(self):
        subjects = self.raw_metadata.get("subject", [])
        for i in range(len(subjects)):
            subject, _ = Subject.objects.get_or_create(
                label=subjects[i],
                gutenberg_id=self.raw_metadata["subject_link"][i].split("/")[-1],
            )
            self.subjects.add(subject)

    def get_raw_text(self):
        self.raw_text = BeautifulSoup(
            r.get(self.raw_text_url).content, "html.parser"
        ).text
        self.text_retrieved_date = timezone.now()
        self.save(update_fields=["raw_text", "text_retrieved_date"])


class Chunk(models.Model):
    CHUNK_SIZE = 3
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="chunks")
    rel_id = models.IntegerField()
    text = models.TextField()


class Vocabulary(models.Model):
    words = ArrayField(models.TextField())
    date_created = models.DateTimeField(auto_now_add=True)


class Entropy(models.Model):
    "the excess information from related_chunk (Q) when current information is chunk (P)"
    chunk = models.ForeignKey(Chunk, on_delete=models.CASCADE, related_name="entropies")
    related_chunk = models.ForeignKey(Chunk, on_delete=models.CASCADE, related_name="+")
    vocabulary = models.ForeignKey(
        Vocabulary, on_delete=models.CASCADE, related_name="entropies"
    )
    value = models.FloatField()

    class Meta:
        unique_together = [
            ["chunk", "related_chunk", "vocabulary"],
        ]

    def __str__(self) -> str:
        return f"{self.chunk_id} --{self.value}--> {self.related_chunk_id}"


class LemmaCount(models.Model):
    chunk = models.ForeignKey(
        Chunk, on_delete=models.CASCADE, related_name="lemma_counts"
    )
    vocabulary = models.ForeignKey(
        Vocabulary, on_delete=models.CASCADE, related_name="lemma_counts"
    )
    counts = models.JSONField()

    class Meta:
        unique_together = [
            ["chunk", "vocabulary"],
        ]


class Line(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="lines")
    chunk = models.ForeignKey(
        Chunk, on_delete=models.SET_NULL, related_name="lines", null=True
    )
    rel_id = models.IntegerField()
    text = models.TextField(null=True, default=None)

    class Meta:
        unique_together = [
            ["rel_id", "book"],
        ]


class Lemma(models.Model):
    text = models.TextField(unique=True, db_index=True)


class Word(models.Model):
    text = models.TextField(db_index=True)
    lemma = models.ForeignKey(Lemma, on_delete=models.CASCADE, related_name="words")

    class Meta:
        unique_together = [
            ["text", "lemma"],
        ]
