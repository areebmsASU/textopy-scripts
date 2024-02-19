import os
import json
import psycopg2


def related_chunk_query(
    chunk_ids, vocabulary_id, positive=False, percentile=95, include_zero=False
):
    order = ["asc", "desc"][int(positive)]
    gt = ["<", ">"][int(positive)]
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
                                        ORDER BY "textropy_entropy"."value" {["asc", "desc"][int(not positive)]}) ))
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


def lambda_handler(event, context):
    query_string_parameters = event.get("queryStringParameters") or {}

    positive = query_string_parameters.get("positive")
    chunks = query_string_parameters.get("chunks")
    if not chunks or not positive in ["0", "1"]:
        return {
            "statusCode": 400,
            "headers": {
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
            },
        }

    try:
        chunk_ids = map(int, chunks.split(","))
    except:
        return {
            "statusCode": 400,
            "headers": {
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
            },
        }

    connection = psycopg2.connect(
        user=os.environ["USER"],
        password=os.environ["PASSWORD"],
        host=os.environ["HOST"],
        database=os.environ["NAME"],
    )
    cursor = connection.cursor()
    cursor.execute(
        """SELECT "textropy_vocabulary"."id" 
        FROM "textropy_vocabulary" 
        ORDER BY "textropy_vocabulary"."id" DESC"""
    )
    vocabulary_id = cursor.fetchone()[0]

    cursor.execute(
        related_chunk_query(
            chunk_ids,
            vocabulary_id,
            positive=int(positive),
            percentile=os.environ["PERCENTILE"],
            include_zero=int(os.environ["ZERO"]),
        )
    )
    query_results = list(cursor.fetchall())
    cursor.close()
    connection.commit()

    results = []
    for (
        chunk_id,
        related_id,
        related_book_id,
        text,
        entropy,
        percentile,
    ) in query_results:
        results.append(
            {
                "id": chunk_id,
                "related_id": related_id,
                "related_book_id": related_book_id,
                "text": text,
                "entropy": round(entropy, 3),
                "percentile": float(percentile),
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
