from django.db import models


class Subject(models.Model):
    label = models.TextField()
    gutenberg_id = models.IntegerField(unique=True, db_index=True)


class Author(models.Model):
    name = models.TextField()
    life_span = models.TextField()
    gutenberg_id = models.IntegerField(unique=True, db_index=True)


class Book(models.Model):
    gutenberg_id = models.IntegerField(unique=True, db_index=True)
    gutenberg_id_retrieved = models.DateTimeField(auto_now_add=True)

    text_retrieved_date = models.DateTimeField(null=True)
    metadata_retrieved_date = models.DateTimeField(null=True)
    raw_text = models.TextField(null=True)
    raw_metadata = models.JSONField(null=True)

    title = models.TextField(null=True)
    authors = models.ManyToManyField(Author, related_name="books")
    subjects = models.ManyToManyField(Subject, related_name="books")

    skipped = models.BooleanField(default=False)
    skipped_reason = models.TextField(null=True, default=None)

    @property
    def metadata_url(self):
        return f"https://gutenberg.org/ebooks/{self.gutenberg_id}/"

    @property
    def raw_text_url(self):
        return f"https://gutenberg.org/cache/epub/{self.gutenberg_id}/pg{self.gutenberg_id}.txt"

    def skip(self, reason):
        self.skipped = True
        self.skipped_reason = reason
        self.save(update_fields=["skipped", "skipped_reason"])


class Chunk(models.Model):
    rel_id = models.IntegerField()
    text = models.TextField()
    lemma = models.TextField()


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
