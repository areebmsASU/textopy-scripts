import os
import json
from collections import defaultdict
import psycopg2


def lambda_handler(event, context):
    connection = psycopg2.connect(
        user=os.environ["USER"],
        password=os.environ["PASSWORD"],
        host=os.environ["HOST"],
        database=os.environ["NAME"],
    )
    cursor = connection.cursor()
    cursor.execute(
        """SELECT "textropy_book"."gutenberg_id", "textropy_book"."title", "textropy_author"."name", "textropy_author"."life_span" 
        FROM "textropy_book" LEFT OUTER JOIN "textropy_book_authors" 
        ON ("textropy_book"."id" = "textropy_book_authors"."book_id") LEFT OUTER JOIN "textropy_author" ON ("textropy_book_authors"."author_id" = "textropy_author"."id") 
        WHERE NOT "textropy_book"."skipped" 
        ORDER BY "textropy_book"."gutenberg_id" ASC"""
    )
    query_results = list(cursor.fetchall())
    cursor.close()
    connection.commit()

    titles = {}
    authors = defaultdict(set)

    for gutenberg_id, title, author, life_span in query_results:
        titles[gutenberg_id] = title
        authors[gutenberg_id].add(author + " (" + life_span + ")")

    results = []
    for gutenberg_id in titles:
        results.append(
            {
                "id": gutenberg_id,
                "title": titles[gutenberg_id],
                "authors": list(authors[gutenberg_id]),
            }
        )

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
        },
        "body": json.dumps(results),
    }
