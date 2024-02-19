from django.core.management.base import BaseCommand
from textropy.models import Entropy, Vocabulary

from django.db.models import F, Window
from django.db.models.functions import PercentRank, Round
from django.db import connection


def related_chunk_query(
    chunk_ids, vocabulary_id, negative=False, percentile=95, include_zero=False
):
    order = ["asc", "desc"][int(negative)]
    gt = ["<", ">"][int(negative)]
    if include_zero:
        gt += "="
    return f"""
        SELECT *
        FROM   (SELECT "textropy_entropy"."chunk_id"      AS "col1",
                    "textropy_entropy"."related_chunk_id" AS "col2",
                    T4."book_id"                          AS "col3",
                    T4."text"                             AS "col4",
                    "textropy_entropy"."value"            AS "col5",
                    Round((( 100 * Percent_rank()
                                        OVER (
                                        ORDER BY "textropy_entropy"."value" {["asc", "desc"][int(not negative)]}) ))
                            ::
                            Numeric(1000, 15), 1)         AS "percentile"
                FROM   "textropy_entropy"
                    INNER JOIN "textropy_chunk" T4
                            ON ( "textropy_entropy"."related_chunk_id" = T4."id" )
                WHERE  ( "textropy_entropy"."vocabulary_id" = {vocabulary_id}
                        AND "textropy_entropy"."value" {gt} 0.0
                        AND "textropy_entropy"."chunk_id" IN ( {",".join(map(str,chunk_ids))} ) )
                ORDER  BY "textropy_entropy"."value" {order}) "qualify"
        WHERE  "percentile" >= {percentile}.0
        ORDER  BY "col5" {order} 
        """


class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def handle(self, *args, **options):
        print(Vocabulary.objects.values("id").order_by("-id").query)

        with connection.cursor() as cursor:
            print(
                cursor.execute(
                    related_chunk_query(
                        list(range(1000)),
                        vocabulary_id,
                        negative=True,
                    )
                ).fetchall()
            )

        print(
            Entropy.objects.filter(vocabulary_id=vocabulary_id)
            .exclude(value=0)
            # .filter(value__gte=0)
            .filter(value__lte=0)
            .annotate(
                percentile=Round(
                    100 * Window(expression=PercentRank(), order_by=F("value").desc()),
                    precision=1,
                )
            )
            .filter(percentile__gte=95, chunk_id__in=[37215])
            .order_by("value")
            .values(
                "chunk",
                "related_chunk",
                "related_chunk__book",
                "related_chunk__text",
                "percentile",
                "value",
            )
            .query
        )

        print(
            Entropy.objects.filter(vocabulary_id=vocabulary_id)
            .exclude(value=0)
            .filter(value__gte=0)
            # .filter(value__lte=0)
            .annotate(
                percentile=Round(
                    100 * Window(expression=PercentRank(), order_by=F("value").asc()),
                    precision=1,
                )
            )
            .filter(percentile__gte=95, chunk_id__in=[37215])
            .order_by("-value")
            .values(
                "chunk",
                "related_chunk",
                "related_chunk__book",
                "related_chunk__text",
                "percentile",
                "value",
            )
            .query
        )
